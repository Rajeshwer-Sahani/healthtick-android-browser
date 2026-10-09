#!/usr/bin/env python3
"""Local HTTP API and MJPEG relay for a single Android Emulator."""

from __future__ import annotations

import json
import logging
import math
import os
import re
import shlex
import signal
import subprocess
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
ADB = os.environ.get(
    "ADB_PATH",
    str(Path.home() / "Library/Android/sdk/platform-tools/adb"),
)
SCRCPY = os.environ.get("SCRCPY_PATH", "scrcpy")
FFMPEG = os.environ.get("FFMPEG_PATH", "ffmpeg")
SERIAL_OVERRIDE = os.environ.get("ADB_SERIAL")
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))
MAX_BODY_BYTES = 16_384
BOUNDARY = b"frame"
FRAME_STALE_SECONDS = 5
STARTUP_TIMEOUT_SECONDS = 15
STARTUP_RETRY_DELAY_SECONDS = 2

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
LOG = logging.getLogger("healthtick.video")


class ApiError(Exception):
    def __init__(self, status: int, message: str):
        super().__init__(message)
        self.status = status


def run_adb(args: list[str], timeout: float = 8) -> bytes:
    try:
        result = subprocess.run(
            [ADB, *args],
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as error:
        raise ApiError(503, f"ADB executable is unavailable: {ADB}") from error
    except subprocess.TimeoutExpired as error:
        raise ApiError(504, "ADB command timed out") from error
    if result.returncode:
        message = result.stderr.decode(errors="replace").strip()
        raise ApiError(502, message or "ADB command failed")
    return result.stdout


def connected_emulator() -> str:
    output = run_adb(["devices"])
    devices = [
        parts[0]
        for line in output.decode(errors="replace").splitlines()[1:]
        if len(parts := line.split()) >= 2
        and parts[0].startswith("emulator-")
        and parts[1] == "device"
    ]
    if SERIAL_OVERRIDE:
        if SERIAL_OVERRIDE not in devices:
            raise ApiError(503, f"Configured emulator {SERIAL_OVERRIDE} is unavailable")
        return SERIAL_OVERRIDE
    if not devices:
        raise ApiError(503, "No connected Android Emulator is available")
    if len(devices) != 1:
        raise ApiError(409, "Multiple emulators are connected; set ADB_SERIAL")
    return devices[0]


def display_size(serial: str) -> tuple[int, int]:
    output = run_adb(["-s", serial, "shell", "wm", "size"]).decode(
        errors="replace"
    )
    sizes = re.findall(r"(?:Physical|Override) size:\s*(\d+)x(\d+)", output)
    if not sizes:
        raise ApiError(502, f"Could not read emulator display size: {output.strip()}")
    return tuple(map(int, sizes[-1]))


class VideoPipeline:
    """One device-side scrcpy capture shared by all connected browser clients."""

    def __init__(self) -> None:
        self.condition = threading.Condition()
        self.lifecycle_lock = threading.Lock()
        self.frame: bytes | None = None
        self.sequence = 0
        self.live_frame_sequence = 0
        self.last_frame_time: float | None = None
        self.started = False
        self.starting = False
        self.closed = False
        self.generation = 0
        self.directory: tempfile.TemporaryDirectory[str] | None = None
        self.ffmpeg: subprocess.Popen[bytes] | None = None
        self.scrcpy: subprocess.Popen[bytes] | None = None
        self.ffmpeg_log: Any | None = None
        self.scrcpy_log: Any | None = None
        self.reader: threading.Thread | None = None
        self.reader_error: str | None = None
        self.start_error: ApiError | None = None
        self.retry_after = 0.0

    def _publish(self, frame: bytes, generation: int) -> None:
        with self.condition:
            if self.closed or generation != self.generation:
                return
            self.frame = frame
            self.sequence += 1
            sequence = self.sequence
            self.live_frame_sequence = self.sequence
            self.last_frame_time = time.monotonic()
            first_frame = self.starting
            self.starting = False
            self.start_error = None
            self.retry_after = 0.0
            self.condition.notify_all()
        if first_frame:
            LOG.info(
                "First live JPEG published: generation=%d sequence=%d bytes=%d at=%s",
                generation, sequence, len(frame),
                time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            )

    def _stale_reason_locked(self) -> str | None:
        if self.closed:
            return "pipeline is shutting down"
        if not self.started:
            return "pipeline is not running"
        if self.starting:
            return None
        if self.reader_error:
            return f"JPEG reader stopped: {self.reader_error}"
        if self.ffmpeg is None:
            return "FFmpeg process is missing"
        if self.ffmpeg.poll() is not None:
            return f"FFmpeg exited with status {self.ffmpeg.returncode}"
        if self.scrcpy is None:
            return "scrcpy process is missing"
        if self.scrcpy.poll() is not None:
            return f"scrcpy exited with status {self.scrcpy.returncode}"
        if self.reader is None or not self.reader.is_alive():
            return "JPEG reader thread is not running"
        if self.last_frame_time is None:
            return "no live frame has been published"
        silent_for = time.monotonic() - self.last_frame_time
        if silent_for > FRAME_STALE_SECONDS:
            return f"no JPEG frame published for {silent_for:.1f} seconds"
        return None

    def is_healthy(self) -> bool:
        with self.condition:
            return (
                self._stale_reason_locked() is None
                and self.live_frame_sequence > 0
            )

    @staticmethod
    def _log_tail(log_file: Any | None) -> str:
        if log_file is None:
            return ""
        try:
            log_file.flush()
            log_file.seek(0, os.SEEK_END)
            size = log_file.tell()
            log_file.seek(max(0, size - 4096))
            return log_file.read().decode(errors="replace").strip()
        except (OSError, ValueError):
            return ""

    def _close_log(self, log_file: Any | None, name: str) -> None:
        details = self._log_tail(log_file)
        if details:
            LOG.warning("%s stderr: %s", name, details)
        if log_file is not None:
            log_file.close()

    @staticmethod
    def _stop_process(process: subprocess.Popen[bytes] | None) -> None:
        if process is None or process.poll() is not None:
            return
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        except OSError:
            process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            except OSError:
                process.kill()
            process.wait()
        except ProcessLookupError:
            pass

    def _stop_resources_locked(self, permanent: bool = False) -> None:
        reader = self.reader
        with self.condition:
            self.generation += 1
            generation = self.generation
            self.started = False
            self.starting = False
            self.reader = None
            self.condition.notify_all()
        self._stop_process(self.scrcpy)
        self._stop_process(self.ffmpeg)
        if reader is not None and reader is not threading.current_thread():
            reader.join(timeout=2)
        if self.ffmpeg is not None and self.ffmpeg.stdout is not None:
            self.ffmpeg.stdout.close()
        self.scrcpy = None
        self.ffmpeg = None
        self._close_log(self.scrcpy_log, "scrcpy")
        self._close_log(self.ffmpeg_log, "FFmpeg")
        self.scrcpy_log = None
        self.ffmpeg_log = None
        if self.directory is not None:
            self.directory.cleanup()
            self.directory = None
        if permanent:
            with self.condition:
                self.closed = True
        LOG.info("Video pipeline stopped: generation=%d permanent=%s", generation, permanent)
        with self.condition:
            self.condition.notify_all()

    def _launch_locked(self) -> int:
        with self.condition:
            self.generation += 1
            generation = self.generation
            self.started = True
            self.starting = True
            self.frame = None
            self.live_frame_sequence = 0
            self.last_frame_time = None
            self.reader_error = None
            self.start_error = None
            self.reader = None
        try:
            serial = connected_emulator()
            display_size(serial)
            self.directory = tempfile.TemporaryDirectory(prefix="healthtick-stream-")
            fifo = Path(self.directory.name) / "scrcpy.mkv"
            os.mkfifo(fifo)
            self.ffmpeg_log = tempfile.TemporaryFile()
            self.scrcpy_log = tempfile.TemporaryFile()

            self.ffmpeg = subprocess.Popen(
                [
                    FFMPEG, "-hide_banner", "-loglevel", "warning",
                    "-i", str(fifo), "-an", "-fps_mode", "passthrough",
                    "-c:v", "mjpeg", "-q:v", "7", "-f", "image2pipe",
                    "-vcodec", "mjpeg", "pipe:1",
                ],
                stdout=subprocess.PIPE,
                stderr=self.ffmpeg_log,
                bufsize=0,
                start_new_session=True,
            )
            env = os.environ.copy()
            env["PATH"] = f"{Path(ADB).parent}:{env.get('PATH', '')}"
            self.scrcpy = subprocess.Popen(
                [
                    SCRCPY, "--no-window", "--no-playback", "--no-control",
                    "--no-audio", "--max-size=720", "--max-fps=15",
                    "--video-bit-rate=2M",
                    f"--record={fifo}", "--record-format=mkv",
                ],
                stdout=subprocess.DEVNULL,
                stderr=self.scrcpy_log,
                env=env,
                start_new_session=True,
            )
            self.reader = threading.Thread(
                target=self._read_jpegs,
                args=(generation,),
                name=f"mjpeg-reader-{generation}",
                daemon=True,
            )
            self.reader.start()
            LOG.info(
                "Video pipeline started: generation=%d device=%s scrcpy_pid=%d ffmpeg_pid=%d fifo=%s",
                generation, serial, self.scrcpy.pid, self.ffmpeg.pid, fifo,
            )
            LOG.info("JPEG reader started: generation=%d", generation)
            with self.condition:
                self.condition.notify_all()
            return generation
        except Exception as error:
            details = "; ".join(
                part for part in (
                    str(error),
                    self._log_tail(self.scrcpy_log),
                    self._log_tail(self.ffmpeg_log),
                ) if part
            )
            self._stop_resources_locked()
            message = f"Could not start live screen capture: {details}"
            LOG.exception("Video pipeline startup failed: generation=%d", generation)
            status = error.status if isinstance(error, ApiError) else 503
            self.start_error = ApiError(status, message)
            self.retry_after = time.monotonic() + STARTUP_RETRY_DELAY_SECONDS
            raise self.start_error from error

    def start(self) -> None:
        with self.lifecycle_lock:
            with self.condition:
                if self.closed:
                    raise ApiError(503, "Video pipeline is shutting down")
                reason = self._stale_reason_locked()
                if self.started and reason is None:
                    generation = self.generation
                else:
                    if (
                        not self.started
                        and self.start_error is not None
                        and time.monotonic() < self.retry_after
                    ):
                        raise ApiError(
                            self.start_error.status,
                            f"Recent capture startup failed; retrying shortly: {self.start_error}",
                        )
                    if self.started:
                        LOG.warning(
                            "Video pipeline stale: generation=%d reason=%s",
                            self.generation, reason,
                        )
                        self._stop_resources_locked()
                    LOG.info("Restarting video capture after: %s", reason)
                    generation = self._launch_locked()
        self._wait_for_live_frame(generation)

    def _wait_for_live_frame(self, generation: int) -> None:
        deadline = time.monotonic() + STARTUP_TIMEOUT_SECONDS
        failure: str | None = None
        with self.condition:
            while generation == self.generation and not self.closed:
                if self.live_frame_sequence > 0:
                    reason = self._stale_reason_locked()
                    if reason is None:
                        return
                    failure = reason
                    break
                if self.reader_error:
                    failure = self.reader_error
                    break
                for name, process in (("FFmpeg", self.ffmpeg), ("scrcpy", self.scrcpy)):
                    if process is not None and process.poll() is not None:
                        failure = f"{name} exited with status {process.returncode}"
                        break
                if failure:
                    break
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    failure = f"no live JPEG frame within {STARTUP_TIMEOUT_SECONDS} seconds"
                    break
                self.condition.wait(min(remaining, 0.25))
            if failure is None:
                failure = "capture pipeline changed while waiting for its first live frame"
        with self.lifecycle_lock:
            if generation == self.generation:
                details = "; ".join(
                    part for part in (
                        failure,
                        self._log_tail(self.scrcpy_log),
                        self._log_tail(self.ffmpeg_log),
                    ) if part
                )
                LOG.error("Video pipeline startup did not produce a live frame: %s", details)
                self._stop_resources_locked()
                failure = details
                self.start_error = ApiError(503, f"Live Android video unavailable: {details}")
                self.retry_after = time.monotonic() + STARTUP_RETRY_DELAY_SECONDS
        raise ApiError(503, f"Live Android video unavailable: {failure}")

    def _read_jpegs(self, generation: int) -> None:
        ffmpeg = self.ffmpeg
        if ffmpeg is None or ffmpeg.stdout is None:
            with self.condition:
                if generation == self.generation:
                    self.reader_error = "FFmpeg stdout is unavailable"
                    self.starting = False
                    self.condition.notify_all()
            return
        stdout = ffmpeg.stdout
        buffer = bytearray()
        start = b"\xff\xd8"
        end = b"\xff\xd9"
        reason = "FFmpeg output closed"
        try:
            while generation == self.generation:
                chunk = stdout.read(65536)
                if not chunk:
                    break
                buffer.extend(chunk)
                while True:
                    frame_start = buffer.find(start)
                    if frame_start < 0:
                        if len(buffer) > 1:
                            del buffer[:-1]
                        break
                    if frame_start:
                        del buffer[:frame_start]
                    frame_end = buffer.find(end, 2)
                    if frame_end < 0:
                        if len(buffer) > 20_000_000:
                            LOG.error("Discarding oversized incomplete JPEG from FFmpeg")
                            buffer.clear()
                        break
                    frame_end += len(end)
                    self._publish(bytes(buffer[:frame_end]), generation)
                    del buffer[:frame_end]
        except Exception as error:
            reason = f"JPEG reader failed: {error}"
            LOG.exception("JPEG reader failed: generation=%d", generation)
        finally:
            with self.condition:
                if generation == self.generation and not self.closed:
                    self.reader_error = reason
                    self.starting = False
                    self.condition.notify_all()
                    LOG.error("JPEG reader stopped: generation=%d reason=%s", generation, reason)

    def current(self) -> tuple[int, bytes | None]:
        with self.condition:
            return self.sequence, self.frame

    def wait_for_frame(self, after: int, timeout: float = 20) -> tuple[int, bytes] | None:
        deadline = time.monotonic() + timeout
        with self.condition:
            while not self.closed:
                if self.frame is not None and self.sequence > after:
                    return self.sequence, self.frame
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return None
                self.condition.wait(remaining)
        return None

    def stop(self) -> None:
        with self.lifecycle_lock:
            if not self.closed:
                self._stop_resources_locked(permanent=True)


VIDEO = VideoPipeline()


def map_point(point: Any, width: int, height: int) -> tuple[int, int]:
    if not isinstance(point, dict):
        raise ApiError(400, "Each point must be an object with normalized x and y")
    x, y = point.get("x"), point.get("y")
    if (
        isinstance(x, bool) or not isinstance(x, (int, float))
        or isinstance(y, bool) or not isinstance(y, (int, float))
        or not math.isfinite(x) or not math.isfinite(y)
        or not 0 <= x < 1 or not 0 <= y < 1
    ):
        raise ApiError(400, "Normalized coordinates must be finite values in [0, 1)")
    return min(int(x * width), width - 1), min(int(y * height), height - 1)


def validate_frame_dimensions(point: Any, width: int, height: int) -> None:
    if not isinstance(point, dict):
        raise ApiError(400, "Captured frame dimensions are invalid")
    frame_width = point.get("frameWidth")
    frame_height = point.get("frameHeight")
    if (
        isinstance(frame_width, bool) or not isinstance(frame_width, int)
        or isinstance(frame_height, bool) or not isinstance(frame_height, int)
        or frame_width <= 0 or frame_height <= 0
    ):
        raise ApiError(400, "Captured frame dimensions are invalid")
    if abs(frame_width / frame_height - width / height) > 0.01:
        raise ApiError(400, "Captured frame aspect ratio does not match Android display")


def key_code(key: str) -> str:
    codes = {
        "Backspace": "67",
        "Enter": "66",
        " ": "62",
        "Tab": "61",
        "Escape": "111",
        "ArrowUp": "19",
        "ArrowDown": "20",
        "ArrowLeft": "21",
        "ArrowRight": "22",
        "Home": "3",
        "Back": "4",
        "Delete": "112",
    }
    if key in codes:
        return codes[key]
    match = re.fullmatch(r"[a-zA-Z0-9]", key)
    if match:
        return str(ord(key.upper()) - ord("A") + 29) if key.isalpha() else str(
            {"0": 7, "1": 8, "2": 9, "3": 10, "4": 11,
             "5": 12, "6": 13, "7": 14, "8": 15, "9": 16}[key]
        )
    raise ApiError(400, f"Unsupported keyboard key: {key!r}")


class Handler(BaseHTTPRequestHandler):
    server_version = "HealthTickExperiment/0.1"

    def _json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> dict[str, Any]:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError as error:
            raise ApiError(400, "Invalid Content-Length") from error
        if length <= 0 or length > MAX_BODY_BYTES:
            raise ApiError(400, "Invalid request body size")
        try:
            data = json.loads(self.rfile.read(length))
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            raise ApiError(400, "Request body must be valid JSON") from error
        if not isinstance(data, dict):
            raise ApiError(400, "JSON body must be an object")
        return data

    def _input_request(self, body: dict[str, Any]) -> tuple[str, int, int]:
        serial = connected_emulator()
        width, height = display_size(serial)
        received = time.perf_counter_ns()
        return serial, width, height

    def _run_input(
        self, serial: str, args: list[str], received: int, sequence_before: int
    ) -> None:
        issued = time.perf_counter_ns()
        run_adb(["-s", serial, "shell", "input", *args])
        completed = time.perf_counter_ns()
        self._json(200, {
            "device": serial,
            "frame_sequence_before": sequence_before,
            "backend_received_unix_ms": received / 1_000_000,
            "adb_issued_unix_ms": issued / 1_000_000,
            "adb_completed_unix_ms": completed / 1_000_000,
            "backend_to_adb_ms": round((issued - received) / 1_000_000, 2),
            "adb_duration_ms": round((completed - issued) / 1_000_000, 2),
        })

    def do_GET(self) -> None:
        route = self.path.split("?", 1)[0]
        if route == "/api/health":
            try:
                serial = connected_emulator()
                width, height = display_size(serial)
                self._json(200, {
                    "device": serial,
                    "width": width,
                    "height": height,
                    "video_ready": VIDEO.is_healthy(),
                })
            except ApiError as error:
                self._json(error.status, {"error": str(error)})
            return
        if route == "/api/metrics":
            sequence, _ = VIDEO.current()
            self._json(200, {"frame_sequence": sequence})
            return
        if route == "/stream.mjpg":
            try:
                VIDEO.start()
            except ApiError as error:
                self._json(error.status, {"error": str(error)})
                return
            self.send_response(200)
            self.send_header(
                "Content-Type", "multipart/x-mixed-replace; boundary=frame"
            )
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
            self.send_header("Connection", "close")
            self.end_headers()
            sequence = 0
            while not VIDEO.closed:
                result = VIDEO.wait_for_frame(sequence, timeout=1)
                if result is None:
                    try:
                        VIDEO.start()
                    except ApiError as error:
                        LOG.error("Closing MJPEG client because recovery failed: %s", error)
                        break
                    continue
                sequence, frame = result
                header = (
                    b"--frame\r\nContent-Type: image/jpeg\r\nContent-Length: "
                    + str(len(frame)).encode()
                    + b"\r\n\r\n"
                )
                try:
                    self.wfile.write(header + frame + b"\r\n")
                    self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError, TimeoutError):
                    LOG.debug("MJPEG client disconnected")
                    break
            return
        if route == "/" or route.startswith("/assets/"):
            self._static(route)
            return
        self._json(404, {"error": "Not found"})

    def do_HEAD(self) -> None:
        if self.path.split("?", 1)[0] != "/stream.mjpg":
            self.send_error(404, "Not found")
            return
        try:
            VIDEO.start()
        except ApiError as error:
            body = json.dumps({"error": str(error)}).encode()
            self.send_response(error.status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            return
        self.send_response(200)
        self.send_header(
            "Content-Type", "multipart/x-mixed-replace; boundary=frame"
        )
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Connection", "close")
        self.end_headers()

    def _static(self, route: str) -> None:
        dist = ROOT / "frontend" / "dist"
        base = dist.resolve()
        requested = (base / route.lstrip("/")).resolve()
        if not requested.is_relative_to(base):
            self._json(404, {"error": "Not found"})
            return
        if route == "/" or not requested.is_file():
            requested = base / "index.html"
        try:
            body = requested.read_bytes()
        except FileNotFoundError:
            self._json(404, {"error": "Frontend build is missing; run npm run build"})
            return
        content_type = {
            ".html": "text/html; charset=utf-8",
            ".js": "text/javascript; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".svg": "image/svg+xml",
        }.get(requested.suffix, "application/octet-stream")
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        try:
            body = self._body()
            route = self.path.split("?", 1)[0]
            serial, width, height = self._input_request(body)
            sequence_before, _ = VIDEO.current()

            if route == "/api/input/tap":
                validate_frame_dimensions(body, width, height)
                x, y = map_point(body, width, height)
                args = ["tap", str(x), str(y)]
            elif route == "/api/input/swipe":
                points = body.get("points")
                duration = body.get("duration_ms", 450)
                if not isinstance(points, list) or not 2 <= len(points) <= 64:
                    raise ApiError(400, "Swipe requires between 2 and 64 points")
                if (
                    isinstance(duration, bool) or not isinstance(duration, int)
                    or not 80 <= duration <= 2000
                ):
                    raise ApiError(400, "duration_ms must be an integer from 80 to 2000")
                validate_frame_dimensions(points[0], width, height)
                first = map_point(points[0], width, height)
                last = map_point(points[-1], width, height)
                args = [
                    "swipe", str(first[0]), str(first[1]), str(last[0]),
                    str(last[1]), str(duration),
                ]
            elif route == "/api/input/scroll":
                delta_x, delta_y = body.get("delta_x", 0), body.get("delta_y", 0)
                if any(
                    isinstance(value, bool) or not isinstance(value, (int, float))
                    or not math.isfinite(value)
                    for value in (delta_x, delta_y)
                ) or (delta_x == 0 and delta_y == 0):
                    raise ApiError(400, "Scroll deltas must be finite and non-zero")
                if abs(delta_y) >= abs(delta_x):
                    x = width // 2
                    start_y, end_y = (
                        (int(height * 0.72), int(height * 0.38))
                        if delta_y > 0
                        else (int(height * 0.38), int(height * 0.72))
                    )
                    args = ["swipe", str(x), str(start_y), str(x), str(end_y), "350"]
                else:
                    y = height // 2
                    start_x, end_x = (
                        (int(width * 0.72), int(width * 0.38))
                        if delta_x > 0
                        else (int(width * 0.38), int(width * 0.72))
                    )
                    args = ["swipe", str(start_x), str(y), str(end_x), str(y), "350"]
            elif route == "/api/input/key":
                key = body.get("key")
                if not isinstance(key, str) or len(key) > 32:
                    raise ApiError(400, "key must be a supported key name")
                args = ["keyevent", key_code(key)]
            elif route == "/api/input/text":
                text = body.get("text")
                if not isinstance(text, str) or not text or len(text) > 256:
                    raise ApiError(400, "text must contain 1 to 256 characters")
                encoded = text.replace("%", "%25").replace(" ", "%s")
                args = ["text", shlex.quote(encoded)]
            else:
                self._json(404, {"error": "Unknown input endpoint"})
                return

            self._run_input(serial, args, time.perf_counter_ns(), sequence_before)
        except ApiError as error:
            self._json(error.status, {"error": str(error)})

    def log_message(self, format_string: str, *args: Any) -> None:
        print(format_string % args, flush=True)


class Server(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def shutdown(signum: int, frame: Any) -> None:
    VIDEO.stop()
    raise SystemExit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    server = Server((HOST, PORT), Handler)
    LOG.info("HealthTick server listening on http://%s:%d", HOST, PORT)
    try:
        server.serve_forever()
    finally:
        VIDEO.stop()
        server.server_close()

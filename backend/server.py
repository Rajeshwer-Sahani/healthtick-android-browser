#!/usr/bin/env python3
"""Local HTTP API and MJPEG relay for a single Android Emulator."""

from __future__ import annotations

import json
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


def jpeg_from_png(png: bytes) -> bytes:
    try:
        result = subprocess.run(
            [
                FFMPEG, "-hide_banner", "-loglevel", "error",
                "-f", "image2pipe", "-vcodec", "png", "-i", "pipe:0",
                "-frames:v", "1", "-q:v", "7", "-f", "image2pipe",
                "-vcodec", "mjpeg", "pipe:1",
            ],
            input=png,
            capture_output=True,
            timeout=10,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as error:
        raise ApiError(503, "FFmpeg could not create an initial screen frame") from error
    if result.returncode or not result.stdout.startswith(b"\xff\xd8"):
        details = result.stderr.decode(errors="replace").strip()
        raise ApiError(502, details or "FFmpeg returned an invalid initial frame")
    return result.stdout


class VideoPipeline:
    """One device-side scrcpy capture shared by all connected browser clients."""

    def __init__(self) -> None:
        self.condition = threading.Condition()
        self.frame: bytes | None = None
        self.sequence = 0
        self.started = False
        self.closed = False
        self.directory: tempfile.TemporaryDirectory[str] | None = None
        self.ffmpeg: subprocess.Popen[bytes] | None = None
        self.scrcpy: subprocess.Popen[bytes] | None = None
        self.logs: list[Any] = []
        self.reader: threading.Thread | None = None
        self.start_error: ApiError | None = None

    def _publish(self, frame: bytes) -> None:
        with self.condition:
            self.frame = frame
            self.sequence += 1
            self.condition.notify_all()

    def start(self) -> None:
        with self.condition:
            if self.started:
                if self.start_error:
                    raise self.start_error
                return
            self.started = True

        try:
            serial = connected_emulator()
            width, height = display_size(serial)
            png = run_adb(["-s", serial, "exec-out", "screencap", "-p"], timeout=15)
            self._publish(jpeg_from_png(png))

            self.directory = tempfile.TemporaryDirectory(prefix="healthtick-stream-")
            fifo = Path(self.directory.name) / "scrcpy.mkv"
            os.mkfifo(fifo)
            ffmpeg_log = tempfile.TemporaryFile()
            scrcpy_log = tempfile.TemporaryFile()
            self.logs.extend((ffmpeg_log, scrcpy_log))

            self.ffmpeg = subprocess.Popen(
                [
                    FFMPEG, "-hide_banner", "-loglevel", "warning",
                    "-i", str(fifo), "-an", "-fps_mode", "passthrough",
                    "-c:v", "mjpeg", "-q:v", "7", "-f", "image2pipe",
                    "-vcodec", "mjpeg", "pipe:1",
                ],
                stdout=subprocess.PIPE,
                stderr=ffmpeg_log,
                bufsize=0,
            )
            time.sleep(0.15)
            if self.ffmpeg.poll() is not None:
                raise ApiError(502, "FFmpeg exited before opening the capture stream")

            env = os.environ.copy()
            env["PATH"] = f"{Path(ADB).parent}:{env.get('PATH', '')}"
            self.scrcpy = subprocess.Popen(
                [
                    SCRCPY, "--no-window", "--no-playback", "--no-control",
                    "--no-audio", "--max-size=1080", "--max-fps=30",
                    f"--record={fifo}", "--record-format=mkv",
                ],
                stdout=subprocess.DEVNULL,
                stderr=scrcpy_log,
                env=env,
            )
            self.reader = threading.Thread(
                target=self._read_jpegs, name="mjpeg-reader", daemon=True
            )
            self.reader.start()
        except ApiError as error:
            self.start_error = error
            self.stop()
            raise
        except OSError as error:
            self.start_error = ApiError(503, f"Could not start screen capture: {error}")
            self.stop()
            raise self.start_error from error
        except Exception:
            self.stop()
            raise

        with self.condition:
            self.condition.notify_all()

    def _read_jpegs(self) -> None:
        assert self.ffmpeg is not None and self.ffmpeg.stdout is not None
        buffer = bytearray()
        start = b"\xff\xd8"
        end = b"\xff\xd9"
        while not self.closed:
            chunk = self.ffmpeg.stdout.read(65536)
            if not chunk:
                return
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
                        buffer.clear()
                    break
                frame_end += len(end)
                self._publish(bytes(buffer[:frame_end]))
                del buffer[:frame_end]

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
        self.closed = True
        for process in (self.scrcpy, self.ffmpeg):
            if process is not None and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
        for log in self.logs:
            log.close()
        if self.directory:
            self.directory.cleanup()
            self.directory = None
        with self.condition:
            self.condition.notify_all()


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
                    "video_ready": VIDEO.frame is not None,
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
            try:
                while not VIDEO.closed:
                    result = VIDEO.wait_for_frame(sequence, timeout=20)
                    if result is None:
                        self.wfile.write(b"\r\n")
                        self.wfile.flush()
                        continue
                    sequence, frame = result
                    header = (
                        b"--frame\r\nContent-Type: image/jpeg\r\nContent-Length: "
                        + str(len(frame)).encode()
                        + b"\r\n\r\n"
                    )
                    self.wfile.write(header + frame + b"\r\n")
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError, TimeoutError):
                pass
            return
        if route == "/" or route.startswith("/assets/"):
            self._static(route)
            return
        self._json(404, {"error": "Not found"})

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


signal.signal(signal.SIGINT, shutdown)
signal.signal(signal.SIGTERM, shutdown)
server = Server((HOST, PORT), Handler)
print(f"HealthTick local server: http://{HOST}:{PORT}", flush=True)
try:
    server.serve_forever()
finally:
    VIDEO.stop()
    server.server_close()

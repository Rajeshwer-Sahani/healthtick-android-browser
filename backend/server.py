#!/usr/bin/env python3
"""Local HTTP API and MJPEG relay for a single Android Emulator."""

from __future__ import annotations

import io
import json
import logging
import math
import os
import re
import shlex
import signal
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from PIL import Image, UnidentifiedImageError


ROOT = Path(__file__).resolve().parent.parent
ADB = os.environ.get(
    "ADB_PATH",
    str(Path.home() / "Library/Android/sdk/platform-tools/adb"),
)
SERIAL_OVERRIDE = os.environ.get("ADB_SERIAL")
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))
MAX_BODY_BYTES = 16_384
CAPTURE_INTERVAL_SECONDS = float(os.environ.get("CAPTURE_INTERVAL_SECONDS", "0.25"))
CAPTURE_COMMAND_TIMEOUT_SECONDS = 10
FRAME_STALE_SECONDS = max(5.0, CAPTURE_INTERVAL_SECONDS * 8)
STARTUP_TIMEOUT_SECONDS = 15
if not math.isfinite(CAPTURE_INTERVAL_SECONDS) or CAPTURE_INTERVAL_SECONDS <= 0:
    raise ValueError("CAPTURE_INTERVAL_SECONDS must be a finite positive number")

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


def encode_screenshot_jpeg(png: bytes) -> bytes:
    try:
        with Image.open(io.BytesIO(png)) as image:
            image.load()
            rgb = image.convert("RGB")
            output = io.BytesIO()
            rgb.save(output, format="JPEG", quality=80)
            return output.getvalue()
    except (UnidentifiedImageError, OSError) as error:
        raise ValueError(f"ADB screencap returned an invalid PNG: {error}") from error


def capture_screenshot(serial: str) -> bytes:
    return run_adb(
        ["-s", serial, "exec-out", "screencap", "-p"],
        timeout=CAPTURE_COMMAND_TIMEOUT_SECONDS,
    )


class VideoPipeline:
    """Continuously poll real emulator screenshots and share the latest JPEG."""

    def __init__(self) -> None:
        self.condition = threading.Condition()
        self.lifecycle_lock = threading.Lock()
        self.frame: bytes | None = None
        self.sequence = 0
        self.frame_generation = 0
        self.last_frame_time: float | None = None
        self.started = False
        self.starting = False
        self.closed = False
        self.generation = 0
        self.worker: threading.Thread | None = None
        self.stop_event: threading.Event | None = None
        self.capture_error: str | None = None

    def _publish(self, frame: bytes, generation: int) -> None:
        with self.condition:
            if self.closed or generation != self.generation:
                return
            self.frame = frame
            self.sequence += 1
            sequence = self.sequence
            self.frame_generation = generation
            self.last_frame_time = time.monotonic()
            first_frame = self.starting
            self.starting = False
            recovered = self.capture_error is not None
            self.capture_error = None
            self.condition.notify_all()
        if first_frame:
            LOG.info(
                "First screenshot JPEG published: generation=%d sequence=%d bytes=%d at=%s",
                generation, sequence, len(frame),
                time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            )
        elif recovered:
            LOG.info("Screenshot capture recovered: generation=%d sequence=%d", generation, sequence)

    def _stale_reason_locked(self) -> str | None:
        if self.closed:
            return "pipeline is shutting down"
        if not self.started:
            return "pipeline is not running"
        if self.worker is None or not self.worker.is_alive():
            return "screenshot capture thread is not running"
        if self.starting:
            return None
        if self.last_frame_time is None:
            return f"no screenshot frame has been published: {self.capture_error or 'capture pending'}"
        silent_for = time.monotonic() - self.last_frame_time
        if silent_for > FRAME_STALE_SECONDS:
            return (
                f"no screenshot frame published for {silent_for:.1f} seconds"
                + (f": {self.capture_error}" if self.capture_error else "")
            )
        return None

    def is_healthy(self) -> bool:
        with self.condition:
            return (
                self._stale_reason_locked() is None
                and self.frame_generation == self.generation
            )

    def diagnostic(self) -> str | None:
        with self.condition:
            return self.capture_error or self._stale_reason_locked()

    def _stop_worker_locked(self, permanent: bool = False) -> None:
        stop_event = self.stop_event
        worker = self.worker
        with self.condition:
            self.generation += 1
            generation = self.generation
            self.started = False
            self.starting = False
            self.worker = None
            self.stop_event = None
            if permanent:
                self.closed = True
            self.condition.notify_all()
        if stop_event is not None:
            stop_event.set()
        if worker is not None and worker is not threading.current_thread():
            worker.join(timeout=CAPTURE_COMMAND_TIMEOUT_SECONDS + 2)
            if worker.is_alive():
                LOG.error("Screenshot capture thread did not stop within its timeout")
        LOG.info("Screenshot capture stopped: generation=%d permanent=%s", generation, permanent)
        with self.condition:
            self.condition.notify_all()

    def _capture_loop(self, generation: int, serial: str, stop_event: threading.Event) -> None:
        while not stop_event.is_set():
            capture_started = time.monotonic()
            try:
                png = capture_screenshot(serial)
                frame = encode_screenshot_jpeg(png)
                self._publish(frame, generation)
            except Exception as error:
                message = str(error)
                with self.condition:
                    if generation != self.generation or self.closed:
                        return
                    changed = message != self.capture_error
                    self.capture_error = message
                    self.condition.notify_all()
                if changed:
                    LOG.exception(
                        "Android screenshot capture failed: generation=%d device=%s",
                        generation, serial,
                    )
            remaining = CAPTURE_INTERVAL_SECONDS - (time.monotonic() - capture_started)
            stop_event.wait(max(0.0, remaining))

    def _launch_locked(self) -> int:
        with self.condition:
            self.generation += 1
            generation = self.generation
            self.started = True
            self.starting = True
            self.capture_error = None
        try:
            serial = connected_emulator()
            display_size(serial)
            stop_event = threading.Event()
            worker = threading.Thread(
                target=self._capture_loop,
                args=(generation, serial, stop_event),
                name=f"screenshot-capture-{generation}",
                daemon=True,
            )
            self.stop_event = stop_event
            self.worker = worker
            worker.start()
            LOG.info(
                "Screenshot capture started: generation=%d device=%s interval_ms=%d",
                generation, serial, round(CAPTURE_INTERVAL_SECONDS * 1000),
            )
            with self.condition:
                self.condition.notify_all()
            return generation
        except Exception as error:
            LOG.exception("Video pipeline startup failed: generation=%d", generation)
            self.started = False
            self.starting = False
            self.capture_error = str(error)
            status = error.status if isinstance(error, ApiError) else 503
            raise ApiError(status, f"Could not start screenshot capture: {error}") from error

    def start(self) -> None:
        with self.lifecycle_lock:
            with self.condition:
                if self.closed:
                    raise ApiError(503, "Screenshot capture pipeline is shutting down")
                healthy_startup = (
                    self.started and self.starting
                    and self.worker is not None and self.worker.is_alive()
                )
                reason = self._stale_reason_locked()
                if self.started and (reason is None or healthy_startup):
                    generation = self.generation
                else:
                    if self.started:
                        LOG.warning(
                            "Screenshot capture stale: generation=%d reason=%s",
                            self.generation, reason,
                        )
                        self._stop_worker_locked()
                    LOG.info("Starting screenshot capture after: %s", reason)
                    generation = self._launch_locked()
        self._wait_for_live_frame(generation)

    def _wait_for_live_frame(self, generation: int) -> None:
        deadline = time.monotonic() + STARTUP_TIMEOUT_SECONDS
        failure: str | None = None
        with self.condition:
            while generation == self.generation and not self.closed:
                if self.frame_generation == generation and self.frame is not None:
                    reason = self._stale_reason_locked()
                    if reason is None:
                        return
                    failure = reason
                    break
                if self.worker is None or not self.worker.is_alive():
                    failure = "screenshot capture thread stopped before publishing a frame"
                    break
                if self.capture_error:
                    failure = self.capture_error
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    failure = (
                        f"no screenshot frame within {STARTUP_TIMEOUT_SECONDS} seconds"
                        + (f": {self.capture_error}" if self.capture_error else "")
                    )
                    break
                self.condition.wait(min(remaining, 0.25))
            if failure is None:
                failure = "screenshot capture pipeline changed while waiting for its first frame"
        if failure:
            raise ApiError(503, f"Live Android screenshot unavailable: {failure}")

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
                self._stop_worker_locked(permanent=True)


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
                    "video_error": VIDEO.diagnostic(),
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
                    if VIDEO.closed:
                        break
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

import io
import itertools
import sys
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
import server


def png_frame(color):
    output = io.BytesIO()
    Image.new("RGB", (32, 64), color).save(output, format="PNG")
    return output.getvalue()


class VideoPipelineTests(unittest.TestCase):
    def setUp(self):
        self.pipeline = server.VideoPipeline()

    def tearDown(self):
        self.pipeline.stop()

    def test_publishes_multiple_complete_jpegs_over_time(self):
        colors = itertools.cycle(("red", "green", "blue"))
        with (
            patch.object(server, "connected_emulator", return_value="emulator-5554"),
            patch.object(server, "display_size", return_value=(32, 64)),
            patch.object(
                server,
                "capture_screenshot",
                side_effect=lambda _serial: png_frame(next(colors)),
            ),
            patch.object(server, "CAPTURE_INTERVAL_SECONDS", 0.03),
        ):
            self.pipeline.start()
            first_sequence, first_frame = self.pipeline.current()
            second = self.pipeline.wait_for_frame(first_sequence, timeout=1)
            third = self.pipeline.wait_for_frame(second[0], timeout=1)

        self.assertGreater(third[0], second[0])
        for _, frame in ((first_sequence, first_frame), second, third):
            with Image.open(io.BytesIO(frame)) as image:
                image.verify()
                self.assertEqual(image.format, "JPEG")
                self.assertEqual(image.size, (32, 64))

    def test_capture_error_is_reported_and_next_capture_recovers(self):
        recovered = threading.Event()
        calls = 0

        def capture(_serial):
            nonlocal calls
            calls += 1
            if calls == 1:
                raise server.ApiError(502, "temporary ADB failure")
            recovered.set()
            return png_frame("purple")

        with (
            patch.object(server, "connected_emulator", return_value="emulator-5554"),
            patch.object(server, "display_size", return_value=(32, 64)),
            patch.object(server, "capture_screenshot", side_effect=capture),
            patch.object(server, "CAPTURE_INTERVAL_SECONDS", 0.03),
        ):
            self.pipeline.start()

        self.assertTrue(recovered.is_set())
        self.assertIsNone(self.pipeline.capture_error)
        self.assertGreaterEqual(calls, 2)
        self.assertTrue(self.pipeline.is_healthy())

    def test_invalid_png_is_reported(self):
        with self.assertRaisesRegex(ValueError, "invalid PNG"):
            server.encode_screenshot_jpeg(b"not a PNG")


class InputRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = server.Server(("127.0.0.1", 0), server.Handler)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()
        cls.base_url = f"http://127.0.0.1:{cls.httpd.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join(timeout=2)

    def post(self, route, payload):
        import json
        import urllib.error
        import urllib.request

        request = urllib.request.Request(
            self.base_url + route,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=3) as response:
                return response.status, json.loads(response.read())
        except urllib.error.HTTPError as error:
            return error.code, json.loads(error.read())

    def get(self, route):
        import json
        import urllib.request

        with urllib.request.urlopen(self.base_url + route, timeout=3) as response:
            return response.status, json.loads(response.read())

    def test_health_and_metrics_routes_remain_available(self):
        with (
            patch.object(server, "connected_emulator", return_value="emulator-5554"),
            patch.object(server, "display_size", return_value=(720, 1600)),
            patch.object(server.VIDEO, "is_healthy", return_value=True),
            patch.object(server.VIDEO, "diagnostic", return_value=None),
            patch.object(server.VIDEO, "current", return_value=(42, None)),
        ):
            status, health = self.get("/api/health")
            self.assertEqual(status, 200)
            self.assertEqual(health["device"], "emulator-5554")
            self.assertTrue(health["video_ready"])

            status, metrics = self.get("/api/metrics")
            self.assertEqual(status, 200)
            self.assertEqual(metrics["frame_sequence"], 42)

    def test_input_routes_and_normalized_coordinate_validation(self):
        with (
            patch.object(server, "connected_emulator", return_value="emulator-5554"),
            patch.object(server, "display_size", return_value=(720, 1600)),
            patch.object(server, "run_adb", return_value=b"") as adb,
        ):
            payloads = (
                ("/api/input/tap", {"x": 0.5, "y": 0.25, "frameWidth": 360, "frameHeight": 800}),
                ("/api/input/swipe", {
                    "points": [
                        {"x": 0.2, "y": 0.7, "frameWidth": 360, "frameHeight": 800},
                        {"x": 0.2, "y": 0.3, "frameWidth": 360, "frameHeight": 800},
                    ],
                    "duration_ms": 450,
                }),
                ("/api/input/scroll", {"delta_x": 0, "delta_y": 120}),
                ("/api/input/key", {"key": "Home"}),
                ("/api/input/key", {"key": "Back"}),
                ("/api/input/text", {"text": "healthtick"}),
            )
            for route, body in payloads:
                with self.subTest(route=route, body=body):
                    status, result = self.post(route, body)
                    self.assertEqual(status, 200, result)
                    self.assertIn("adb_duration_ms", result)
            self.assertEqual(adb.call_count, len(payloads))

            status, result = self.post(
                "/api/input/tap",
                {"x": 1.0, "y": 0.25, "frameWidth": 360, "frameHeight": 800},
            )
            self.assertEqual(status, 400)
            self.assertIn("Normalized coordinates", result["error"])
            self.assertEqual(adb.call_count, len(payloads))


class MultipartStreamTests(unittest.TestCase):
    def test_stream_endpoint_delivers_multiple_complete_jpeg_parts(self):
        import urllib.request

        pipeline = server.VideoPipeline()
        httpd = server.Server(("127.0.0.1", 0), server.Handler)
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        payload = bytearray()
        response = None
        try:
            with (
                patch.object(server, "VIDEO", pipeline),
                patch.object(server, "connected_emulator", return_value="emulator-5554"),
                patch.object(server, "display_size", return_value=(32, 64)),
                patch.object(server, "capture_screenshot", return_value=png_frame("orange")),
                patch.object(server, "CAPTURE_INTERVAL_SECONDS", 0.03),
            ):
                response = urllib.request.urlopen(
                    f"http://127.0.0.1:{httpd.server_port}/stream.mjpg",
                    timeout=5,
                )
                self.assertIn(
                    "multipart/x-mixed-replace",
                    response.headers.get("Content-Type", ""),
                )
                deadline = time.monotonic() + 2
                while payload.count(b"--frame\r\n") < 3 and time.monotonic() < deadline:
                    payload.extend(response.read1(65536))
                pipeline.stop()
                payload.extend(response.read())
        finally:
            if response is not None:
                response.close()
            pipeline.stop()
            httpd.shutdown()
            httpd.server_close()
            thread.join(timeout=2)

        self.assertGreaterEqual(payload.count(b"--frame\r\n"), 3)
        self.assertGreaterEqual(payload.count(b"\xff\xd8"), 3)
        self.assertGreaterEqual(payload.count(b"\xff\xd9"), 3)


if __name__ == "__main__":
    unittest.main()

import unittest
from pathlib import Path

from server import ffmpeg_command


class FfmpegCommandTests(unittest.TestCase):
    def test_matroska_input_is_probed_before_input_and_mjpeg_is_set_once(self):
        command = ffmpeg_command(Path("/tmp/scrcpy.mkv"))
        input_index = command.index("-i")

        self.assertEqual(command[command.index("-f") + 1], "matroska")
        self.assertLess(command.index("-probesize"), input_index)
        self.assertLess(command.index("-analyzeduration"), input_index)
        self.assertEqual(command.count("-c:v"), 1)
        self.assertNotIn("-vcodec", command)
        self.assertEqual(command[command.index("-c:v") + 1], "mjpeg")


if __name__ == "__main__":
    unittest.main()

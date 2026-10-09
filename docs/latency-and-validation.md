# Screenshot Stream Validation and Latency

The backend uses one shared polling worker:

```text
Android Emulator -> ADB screencap PNG -> Pillow JPEG -> latest-frame buffer
                 -> multipart MJPEG -> browser <img>
```

`CAPTURE_INTERVAL_SECONDS` sets the target interval between screenshot
captures (default `0.25`, or 250 ms). Capture cadence is also affected by the
ADB command, PNG decode/JPEG encode time, and host scheduling. This is
screenshot polling, not a continuous video encoder; no latency, frame-rate, or
CPU performance result is claimed until measured on the target VM.

## Live stream verification

After deployment and restarting the service:

1. Confirm `GET /api/health` reports the expected emulator and
   `"video_ready": true`.
2. Stream `/stream.mjpg` and save the multipart response for several seconds.
   Confirm it contains multiple `--frame` boundaries and matching complete
   JPEG SOI (`FF D8`) / EOI (`FF D9`) marker pairs.
3. Decode more than one extracted JPEG with Pillow and confirm the dimensions
   match the Android display aspect ratio.
4. Load the public page in a fresh browser tab and verify the real emulator
   screen appears without touching Android.
5. Test tap, swipe, wheel scroll, text/special keys, resize, reconnect, and
   more than one browser client. Check that the emulator responds to input and
   that `/api/metrics` advances while the page is open.
6. Leave the page open and inspect the backend journal for repeated capture
   failures or stalled frame sequences.

A successful HTTP status alone is not sufficient evidence that frames are
being captured or rendered.

## Latency measurement

For a browser input, record the action and the displayed `Input response`,
`Backend to ADB`, `ADB command`, and `Changed frame` timings. The changed-frame
measurement ends when browser polling observes a larger frame sequence; it
does not observe the browser compositor's exact presentation time.

At a 250 ms target interval, capture scheduling can contribute up to roughly
one polling interval before the next capture begins, in addition to ADB,
conversion, network, and scheduling delays. This is a description of the
configured cadence, not a measured end-to-end latency. Use repeated samples
for each interaction and report the test device, viewport, interval, sample
count, and distribution if publishing results.

## systemd Pillow environment migration

The service must run the backend from a virtual environment containing Pillow.
For a checkout at `/home/rajeshwersahani720/healthtick-android-browser`, the
core installation steps are:

```sh
cd /home/rajeshwersahani720/healthtick-android-browser
python3 -m venv backend/.venv
backend/.venv/bin/python -m pip install --upgrade pip
backend/.venv/bin/python -m pip install -r backend/requirements.txt
```

Inspect the current unit first:

```sh
sudo systemctl cat healthtick-backend.service
```

The following drop-in overrides only `ExecStart`; the unit's existing user,
working directory, environment variables (including `ADB_PATH`,
`ADB_SERIAL`, `HOST`, and `PORT`), restart policy, and other settings remain
inherited:

```sh
sudo mkdir -p /etc/systemd/system/healthtick-backend.service.d
sudo tee /etc/systemd/system/healthtick-backend.service.d/pillow.conf >/dev/null <<'EOF'
[Service]
ExecStart=
ExecStart=/home/rajeshwersahani720/healthtick-android-browser/backend/.venv/bin/python /home/rajeshwersahani720/healthtick-android-browser/backend/server.py
EOF
sudo systemctl daemon-reload
sudo systemctl restart healthtick-backend.service
sudo systemctl --no-pager --full status healthtick-backend.service
sudo journalctl -u healthtick-backend.service -n 50 --no-pager
```

Verify that `/api/health` shows `"video_ready": true` and that `/stream.mjpg`
contains multiple complete JPEG parts. The service must not continue using its
system Python if Pillow was installed only in the virtual environment.

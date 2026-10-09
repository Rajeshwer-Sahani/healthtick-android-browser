# HealthTick Android Browser

An interactive real Android Emulator streamed to a browser.

**Public deployment:** <http://34.14.173.43:8000/>

**Public repository:** <https://github.com/Rajeshwer-Sahani/healthtick-android-browser>

**Hosting:** Google Cloud VM, Debian 13, Android Emulator API 35, ADB device
`emulator-5554`, logical display 720 × 1600.

As manually verified by the project owner on 2026-10-09, the public page
displayed the live Android screen and responded to tap, swipe, scroll,
keyboard input, browser resize, and reconnect. An 8-second stream test
contained 11 valid JPEG frames. One owner-reported UI sample showed 692 ms
from action to observation of a later published frame sequence; it is one
observation, not a benchmark or average. The metric does not check whether
image pixels changed.
See [validation and latency notes](./docs/latency-and-validation.md).

The public service uses plain HTTP and has no authentication. Anyone who can
reach the URL can view and operate the one shared emulator. Do not enter
personal, confidential, or sensitive information.

## Architecture

```text
Video:
Android Emulator
  -> ADB exec-out screencap -p (250 ms default polling interval)
  -> Pillow PNG decode / JPEG encode
  -> shared latest-frame buffer and sequence
  -> Python multipart MJPEG endpoint
  -> React <img> in Chrome

Input:
Chrome pointer / wheel / keyboard
  -> Python HTTP API
  -> ADB input commands
  -> Android Emulator
```

One shared backend worker captures real emulator screenshots; the browser
does not receive mock or prerecorded frames. `CAPTURE_INTERVAL_SECONDS`
configures the target interval (default `0.25` seconds). Actual cadence
depends on ADB, conversion, network, and scheduling. Details and rejected
approaches are in the [architecture write-up](./docs/architecture.md).

## Local prerequisites

- Python 3.11 (or a compatible Python 3 with venv support).
- Android SDK Platform Tools / ADB and a bootable Android Emulator AVD.
- Node.js and npm.
- Google Chrome.
- Pillow, installed from `backend/requirements.txt`.

The previously tested local AVD is `Pixel_7` on Android 34 arm64. Its
generated runtime data is not stored in this repository. See
[emulator setup](./emulator/README.md).

Check that the tools resolve:

```sh
python3.11 --version
adb version
node --version
npm --version
```

If the Android SDK tools are not on `PATH`, add the standard macOS SDK paths:

```sh
export PATH="$HOME/Library/Android/sdk/platform-tools:$HOME/Library/Android/sdk/emulator:$PATH"
```

The backend defaults `ADB_PATH` to
`$HOME/Library/Android/sdk/platform-tools/adb`. Override `ADB_PATH` for another
SDK location. Set `ADB_SERIAL` if more than one emulator is attached.

## Local setup and startup

Use separate terminals.

### 1. Start the emulator

```sh
emulator -avd Pixel_7
adb -e wait-for-device
adb -e shell getprop sys.boot_completed
adb -e shell wm size
```

Wait for `sys.boot_completed` to report `1`.

### 2. Build the frontend

From the repository root:

```sh
cd frontend
npm ci
npm run build
cd ..
```

The Python backend serves the production build from the same origin as the
long-lived MJPEG stream.

### 3. Install Pillow and start the backend

```sh
python3.11 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
backend/.venv/bin/python backend/server.py
```

The default server bind is `127.0.0.1:8000`. Set
`CAPTURE_INTERVAL_SECONDS` to change the target screenshot interval (for
example, `0.25`). Shorter intervals increase ADB and image-conversion load.
To stop the backend, press `Ctrl+C`; it signals the capture thread and waits
for the in-flight ADB screenshot operation to finish within its timeout.

### 4. Try the app

Open <http://127.0.0.1:8000/>. No account or credentials are required for the
public deployment. To exercise the controls:

- **Tap:** click a visible Android control.
- **Swipe:** drag on the Android image.
- **Scroll:** use the mouse wheel over the image; wheel motion is translated
  into an ADB swipe.
- **Keyboard:** click a text field on Android, focus the screen, then type.
  The first key may wait up to one second after the last tap for the IME.
  Backspace, Enter, Space, navigation keys, Home, and Back are handled as
  Android key events.
- **Resize:** resize the browser and operate a visible screen target again.
- **Reconnect:** reload the page or open a fresh tab; the frontend reconnects
  to the shared stream.

The public VM deployment itself runs from systemd and does not depend on the
developer's computer remaining online.

## Coordinate mapping

The browser uses the rendered image bounds and the stream's natural
`frameWidth`/`frameHeight`; it does not equate CSS pixels with Android pixels.
If the image is letterboxed, clicks in the unused area are ignored. For the
visible image area:

```text
normalizedX = (pointerX - imageContentLeft) / drawnWidth
normalizedY = (pointerY - imageContentTop) / drawnHeight
androidX = floor(normalizedX * AndroidDisplayWidth)
androidY = floor(normalizedY * AndroidDisplayHeight)
```

The same normalized coordinates are used for swipe points. The backend
validates coordinates and checks image/device aspect ratios. Because the
browser recalculates image bounds and uses normalized coordinates, resizing
does not require hardcoded browser dimensions.

## Known limitations

- One emulator is shared by every visitor. There is no per-user device,
  session, file, or application-state isolation.
- App restrictions are not enforced. A user can navigate outside one app or
  reach system controls, including Android Home/Back.
- The public service is unauthenticated plain HTTP. Screen contents and
  control requests are not protected by TLS or user authorization. Anyone
  able to reach the URL can operate the shared device.
- Repeated PNG screenshots and JPEG conversion are less efficient and may
  look less smooth than a continuous encoded-video transport. There is no
  audio.
- The deployment has not been load-tested for concurrent viewers or
  long-duration stability. Scaling beyond a few users is not supported.
- ADB text input does not comprehensively support arbitrary Unicode or IME
  behaviors; wheel scroll is an approximate swipe.
- Two-way clipboard and session recording are not implemented.
- A continuous 3–5 minute demo video is required by the assignment but is not
  in this repository. Add it before final submission.
- The assignment asks candidates to report actual time spent. This repository
  does not establish that figure; the author must provide it.

## What went wrong

- The Google Android Emulator WebRTC/gRPC route reached the gateway, but
  `Rtc.RequestRtcStream` returned `UNIMPLEMENTED` on tested emulator builds.
  The RTC stream therefore never reached the browser.
- The scrcpy/FFmpeg experiment displayed a real screen locally, but the
  deployed Matroska-over-FIFO stream repeatedly failed to publish live frames.
  A finite recording decoding successfully did not prove a live FIFO worked;
  probing changes did not establish a fix.
- A direct Android `screenrecord` H.264 test produced a JPEG, but continuous
  frame delivery while the process remained alive was not verified. It was
  rejected as an unproven streaming source, not declared inherently
  incompatible.
- The adopted screenshot-polling path is simpler and was manually verified
  on the public deployment. Its trade-offs are repeated ADB capture, image
  conversion work, increased bandwidth, and potentially less fluid display
  updates.

## With more time

- **Scaling:** for more than a few users, provide authenticated session
  ownership and isolated emulator instances, with quotas, concurrency limits,
  and reliable idle cleanup. Measure CPU, memory, capture/conversion cost,
  ADB throughput, network egress, and per-viewer bandwidth before capacity
  planning. Autoscaling/clustering is not implemented or currently required.
- **Security:** add TLS and authentication/authorization, rate limits, strict
  input validation, and private networking for ADB/emulator/debug interfaces.
  Isolate users at the server/device boundary; browser-only restrictions are
  not security controls. The current public unauthenticated endpoint is not
  suitable for sensitive use.
- **Transport:** evaluate a continuous encoded stream after measuring
  screenshot-polling latency, quality, and resource consumption on the VM.

## Assignment deliverables and AI record

- Public repository: this repository.
- Deployed link and usage: <http://34.14.173.43:8000/> (no credentials;
  shared emulator).
- Local setup and feature instructions: this README.
- Architecture and alternatives: [docs/architecture.md](./docs/architecture.md).
- Measured validation: [docs/latency-and-validation.md](./docs/latency-and-validation.md).
- AI process record: [PROCESS_LOG.md](./PROCESS_LOG.md).
- Demo video: **still to be added**; record one continuous 3–5 minute demo of
  the deployed system.

## Human-authored submission notes — complete before submission

The assignment requires the candidate's own short reflection on decisions
they made that the AI did not suggest, and one place where AI was wrong or
unhelpful. Do not submit this as the candidate's personal account without
review and rewriting it in your own words:

- **My decisions beyond AI suggestions:** `[Author: describe your decisions in your own words.]`
- **One AI mistake or unhelpful suggestion:** `[Author: review the candidate example in docs/architecture.md, then explain what you noticed and how you corrected course in your own words.]`
- **Time spent on the assignment:** `[Author: enter your actual time spent.]`

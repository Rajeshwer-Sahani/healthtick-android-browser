# HealthTick Android Browser

A minimal implementation of the HealthTick take-home core: view and control a
real Android Emulator from Chrome. A cloud VM deployment exists, but the
screenshot-polling revision documented here must be deployed and verified
there before that deployment is considered current.

## Current status

The backend captures real Android Emulator screenshots using ADB, converts
them to JPEG, and publishes the latest frame to browser clients. Verify live
capture, deployment, and browser interaction in the target environment before
claiming those behaviors for this revision.

## Architecture

```text
Video:
Pixel_7 Android Emulator
  -> ADB exec-out screencap -p (250 ms default interval)
  -> Pillow PNG decode / JPEG encode
  -> shared latest-frame buffer
  -> Python multipart MJPEG endpoint
  -> React <img> in Chrome

Input:
Chrome pointer / wheel / keyboard
  -> Python HTTP API
  -> ADB input commands
  -> Pixel_7 Android Emulator
```

One background thread is shared by all stream clients. It repeatedly runs
`adb -s <serial> exec-out screencap -p`, validates and converts each PNG with
Pillow, then publishes a JPEG with an increasing frame sequence. The target
interval is configurable with `CAPTURE_INTERVAL_SECONDS` (default `0.25`
seconds); actual cadence also depends on ADB, image conversion, and host
scheduling. Frames are captured from the real emulator, not mocked or
prerecorded.

## Prerequisites

The tested local environment was macOS on Apple Silicon with:

- Android Emulator 37.2.12.0 and a bootable `Pixel_7` AVD (Android 34, arm64).
- Android SDK Platform Tools / ADB 36.0.0.
- Python 3.11.16.
- Pillow installed from `backend/requirements.txt`.
- Node.js 24.13.1 and npm 11.8.0.
- Google Chrome.

The AVD must be configured in the local Android SDK; generated AVD data is not
part of this repository. See [emulator setup](./emulator/README.md).

Confirm the tools resolve in the shell used to start the backend:

```sh
python3.11 --version
adb version
node --version
npm --version
```

If the Android SDK tools are not on `PATH`, add the standard SDK directories
for the current terminal:

```sh
export PATH="$HOME/Library/Android/sdk/platform-tools:$HOME/Library/Android/sdk/emulator:$PATH"
```

If `adb` is not on `PATH`, the backend defaults to
`$HOME/Library/Android/sdk/platform-tools/adb`. Override that path with
`ADB_PATH` if the SDK is installed elsewhere.

## Local setup and startup

Use separate terminals.

### 1. Start Pixel_7

Start the existing AVD (use the full SDK path if `emulator` is not on `PATH`):

```sh
emulator -avd Pixel_7
```

Wait for Android to finish booting and confirm the target and display size:

```sh
adb -e wait-for-device
adb -e shell getprop sys.boot_completed
adb -e shell wm size
```

The boot property should be `1`. The tested display size was `1080x2400`.
When more than one emulator is connected, set `ADB_SERIAL` to the desired
serial (the tested emulator serial was `emulator-5554`).

### 2. Build the React/Vite frontend

From the repository root:

```sh
cd frontend
npm ci
npm run build
cd ..
```

The build output is ignored by Git and is served by the Python backend. Using
this same-origin local path avoids relying on the Vite development proxy for
the long-lived multipart MJPEG response.

### 3. Start the Python backend

From the repository root:

```sh
python3.11 -m venv backend/.venv
backend/.venv/bin/python -m pip install -r backend/requirements.txt
backend/.venv/bin/python backend/server.py
```

The backend uses Python's standard library and Pillow. ADB must be executable
by the backend process. The server binds to `127.0.0.1:8000`. On a deployed
systemd service, use the same virtual environment for the service executable;
see the deployment procedure in the validation notes.

Set `CAPTURE_INTERVAL_SECONDS` to change the target capture cadence (for
example, `0.25` for 250 ms). Lower intervals increase ADB and image-conversion
load; screenshot polling is not a substitute for a low-latency encoded-video
transport.

### 4. Open Chrome

Visit <http://127.0.0.1:8000/>. The initial real emulator frame should appear
without touching the device. Keep the emulator and backend running while using
the browser.

To stop the backend, press `Ctrl+C`; the screenshot worker is signaled to stop
and the server waits for an in-flight ADB command to finish, bounded by its
command timeout. The emulator can be stopped separately from its terminal.

## Try the controls

Use a real Android screen such as Settings:

- **Tap:** click a visible Android control or row in the image.
- **Swipe:** press and drag on the image, then release.
- **Scroll:** place the pointer over the image and use the mouse wheel. Wheel
  movement is translated to a short ADB swipe.
- **Keyboard:** click a text field on Android, keep the browser screen focused,
  then type. To allow Android's field and keyboard to settle, the first key
  after a screen tap is sent no earlier than one second after that tap;
  Backspace, Enter, and Space are handled as Android key events.
- **Resize:** resize Chrome and tap the same visible Android control again.
- **Latency:** after an action, inspect the displayed backend/ADB timings and
  the time until a new frame sequence is observed.

## Coordinate mapping

The browser does not treat CSS pixels as Android pixels. The client measures
the rendered image element and its natural stream dimensions (`frameWidth`,
`frameHeight`). For element bounds `Rw × Rh` and frame dimensions `Wf × Hf`:

```text
scale = min(Rw / Wf, Rh / Hf)
drawnWidth  = Wf * scale
drawnHeight = Hf * scale
left/top letterbox = centered unused space within the element
normalizedX = (pointerX - imageContentLeft) / drawnWidth
normalizedY = (pointerY - imageContentTop) / drawnHeight
androidX = floor(normalizedX * AndroidDisplayWidth)
androidY = floor(normalizedY * AndroidDisplayHeight)
```

Clicks in the letterboxed area are ignored. The backend rejects invalid
normalized coordinates and checks that the captured frame aspect ratio matches
the Android display before sending `adb shell input tap`. The same normalized
coordinates are used for swipe endpoints.

## Latency and measurement

The UI reports the browser request duration, backend-to-ADB dispatch duration,
ADB command duration, and approximate time until a newer MJPEG frame sequence
is observed. The last measurement includes frontend polling and scheduling;
it does not measure the exact physical display/compositor presentation time.

No performance result for this screenshot-polling revision is claimed. See
[the latency notes and procedure](./docs/latency-and-validation.md).

## Known limitations

- One connected emulator is supported at a time; the backend is not a
  multi-user service.
- Video uses repeated ADB PNG screenshots delivered as MJPEG over HTTP. It has
  no audio and may look less smooth and consume more bandwidth than a
  continuous encoded-video transport.
- Text is sent through ADB's text input command; Unicode, clipboard, and
  arbitrary IME behaviors have not been validated.
- Mouse-wheel input is an approximate swipe, not a native Android wheel event.
- The backend has no authentication. Its default local bind is loopback; a
  deployed service can expose it on the VM's configured interface.
- Emulator disconnect recovery, long-duration soak testing, and deployed
  performance must be verified in the target environment.
- Earlier RTC/gRPC and scrcpy/FFmpeg capture experiments did not provide a
  reliable deployed stream; the current capture path uses screenshot polling.

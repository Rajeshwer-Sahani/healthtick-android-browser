# Architecture and Assignment Trade-offs

## Implemented system

The deployed system uses one Android Emulator on a Google Cloud VM. It is
intentionally a single-device implementation, not a multi-tenant session
platform.

### Video path

```text
Android Emulator (API 35, emulator-5554, 720 × 1600)
  -> ADB exec-out screencap -p
  -> Python capture worker (250 ms target interval)
  -> Pillow decodes PNG and encodes JPEG
  -> synchronized latest-frame buffer + increasing sequence
  -> HTTP multipart/x-mixed-replace MJPEG
  -> browser <img>
```

One background worker is shared across browser connections. It captures the
real emulator, publishes a complete JPEG as the latest frame, and increments
the frame sequence. Each stream client receives new frames from that shared
buffer; opening another tab does not create another emulator capture loop.
Capture interval is configurable with `CAPTURE_INTERVAL_SECONDS`. ADB,
conversion, scheduling, and network time add to the configured interval.

The public service is hosted on a Google Cloud Debian 13 VM. The application
does not depend on a developer workstation being online. The deployed URL is
<http://34.14.173.43:8000/>.

### Input path and coordinate mapping

```text
Browser pointer / wheel / keyboard
  -> JSON HTTP input routes
  -> Python validation and timing
  -> ADB shell input
  -> Android Emulator
```

Tap and swipe events carry normalized image coordinates. The browser computes
the displayed image content rectangle from the image's rendered bounds and
natural frame dimensions, accounting for centered letterboxing. It ignores
clicks outside the image content. The backend validates normalized values and
the captured frame's aspect ratio, then scales coordinates to the current
Android display width and height. This separates device coordinates from CSS
pixels and supports browser resizing. Wheel input is translated to an ADB
swipe. Text and supported keys are sent using ADB input commands; Android
Home and Back are key events.

The backend returns timestamps for request receipt, ADB dispatch, and ADB
completion. The browser also measures request response time and polls the
backend frame sequence until it observes a later published sequence. This
time-to-later-sequence includes capture cadence, ADB, conversion, network
delivery, browser polling, and scheduling; it does not verify pixel changes
or instrument an exact compositor presentation timestamp. The single
observed public sample is recorded in
[latency-and-validation.md](./latency-and-validation.md).

## Alternatives considered

- **Google Emulator WebRTC/gRPC:** the tested native emulator builds accepted
  gateway connectivity, but `Rtc.RequestRtcStream` returned
  `UNIMPLEMENTED`. The required RTC media path therefore could not be
  validated on those builds.
- **scrcpy recording to a Matroska FIFO, then FFmpeg to MJPEG:** this produced
  a real browser stream in local experiments, but the deployed pipeline
  repeatedly failed to publish live frames. A completed MKV file being
  decodable did not prove that the non-seekable FIFO worked continuously.
  FFmpeg probing-option changes did not establish a working deployment.
- **Android `screenrecord` H.264 piped to FFmpeg:** a shell test produced a
  JPEG, but continuous frame delivery while `screenrecord` remained alive was
  not verified. It was not selected because it did not meet the live-stream
  evidence requirement.
- **ADB screenshot polling:** selected because it uses the already working
  ADB connection and a direct, inspectable PNG capture, removes media process
  and FIFO lifecycle complexity, and was manually verified on the public
  deployment. Its cost is per-capture ADB and image-processing work, MJPEG
  bandwidth, and potentially less fluid updates than a continuous encoded
  stream. The configured 250 ms interval is a target, not a measured frame
  rate or latency guarantee.

The implementation uses open-source Android SDK/ADB and Pillow, plus the
project's open-source Python and browser dependencies. It does not use a
hosted Android device farm or commercial streaming SDK.

## Isolation, restrictions, and security

**Isolation is not implemented.** All visitors share the same emulator,
screen, installed apps, files, and Android state. There are no per-user
sessions, instance allocation, session cleanup, or resource quotas.

**Restricted app access is not implemented.** A user can leave any app and
reach Android system UI; the browser's controls are not a security boundary.

The public endpoint is plain HTTP and unauthenticated. Anyone who can reach
the URL can view the screen and send input to the shared emulator. Screen
contents and actions are not protected by transport encryption or identity
checks. The service is not appropriate for secrets or personal information.
ADB and emulator/debug interfaces must remain private to the VM environment;
the public web port should be the only externally exposed application
interface. The current service does not supply user isolation or access
control.

## What went wrong

The first planned route was the Google Emulator RTC/gRPC gateway. The RPC
required for RTC streaming returned `UNIMPLEMENTED`, so the browser could
not start a stream. The next route, scrcpy plus FFmpeg, worked in some local
recording/browser experiments but was unreliable in the deployed FIFO/live
pipeline. A file that decodes after recording is not proof that live frames
arrive over a FIFO. Raising FFmpeg probing settings did not resolve the
production failure. A one-frame `screenrecord` shell result likewise did not
prove a persistent stream. The project changed to the simpler ADB screenshot
poller rather than treating those partial results as live validation.

### Human review required: AI mistake/unhelpful work candidate

The process history shows an AI change that added Matroska probing options
and then described insufficient probing as the diagnosed production cause,
despite lacking a live production frame test. Later production reports still
showed no JPEG frames. This is an evidence-backed candidate for the
candidate's required reflection on an AI mistake; it does **not** establish
the candidate's personal view or replace their own account. Review and
rewrite this in the candidate's own words before submission. See the
[append-only AI process record](../PROCESS_LOG.md).

## With more time

Scaling beyond a few users would require authenticated session ownership,
isolated emulator instances, bounded concurrency, quotas, and cleanup of
abandoned sessions. Capacity should be based on measured CPU, memory, ADB
capture/conversion cost, network egress, and simultaneous viewer load; this
assignment does not require autoscaling or clustering.

The highest security risks are unauthenticated public control, unencrypted
screen/input traffic, cross-user access to the shared device state, and
possible exposure of ADB or emulator control interfaces. A production system
should add TLS and authentication/authorization, private control-plane
networking, server-enforced session boundaries, rate limits, and auditable
cleanup. Client-side restrictions alone are insufficient.

## Submission deliverables

The author still needs to complete these assignment deliverables:

- Record and include the required continuous 3–5 minute demo of the deployed
  application.
- Add the actual time spent on the assignment.
- Write the human-authored reflection describing personal decisions and one
  instance where AI was wrong or unhelpful.

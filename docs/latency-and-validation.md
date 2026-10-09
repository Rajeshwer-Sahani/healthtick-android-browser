# Deployment Validation and Latency

This record separates **project-owner-reported manual verification** from
performance and reliability claims that have not been measured. The assistant
did not independently access the VM or repeat the browser checks during this
documentation audit.

## Verified deployment behavior

The project owner reported manually testing the deployed page at
<http://34.14.173.43:8000/> on 2026-10-09:

- Google Cloud VM, Debian 13, Android Emulator API 35.
- Health response: `emulator-5554`, 720 × 1600, `video_ready=true`,
  `video_error=null`.
- An 8-second `/stream.mjpg` test contained 11 valid JPEG frames.
- The public page displayed the real live screen; tap, swipe, scroll, keyboard
  input, browser resize, and reconnect were tested successfully.

These are reported manual checks, not a load test or a claim of multi-user
isolation. The 11-frame observation is one bounded stream test; it is not a
sustained frame-rate benchmark.

## Latency observation

One project-owner-reported public UI sample showed **692 ms** from an action
to observation of a later published frame sequence. The action type,
viewport, test repetition count, and distribution were not provided. Treat
this as one sample only—not an average, percentile, latency guarantee, or
benchmark. The frontend polls until the backend sequence number increases;
it does not compare frame pixels to determine whether the image changed. The
measurement also does not instrument the exact physical-display or
browser-compositor presentation time.

For a repeatable future measurement, record action type, viewport, capture
interval, device state, input response, backend-to-ADB time, ADB duration,
time to later published sequence across repeated trials. Report the sample
count and distribution, and keep sequence observation separate from physical
display presentation timing.

## Not measured or not verified

- No latency average, percentile, jitter, or frame-rate benchmark has been
  collected for screenshot polling.
- No CPU, memory, bandwidth, multi-viewer, soak, or long-duration recovery
  test has been reported.
- The 250 ms `CAPTURE_INTERVAL_SECONDS` default is a configured target
  interval, not proof of four frames per second. Each iteration also consumes
  ADB, PNG/JPEG conversion, and scheduling time.
- Public behavior and interactions above were manually tested by the project
  owner. They were not independently re-executed as part of this audit.

## Local setup and service dependency

See the root [README](../README.md) for local emulator setup, backend
installation, and feature test instructions. Install Pillow from
`backend/requirements.txt` into the exact Python environment used by the
backend.

For the Debian systemd service, the deployment migration uses a virtual
environment with Pillow and a drop-in changing `ExecStart` while preserving
the existing unit environment. The [architecture write-up](./architecture.md)
and repository process log describe the deployed capture path and prior
experiments.

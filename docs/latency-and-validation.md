# Local Validation and Latency

This note records the local measurement method and observations from the
implementation test on Pixel_7. These are approximate interactive checks, not
laboratory measurements or deployment results.

## Repeatable procedure

1. Start the Pixel_7 AVD, build the frontend, and start the Python backend as
   described in the root README.
2. Open `http://127.0.0.1:8000/` in Chrome without touching the emulator.
   Confirm the initial Settings screen appears.
3. Perform one browser tap, swipe, wheel scroll, or text/key action on a
   visible Android target.
4. Read the UI's `Input response` and `Changed frame` values. The former is
   elapsed browser time through the input HTTP response. The latter is the
   elapsed browser time until polling observes a newer backend frame sequence.
5. For swipe/scroll checks, optionally compare ADB screenshots captured just
   before and after the gesture. Use a scrollable Android screen so that a
   changed image is meaningful.

The backend also returns the elapsed time from its input-dispatch timestamp
until ADB is invoked and the ADB command duration. The dispatch timestamp is
recorded after emulator/display discovery. Browser polling, operating-system
scheduling, emulator rendering, and stream delivery are included in the
browser elapsed values; the browser compositor's exact presentation time is
not measured.

## Observed examples

| Action | Browser viewport | Backend to ADB | ADB command | Input response | Changed frame |
| --- | ---: | ---: | ---: | ---: | ---: |
| Tap a Settings row | 1024 x 768 | 0 ms | 130 ms | 243 ms | 554 ms |
| Tap the same logical row | 640 x 480 | 0 ms | 133 ms | 274 ms | 796 ms |
| Swipe Settings list | 1024 x 768 | 0 ms | 381 ms | 538 ms | 642 ms |
| Mouse-wheel scroll | 1024 x 768 | 0 ms | 480 ms | 575 ms | 678 ms |
| Type `healthtick` after the focus-settle delay | 1024 x 768 | 0 ms | 61 ms | 118 ms | Streaming continuously |
| Type `healthtick` starting 400 ms after the tap | 1024 x 768 | 0 ms | 53 ms | 877 ms for the last queued character | Streaming continuously |

Values are from individual local runs and vary with emulator/UI state. The
backend-to-ADB values round to zero because the timestamp is taken immediately
before command execution; it should not be interpreted as end-to-end latency.

The first keyboard attempt dropped the first character when typing soon after
focusing the Android search field. The client now defers the first keyboard
event until one second after a screen tap; that wait is included in the
browser-side input-response measurement. Typing begun 400 ms after the tap
then displayed the full `healthtick` text in Android's UI accessibility dump.
Space, Backspace, and Enter were issued through Android key events; Enter
returned an observed changed frame.

No CPU benchmark or long-duration reliability/soak test was performed.

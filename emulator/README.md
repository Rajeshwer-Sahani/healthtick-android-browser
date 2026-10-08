# Local Android Emulator

The emulator is supplied by the local Android SDK and is deliberately not
checked into this repository. The tested AVD is named `Pixel_7`, uses Android
34 arm64, and reports a `1080x2400` display.

Start it from a terminal with the SDK tools on `PATH`:

```sh
emulator -avd Pixel_7
adb -e wait-for-device
adb -e shell getprop sys.boot_completed
adb -e shell wm size
```

The boot-complete property should report `1`. If the tools are not on `PATH`,
use `$HOME/Library/Android/sdk/emulator/emulator` and
`$HOME/Library/Android/sdk/platform-tools/adb`, or install/configure an
equivalent Android SDK location. The backend accepts `ADB_PATH` and
`ADB_SERIAL` environment overrides.

Do not copy generated `.avd` runtime data or emulator snapshots into this
repository.

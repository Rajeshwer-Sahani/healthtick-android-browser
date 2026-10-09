# AI Process Log

This file records meaningful AI-assisted work performed during the HealthTick
Real-Time Android Device in the Browser assignment.

Entries are append-only.

Earlier entries must never be rewritten or deleted.

---

## Entry 001 — Project Foundation and AI Workflow Setup

### Time

2026-10-08 — IST

### User Prompt

> okay so now Step 3D — Set up `AGENTS.md` and `PROCESS_LOG.md` okay

### What AI Did

- Reviewed the HealthTick assignment's mandatory AI coding-agent logging requirements.
- Confirmed that `AGENTS.md` must contain the required PROCESS_LOG instruction before using an AI coding agent.
- Prepared the project-specific `AGENTS.md` instructions.
- Prepared the initial `PROCESS_LOG.md` structure.
- Preserved the assignment's mandatory AI logging instruction verbatim.
- Established rules for recording meaningful AI-assisted development steps, failures, dead ends, user decisions, and abandoned approaches.
- Confirmed that the project must not use fake/mock Android functionality.

### Errors / Failures

No implementation error occurred during this step.

No AI coding-agent implementation has been started yet.

### User Decision / Next Step

The user decided to establish the AI-agent instructions and process log before beginning AI-assisted implementation.

Next step: complete the remaining repository foundation files, create the initial Git commit, and push the project foundation to GitHub before starting the technical Android Emulator/WebRTC validation.

---

## Entry 002 — Local Android Emulator/WebRTC Feasibility Investigation

### Time

2026-10-08 11:14 IST (session timestamp)

### User Prompt (verbatim)

```text
We are starting the HealthTick Software Developer Intern take-home assignment
from a completely clean repository.

Read AGENTS.md first and follow it exactly.

Read PROCESS_LOG.md before doing anything.

IMPORTANT:
This is an investigation and validation step only.
Do NOT build the application yet.
Do NOT create mock/fake Android functionality.
Do NOT create a fake device UI.
Do NOT create the React application yet.
Do NOT implement the Python gateway yet.
Do NOT deploy anything.

Assignment goal:

Build a real-time interactive Android device inside a web browser.

The currently planned architecture is:

Browser
→ React frontend
→ WebRTC / WebSocket
→ Python Gateway
→ gRPC
→ Android Emulator

The architecture is not considered validated yet.

Your task is ONLY to investigate and prepare the first local technical experiment.

1. Inspect the current repository structure and existing files.

2. Inspect the local development environment and report what is already installed and usable:
   - macOS version
   - Android SDK
   - Android Emulator
   - adb
   - Python
   - Docker
   - Node.js
   - npm
   - Git

3. Research the official Google Android Emulator WebRTC/container projects relevant
   to this architecture.

   Prefer official Google repositories/documentation.

4. Determine the smallest realistic local experiment that can prove:

   Android Emulator
   → Google Emulator WebRTC stack
   → Gateway
   → Browser

5. Identify all required prerequisites for that experiment.

6. Identify whether the Google Emulator WebRTC/container approach is compatible
   with the current Mac development environment.

7. If there is an important limitation on macOS, explain it clearly and determine
   the correct alternative development setup without changing the final architecture
   unnecessarily.

8. Do not install or modify anything unless explicitly necessary and safe.
   First report what you recommend installing or changing.

9. Do not guess commands or dependencies.
   Verify them from authoritative documentation where possible.

10. Clearly separate:
    - verified facts
    - recommendations
    - assumptions
    - unresolved questions

11. Identify the first concrete experiment we should run.

12. Stop after the investigation and report your findings.
    Do not proceed to implementation.

After completing the investigation, update PROCESS_LOG.md according to the
mandatory logging instructions in AGENTS.md.

For the PROCESS_LOG entry:
- preserve my exact prompt verbatim;
- describe what you actually investigated;
- record commands/checks performed;
- record errors/failures;
- record any dead ends;
- record the resulting recommendation;
- record what decision is now required from me.

Do not fabricate successful results.
```

### What AI Did

- Read `AGENTS.md` and the pre-existing `PROCESS_LOG.md` before inspecting other project files.
- Inspected the project tree, `README.md`, `THIRD_PARTY_NOTICES.md`, and Git status. The repository contains foundation documentation and empty placeholder files/directories; no application or gateway implementation is present, and the worktree was clean on `main`.
- Checked the host with `sw_vers`, `uname -a`, `command -v`, tool version commands, Android SDK paths, `emulator -list-avds`, `emulator -accel-check`, `adb devices -l`, SDK image directories, and AVD configuration.
- Observed macOS 27.0 on Apple silicon (arm64/T8103); Android SDK tools are installed under `~/Library/Android/sdk`, but `ANDROID_HOME` and `ANDROID_SDK_ROOT` are unset and `adb`/`emulator` are not on PATH.
- Verified installed Android Emulator 35.6.11, Platform-Tools/ADB 36.0.0, SDK command-line tools 19.0, an existing `Pixel_7` AVD with an Android 34 arm64 image, and a successful `emulator -accel-check` reporting Hypervisor.Framework. No emulator was running and `adb devices -l` listed no devices.
- Observed system `python3` is 3.9.6; a separate executable `~/.local/bin/python3.11` is installed at version 3.11.16. No `python3` alias is present in `~/.local/bin`, so the upstream setup script's `python3` invocation would still select 3.9.6 unless the virtual environment is created explicitly with Python 3.11.
- Verified Node.js 24.13.1, npm 11.8.0, and Git 2.50.1. Docker, Docker Desktop, Podman, Colima, and Rancher executables were not found; `/Applications/Docker.app` is absent.
- Read the official `google/android-emulator-container-scripts` README, its `gateway/DEMO.md`, `gateway/launch_video_demo.sh`, `gateway/setup_env.sh`, and `gateway/pyproject.toml`; read the Android Emulator acceleration/command-line documentation and the official `google/android-emulator-webrtc` README/protocol/package metadata.
- Confirmed the Google demo documents a macOS native-emulator discovery-file location and a local gateway plus React/Vite sample flow. The gateway package declares Python >=3.10 and dependencies `aiohttp`, `grpcio`, `protobuf`, and `websockets`. The emulator CLI help on this host documents `-grpc <port>` as the switch to enable its gRPC control service.
- Noted a documentation discrepancy to resolve at experiment time: upstream demo docs name `~/Library/Android/avd/running/pid_<PID>.ini`, while this installed emulator's CLI help reports `$HOME/Library/Caches/TemporaryItems/avd/running/pid_<PID>_info.ini`. The actual discovery file must be located after launching the emulator; do not assume either path or record its token in the log.
- Confirmed upstream container requirements explicitly require Linux, Docker Engine/Compose, and KVM, and explicitly state Docker Desktop on macOS is unsupported for KVM acceleration. Google's registry documentation repeats that macOS/Windows Docker Desktop is unsupported.

### Commands / Checks Performed

- `sw_vers`
- `uname -a`
- `command -v` checks for `emulator`, `adb`, Python, Docker, Node.js, npm, Git, Podman, Colima, and Rancher
- Version checks for system Python, Python 3.11, Node.js, npm, Git, Android Emulator, ADB, and SDK command-line tools
- `git status --short --branch`
- Shallow listing of `~/Library/Android/sdk`
- `emulator -list-avds`
- `emulator -accel-check`
- `adb devices -l`
- SDK system-image/platform directory listing and AVD `config.ini` inspection
- `emulator -help-all` filtered for gRPC/WebRTC/discovery options
- Checked for `/Applications/Docker.app` and `/Applications/Android Studio.app`
- Fetched primary-source documentation and upstream project files listed above; no local emulator, gateway, browser, or WebRTC streaming session was started.

### Errors / Failures / Dead Ends

- `command -v adb` and `command -v emulator` initially found nothing because the SDK's `platform-tools` and `emulator` executables are not on PATH; direct checks at their installed SDK paths succeeded.
- The first check of `emulator -version` emitted the version and an expected “No AVD specified” message; subsequent checks used supported listing/help/acceleration commands instead.
- An attempted fetch of `gateway/requirements.txt` returned HTTP 404. The dependency source was verified from the existing upstream `gateway/pyproject.toml` instead; no dependency was inferred from the failed URL.
- No install, file change outside this appended log entry, emulator boot, or deployment was attempted.

### Recommendation

Keep the agreed architecture. For the first local proof, prefer the native Android Emulator already installed on this Apple-silicon Mac and Google's documented Python Gateway/WebRTC browser demo; do not try to run the emulator in Docker Desktop on this Mac. Use Python 3.11 explicitly in an isolated virtual environment, and obtain the active emulator discovery file from the running process rather than assuming a documented path. If container-based emulator testing is later required, use a Linux host with Docker Engine/Compose and working KVM (bare metal, or a cloud VM with nested virtualization); that is an environment-specific test setup, not a reason to change the target architecture.

The proposed, not-yet-run experiment is: boot the existing `Pixel_7` AVD with gRPC explicitly enabled using the locally documented emulator option; inspect its generated discovery file; start the upstream Python Gateway using its documented `--discovery_file`; run the upstream `js/example` React/Vite app; connect a browser to the local gateway; verify a live emulator frame and one real touch/input round-trip. Keep all downloaded Python/npm dependencies in a temporary upstream checkout and isolated environment if the experiment is approved.

### User Decision / Next Step

The investigation is complete; no experiment has yet been run. The user must decide whether to authorize this native-Mac experiment, which will boot the existing AVD and install upstream Python/npm dependencies in isolated temporary locations. If it fails due to the native emulator's gRPC/WebRTC capability, reassess with evidence before recommending any Linux/KVM host or other setup change.

---

## Entry 003 — Native Mac Emulator/WebRTC Experiment (Blocked at Gateway Install)

### Time

2026-10-08 11:24 IST

### User Prompt (verbatim)

```text
We authorize the native-Mac technical experiment described in your previous
investigation.

Read AGENTS.md and PROCESS_LOG.md first.

This is still a validation experiment, NOT full application implementation.

Goal:

Prove whether this exact local chain can work:

Pixel_7 Android Emulator
→ Google Android Emulator WebRTC/gRPC path
→ Python Gateway
→ React/Vite browser client
→ Chrome

Proceed incrementally and stop at the first blocking issue.

IMPORTANT RULES:

1. Do NOT build the HealthTick application yet.
2. Do NOT create a fake/mock Android UI.
3. Do NOT create our production frontend.
4. Do NOT create our production backend.
5. Do NOT modify the agreed architecture without explaining why.
6. Do NOT install Docker Desktop on macOS for this experiment.
7. Do NOT replace the native Mac emulator with a different emulator unless
   the current experiment proves impossible.
8. Use Python 3.11 explicitly for the gateway environment.
9. Prefer official Google repositories/documentation.
10. Keep upstream source/dependencies isolated from our production source tree
    where practical.
11. Do not commit generated files, virtual environments, node_modules,
    emulator runtime data, or secrets.
12. Do not claim success unless the behavior is actually observed.

Perform these steps one at a time:

A. Verify the existing Pixel_7 AVD configuration.
B. Start the Pixel_7 emulator with the required gRPC configuration.
C. Verify the emulator is actually running and accessible.
D. Identify the actual discovery file generated by this running emulator.
E. Verify whether the running emulator exposes the RTC/gRPC service expected
   by Google's gateway.
F. Create an isolated Python 3.11 environment for the upstream gateway.
G. Obtain the minimum upstream gateway dependencies.
H. Run the upstream Python gateway using the actual discovery file.
I. Run the upstream React/Vite example documented by Google.
J. Open the local browser client.
K. Determine whether the real Android screen is displayed.
L. If displayed, test at least one real interaction (touch/click or hardware
   key) and verify that the Android Emulator responds.
M. If any step fails, stop at that failure and diagnose it rather than
   jumping to an unrelated architecture.

For every step, report:

- exact command executed
- observed result
- whether it succeeded or failed
- relevant logs/errors
- what the result proves
- what it does NOT prove
- recommended next step

At the end, provide a clear result:

VALIDATED
or
BLOCKED

If BLOCKED, identify the exact blocker and the smallest credible next
experiment.

Update PROCESS_LOG.md after this meaningful step using the mandatory rules
in AGENTS.md. Preserve my exact prompt verbatim and record all commands,
results, errors, dead ends, and the decision needed from me.

Do not continue into full implementation after the experiment.
Stop and report the results.
```

### Scope and Isolation

- Re-read `AGENTS.md` and the start of the existing `PROCESS_LOG.md` before running experiment commands.
- Used the official `google/android-emulator-container-scripts` repository in `/var/folders/57/86xvztc16tbdx4s4lvjn9ljw0000gn/T/healthtick-webrtc-experiment-20261008/upstream`, outside the production repository. The sparse checkout contains `gateway/` and `js/`.
- Created an isolated environment at `/var/folders/57/86xvztc16tbdx4s4lvjn9ljw0000gn/T/healthtick-webrtc-experiment-20261008/venv` with Python 3.11.16.
- No production frontend/backend, Docker setup, deployment, npm install, browser session, screen capture, or emulator interaction was attempted. No discovery token was copied into this log.

### Step Results and Commands

#### A. Verify Pixel_7 configuration — SUCCEEDED

```sh
SDK="$HOME/Library/Android/sdk"; AVD="$HOME/.android/avd/Pixel_7.avd/config.ini"; "$SDK/emulator/emulator" -list-avds; grep -E '^(abi.type|hw.cpu.arch|image.sysdir.1|hw.ramSize|hw.lcd.width|hw.lcd.height|avd.ini.displayname)=' "$AVD"; test -d "$SDK/system-images/android-34/default/arm64-v8a" && printf '%s\n' 'android-34/default/arm64-v8a present'; "$SDK/platform-tools/adb" devices -l
```

Observed AVD `Pixel_7` / display name `Pixel 7`, ABI/CPU `arm64-v8a` / `arm64`, installed Android 34 default arm64 image, 2048 MB configured RAM, and display 1080 x 2400. No device was running before startup. This proves the configured AVD and image exist, not that boot or RTC works. Next: launch it with gRPC enabled.

#### B. Start emulator with gRPC — SUCCEEDED

```sh
"$HOME/Library/Android/sdk/emulator/emulator" -avd Pixel_7 -grpc 8554
```

Launched in an attached background shell; output identified Emulator 35.6.11 and the Android 34 arm64 image. The emulator process ran as PID 63151. Startup showed non-fatal Qt/XR warnings and a transient ADB-offline warning during boot. This proves the emulator accepted `-grpc 8554` and started, not that the RTC RPC API is available. Next: verify boot, ADB, and the listening port.

#### C. Verify emulator running/accessibility — SUCCEEDED

```sh
"$HOME/Library/Android/sdk/emulator/emulator" -accel-check
"$HOME/Library/Android/sdk/platform-tools/adb" devices -l
"$HOME/Library/Android/sdk/platform-tools/adb" -e shell getprop sys.boot_completed
lsof -nP -iTCP:8554 -sTCP:LISTEN
```

Observed during this experiment: ADB device `emulator-5554` in `device` state, `sys.boot_completed` value `1`, and PID 63151 listening on TCP 8554. The Hypervisor.Framework acceleration check was observed in the preceding investigation, not rerun in this experiment. This proves the guest booted and the configured TCP port listens, not that the gateway's gRPC service methods work. Next: identify the process discovery file and probe its API.

#### D. Identify actual discovery file — SUCCEEDED

```sh
find "$HOME/Library/Android/avd/running" "$HOME/Library/Caches/TemporaryItems/avd/running" -maxdepth 1 -type f -name '*.ini' -print 2>/dev/null
```

Observed `/Users/rajeshwer/Library/Caches/TemporaryItems/avd/running/pid_63151.ini`; inspected non-secret fields showed `avd.name=Pixel 7` and `grpc.port=8554`. The token value was not printed. This proves a discovery file was generated and advertises the listening port, not that gateway authentication/signaling works. Next: make an actual service-level gRPC probe.

#### E. Verify gateway RTC gRPC API — INCONCLUSIVE; NOT REACHED

```sh
command -v grpcurl
"$HOME/.local/bin/python3.11" -c 'import grpc; print("grpcio", grpc.__version__)'
python3 -c 'import socket; s=socket.create_connection(("127.0.0.1",8554),2); print("TCP connection to emulator gRPC port succeeded"); s.close()'
```

Observed no `grpcurl`; importing `grpc` from the initially installed Python 3.11 environment failed with `ModuleNotFoundError: No module named 'grpc'`; raw TCP connection succeeded. This proves only TCP reachability. The expected RTC service/method was not invoked, so RTC capability remains unknown. Next: use the gateway's API after its documented build inputs are available.

#### F. Prepare isolated Python 3.11 environment/upstream checkout — SUCCEEDED

```sh
EXPERIMENT_DIR="${TMPDIR:-/tmp}/healthtick-webrtc-experiment-20261008"; if [ -e "$EXPERIMENT_DIR" ]; then printf 'Refusing to reuse existing path: %s\n' "$EXPERIMENT_DIR"; exit 2; fi; mkdir -p "$EXPERIMENT_DIR"; git clone --depth 1 --filter=blob:none --sparse https://github.com/google/android-emulator-container-scripts.git "$EXPERIMENT_DIR/upstream" && git -C "$EXPERIMENT_DIR/upstream" sparse-checkout set gateway js && python3.11 -m venv "$EXPERIMENT_DIR/venv" && "$EXPERIMENT_DIR/venv/bin/python" --version && git -C "$EXPERIMENT_DIR/upstream" rev-parse --short HEAD
```

Observed successful official sparse checkout, commit `0aa7b0d`, and virtual-environment Python 3.11.16. This proves source/environment isolation and the declared Python-version prerequisite, not gateway installation/runtime. Next: install the upstream gateway.

#### G. Install upstream gateway/dependencies — FAILED; FIRST BLOCKER

```sh
"$EXPERIMENT_DIR/venv/bin/python" -m pip install -e "$EXPERIMENT_DIR/upstream/gateway"
```

The editable build exited status 1:

```text
ERROR: BAZEL_ROOT environment variable is not set.
Please set BAZEL_ROOT to the root of the emu-main-next workspace.
ERROR: Failed building editable for goldfish-videobridge-gateway
ERROR: Could not build wheels for goldfish-videobridge-gateway, which is required to install pyproject.toml-based projects
```

No `videobridge-gateway` entry point was installed; `pip list` contained only `pip` and `setuptools`. Inspected upstream `gateway/setup.py`: it requires `BAZEL_ROOT/hardware/google/aemu/protos` to contain the emulator-controller proto and the WebRTC `rtc_service_v2.proto` and `ice_config.proto`, then generates Python stubs under `gateway/src/videobridge_gateway/proto`. Upstream `gateway/setup_env.sh` calls `pip install -e .` without setting `BAZEL_ROOT`; the demo's fresh-checkout instructions omit this external build prerequisite.

This proves the upstream documented fresh gateway install is incomplete without the `emu-main-next` proto source workspace/configuration. It does **not** prove the emulator lacks RTC support: no gRPC RPC was attempted. Recommended next step: retrieve the exact proto inputs (and any imports required to compile them) from the official Android Emulator `emu-main-next` source tree into an isolated temporary location, set `BAZEL_ROOT` there, retry the unmodified gateway install, and then probe the running native emulator. No architecture change is justified by this packaging/build-input failure.

#### H–L. Gateway runtime, React/Vite, Chrome, frame, interaction — NOT RUN

Stopped at the step G blocker as requested. No npm install or client startup command was issued; Chrome was not opened; real screen display and input were not tested.

### Errors, Cleanup, and Repository State

- `adb -e emu kill` was rejected by the command runner before execution because its process-termination safeguard interpreted the `kill` subcommand as an invalid process-kill command. This was a tool-policy rejection, not an emulator error.
- Stopped the experiment's specific emulator process with `kill -TERM 63151`. Follow-up checks reported TCP 8554 closed and `adb -s emulator-5554 get-state` returned `device ... not found`; the AVD process exited.
- An upstream fetch for nonexistent `gateway/requirements.txt` earlier returned HTTP 404; gateway dependencies/build configuration were verified from upstream `pyproject.toml`, `setup.py`, and `setup_env.sh`.
- No production files or dependencies were changed; no npm packages, Docker, deployment, or secret material were used. Final `git diff --check` and production worktree status checks are still pending after this log append.

### Result and User Decision Required

**BLOCKED.** Exact current blocker: upstream gateway installation requires `BAZEL_ROOT` to reference an `emu-main-next` source workspace for gRPC proto generation; the documented setup script does not provide it. Native emulator boot, ADB readiness, actual discovery file generation, and gRPC TCP listening succeeded. RTC method compatibility and every gateway/browser step remain unverified. The user must decide whether to authorize fetching/preparing the official proto build inputs in the isolated temporary experiment directory and retrying the unmodified upstream gateway.

---

## Entry 004 — Authorization to Resolve the Upstream Proto Build Input

### Time

2026-10-08 — IST; exact selection time unavailable.

### User Decision (verbatim)

> Continue with isolated official proto inputs (Recommended)

### What AI Did

- Resumed only the blocked gateway-build investigation, retaining the official upstream checkout and Python 3.11 virtual environment in the isolated temporary experiment directory.
- Confirmed `google/android-emulator-container-scripts` `gateway/setup.py` requires three proto sources under `BAZEL_ROOT/hardware/google/aemu/protos/services/...`.
- Inspected the official AOSP `platform/hardware/google/aemu` repository top-level via Gitiles JSON; it has no `protos/` directory, so that guessed source location is not usable.
- Inspected the official `platform/tools/base` `emulator/proto/README.md`, which says these proto files are copied from the Android Emulator code base and identifies `platform/external/qemu` branch `emu-master-dev`, directory `android/android-grpc`, as their master source.
- The first Gitiles probes against `platform/hardware/google/aemu` paths and `platform/external/qemu` branch `main` returned HTTP 404; these were abandoned in favor of the branch/path named by the official proto README.

### Errors / Failures

No additional local installation or source-file download has occurred yet. The preceding editable gateway installation blocker remains unresolved; the gRPC RTC API has not been tested.

### User Decision / Next Step

The user authorized obtaining the official proto build inputs in isolation and retrying the unmodified upstream gateway installation. Next: verify the documented Android Emulator proto master source branch/path, stage only the required proto files (and import dependencies) in a temporary workspace, then retry the gateway install with `BAZEL_ROOT` set.

---

## Entry 005 — Gateway RPC Success; Upstream Browser Demo Blocked on Missing Dependency

### Time

2026-10-08 11:33 IST

### User Decision (verbatim)

> Continue with isolated official proto inputs (Recommended)

### What AI Did

- Verified the official `platform/tools/base` `mirror-goog-studio-main` source branch at commit `76ab4f9bcdb8e7911b580c6398df2a031be549ff`.
- Used its officially mirrored `emulator/proto` files to stage only `emulator_controller.proto`, `rtc_service_v2.proto`, and `ice_config.proto` in the isolated temporary `BAZEL_ROOT` layout expected by the upstream gateway. Verified the proto headers and imports; imports were standard protobuf definitions and `ice_config.proto`.
- Retried the unchanged upstream editable gateway install with `BAZEL_ROOT` set. Python 3.11.16 successfully built/installed the gateway and generated the Python gRPC stubs.
- Restarted the same native `Pixel_7` AVD with gRPC on port 8554, confirmed boot completion and found the new discovery file `/Users/rajeshwer/Library/Caches/TemporaryItems/avd/running/pid_64133.ini`.
- Started the unmodified upstream Python gateway on port 8080 with that discovery file. Its logs reported connection to Emulator gRPC at localhost:8554 and direct use of that channel for the RTC service.
- Issued `GET /api/v1/emulator/status` through the gateway. The request returned HTTP 200 and real emulator data: version `35.6.11.0 (35.6.11-13610412)`, `booted: true`, hypervisor type 4, 16 CPU cores, and 2 GiB RAM. Hardware/platform config maps were empty.
- Installed the isolated upstream example's npm dependencies. npm reported 7 vulnerabilities total (2 moderate, 5 high); no automatic fixes/audit-fix command was run. A production-dependencies-only audit reported 0 vulnerabilities.
- Started the documented Vite dev command. Vite announced readiness at `http://127.0.0.1:5173/android-emulator-webrtc/`, but its dependency scan failed because `loglevel` imported by `js/src/components/emulator/net/logger.ts` was absent from the example's installed dependency tree.
- Compared manifests: `js/package.json` declares `loglevel` (`^1.9.2`), but the upstream `js/example/package.json` does not declare it. `npm ls loglevel` in the example reported `(empty)`. This is a concrete upstream sample dependency omission.
- Stopped the experiment's gateway, Vite, and exact emulator PID after this blocker. Follow-up showed ports 8080, 5173, and 8554 closed and ADB listed no devices.

### Commands and Observed Results

Official source reference:

```sh
git ls-remote https://android.googlesource.com/platform/tools/base refs/heads/mirror-goog-studio-main
```

Observed branch commit: `76ab4f9bcdb8e7911b580c6398df2a031be549ff`. The Gitiles directory `emulator/proto/` contained the three expected `.proto` files; its README states the files are copies of the emulator proto sources. Initial probes of `platform/hardware/google/aemu/.../protos` and `platform/external/qemu` branch `main` returned 404. The named `platform/external/qemu` branch `emu-master-dev` directory listing did not expose the expected WebRTC proto path, so that direct-source route was not used.

Proto staging (files written only beneath the temp experiment directory):

```sh
EXPERIMENT_DIR="${TMPDIR:-/tmp}/healthtick-webrtc-experiment-20261008"; AOSP_ROOT="$EXPERIMENT_DIR/proto-source"; BASE="$AOSP_ROOT/hardware/google/aemu/protos"; mkdir -p "$BASE/services/emulator-controller" "$BASE/services/webrtc"; SOURCE='https://android.googlesource.com/platform/tools/base/+/76ab4f9bcdb8e7911b580c6398df2a031be549ff/emulator/proto'; for item in 'emulator_controller.proto services/emulator-controller' 'rtc_service_v2.proto services/webrtc' 'ice_config.proto services/webrtc'; do set -- $item; file="$1"; dest="$BASE/$2/$1"; curl --fail --silent --show-error "$SOURCE/$file?format=TEXT" | base64 -D > "$dest" || exit 1; done; find "$BASE/services" -type f -name '*.proto' -exec ls -l {} \;; grep -hE '^import ' "$BASE/services/emulator-controller/emulator_controller.proto" "$BASE/services/webrtc/rtc_service_v2.proto" "$BASE/services/webrtc/ice_config.proto"
```

Observed file sizes: emulator-controller 82,399 bytes; RTC service 5,822 bytes; ICE config 5,316 bytes. Imports were `google/protobuf/empty.proto`, `google/protobuf/any.proto`, `ice_config.proto`, and `google/protobuf/duration.proto`.

Gateway install retry:

```sh
EXPERIMENT_DIR="${TMPDIR:-/tmp}/healthtick-webrtc-experiment-20261008"; BAZEL_ROOT="$EXPERIMENT_DIR/proto-source" "$EXPERIMENT_DIR/venv/bin/python" -m pip install -e "$EXPERIMENT_DIR/upstream/gateway"
```

Observed successful editable-wheel build and installation of `goldfish-videobridge-gateway`, `grpcio 1.84.0`, `protobuf 7.36.2`, `aiohttp 3.14.4`, `websockets 17.2`, and transitive dependencies into the isolated Python 3.11 environment.

Emulator restart/readiness:

```sh
"$HOME/Library/Android/sdk/emulator/emulator" -avd Pixel_7 -grpc 8554
"$HOME/Library/Android/sdk/platform-tools/adb" wait-for-device
"$HOME/Library/Android/sdk/platform-tools/adb" devices -l
"$HOME/Library/Android/sdk/platform-tools/adb" -e shell getprop sys.boot_completed
lsof -nP -iTCP:8554 -sTCP:LISTEN
find "$HOME/Library/Caches/TemporaryItems/avd/running" -maxdepth 1 -type f -name '*.ini' -print 2>/dev/null
```

Observed ADB device `emulator-5554` ready, boot property `1`, gRPC listener PID 64133, and discovery path ending `pid_64133.ini`.

Gateway and actual RPC-backed status request:

```sh
"$EXPERIMENT_DIR/venv/bin/videobridge-gateway" --port=8080 --discovery_file="$HOME/Library/Caches/TemporaryItems/avd/running/pid_64133.ini"
curl --max-time 15 -sS -i http://127.0.0.1:8080/api/v1/emulator/status
```

Observed startup logs: `Connecting to Emulator gRPC service at: localhost:8554`, `No separate Video Bridge specified; using Emulator gRPC channel directly for Rtc service`, and `Gateway Webserver listening on http://0.0.0.0:8080`. The status request returned HTTP 200 and the real device metadata listed above. This proves Python 3.11 gateway operation and EmulatorController gRPC status. It does **not** prove the `Rtc.RequestRtcStream` method or media/data stream has been exercised.

Frontend install/start:

```sh
cd "$EXPERIMENT_DIR/upstream/js/example" && npm install
cd "$EXPERIMENT_DIR/upstream/js/example" && npm run dev -- --host 127.0.0.1
cd "$EXPERIMENT_DIR/upstream/js/example" && npm ls loglevel
curl --max-time 10 -sS -I http://127.0.0.1:5173/
```

Observed npm install exit 0 and 7 reported vulnerabilities (2 moderate, 5 high). Vite 4.5.14 reported ready in 357 ms at the `/android-emulator-webrtc/` base path, then failed dependency resolution with:

```text
The following dependencies are imported but could not be resolved:
  loglevel (imported by .../js/src/components/emulator/net/logger.ts)
Are they installed?
```

`npm ls loglevel` returned `(empty)`. Vite's root returned HTTP 302 to `/android-emulator-webrtc/`; this is only the dev server's base-path redirect, not successful app rendering. `npm audit --omit=dev --audit-level=moderate` reported `found 0 vulnerabilities`; no audit fixes were applied.

### Errors / Failures / Dead Ends

- Fetches for guessed Gitiles proto paths under `platform/hardware/google/aemu` and branch `main` returned HTTP 404. The official Android Studio mirror was used instead.
- A `view` request for a presumed `js/example/vite.config.ts` file returned file-not-found; it caused no source modification. The Vite diagnostic and package manifests identified the actual dependency issue.
- Vite's dependency scan fails due to missing `loglevel` in the example install. The upstream source module declares it, but the example package does not. This is the first blocking failure in the browser-demo step.
- No Chrome page was opened, no frame was seen, no `Rtc.RequestRtcStream` was invoked from the browser, and no touch/hardware input or latency was tested.
- The test services and emulator were terminated after the failure; ports 8080/5173/8554 closed and ADB returned an empty device list.

### Result and User Decision Required

**BLOCKED.** Python 3.11 plus the upstream gateway can install and serve a successful real `EmulatorController` status RPC on native macOS. The browser stage currently cannot compile because the upstream Vite example omits its source package's `loglevel` dependency. Therefore RTC streaming, Chrome display, and input remain unvalidated. The next minimal action is to authorize adding/installing the missing upstream `loglevel` dependency in the isolated temporary demo only, restarting the unchanged gateway/emulator, and then opening the local demo in Chrome. No production code or architecture change is warranted.

---

## Entry 006 — Isolated JS Dependency Resolution and Missing Generated Proto

### Time

2026-10-08 11:39 IST

### User Decision (verbatim)

> Authorize isolated loglevel install and continue (Recommended)

### What AI Did

- Installed the upstream-declared `loglevel@^1.9.2` in the isolated example directory, as authorized. Vite still could not resolve it when imported from the sibling `js/src` tree because Node module lookup from that source tree does not search the child `js/example/node_modules`.
- Confirmed `js/package.json` declares `loglevel`; installed the upstream package runtime dependencies at the `js/` source root without saving package/lock changes, making `loglevel` resolvable from `js/src`.
- Ran the upstream example production build. The loglevel resolution problem was cleared (40 modules transformed), exposing the next required generated input: `js/src/proto/emulator_controller_pb.js` is absent.
- Read the upstream `js/example/README.md`, `js/Makefile`, and `js/.gitignore`. The README explicitly requires running `make protoc` or `make build` in the `js/` root first; the Makefile requires a `protoc` executable plus the npm `protoc-gen-js` plugin; `.gitignore` excludes generated `src/proto/*pb.js`.
- Checked the host and found `protoc` is not installed or on PATH. The system compiler was not installed, no generated proto file was created, and no Chrome/browser session was opened.

### Commands and Results

```sh
EXPERIMENT_DIR="${TMPDIR:-/tmp}/healthtick-webrtc-experiment-20261008"; cd "$EXPERIMENT_DIR/upstream/js/example" && npm install 'loglevel@^1.9.2'
```

Succeeded; npm again reported 7 vulnerabilities total (2 moderate, 5 high), with no automatic fixes.

```sh
EXPERIMENT_DIR="${TMPDIR:-/tmp}/healthtick-webrtc-experiment-20261008"; kill -TERM 64802; npm install --prefix "$EXPERIMENT_DIR/upstream/js" --no-save --package-lock=false --omit=dev 'loglevel@^1.9.2' && node -e 'const path=process.argv[1]; console.log(require.resolve("loglevel", {paths:[path]}))' "$EXPERIMENT_DIR/upstream/js/src/components/emulator/net" && cd "$EXPERIMENT_DIR/upstream/js/example" && npm run build
```

Observed `loglevel` resolution at `js/node_modules/loglevel/lib/loglevel.js`; build then transformed 40 modules and failed with `Could not resolve "../../proto/emulator_controller_pb"` from the upstream `emulator.tsx`.

```sh
command -v protoc
protoc --version
command -v make
make --version
```

Observed `protoc: command not found`; GNU Make 3.81 is installed.

The upstream example dev server's first run reported unresolved `loglevel`; after the dependency install, the example root and transformed `App.tsx` returned HTTP 200, but this did not establish a successful browser application or WebRTC stream. The later production build proved the generated protobuf JS module is also required.

### Errors / Failures

- Installing loglevel under `js/example/node_modules` alone did not fix imports originating from sibling `js/src`; source-root resolution was confirmed and the dependency was installed in the upstream source root.
- The upstream build then failed at the missing generated protobuf module.
- Upstream docs provide the remedy (`make protoc`), but its compiler prerequisite (`protoc`) is absent. The Makefile says the compiler may be installed with Homebrew (`brew install protobuf`); no system-wide install was attempted.
- Test emulator/gateway/Vite processes are stopped; ports 8080, 5173, and 8554 are closed; no ADB device remains.
- The repository changes remain limited to this append-only process log; no upstream generated proto file exists and no source/build manifest in the production repository was changed.

### Result and User Decision Required

**BLOCKED.** The immediate browser build blocker is the absent generated `emulator_controller_pb.js`; the documented generator requires `protoc`, which is absent on the host. The user must decide whether to authorize a protobuf compiler setup for this isolated upstream experiment (recommended documented route: `brew install protobuf`, then the upstream `make protoc` target and its npm plugin prerequisites), or to stop here. RTC streaming, Chrome display, and real input remain untested.

---

## Entry 007 — Chrome Reaches Gateway; Emulator RTC RPC Is Unimplemented

### Time

2026-10-08 11:49 IST

### User Decision (verbatim)

> Authorize `brew install protobuf` and continue (Recommended)

### What AI Did

- Installed the user-authorized Homebrew `protobuf` compiler. Homebrew auto-updated its core/cask taps, installed `abseil` and `protobuf 36.2`, and ran its automatic cache cleanup; cached artifacts/logs for pcre2, portable-ruby, and several older packages were removed. This system-level change was authorized by the user.
- Ran the upstream JavaScript protobuf generation target. The first invocation generated `emulator_controller_pb.js` but returned failure because the upstream Makefile hardcodes `python`, which is absent; only `python3` and Python 3.11 are present. The helper script is a standard-library-only prefix writer. Re-ran the target with its supported `PYTHON` override set to the existing Python 3.11 executable; `make -B protoc PYTHON="$HOME/.local/bin/python3.11"` succeeded.
- The upstream example then built successfully with Vite/Rollup.
- Started the same native `Pixel_7` AVD, upstream Vite client, and upstream Python 3.11 gateway, using the discovery file produced by that emulator process.
- Opened the upstream example in the integrated Chrome-based browser. The shortcut URL with `?url=localhost:8080` returned Vite 403 due to the example's file-serving allowlist; opening the documented base page without query loaded the actual upstream demo form, where the gateway URI was entered manually.
- Clicked the real upstream “Connect to Emulator” control. Chrome established the gateway WebSocket (`GET /api/v1/emulator/ws-jsep` returned 101), after which the gateway's actual `Rtc.RequestRtcStream` RPC returned gRPC `StatusCode.UNIMPLEMENTED`.
- Stopped the experiment processes and confirmed ports 8080/5173/8554 closed and ADB had no running device.

### Commands / Observed Results

Compiler installation and generation:

```sh
brew install protobuf
protoc --version
cd "$EXPERIMENT_DIR/upstream/js" && make protoc
cd "$EXPERIMENT_DIR/upstream/js" && make -B protoc PYTHON="$HOME/.local/bin/python3.11"
cd "$EXPERIMENT_DIR/upstream/js/example" && npm run build
```

`brew install protobuf` succeeded with `libprotoc 36.2`. Initial `make protoc` generated the 441,017-byte JS protobuf output, then failed with `make: python: No such file or directory` at `python eslint_prefix.py`. The retry with the Makefile's `PYTHON` variable set to Python 3.11 completed both compiler and helper steps with exit status 0. The upstream example `npm run build` then succeeded: 47 modules transformed and Vite generated its `dist` bundle.

The upstream `js` root `npm install` performed by `make protoc` added 750 packages and reported 40 dependency vulnerabilities (3 moderate, 37 high). Earlier the example dependency install reported 7 (2 moderate, 5 high). No `npm audit fix` was run. These generated/dependency files exist only in the temporary upstream checkout, not in the production worktree.

Runtime commands:

```sh
"$HOME/Library/Android/sdk/emulator/emulator" -avd Pixel_7 -grpc 8554
cd "$EXPERIMENT_DIR/upstream/js/example" && npm run dev -- --host 127.0.0.1
"$EXPERIMENT_DIR/venv/bin/videobridge-gateway" --port=8080 --discovery_file="$HOME/Library/Caches/TemporaryItems/avd/running/pid_66229.ini"
curl --max-time 15 -sS -i http://127.0.0.1:8080/api/v1/emulator/status
```

Observed the Vite page at `http://127.0.0.1:5173/android-emulator-webrtc/` and the gateway status response HTTP 200 with `booted: true`, emulator version `35.6.11.0 (35.6.11-13610412)`. The actual `RTC` gRPC operation failed:

```text
File ".../gateway_server.py", line 207, in handle_websocket_jsep
  response = await rtc_stub.RequestRtcStream(stream_req, metadata=bridge_metadata)
grpc.aio._call.AioRpcError:
  status = StatusCode.UNIMPLEMENTED
  details = ""
```

The browser logged a WebSocket-close warning and showed the upstream demo controls/connection panel, but no Android screen/video. The gateway log confirms the WebSocket handshake itself succeeded (HTTP 101); the server then rejected `RequestRtcStream`. The HTTP status RPC and GPS API are separate EmulatorController methods and had returned successfully; they do not substitute for RTC.

Browser URL outcomes:

- `http://127.0.0.1:5173/android-emulator-webrtc/?url=localhost:8080` returned `403 Restricted`, stating request `/?url=localhost:8080` was outside the Vite serving allow list.
- `http://127.0.0.1:5173/android-emulator-webrtc/` loaded the upstream “Android Emulator WebRTC Demo” connection form in the browser.
- After entering `127.0.0.1:8080` and clicking Connect, the frontend attempted the expected gateway WebSocket and triggered the real failing RTC RPC.

Cleanup:

```sh
kill -TERM 66321
kill -TERM 66227
kill -TERM 66229
```

After waiting for the emulator's orderly snapshot shutdown, `ps`, `lsof` on ports 8080/5173/8554, and `adb devices -l` confirmed the processes/listeners were gone and no emulator remained.

### Errors / Failures / Dead Ends

- The first documented `make protoc` run failed only at the helper invocation because this host has no `python` alias. The supported Makefile override to the already-installed Python 3.11 succeeded; no additional Python install was needed.
- The Vite query-string shortcut was denied by its `server.fs.allow` handling. The documented base URL and manual URI form worked, so no Vite configuration change was made.
- The main architecture blocker is not a browser build failure: the installed native Android Emulator 35.6.11 accepts TCP gRPC and implements the `EmulatorController` status API, but its gRPC server returns `UNIMPLEMENTED` for `android.emulation.control.v2.Rtc.RequestRtcStream`, the method required by the upstream gateway. Therefore the WebRTC offer/media stream cannot start on this exact emulator build/configuration.
- Chrome never displayed a real Android frame; no real touch/key input or latency was tested.
- All runtime processes were stopped. No emulator/WebRTC source code or generated file was copied into the production tree.

### Result and User Decision Required

**BLOCKED.** The exact blocker is `StatusCode.UNIMPLEMENTED` from `Rtc.RequestRtcStream` on the user's native Android Emulator 35.6.11. This experimentally proves that this installed emulator build cannot serve this gateway's required RTC path; it does not prove that all native macOS Android Emulator releases are incompatible. The smallest credible next experiment is to identify, from official emulator release/source information, a native macOS Emulator build that implements this RTC v2 service, then repeat the same `RequestRtcStream` probe against the same AVD before opening the browser. Do not alter the architecture or install/update another emulator package until that candidate version and required change are confirmed with the user. The user must decide whether to authorize that narrow official-version investigation.

---

## Entry 008 — Official Native Emulator Version Follow-Up (Research Only)

### Time

2026-10-08 11:52 IST

### User Decision (verbatim)

> Investigate official native emulator support (Recommended)

### What AI Did

- Reviewed Google's official Android Emulator release notes, the official Android Emulator archive guidance, the Google `android-emulator-container-scripts` merged WebRTC v2 pull request, and the official `platform/tools/base` RTC proto documentation.
- Verified that Google's release notes identify Android Emulator 37.2.12 as Stable (September 29, 2026); the notes include a macOS Apple Silicon gRPC `streamScreenshot` fix. They also list 37.1.11 and 36.6.11 stable releases.
- Verified that merged upstream PR `google/android-emulator-container-scripts#415` describes the new gateway as calling the native `android.emulation.control.v2.Rtc` gRPC service on port 8554.
- The official `rtc_service_v2.proto` labels RTC experimental and defines `Rtc.RequestRtcStream`. No version floor or release note guaranteeing this method on the native macOS emulator was found in the reviewed official sources.
- Did not query SDK Manager for install/update, download any newer emulator, modify the SDK, or restart the emulator. Current installed binary remains 35.6.11.0.

### Errors / Failures

- GitHub code/repository searches did not reveal a documented minimum native emulator version supporting `RequestRtcStream`.
- Official Android Emulator release notes discuss gRPC screenshot support on current macOS, but that does not establish the separate RTC service's presence.
- Therefore 37.2.12 is a concrete latest-stable candidate to test, **not** a verified RTC-capable version.

### Recommendation and User Decision

Architecture remains unchanged. The smallest credible next experiment is to obtain the official native macOS Emulator 37.2.12 package in a separate temporary SDK/package location if feasible, launch the same `Pixel_7` AVD using `-grpc 8554`, and invoke the exact same gateway `Rtc.RequestRtcStream` probe before attempting another browser session. This isolates version capability without overwriting the currently installed emulator. Whether a side-by-side package location can run against the current SDK/AVD needs verification before doing it.

The user authorized source/version investigation only; the user must now decide whether to authorize this isolated newer-native-emulator runtime test. No further install or SDK mutation was performed.

---

## Entry 009 — Authorized Final Native Emulator Version Experiment

### Time

2026-10-08 12:08 IST

### User Prompt (verbatim)

```text
We need to move quickly now.

Read AGENTS.md and PROCESS_LOG.md first.

The previous technical experiment is officially recorded as:

Emulator 35.6.11
→ Python Gateway
→ Google WebRTC
→ React browser
→ Rtc.RequestRtcStream
→ UNIMPLEMENTED

The assignment does NOT require Google's Rtc.RequestRtcStream specifically.
It requires a real live Android device in the browser with interaction.

Therefore this is our LAST small experiment with the Google native RTC path.

TASK:

Test the latest stable Android Emulator available through the Android SDK
that is appropriate for this macOS Apple Silicon machine.

Do NOT redesign the application.
Do NOT build production frontend/backend.
Do NOT build mock UI.
Do NOT install Docker Desktop.
Do NOT add unrelated dependencies.

Goal:

Determine whether a newer official Android Emulator implementation supports
the RTC service required by the existing Google Python Gateway.

Process:

1. Verify the currently installed Android Emulator version.

2. Check the official Android Emulator release/update information.

3. If an appropriate newer stable version is available, upgrade the Android
   Emulator using the normal Android SDK tooling.

4. Verify the resulting emulator version.

5. Reuse the existing Pixel_7 AVD if compatible.

6. Boot Pixel_7 with the gRPC configuration required by the Google gateway.

7. Generate/locate the correct discovery file.

8. Start the existing isolated Python 3.11 gateway.

9. Start the existing upstream React/Vite WebRTC demo.

10. Attempt the same Rtc.RequestRtcStream flow.

11. Determine whether a REAL Android video frame appears in the browser.

12. If the stream works, test ONE real browser interaction such as tapping
    an Android UI element and verify that the emulator responds.

13. If the stream does not work, STOP. Do not start implementing another
    architecture in this task.

Report:

- emulator version before
- emulator version after
- exact commands used
- whether RTC.RequestRtcStream works
- whether a real Android frame appears
- whether browser input works
- exact error if it fails
- what this proves
- what it does not prove

IMPORTANT:

If the newer emulator still returns UNIMPLEMENTED, classify the Google native
RTC path as BLOCKED for this Mac experiment and STOP.

Do not spend additional time trying random emulator flags or undocumented
workarounds.

After the experiment, update PROCESS_LOG.md according to AGENTS.md,
including my exact prompt verbatim, commands, results, errors, failures,
and the resulting decision.

Do not implement the fallback streaming architecture yet.

Stop and report the result.
```

### What AI Did / Initial Checks

- Re-read `AGENTS.md` and the existing `PROCESS_LOG.md` before running experiment commands.
- Confirmed the installed emulator reports 35.6.11.0 (build ID 13610412); SDK Manager lists installed package `emulator | 35.6.11`.
- Checked the official Android Emulator release notes. They list 37.2.12 Stable (September 29, 2026), including a macOS Apple Silicon gRPC screenshot fix. This release note does not specifically promise that `Rtc.RequestRtcStream` is implemented.
- Ran SDK Manager package listing. It lists emulator 37.2.12 as latest available and shows an available update from 35.6.11 to 37.2.12. SDK Manager also lists command-line tools 23.0 and Platform-Tools 37.0.1 updates, which are out of scope and must not be installed for this experiment.
- Verified the existing `Pixel_7` AVD remains Android 34 arm64, 1080x2400, configured RAM 2048 MB, and its Android 34 default arm64 system image exists. No emulator/runtime service was active before the update.
- Observed 5.6 GiB free on the SDK filesystem; the upgrade has not yet been attempted, so download/install feasibility is not established.

### Exact Commands Already Performed

```sh
git status --short --branch
git diff --check
"$HOME/Library/Android/sdk/emulator/emulator" -version
"$HOME/Library/Android/sdk/cmdline-tools/latest/bin/sdkmanager" --list_installed
"$HOME/Library/Android/sdk/cmdline-tools/latest/bin/sdkmanager" --list --channel=0
df -h "$HOME/Library/Android/sdk"
"$HOME/Library/Android/sdk/emulator/emulator" -list-avds
grep -E '^(avd.ini.displayname|abi.type|hw.cpu.arch|image.sysdir.1|hw.ramSize|hw.lcd.width|hw.lcd.height)=' "$HOME/.android/avd/Pixel_7.avd/config.ini"
"$HOME/Library/Android/sdk/platform-tools/adb" devices -l
```

### Errors / Failures / Resulting Decision

No SDK upgrade or runtime test has occurred yet. Initial checks succeeded. Continue by installing only the `emulator` SDK package at the listed stable version through SDK Manager, then verify the package version before launching the existing AVD.

### User Decision / Next Step

The user's prompt explicitly authorizes the normal Android SDK tooling upgrade. No additional approval is required to install emulator 37.2.12. Do not update command-line tools, Platform-Tools, AVD image, or unrelated packages.

---

## Entry 010 — Latest Stable Emulator RTC Retry (Still Blocked)

### Time

2026-10-08 12:15 IST

### User Prompt (verbatim)

```text
We need to move quickly now.

Read AGENTS.md and PROCESS_LOG.md first.

The previous technical experiment is officially recorded as:

Emulator 35.6.11
→ Python Gateway
→ Google WebRTC
→ React browser
→ Rtc.RequestRtcStream
→ UNIMPLEMENTED

The assignment does NOT require Google's Rtc.RequestRtcStream specifically.
It requires a real live Android device in the browser with interaction.

Therefore this is our LAST small experiment with the Google native RTC path.

TASK:

Test the latest stable Android Emulator available through the Android SDK
that is appropriate for this macOS Apple Silicon machine.

Do NOT redesign the application.
Do NOT build production frontend/backend.
Do NOT build mock UI.
Do NOT install Docker Desktop.
Do NOT add unrelated dependencies.

Goal:

Determine whether a newer official Android Emulator implementation supports
the RTC service required by the existing Google Python Gateway.

Process:

1. Verify the currently installed Android Emulator version.

2. Check the official Android Emulator release/update information.

3. If an appropriate newer stable version is available, upgrade the Android
   Emulator using the normal Android SDK tooling.

4. Verify the resulting emulator version.

5. Reuse the existing Pixel_7 AVD if compatible.

6. Boot Pixel_7 with the gRPC configuration required by the Google gateway.

7. Generate/locate the correct discovery file.

8. Start the existing isolated Python 3.11 gateway.

9. Start the existing upstream React/Vite WebRTC demo.

10. Attempt the same Rtc.RequestRtcStream flow.

11. Determine whether a REAL Android video frame appears in the browser.

12. If the stream works, test ONE real browser interaction such as tapping
    an Android UI element and verify that the emulator responds.

13. If the stream does not work, STOP. Do not start implementing another
    architecture in this task.

Report:

- emulator version before
- emulator version after
- exact commands used
- whether RTC.RequestRtcStream works
- whether a real Android frame appears
- whether browser input works
- exact error if it fails
- what this proves
- what it does not prove

IMPORTANT:

If the newer emulator still returns UNIMPLEMENTED, classify the Google native
RTC path as BLOCKED for this Mac experiment and STOP.

Do not spend additional time trying random emulator flags or undocumented
workarounds.

After the experiment, update PROCESS_LOG.md according to AGENTS.md,
including my exact prompt verbatim, commands, results, errors, failures,
and the resulting decision.

Do not implement the fallback streaming architecture yet.

Stop and report the result.
```

### Commands Performed

Initial inventory and official release check:

```sh
"$HOME/Library/Android/sdk/emulator/emulator" -version
"$HOME/Library/Android/sdk/cmdline-tools/latest/bin/sdkmanager" --list_installed
"$HOME/Library/Android/sdk/cmdline-tools/latest/bin/sdkmanager" --list --channel=0
df -h "$HOME/Library/Android/sdk"
"$HOME/Library/Android/sdk/emulator/emulator" -list-avds
grep -E '^(avd.ini.displayname|abi.type|hw.cpu.arch|image.sysdir.1|hw.ramSize|hw.lcd.width|hw.lcd.height)=' "$HOME/.android/avd/Pixel_7.avd/config.ini"
"$HOME/Library/Android/sdk/platform-tools/adb" devices -l
```

Observed before version 35.6.11.0 (build ID 13610412). Official Android Emulator release notes identify 37.2.12 Stable (September 29, 2026); SDK Manager listed `emulator 37.2.12` as the available update from installed 35.6.11. SDK filesystem had 5.6 GiB free. `Pixel_7` was present and its API 34 arm64 image was installed.

SDK update and verification:

```sh
"$HOME/Library/Android/sdk/cmdline-tools/latest/bin/sdkmanager" --install 'emulator'
"$HOME/Library/Android/sdk/emulator/emulator" -version
"$HOME/Library/Android/sdk/cmdline-tools/latest/bin/sdkmanager" --list_installed
"$HOME/Library/Android/sdk/emulator/emulator" -list-avds
test -d "$HOME/Library/Android/sdk/system-images/android-34/default/arm64-v8a"
df -h "$HOME/Library/Android/sdk"
```

SDK Manager successfully installed only the `emulator` package (37.2.12, build ID 16428233). Command-line tools, platform-tools, and system images were not updated. AVD `Pixel_7` and the API 34 arm64 image remained present. Free space after install: 5.3 GiB.

Emulator start and discovery:

```sh
"$HOME/Library/Android/sdk/emulator/emulator" -avd Pixel_7 -grpc 8554
"$HOME/Library/Android/sdk/platform-tools/adb" wait-for-device
"$HOME/Library/Android/sdk/platform-tools/adb" devices -l
"$HOME/Library/Android/sdk/platform-tools/adb" -e shell getprop sys.boot_completed
lsof -nP -iTCP:8554 -sTCP:LISTEN
find "$HOME/Library/Caches/TemporaryItems/avd/running" -maxdepth 1 -type f -name '*.ini' -print
```

Observed Emulator 37.2.12 launch, `emulator-5554` in `device` state, `sys.boot_completed=1`, TCP listener on port 8554, and active discovery file `/Users/rajeshwer/Library/Caches/TemporaryItems/avd/running/pid_68732.ini`. Non-secret discovery fields were `avd.name=Pixel 7` and `grpc.port=8554`. Emulator startup logged `Increasing RAM size to 2560MB`; no assertion is made that this changed the saved AVD configuration.

Gateway and Vite startup:

```sh
EXPERIMENT_DIR="${TMPDIR:-/tmp}/healthtick-webrtc-experiment-20261008"
"$EXPERIMENT_DIR/venv/bin/videobridge-gateway" --port=8080 --discovery_file="$HOME/Library/Caches/TemporaryItems/avd/running/pid_68732.ini"
cd "$EXPERIMENT_DIR/upstream/js/example" && npm run dev -- --host 127.0.0.1
curl --max-time 15 -sS -i http://127.0.0.1:8080/api/v1/emulator/status
curl --max-time 10 -sS -o /dev/null -w 'HTTP %{http_code} %{content_type}\n' http://127.0.0.1:5173/android-emulator-webrtc/
```

Gateway connected to localhost:8554 and bound port 8080. Status endpoint returned HTTP 200 with emulator version `37.2.12.0 (37.2.12-16428233)`, `booted: true`, 16 CPU cores, and 2.5 GiB RAM. Vite 4.5.14 reported ready at `http://127.0.0.1:5173/android-emulator-webrtc/`; the page returned HTTP 200.

Chrome interaction:

- Navigated the existing integrated Chrome page to `http://127.0.0.1:5173/android-emulator-webrtc/`.
- Entered gateway URI `127.0.0.1:8080` and clicked “Connect to Emulator”.
- The gateway logs record the browser WebSocket route returning HTTP 101, then the same RTC call failure shown below.

### Result

**BLOCKED.** `Rtc.RequestRtcStream` does not work on the latest stable native macOS Emulator available through SDK Manager (37.2.12). Gateway error:

```text
grpc.aio._call.AioRpcError:
  status = StatusCode.UNIMPLEMENTED
  details = ""
  debug_error_string = "UNIMPLEMENTED"
```

The exception occurs at the gateway call to `rtc_stub.RequestRtcStream(...)`. Chrome shows the demo controls but no real Android video frame; the WebSocket closes before SDP/WebRTC setup. Browser input was not tested because no device stream existed. Some demo interaction logs ignored pointer coordinates as out of bounds; those are not evidence of device input reaching the emulator.

### What This Proves / Does Not Prove

- Proves that this current native Mac setup—Google Python Gateway and Android Emulator 37.2.12.0 with the existing `Pixel_7` AVD—does not implement the RTC v2 method required by the Google gateway.
- Proves that the gateway can still call the separate EmulatorController status RPC successfully, and that Chrome can load the upstream demo and reach its WebSocket endpoint.
- Does not prove every Android Emulator version/platform lacks this RTC service, nor that another real-emulator streaming transport cannot satisfy the assignment.
- Does not validate live video, browser-to-device input, or latency.

### Errors, Cleanup, and Decision

- No additional emulator flags, undocumented workarounds, or alternate architecture were attempted.
- Stopped the gateway, Vite, and the exact Emulator PID (68732) with targeted `kill -TERM` commands. After waiting for orderly emulator shutdown, checked `ps`, listeners on 8080/5173/8554, and `adb devices -l`; no test emulator or service remained.
- The new stable emulator package 37.2.12 remains installed through Android SDK Manager. No production implementation, Docker, deployment, mock UI, or other SDK package was added.
- Final verification: `git diff --check` passed; `git status --short --branch` reports only `M PROCESS_LOG.md`; no generated or experiment runtime files were added to the repository. `adb devices -l` lists no devices, and no listeners remain on 8080/5173/8554. The saved `Pixel_7.avd/config.ini` still reports `hw.ramSize=2048`, so the 2560 MB startup message did not persist as a configuration change. Installed emulator reports 37.2.12.0 (build ID 16428233).

The Google native RTC path is **BLOCKED for this Mac experiment**. The user’s assignment accepts other real-device streaming paths, but fallback architecture is explicitly outside this task. The next decision is whether to begin a separately scoped investigation of an alternative real Android Emulator streaming transport; no alternative has been selected or implemented.

---

## Entry 011 — Native scrcpy/FFmpeg Browser Screen-Capture Experiment

### Time

2026-10-08 12:33 IST

### User Prompt (verbatim)

```text
We are moving to the fallback real-device streaming experiment.

Read AGENTS.md and PROCESS_LOG.md first.

IMPORTANT CONTEXT:

The previous two experiments tested the Google native Android Emulator
WebRTC/RTC path:

1. Emulator 35.6.11.0
   → Python Gateway
   → Google WebRTC
   → Rtc.RequestRtcStream
   → UNIMPLEMENTED

2. Emulator 37.2.12.0
   → Python Gateway
   → Google WebRTC
   → Rtc.RequestRtcStream
   → UNIMPLEMENTED

Therefore the Google native RTC path is now officially BLOCKED for this
macOS experiment.

Do NOT spend any more time on:
- Rtc.RequestRtcStream
- undocumented emulator RTC flags
- random emulator flags
- upgrading the emulator again
- Docker Desktop
- fake/mock Android screens
- simulated device UI

The assignment does NOT require Google's RTC implementation specifically.
The assignment requires a REAL Android environment displayed and controlled
from a browser.

Our next goal is to find and validate a simple alternative transport.

==================================================
EXPERIMENT GOAL
==================================================

Prove that we can display the REAL Pixel_7 Android Emulator screen inside
a browser without using Google's native RTC service.

For this experiment ONLY, focus on:

Android Emulator
        ↓
real screen capture
        ↓
local transport
        ↓
browser
        ↓
REAL Android screen

Do NOT implement the complete production application yet.

Do NOT implement authentication.

Do NOT implement database.

Do NOT implement polished UI.

Do NOT implement deployment.

Do NOT implement bonuses.

Do NOT implement the complete input system yet.

The only required success criterion for this experiment is:

A real Pixel_7 Android Emulator screen must appear in the browser and
continue updating without manually refreshing the browser.

==================================================
RESEARCH FIRST
==================================================

Before writing implementation code, investigate practical open-source
ways to capture the Android Emulator screen that are compatible with this
macOS Apple Silicon environment.

Prioritize approaches that can provide real-time or near-real-time frames
to a browser.

Consider, at minimum:

1. ADB-based screen capture
2. Android `screenrecord`
3. scrcpy or components of scrcpy
4. FFmpeg-based conversion/transport
5. MJPEG or another browser-compatible streaming format
6. WebSocket-based frame transport
7. WebRTC only if it does NOT depend on the blocked Google Emulator RTC API

Use authoritative documentation or official project documentation where
possible.

Do not assume a technology works just because it sounds appropriate.
Verify the actual capabilities and commands before choosing it.

==================================================
IMPORTANT DESIGN PRINCIPLE
==================================================

Choose the SIMPLEST approach that can prove the real screen can reach the
browser.

Reliability and speed are more important than building a sophisticated
media architecture during this experiment.

If a simple ADB screenshot stream can prove the vertical path quickly,
that is acceptable as an EXPERIMENT.

However, explicitly measure/observe its approximate update rate and
latency and state whether it is likely sufficient for the final assignment.

If the simple approach is clearly unsuitable for the final real-time
requirement, document that and test the next most promising approach.

Do not hide limitations.

==================================================
LOCAL ENVIRONMENT
==================================================

We are working on:

macOS Apple Silicon

Existing Android Emulator:
37.2.12.0

Existing AVD:
Pixel_7

Android:
34 arm64

ADB:
already installed and previously verified

The Google Python Gateway and upstream React WebRTC demo are NOT required
for this experiment unless they become useful for comparison.

Reuse the existing Pixel_7 AVD.

Do not create another emulator unless the existing AVD is genuinely
incompatible.

==================================================
EXPERIMENT STEPS
==================================================

1. Verify the current Android Emulator version.

2. Start Pixel_7.

3. Verify through ADB that the emulator is fully booted.

4. Verify that ADB can capture the REAL emulator screen.

5. Test the simplest viable screen-capture method.

6. Build only the minimum temporary browser/backend code needed to display
   those REAL frames in a browser.

7. Open the browser.

8. Confirm that the browser displays the REAL Android UI.

9. Change something visible on the Android emulator, for example:
   - open/close an app
   - open the notification shade
   - navigate to another screen

10. Verify that the browser view changes automatically without a browser
    refresh.

11. Estimate the update rate and visible latency.

12. If the first method is too slow for a convincing real-time experience,
    test the next most promising open-source method.

13. Stop once we have either:
    A. a convincing real-time/near-real-time browser stream, OR
    B. clear evidence that the tested fallback approach is unsuitable.

==================================================
STRICT STOP CONDITIONS
==================================================

If a method fails because of a missing dependency, investigate only the
smallest necessary fix.

Do not spend a long time debugging an approach that is fundamentally
unsuitable.

If the chosen method becomes complicated enough that we are effectively
building a new media server before proving basic browser streaming,
STOP and report the problem.

Do not start implementing the final architecture automatically.

Do not add unrelated packages to the main project unless absolutely
necessary.

Prefer isolated experiment dependencies where practical.

==================================================
SUCCESS CRITERIA
==================================================

SUCCESS means:

- Pixel_7 is a real Android Emulator.
- Browser displays frames captured from that emulator.
- Frames update without browser refresh.
- Changing the Android emulator screen causes the browser view to change.
- No fake/mock/simulated Android screen is used.

Record:

- capture method
- transport method
- exact commands
- dependencies installed
- browser technology used
- approximate frame/update rate
- approximate visible latency
- CPU/resource observations if obvious
- problems encountered
- whether this approach is suitable for the final assignment
- what would still be required for browser → Android input

==================================================
PROCESS_LOG REQUIREMENT
==================================================

After the experiment, update PROCESS_LOG.md according to AGENTS.md.

Append a new entry only.

Include:

- time
- my exact prompt above verbatim
- what you investigated
- sources/documentation consulted
- commands used
- files created/changed
- errors/failures
- successful results
- dead ends
- performance observations
- your conclusion
- what I need to decide next

NEVER rewrite or delete previous PROCESS_LOG entries.

==================================================
GIT SAFETY
==================================================

Do not commit automatically.

Before finishing, run:

git status
git diff --check

Clearly report exactly which project files changed.

Do not modify README architecture claims unless the experiment actually
proves the new architecture.

==================================================
FINAL REPORT
==================================================

At the end, report exactly:

RESULT: SUCCESS / PARTIAL / BLOCKED

Capture method:
Transport:

Real Android frame in browser:
YES / NO

Browser auto-updated:
YES / NO

Approximate update rate:

Approximate visible latency:

Browser → Android input:
NOT TESTED

Main technical limitation:

Is this suitable as the foundation for the final assignment:
YES / NO / NEEDS ANOTHER EXPERIMENT

Recommended next step:

Then STOP.

Do not implement the complete application in this task.
```

### What Was Investigated and Sources Consulted

- Re-read `AGENTS.md` and `PROCESS_LOG.md` before the experiment.
- Verified Android Emulator **37.2.12.0 (build 16428233)**, the existing `Pixel_7` AVD, and its Android 34 arm64 image; verified macOS 27.0/arm64 and SDK ADB 36.0.0. The `adb` executable was not on shell `PATH`, so commands used the SDK-installed executable at `$HOME/Library/Android/sdk/platform-tools/adb`.
- Consulted the Android Developers ADB/screen-capture page: https://developer.android.com/tools/adb#screencap
- Consulted the official scrcpy project README and documentation:
  - https://github.com/Genymobile/scrcpy
  - https://github.com/Genymobile/scrcpy/blob/master/doc/macos.md
  - https://github.com/Genymobile/scrcpy/blob/master/doc/video.md
  - https://github.com/Genymobile/scrcpy/blob/master/doc/recording.md
  - https://github.com/Genymobile/scrcpy/blob/master/doc/develop.md
- The upstream scrcpy README says macOS is supported and advertises 30–120 FPS and 35–70 ms latency; those are upstream claims, not measurements for this experiment. Its documentation confirms the device-side server sends raw H.264 by default and the client can record video to Matroska.
- Checked Android's on-device `screenrecord --help`. The installed Android 34 tool records MP4 to a filename, defaults to a 180-second limit (with `--time-limit 0` to remove it), and does not document a raw-H.264 stdout mode. Did not use it for a browser stream.
- Queried installed FFmpeg (`ffmpeg -hide_banner -h muxer=mpjpeg`); the installed build exposes an `mpjpeg` MIME multipart JPEG muxer with a configurable boundary, providing a browser `<img>` stream format without a separate browser media decoder.

### Commands and Observed Results

Environment, AVD, and boot:

```sh
"$HOME/Library/Android/sdk/emulator/emulator" -version
"$HOME/Library/Android/sdk/emulator/emulator" -list-avds
"$HOME/Library/Android/sdk/platform-tools/adb" version
sw_vers
uname -m
grep -E '^(avd.ini.displayname|abi.type|hw.cpu.arch|image.sysdir.1|hw.ramSize|hw.lcd.width|hw.lcd.height)=' "$HOME/.android/avd/Pixel_7.avd/config.ini"
"$HOME/Library/Android/sdk/emulator/emulator" -avd Pixel_7
"$HOME/Library/Android/sdk/platform-tools/adb" wait-for-device
"$HOME/Library/Android/sdk/platform-tools/adb" -e shell getprop sys.boot_completed
"$HOME/Library/Android/sdk/platform-tools/adb" devices -l
```

Observed Emulator 37.2.12.0 and `Pixel_7`. Boot completed (`sys.boot_completed=1`); ADB listed `emulator-5554` in `device` state. Existing display was 1080x2400 at density 420.

Direct ADB capture and throughput check:

```sh
mkdir -p /tmp/healthtick-fallback-20261008
"$HOME/Library/Android/sdk/platform-tools/adb" -e exec-out screencap -p > /tmp/healthtick-fallback-20261008/pixel7-initial.png
file /tmp/healthtick-fallback-20261008/pixel7-initial.png
sips -g pixelWidth -g pixelHeight /tmp/healthtick-fallback-20261008/pixel7-initial.png
python3.11 - <<'PY'
import subprocess, time, statistics
adb = '/Users/rajeshwer/Library/Android/sdk/platform-tools/adb'
values=[]
start=time.perf_counter()
for _ in range(15):
    t=time.perf_counter()
    result=subprocess.run([adb,'-e','exec-out','screencap','-p'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    values.append((time.perf_counter()-t)*1000)
elapsed=time.perf_counter()-start
print(f'capture_count={len(values)} total_s={elapsed:.3f} approximate_serial_fps={len(values)/elapsed:.2f}')
print(f'capture_ms_median={statistics.median(values):.1f} p95={sorted(values)[int(.95*(len(values)-1))]:.1f} min={min(values):.1f} max={max(values):.1f}')
print(f'png_bytes_last={len(result.stdout)}')
PY
```

Capture succeeded and produced a viewable real Android home screen PNG at 1080x2400. One screenshot took 1.164 s. Fifteen serial captures took 10.819 s: **1.39 captures/s**, median 700.1 ms, p95 837.0 ms, last PNG 1,307,340 bytes. This proved ADB capture reaches a real screen but was too slow and bandwidth-heavy to serve as the live path.

Capture-method documentation checks and relevant dependency installation:

```sh
"$HOME/Library/Android/sdk/platform-tools/adb" -e shell screenrecord --help
ffmpeg -hide_banner -h muxer=mpjpeg
brew info scrcpy
brew list --versions ffmpeg libusb sdl3 scrcpy
brew install scrcpy
PATH="/opt/homebrew/bin:$HOME/Library/Android/sdk/platform-tools:$PATH" scrcpy --version
PATH="/opt/homebrew/bin:$HOME/Library/Android/sdk/platform-tools:$PATH" scrcpy --help | grep -E -- '--no-window|--no-playback|--record-format|--max-size|--max-fps'
```

`brew install scrcpy` installed scrcpy 5.0 and missing `libusb`; Homebrew also upgraded already-installed dependency formulas: `ffmpeg` 9.0.1_1→9.0.2, `libvmaf` 3.2.0→3.2.1, `ca-certificates` 2026-08-13→2026-09-25, `openssl@3` 3.6.3→3.6.5, `sdl3` 3.4.14→3.4.18, `sdl2-compat` 2.32.70→2.32.74, and `xz` 5.8.3→5.8.4. This was an unanticipated Homebrew dependency resolution side effect; no Homebrew or experiment files were added to the project.

Verified scrcpy-to-FFmpeg FIFO input:

```sh
mkfifo /tmp/healthtick-fallback-20261008/scrcpy-video.mkv
ffmpeg -hide_banner -loglevel info -i /tmp/healthtick-fallback-20261008/scrcpy-video.mkv -an -f null -
scrcpy --no-window --no-playback --no-control --no-audio --max-size=720 --max-fps=20 --record=/tmp/healthtick-fallback-20261008/scrcpy-video.mkv --record-format=mkv
```

The isolated Python test launched FFmpeg reading the FIFO, launched scrcpy writing its documented MKV recording to the FIFO, ran for 10 seconds, then stopped the child processes. Both exited with code 0 and FFmpeg decoded 11 H.264 frames (324x720, 10 fps timebase). The first attempt did not establish live browser delivery; the downstream end-to-end test below was needed to validate streaming behavior.

Temporary bridge and browser test:

```sh
python3.11 -m py_compile /tmp/healthtick-fallback-20261008/server.py
python3.11 /tmp/healthtick-fallback-20261008/server.py
curl --max-time 5 -sS -i http://127.0.0.1:8765/
curl --max-time 5 -sS http://127.0.0.1:8765/metrics
```

The temporary file `/tmp/healthtick-fallback-20261008/server.py` uses only Python 3.11 standard-library HTTP/threading/process APIs. It starts scrcpy (H.264 capture/record to a local Matroska FIFO), FFmpeg (decode and transcode to multipart JPEG), and serves the page and `/stream.mjpg` at `http://127.0.0.1:8765/`. The browser displays the stream in an `<img>` and polls only a metrics endpoint; it does not refresh the page. No npm, Python package, React project, production source, or persistent project-side dependency was created.

The first `py_compile` failed with `SyntaxError: bytes can only contain ASCII literal characters` because the initial HTML bytes literal contained a Unicode ellipsis. Changed the temporary page literal to Unicode text encoded as UTF-8; compilation and HTTP serving then succeeded.

The first FFmpeg relay used its default output frame synchronization and initially reported over 10,000 duplicated frames. The first metrics parser also retained too much boundary overlap and overcounted frames. Those values were invalid and are not used in the final measurements. Corrected the temporary relay to use FFmpeg `-fps_mode passthrough` and retain only the six-byte multipart-marker overlap. The corrected FFmpeg log had no duplicate-frame warnings.

Browser and real Android screen transition:

```sh
curl --max-time 5 -sS http://127.0.0.1:8765/mark
"$HOME/Library/Android/sdk/platform-tools/adb" -e shell am start -a android.settings.SETTINGS
"$HOME/Library/Android/sdk/platform-tools/adb" -e shell input keyevent 3
"$HOME/Library/Android/sdk/platform-tools/adb" -e shell input swipe 540 5 540 1800 500
curl --max-time 5 -sS http://127.0.0.1:8765/metrics
```

Navigated the shared Chrome page to `http://127.0.0.1:8765/`. It visibly displayed the real emulator home screen, then Settings, then the notification shade; the `<img>` stream changed automatically while the browser stayed on the same page. `adb dumpsys activity activities` confirmed Settings was the actual foreground Android activity during the Settings check. The notification-shade screenshot in Chrome matched the real Pixel_7 UI.

Before the 500 ms notification-shade swipe, `/mark` returned frame count 72. Metrics then reported 88 frames at t+0.5 s, 99 at t+1 s, 105 at t+2 s, and 105 at t+3 s. This is approximately **20–25 forwarded frames/s while the screen was changing** (33 multipart frames over roughly 1.5 seconds), with no new frames once the display became static. The overall average across the largely static 89-second sample was 114/89.17 = 1.28 frames/s; that low overall figure reflects scrcpy's change-driven output and long idle time, not a fixed-rate screenshot poll.

The relay's first frame after the action marker arrived at **233.9 ms**. The browser visibly rendered the frame; exact browser compositor/display timing was not instrumented, so 0.23 s is a measured first-frame delivery time and only an approximate lower bound for visible latency. A process sample while static showed the Python relay at 0.0% CPU and 0.2% memory; no CPU sample under sustained motion or total emulator/FFmpeg load was taken.

### Outcome, Limitations, and Cleanup

**SUCCESS for the screen-only criterion.** The capture is real Pixel_7 content. Capture method: scrcpy device-side H.264 screen capture. Transport: scrcpy records to a local Matroska FIFO → FFmpeg converts to multipart MJPEG → minimal Python 3.11 HTTP server → Chrome `<img>`. No Google RTC RPC or mock/simulated screen was used.

The first ADB screenshot route is unsuitable for convincing real-time updates at ~1.4 FPS and ~700 ms median capture cost. The scrcpy/FFmpeg/MJPEG local route achieved about 20–25 FPS during a UI transition and around 234 ms to first frame delivery. It is a credible local screen-stream foundation but is **not yet approved as the assignment architecture**: browser-to-Android input was not tested, and behavior under sustained animation, remote transport, production lifecycle/reconnects, and deployment was not tested. Browser input was deliberately not tested; the only UI-changing commands were issued through ADB.

No Google RTC experiment was retried. No production frontend/backend, authentication, database, deployment, React app, mock UI, or architecture/documentation change was made. The temporary relay, screenshot, and test logs were located under `/tmp/healthtick-fallback-20261008/`, outside the repository. The relay and scrcpy/FFmpeg child processes stopped; the experiment emulator process exited and ADB subsequently listed no devices; ports 8765, 5554, and 5555 had no listeners.

Final Git checks: `git status --short --branch` showed only `M PROCESS_LOG.md`; `git diff --check` passed. No commit was created. The next decision is whether to authorize a separate, minimal experiment to validate browser-to-Android input using this transport before selecting it as a foundation; no final architecture selection was made.

### Post-Experiment Cleanup

After recording the entry, removed the named temporary Python source, screenshot, logs, Matroska FIFO, and Python bytecode cache from `/tmp/healthtick-fallback-20261008/`; the temporary directory is now absent. No project runtime or generated artifact remains.

---

## Entry 012 — Browser Tap Through Python and ADB

### Time

2026-10-08 12:43 IST

### User Prompt (verbatim)

```text
We now have a successful real Android → browser video experiment.

Read AGENTS.md and PROCESS_LOG.md first.

PREVIOUS EXPERIMENT RESULT:

Pixel_7 Android Emulator
→ scrcpy device-side H.264 capture
→ Matroska FIFO
→ FFmpeg multipart MJPEG
→ Python 3.11 HTTP
→ Chrome <img>

Result:
- REAL Android frame appeared in browser: YES
- Browser updated without refresh: YES
- Approximately 20–25 FPS during screen transitions
- Approximately 234 ms first-frame delivery
- PROCESS_LOG.md was updated
- No project files changed except PROCESS_LOG.md
- No commit was made

This experiment is successful.

IMPORTANT:

Do NOT redesign the video transport yet.

Do NOT replace scrcpy.

Do NOT return to Google Emulator WebRTC.

Do NOT implement deployment.

Do NOT implement authentication.

Do NOT implement database.

Do NOT implement bonuses.

Do NOT build a polished UI.

Our only goal now is to prove:

BROWSER → BACKEND → ANDROID EMULATOR

using the same real Pixel_7 emulator and the existing screen-streaming
experiment.

==================================================
EXPERIMENT GOAL
==================================================

Add ONE browser-originated interaction to the existing experiment.

The preferred first interaction is:

BROWSER CLICK
      ↓
Python backend
      ↓
ADB input command
      ↓
Pixel_7 Android Emulator
      ↓
screen changes
      ↓
existing browser video stream updates

Use a simple visible Android target so success is unambiguous.

For example, clicking a coordinate that opens an Android UI element or
changes the current screen.

Do NOT rely on the user clicking an arbitrary location without explaining
what should happen.

==================================================
FIRST TEST — TAP
==================================================

Implement the minimum possible browser interaction:

1. Browser displays the existing REAL Android screen.

2. User clicks/taps somewhere on the displayed Android screen.

3. Browser sends the click coordinates to the Python backend.

4. Backend converts browser/display coordinates into Android screen
   coordinates.

5. Backend sends the corresponding input event to the Pixel_7 emulator.

6. Android responds.

7. Existing video stream reflects the change in the browser.

The Android screen must be REAL.

Do not simulate the response in JavaScript.

Do not change the browser image artificially.

==================================================
COORDINATE MAPPING
==================================================

This is important because the assignment explicitly requires coordinate
accuracy regardless of browser window size.

Determine the actual Android frame dimensions.

Determine the displayed browser image dimensions.

Implement the minimum coordinate transformation required:

browser/display coordinates
        ↓
normalized coordinates
        ↓
Android frame coordinates
        ↓
ADB input

Account for aspect ratio and any letterboxing/padding.

Do NOT assume browser pixels equal Android pixels.

Document the transformation.

==================================================
TESTING
==================================================

Test at least:

TEST 1:
Display the Android screen at its normal browser size.
Click a known Android target.
Verify Android responds.

TEST 2:
Resize the browser window significantly.
Click the same logical Android target.
Verify Android responds at the correct location.

TEST 3:
Change the browser display size again.
Repeat the interaction.

The purpose of TEST 2 and TEST 3 is to verify coordinate mapping rather
than just proving that one hardcoded coordinate works.

==================================================
INPUT METHOD
==================================================

Prefer a simple, reliable input method.

ADB is acceptable for this experiment.

Investigate the correct ADB input command for touch/tap events and use
the real Pixel_7 device.

Do not implement a custom Android application.

Do not install an input helper app on the emulator.

Do not use fake events.

If ADB input works reliably, keep it simple.

==================================================
LATENCY
==================================================

For the tap experiment, estimate:

browser click
→ backend receives event
→ Android responds
→ changed frame becomes visible in browser

Do not claim laboratory-grade latency.

If exact end-to-end timing is difficult, report the measurement method and
limitations honestly.

==================================================
ERROR HANDLING
==================================================

If the browser sends invalid coordinates:

- backend must reject them safely.

If the emulator is disconnected:

- backend must return a clear error.

Do not over-engineer this.

==================================================
ARCHITECTURE CHECK
==================================================

At the end, determine whether this architecture is now sufficient as the
basis for the assignment:

Video:
Android Emulator
→ scrcpy
→ FFmpeg
→ MJPEG
→ Python
→ Browser

Input:
Browser
→ Python
→ ADB
→ Android Emulator

Do NOT implement swipe, scroll, keyboard, deployment, or bonuses yet.

We first need one reliable tap.

==================================================
PROCESS_LOG REQUIREMENT
==================================================

After the experiment, append a new entry to PROCESS_LOG.md according to
AGENTS.md.

Include:

- time
- my exact prompt above verbatim
- investigation performed
- commands used
- files changed
- dependencies added
- successful results
- errors/failures
- coordinate mapping approach
- test results
- latency observations
- limitations
- conclusion
- recommended next step

NEVER rewrite or delete previous PROCESS_LOG entries.

==================================================
GIT SAFETY
==================================================

Do not commit automatically.

Before finishing:

git status
git diff --check

Report exactly which project files changed.

==================================================
FINAL REPORT
==================================================

End with exactly this structure:

RESULT: SUCCESS / PARTIAL / BLOCKED

Real Android video:
YES / NO

Browser → backend input:
YES / NO

Backend → Android input:
YES / NO

Android visibly responded:
YES / NO

Coordinate mapping:
WORKING / PARTIAL / FAILED

Resize test:
PASSED / FAILED

Approximate tap latency:

Main limitation:

Is this architecture suitable as the foundation for the final assignment:
YES / NO / NEEDS ANOTHER EXPERIMENT

Recommended next step:

Then STOP.

Do not implement additional features automatically.
```

### Investigation and Setup

- Re-read `AGENTS.md` and `PROCESS_LOG.md` before experiment commands.
- Verified Emulator 37.2.12.0, `Pixel_7` AVD, SDK ADB 36.0.0, Python 3.11.16, scrcpy 5.0, and FFmpeg 9.0.2. Reused the installed tools from the prior experiment; no dependencies were installed or upgraded in this step.
- Reused the actual Android 34 arm64 `Pixel_7`, booted to `sys.boot_completed=1`, with physical Android size 1080x2400 and density 420.
- Consulted Android ADB command documentation https://developer.android.com/tools/adb#shellcommands and scrcpy control documentation https://github.com/Genymobile/scrcpy/blob/master/doc/control.md. Used Android's shell `input tap` for the browser-triggered tap.
- Created one temporary Python 3.11 server at `/tmp/healthtick-tap-experiment/server.py` (outside the project). It re-created the existing scrcpy → Matroska FIFO → FFmpeg MJPEG stream and added a minimal page and `POST /tap`. It has no third-party Python dependencies and binds only to `127.0.0.1`.
- The browser derives actual visible-content bounds for `object-fit: contain`: `scale=min(elementBoxWidth/frameWidth, elementBoxHeight/frameHeight)`, then centers the content within the image element, removes letterbox offsets, and normalizes the pointer position. The backend validates finite normalized coordinates in `[0,1)`, checks the captured-frame aspect ratio against the live Android display, reads active dimensions with `adb shell wm size`, then maps `x=floor(nx*androidWidth)` and `y=floor(ny*androidHeight)` and runs `adb -s <serial> shell input tap <x> <y>`. Coordinates are bounded to the display.
- Device health/tap requests return HTTP 503 with a JSON error when there is no connected emulator. Invalid normalized coordinates return HTTP 400 without sending an ADB input command.

### Commands Executed

Version, boot, and display verification:

```sh
"$HOME/Library/Android/sdk/emulator/emulator" -version
"$HOME/Library/Android/sdk/emulator/emulator" -list-avds
"$HOME/Library/Android/sdk/platform-tools/adb" version
PATH="/opt/homebrew/bin:$HOME/Library/Android/sdk/platform-tools:$PATH" scrcpy --version
ffmpeg -version
python3.11 --version
"$HOME/Library/Android/sdk/emulator/emulator" -avd Pixel_7
"$HOME/Library/Android/sdk/platform-tools/adb" wait-for-device
"$HOME/Library/Android/sdk/platform-tools/adb" -e shell getprop sys.boot_completed
"$HOME/Library/Android/sdk/platform-tools/adb" devices -l
"$HOME/Library/Android/sdk/platform-tools/adb" -e shell wm size
"$HOME/Library/Android/sdk/platform-tools/adb" -e shell wm density
"$HOME/Library/Android/sdk/platform-tools/adb" -e shell am start -a android.settings.SETTINGS
```

Observed boot completion, `emulator-5554` in device state, and display size 1080x2400.

Temporary relay:

```sh
mkdir -p /tmp/healthtick-tap-experiment
PYTHONDONTWRITEBYTECODE=1 python3.11 /tmp/healthtick-tap-experiment/server.py
curl --max-time 5 -sS http://127.0.0.1:8765/health
curl --max-time 5 -sS -o /dev/null -w 'HTTP %{http_code}\n' http://127.0.0.1:8765/
```

The health endpoint reported `{"device":"emulator-5554","android_width":1080,"android_height":2400}`. Initial scrcpy MJPEG display was blank while the emulator's restored UI was static; a real ADB-triggered screen transition (notification shade swipe, then restored Settings) caused scrcpy frames to flow. After that, the browser showed the live real screen. This is an observed stream-start limitation for a completely static screen at this test startup, not evidence of a fake frame.

### Three Browser Tap Tests

Target was the real Android Settings main-page row **“Network & internet”**. On each test, a browser click at the same normalized content location approximately `(0.5, 0.362)` was converted and delivered through the backend. After each successful click, `adb dumpsys activity activities` reported the actual Android foreground activity `com.android.settings/.SubSettings`; the live browser stream displayed the Network & internet settings page.

| Test | Browser viewport | Actual frame | Displayed content bounds | Normalized target | ADB tap coordinates | Result |
|---|---:|---:|---:|---:|---:|---|
| 1 — normal | 582×789 | 486×1080 | 248.53×552.30 CSS px within 550×552.30 image box | (0.500000, 0.362124) | (540, 869) | Opened Network & internet |
| 2 — resized | 1280×900 | 486×1080 | 340.20×756 CSS px within 970×756 image box | (0.500000, 0.361111) | (540, 866) | Opened Network & internet |
| 3 — resized again | 900×600 | 486×1080 | 226.80×504 CSS px within 590×504 image box | (0.500000, 0.361111) | (540, 866) | Opened Network & internet |

Small y-coordinate variation (3 Android pixels between the normal-size test and resized tests) comes from browser pointer coordinate rounding; all three selected the same Settings row and opened the same page. The natural video frame is 486x1080, while Android's ADB display is 1080x2400; their aspect ratios match and are scaled independently. Thus the test did not equate browser CSS pixels, encoded frame pixels, and Android physical pixels.

Latency observations (not lab-grade):

- First test: browser click until UI metrics observed a forwarded changed frame, about **695 ms**; server-measured first frame after tap marker, **434 ms**.
- Second test: about **515 ms** click-to-frame observation; backend marker to frame, **327 ms**.
- Third test: about **398 ms** click-to-frame observation; backend marker to frame, **277 ms**.
- These are approximate delivery/observation timings, including browser polling interval and local process scheduling; the browser compositor's exact physical display time was not instrumented. A reasonable observed range is **~0.4–0.7 seconds** from browser click until the frontend detected a new streamed frame.

### Error Handling, Failures, and Dead Ends

- Initial browser-page sizing let the portrait image's intrinsic height overflow the viewport container; coordinate tests would have been invalid. Fixed the temporary page to use a positioned image constrained to its viewport stage and explicit `object-fit: contain` content-bound mapping. Confirmed no page scroll and measured the final stage/frame/content bounds for each test.
- On starting a fresh scrcpy stream while Android was static, the `<img>` initially remained blank and the multipart output counter stayed at zero until a real display update occurred. ADB-driven swipe/back/settings transitions generated actual frames. The subsequent three browser-originated tap transitions all streamed normally. This initial-frame behavior should be addressed/validated in a later reliability test.
- Invalid-input probe:

```sh
fetch('/tap', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({nx:1,ny:0.5,frameWidth:486,frameHeight:1080})})
```

Observed HTTP 400: `{"error":"Normalized tap coordinates must be finite values in [0, 1)"}`. No emulator input was issued for invalid coordinates.
- Emulator-disconnect probe: stopped the exact QEMU PID for this experiment, waited for ADB to list no devices, restarted the temporary API without launching an emulator, and POSTed a syntactically valid tap. Observed HTTP 503: `{"error":"No connected Android Emulator is available"}`. An initial POST attempted during emulator shutdown timed out during the transition; the stable disconnected-state retry returned the expected 503.
- No custom Android app, helper app, fake UI, non-Google RTC path, production system, or extra Python package was used.

### Result, Files, and Next Decision

The end-to-end tap chain succeeded: **browser click → Python HTTP backend → ADB `input tap` → real Pixel_7 Settings navigation → scrcpy/FFmpeg MJPEG frame automatically delivered back to the browser**. Resize tests passed at three significantly different viewport sizes. The video method remained unchanged.

This validates that the video-plus-input approach is a technically plausible assignment foundation for a local emulator experiment. It is **not yet a complete assignment architecture**: only taps are tested; swipes, scrolling, keyboard/text input, repeatability under continuous activity, production UI/API hardening, server deployment, and remote transport remain untested. The initial static-screen first-frame observation also needs a deliberate reliability check.

Files changed in the project: only `PROCESS_LOG.md` (this append-only entry). Temporary script, screenshots, logs, Matroska FIFO, and bytecode were under `/tmp/healthtick-tap-experiment/`, not project source. `scrcpy` 5.0 and dependencies were already installed by the preceding experiment; no dependency was added in this experiment. No README or architecture claims were edited.

Stopped the temporary Python server and exact experiment emulator process. ADB lists no device; listeners and capture processes are stopped. Temporary experiment files are being removed. No commit was made. The next user decision is whether to authorize proceeding to the next scoped milestone (for example swipe/scroll) using this validated local transport; no additional feature is started automatically.

### Final Cleanup Verification

Removed the temporary experiment directory and its server source, screenshots, logs, and Python bytecode. Confirmed no ADB device, listeners on ports 8765/5554/5555, emulator process, scrcpy process, FFmpeg capture process, or Python tap server remains. `git status --short --branch` shows only `M PROCESS_LOG.md`; `git diff --check` passed. No commit was created.

## Entry 013 — Local Core Implementation: Video, Gesture, Keyboard, and Setup

### Time

2026-10-08T13:30:25+05:30 (local time observed during final validation; implementation and tests continued after this timestamp).

### User Prompt (verbatim)

```text
We have now validated the core architecture successfully.

Read AGENTS.md and PROCESS_LOG.md first.

IMPORTANT: We are now in IMPLEMENTATION MODE.

We need to finish the assignment quickly.

Do NOT start another architecture experiment.
Do NOT return to Google Emulator WebRTC.
Do NOT redesign the streaming architecture.
Do NOT build authentication.
Do NOT build a database.
Do NOT add optional bonus features yet.
Do NOT spend time on visual polish.

The validated architecture is:

Android Emulator
    ↓
scrcpy device-side H.264
    ↓
FFmpeg
    ↓
MJPEG
    ↓
Python backend
    ↓
Browser

Input:

Browser
    ↓
Python backend
    ↓
ADB
    ↓
Android Emulator

Validated successfully:
- REAL Android video in browser
- Browser auto-updates
- Browser → backend input
- Backend → Android input
- Android visibly responds
- Coordinate mapping works
- Browser resize test passes
- Tap latency approximately 0.4–0.7 seconds

The assignment's remaining core requirements are:
1. Live Android screen
2. Tap/click
3. Swipe
4. Scroll
5. Keyboard input
6. Coordinate accuracy regardless of browser size
7. Latency measurement
8. Public deployment with Android environment/backend on server

We now need to implement the remaining core requirements and prepare for
deployment.

==================================================
PHASE 1 — FIX INITIAL FRAME
==================================================

Fix the known problem:

When the stream starts while the Android screen is static, the browser
image can remain blank until Android produces a screen change.

The browser should receive/display an initial frame reliably when a session
starts.

Do NOT redesign the transport.

Use the existing scrcpy + FFmpeg + MJPEG approach.

Choose the smallest reliable fix.

Verify that:

1. Start Android emulator.
2. Start backend/stream.
3. Open browser.
4. Without touching Android, the browser eventually displays the real
   Android screen.

Do not proceed until this is working.

==================================================
PHASE 2 — SWIPE
==================================================

Add browser swipe support.

The browser must capture:

pointer/touch down
pointer movement
pointer/touch up

Send the required gesture information to the Python backend.

Backend must convert browser coordinates to Android coordinates using the
same coordinate mapping already validated.

Then generate the corresponding real Android touch gesture through ADB.

Do NOT simulate scrolling in the browser.

The Android emulator itself must receive the gesture.

Test:

- swipe upward
- swipe downward
- swipe left/right if useful

Use an Android screen where the result is visually obvious, such as
Settings or another scrollable screen.

Verify the browser video reflects the Android response.

==================================================
PHASE 3 — SCROLL
==================================================

Support mouse-wheel scrolling.

Browser:

wheel event
    ↓
backend
    ↓
Android input
    ↓
real Android scroll response

If Android/ADB does not have a clean direct wheel equivalent, translate
the browser wheel action into an appropriate short vertical swipe.

Keep the implementation simple.

Test scrolling on a real scrollable Android screen.

Do NOT implement fake browser-side scrolling.

==================================================
PHASE 4 — KEYBOARD INPUT
==================================================

Add keyboard input.

When the Android emulator has a text field focused:

Browser keyboard event
    ↓
backend
    ↓
ADB text/key input
    ↓
Android text field

Support at least normal text entry.

Handle special keys where reasonably practical, such as:

- Backspace
- Enter
- Space

Do not attempt to support every possible keyboard key if that would delay
completion.

Test using a real Android text input field.

For text containing spaces or special characters, use a safe encoding/
escaping strategy appropriate for ADB.

Do NOT fake the text in the browser.

==================================================
PHASE 5 — COORDINATE MAPPING
==================================================

Keep the existing coordinate mapping implementation that already passed
the resize test.

Do not replace it unnecessarily.

Make sure it handles:

- browser scaling
- different displayed image sizes
- aspect ratio
- letterboxing/padding if present
- device resolution

Document the formula clearly in code/comments or documentation.

Test at least two substantially different browser sizes.

==================================================
PHASE 6 — LATENCY MEASUREMENT
==================================================

Create a simple repeatable latency measurement procedure.

Measure separately where practical:

1. Browser input → backend received
2. Backend → ADB input issued
3. Android screen change → browser-visible changed frame

Then report the approximate end-to-end latency.

Do NOT claim precision that was not actually measured.

Keep the methodology simple enough to explain in the final write-up.

==================================================
PHASE 7 — RELIABILITY
==================================================

Add only lightweight reliability handling:

- clear error if emulator is unavailable
- clear error if ADB command fails
- browser should reconnect/recover from a temporary stream disconnect
  where practical
- cleanly terminate child processes
- avoid orphaned scrcpy/FFmpeg/backend processes

Do not build a complex session manager.

==================================================
PHASE 8 — TEST THE COMPLETE LOCAL CORE
==================================================

Run a complete local test covering:

1. Open browser.
2. Real Android screen appears automatically.
3. Tap.
4. Swipe.
5. Scroll.
6. Focus Android text field.
7. Type text from browser keyboard.
8. Resize browser.
9. Repeat tap at resized display.
10. Verify Android responds correctly.

Record any failures.

==================================================
IMPORTANT SCOPE RULE
==================================================

The assignment does NOT require:

- authentication
- database
- multi-user system
- Kubernetes
- autoscaling
- CI/CD
- sophisticated session management
- production-grade media infrastructure
- optional clipboard
- recording/playback
- restricted app mode

Do not implement these now.

We need the required core functionality first.

==================================================
PROJECT STRUCTURE
==================================================

Now that the architecture is validated, move the successful experiment code
into the actual project structure cleanly.

Use:

frontend/
backend/
emulator/
docs/

Do not leave the final implementation dependent on an arbitrary temporary
directory outside the project.

The exact implementation structure is your decision, but keep it small
and understandable.

==================================================
README
==================================================

After the local core works, update README.md with the ACTUAL architecture
and local setup instructions.

Do not document anything that was not actually tested.

Include:

- architecture
- prerequisites
- Android Emulator setup
- Pixel_7 setup
- scrcpy requirement
- FFmpeg requirement
- Python requirement
- backend startup
- frontend/browser startup
- how to test tap
- how to test swipe
- how to test scroll
- how to test keyboard
- coordinate mapping explanation
- known limitations

Do not write deployment instructions yet unless the deployment has actually
been tested.

==================================================
PROCESS_LOG
==================================================

Append to PROCESS_LOG.md after meaningful implementation milestones.

Never rewrite or delete previous entries.

Record:
- exact user prompts
- actions
- commands
- failures
- fixes
- decisions
- test results

The existing successful experiments must remain preserved.

==================================================
GIT
==================================================

Do NOT commit automatically.

Before finishing:

git status
git diff --check

Report all changed files.

==================================================
STOP CONDITION
==================================================

Stop after the complete LOCAL CORE works.

Do NOT deploy in this task yet.

At the end report:

RESULT: SUCCESS / PARTIAL / BLOCKED

Initial frame:
WORKING / FAILED

Tap:
WORKING / FAILED

Swipe:
WORKING / FAILED

Scroll:
WORKING / FAILED

Keyboard:
WORKING / FAILED

Coordinate mapping:
WORKING / FAILED

Resize test:
PASSED / FAILED

Latency measurement:
COMPLETED / PARTIAL / NOT COMPLETED

Local core:
READY FOR DEPLOYMENT / NOT READY

Remaining blocker:

Recommended next step:

Do not implement bonuses.
Do not implement deployment yet.
```

### Actions Taken

- Continued from the in-progress project implementation after reading the existing agent instructions and log in the earlier implementation context. Kept the chosen scrcpy → FFmpeg → MJPEG video path and ADB input; did not return to Google RTC or begin deployment.
- Inspected and corrected the project backend input setup: `_input_request` now assigns actual Android `width, height` from `display_size(serial)` before coordinate mapping. Also reject malformed swipe-frame points with an explicit 400 response and constrain resolved static-file paths to the built frontend directory.
- Kept a real ADB screenshot converted through FFmpeg as the first MJPEG part, followed by the scrcpy/FFmpeg live stream.
- Added a one-second first-key settle deadline after an Android screen tap. The deadline is honored in the serialized input queue and included in browser-side response timing. This addressed the observed missing first character when text started during Android's field/IME transition.
- Updated the responsive React input client for tap, pointer swipe, wheel-to-swipe, keyboard text/special keys, and approximate frame-arrival timing; preserved its letterbox-aware normalized coordinate calculation.
- Updated `.gitignore` for Python bytecode/venv and frontend `node_modules`/`dist`.
- Replaced the stale planned-WebRTC README with the tested local architecture and setup/use/limitations, added the AVD notes in `emulator/README.md`, and recorded the measurement method/examples in `docs/latency-and-validation.md`.
- Frontend dependencies in the existing project manifest are React 18.3.1, React DOM 18.3.1, Vite 6.4.4, and `@vitejs/plugin-react` 4.3.4. No dependency was installed during the final validation continuation. Earlier in the implementation sequence, an install attempt from the repository root failed because there is no root `package.json`; its accidental empty root lockfile was removed. Dependencies were then installed under `frontend/`, and Vite was pinned to 6.4.4 after audit advisories. The exact earlier install command is not available in this continuation, so it is not repeated here.

### Commands and Checks Performed

Commands directly observed during this continuation included:

```sh
python3.11 -m py_compile backend/server.py
npm --prefix frontend run build
npm --prefix frontend audit --audit-level=moderate
curl -sS --max-time 5 http://127.0.0.1:8000/api/health
curl -sS --max-time 5 http://127.0.0.1:8000/api/metrics
curl -sS --max-time 5 -X POST http://127.0.0.1:8000/api/input/tap \
  -H 'Content-Type: application/json' \
  --data '{"x":1,"y":0.5,"frameWidth":486,"frameHeight":1080}'
adb -e shell wm size
adb -e shell am force-stop com.android.settings
adb -e shell am start -a android.settings.SETTINGS
adb -e exec-out screencap -p
adb -e shell uiautomator dump /sdcard/healthtick-ui.xml
adb -e pull /sdcard/healthtick-ui.xml /tmp/healthtick-ui.xml
git status --short --untracked-files=all
git diff --check
```

`adb` in those commands resolved to `$HOME/Library/Android/sdk/platform-tools/adb`. Additional browser actions were performed in Chrome at `http://127.0.0.1:8000/`; the production build was served by the Python backend on the same origin. Viewports exercised in this continuation included 1024x768 and 640x480.

### Results

- **Initial frame — WORKING:** after restarting the backend and loading the built React frontend on the same origin, a real static Pixel_7 Settings frame appeared without touching Android. The backend's direct MJPEG response contained a complete 117,990-byte JPEG initial part. The production app's `<img>` loaded the real 486x1080 frame. No manually fabricated UI or screen content was used.
- **Tap — WORKING:** clicking the visible Settings row in Chrome at 1024x768 sent a real ADB tap. Chrome reported a newer frame in about 554 ms; the Android top activity changed to `com.android.settings/.SubSettings`. Repeating the same logical Settings-row tap at 640x480 reported a newer frame in about 796 ms; the direct emulator screen showed the Network & internet page.
- **Swipe — WORKING:** dragged upward over the scrollable real Settings screen at 1024x768. The frontend reported a changed frame in about 642 ms. SHA-256 of direct ADB screenshots before/after differed (`f7222936…a7964a` vs. `2cb6957f…bd009`).
- **Scroll — WORKING:** a Chrome wheel action over the same Android screen was translated to an ADB swipe. The frontend reported a changed frame in about 678 ms. ADB screenshot hashes differed (`3f88d0f5…c496c4` vs. `6f668fcd…bd009`).
- **Keyboard — WORKING after focus settling:** a first attempt that typed too soon showed `ealthtick`, missing its first character. The client was changed to defer the first key until one second after the tap. A subsequent browser typing run begun 400 ms after tap displayed the complete `healthtick` in the actual Android Settings search field; `uiautomator dump` returned `text="healthtick"` for `android:id/search_src_text`. Space, Backspace, and Enter were sent through ADB key events; Enter produced an observed changed frame.
- **Coordinate mapping / resize — WORKING:** frame dimensions were 486x1080 and Android display dimensions were 1080x2400 (same aspect ratio). The same visible Android target was reached at 1024x768 and 640x480. The calculation uses the CSS image-element bounds, `object-fit: contain` scale, centered letterbox offsets, normalized image coordinates, and Android display dimensions; the backend rejects out-of-range coordinates and aspect-ratio mismatch.
- **Latency — COMPLETED:** the UI separates browser input-response timing, backend-dispatch-to-ADB timing, ADB command duration, and time until the frontend observes a higher frame sequence. The tested tap/swipe/scroll frame observations were approximately 0.55–0.80 seconds. This includes polling/scheduling and is not physical display-presentation instrumentation. More detailed values and methodology are in `docs/latency-and-validation.md`.
- Invalid normalized coordinate `x=1` returned HTTP 400 with `{"error": "Normalized coordinates must be finite values in [0, 1)"}`; no ADB input was issued.
- `python3.11 -m py_compile backend/server.py` passed. `npm --prefix frontend run build` passed after the final keyboard change. `npm --prefix frontend audit --audit-level=moderate` reported zero vulnerabilities.

### Errors, Failures, and Limitations

- A failed tap calculation occurred after an automated browser action scrolled the page to an off-screen control; the resulting image rectangle was above the viewport. Subsequent tests explicitly returned the page to scroll position zero and calculated clicks only when image coordinates were visible. The normalized mapping itself was verified at both final test sizes.
- The Vite development page did not reliably display the multipart MJPEG stream after a backend restart, while the same-origin production build served by Python loaded it and was tested successfully. The documented/tested startup therefore builds Vite assets and has Python serve them; no claim is made that the Vite dev stream proxy works.
- During initial keyboard testing, the first character was dropped if input arrived before Android's search field/IME had settled. Added the explicit one-second post-tap first-key deadline and re-tested a 400 ms user start delay; the complete text was confirmed in Android's actual UI tree.
- Emulator-disconnect recovery was not actively tested against the project backend, though health checks and ADB errors return explicit error responses in the implementation. CPU use and long-duration reliability were not benchmarked. The frontend's stream error handler retries a failed image request, but exhaustive disconnect/reconnect testing remains open.
- This work did not add authentication, a database, deployment, or optional features. No deployment attempt was made.

### Project Files Changed

`.gitignore`, `README.md`, `PROCESS_LOG.md`, `backend/server.py`, `docs/latency-and-validation.md`, `emulator/README.md`, `frontend/index.html`, `frontend/package.json`, `frontend/package-lock.json`, `frontend/vite.config.js`, `frontend/src/App.jsx`, `frontend/src/main.jsx`, and `frontend/src/style.css`.

### Decision / Next Step

The requested local core is ready to begin a separate deployment task; deployment itself is unimplemented and untested. The next decision is whether to authorize deployment work in a subsequent task. The emulator remains a local prerequisite, and no commit was created.

### Post-Validation Cleanup Supplement

Time: 2026-10-08T13:37:11+05:30.

A diagnostic Python reader timed out while waiting for a 65,536-byte socket read from the long-lived MJPEG response; this was a diagnostic-client buffering issue, not evidence that the MJPEG endpoint lacked a frame. A bounded `curl` probe then received a complete JPEG frame, and Chrome's same-origin production page displayed the emulator. The attempted cleanup included `/tmp/healthtick-stream.jpg`, which had not been created by that timed-out reader; `rm` reported that one path missing. The remaining explicitly named temporary screenshots/dumps and the matching emulator UI dump were removed. No project files other than this append-only log were changed by cleanup. The Vite dev server exited with status 143 after the requested targeted `kill`; the backend handled termination and its scrcpy/FFmpeg children were confirmed absent. The Android Emulator itself was left running for the user. No commit was created.

## Entry 014 — Cloud Deployment Preflight Blocked: Google Cloud CLI Missing

### Time

2026-10-08T15:39:08+05:30 (user-provided task timestamp; local check completed shortly after).

### User Prompt (verbatim)

```text
We are now moving to the FINAL DEPLOYMENT PHASE.

Read AGENTS.md, PROCESS_LOG.md, README.md, and docs/latency-and-validation.md
before doing anything.

The local core is COMPLETE and VALIDATED.

DO NOT redesign the application.

DO NOT return to Google Emulator WebRTC.

DO NOT run another local architecture experiment.

DO NOT add authentication.

DO NOT add database.

DO NOT add bonus features.

DO NOT add multi-user support.

DO NOT add Kubernetes.

DO NOT add autoscaling.

Our priority is:

GET THE EXISTING WORKING APPLICATION PUBLICLY ACCESSIBLE.

==================================================
CURRENT VERIFIED ARCHITECTURE
==================================================

Video:

Android Emulator
    ↓
scrcpy device-side H.264
    ↓
FFmpeg
    ↓
MJPEG
    ↓
Python backend
    ↓
React browser

Input:

React browser
    ↓
Python backend
    ↓
ADB
    ↓
Android Emulator

The local implementation has already verified:

- real Android video
- live browser updates
- tap
- swipe
- scroll
- keyboard input
- coordinate mapping
- browser resize
- latency measurement

Do not replace this architecture unless deployment makes it
technically impossible.

==================================================
DEPLOYMENT TARGET
==================================================

Use a Linux cloud VM capable of running Android Emulator with KVM.

Preferred provider:

Google Cloud Compute Engine.

Reason:

Google officially supports nested virtualization for Linux KVM on
appropriate Compute Engine VM types.

Before provisioning anything, inspect the current environment and determine:

1. Is gcloud installed?
2. Is the user authenticated?
3. Is a Google Cloud project already configured?
4. Is billing enabled?
5. Is there an existing suitable VM?
6. Which suitable Intel machine type/zone is available?

Do NOT create a cloud resource if authentication/project/billing information
is missing.

If user action is required, STOP and tell me exactly what I need to do.

Do NOT guess credentials.

Do NOT print or expose credentials.

==================================================
COST CONTROL
==================================================

This is an internship assignment, not a production service.

Prefer the smallest practical VM that can reliably run:

- Linux
- KVM
- Android Emulator
- scrcpy
- FFmpeg
- Python backend

Do not choose a huge instance.

Before creating the VM, report:

- machine type
- region/zone
- approximate hourly cost if available
- why the machine is sufficient

Do not provision an expensive resource without explicit confirmation.

If an existing suitable VM is available, inspect and reuse it.

==================================================
PHASE 1 — CLOUD VM VALIDATION
==================================================

Provision or use the selected Linux VM.

Verify:

uname -a

CPU architecture

KVM availability:

ls -l /dev/kvm

and appropriate KVM checks.

Verify hardware virtualization is exposed.

If KVM is unavailable:

STOP.

Do not attempt software-emulated Android as a workaround.

Report the exact problem.

==================================================
PHASE 2 — ANDROID EMULATOR
==================================================

Install/configure the Android Emulator on the Linux VM.

Use an x86_64 Android system image compatible with KVM.

Do not assume the local macOS Pixel_7 AVD can simply be copied.

Create a suitable server-side AVD if necessary.

Boot the emulator headlessly.

Verify:

- emulator starts
- ADB sees it
- Android fully boots
- screen can be captured

Use a reasonable resolution to reduce bandwidth and CPU usage.

Do not use an unnecessarily large phone resolution.

==================================================
PHASE 3 — STREAMING STACK
==================================================

Install and configure:

- scrcpy
- FFmpeg
- Python 3
- required Python dependencies

Reproduce the SAME architecture already validated locally:

scrcpy
→ FFmpeg
→ MJPEG
→ Python
→ browser

Do not introduce WebRTC again.

Do not introduce another media server unless absolutely required by the
cloud environment.

==================================================
PHASE 4 — APPLICATION DEPLOYMENT
==================================================

Move/use the current project implementation on the VM.

Backend:

backend/server.py

Frontend:

build the React application using the existing tested production build.

Do NOT use the unreliable Vite development server for production.

Serve the tested frontend build through the Python backend or the same
tested build-and-serve mechanism documented in README.md.

Verify the application works locally ON THE CLOUD VM before exposing it
publicly.

==================================================
PHASE 5 — NETWORKING
==================================================

Expose only the required application port.

Do not expose ADB publicly.

Do not expose unnecessary emulator/gRPC/debug ports publicly.

The browser should communicate with the backend through the public
application endpoint.

If possible, bind ADB/emulator control interfaces to localhost/private
interfaces only.

==================================================
PHASE 6 — HTTPS
==================================================

The final demo should use HTTPS if practical.

Determine the simplest reliable way to provide HTTPS for the assignment.

Possible approach:

- reverse proxy such as Caddy or Nginx
- Let's Encrypt certificate
- public DNS if required

Do not buy a domain just for this assignment unless necessary.

If HTTPS setup requires a domain and no domain exists, first determine
whether the application can be demonstrated safely over the cloud VM's
public endpoint or whether a temporary domain is required.

Do not spend hours on domain configuration.

==================================================
PHASE 7 — PUBLIC END-TO-END TEST
==================================================

From a browser that is NOT the server's local environment:

Open the public application.

Verify:

1. Real Android screen appears.
2. Initial frame appears automatically.
3. Tap works.
4. Swipe works.
5. Scroll works.
6. Keyboard input works.
7. Coordinate mapping works after browser resize.
8. Android changes are visible in the browser.

This is the most important deployment test.

The Android environment must actually be running on the cloud server.

Do not use my Mac as the Android device.

==================================================
PHASE 8 — BASIC RELIABILITY
==================================================

Perform only a short reliability test.

Verify:

- backend process remains alive
- scrcpy remains alive
- FFmpeg remains alive
- emulator remains alive
- browser can reconnect after a temporary refresh

Do not implement sophisticated orchestration.

If a process dies, document the failure and fix only what is necessary
for a reliable demo.

==================================================
PHASE 9 — SECURITY MINIMUM
==================================================

Because the assignment requires a public deployment, apply basic security:

- never expose ADB publicly
- never expose SSH credentials
- never commit secrets
- restrict unnecessary ports
- validate browser input coordinates server-side
- reject invalid/out-of-range coordinates
- avoid arbitrary shell command construction from browser input
- use safe subprocess argument handling
- do not allow arbitrary ADB commands from the browser

Do NOT build authentication unless it is necessary for safe deployment.

==================================================
PHASE 10 — README
==================================================

After deployment is actually verified, update README.md.

Document the ACTUAL deployment.

Include:

- architecture diagram
- local setup
- cloud architecture
- cloud VM requirements
- emulator setup
- scrcpy/FFmpeg setup
- backend startup
- frontend build/serve
- public URL
- how to test tap
- how to test swipe
- how to test scroll
- how to test keyboard
- coordinate mapping
- latency methodology
- known limitations
- shutdown/cost-control instructions

Do not document commands that were not actually tested.

==================================================
DEPLOYMENT WRITE-UP
==================================================

Create/update the architecture documentation needed for the assignment.

Explain:

1. Android screen → browser

2. Browser input → Android

3. Coordinate transformation

4. Why Google Emulator native RTC was rejected

5. Why scrcpy + FFmpeg + MJPEG was selected

6. Deployment architecture

7. Isolation/security considerations

8. What remains limited

Keep it concise and suitable for the assignment's 1–2 page architecture
write-up.

==================================================
"WHAT WENT WRONG"
==================================================

Preserve the existing Google RTC failure in PROCESS_LOG.md and the
write-up.

Explain that:

Emulator 35.6.11
and
Emulator 37.2.12

both returned:

Rtc.RequestRtcStream
StatusCode.UNIMPLEMENTED

Therefore that implementation path was abandoned after controlled testing.

Do not hide this failure.

It is part of the engineering/problem-solving story.

==================================================
DEMO PREPARATION
==================================================

After deployment succeeds, prepare a simple demo flow:

1. Open public URL.
2. Show real Android screen.
3. Tap.
4. Swipe.
5. Scroll.
6. Focus a text field.
7. Type text from keyboard.
8. Resize browser.
9. Perform another tap.
10. Show the Android response.

The demo must use the DEPLOYED version, not localhost.

Do not create a fake demo.

==================================================
PROCESS_LOG
==================================================

Append to PROCESS_LOG.md throughout this deployment.

Never rewrite/delete previous entries.

Record:

- exact user prompt
- cloud provider
- VM type
- region
- provisioning
- commands
- failures
- fixes
- emulator setup
- streaming setup
- public networking
- HTTPS
- testing results
- latency
- security decisions
- final deployment URL
- remaining limitations

Do not put secrets in PROCESS_LOG.md.

==================================================
GIT
==================================================

Do not commit automatically.

Before finishing:

git status
git diff --check

Review all changed files.

==================================================
STOP CONDITIONS
==================================================

STOP and report if:

- cloud credentials are missing
- billing/project setup requires my action
- suitable KVM VM cannot be obtained
- Android Emulator cannot run with KVM
- public networking cannot be configured safely
- deployment becomes blocked by a provider limitation

Do not silently switch to a completely different architecture.

==================================================
FINAL REPORT
==================================================

At the end report exactly:

RESULT: SUCCESS / PARTIAL / BLOCKED

Cloud provider:

VM type:

Region/zone:

KVM:
WORKING / FAILED

Android Emulator on server:
WORKING / FAILED

Real Android video publicly:
YES / NO

Tap:
WORKING / FAILED

Swipe:
WORKING / FAILED

Scroll:
WORKING / FAILED

Keyboard:
WORKING / FAILED

Coordinate mapping:
WORKING / FAILED

Browser resize:
PASSED / FAILED

HTTPS:
WORKING / NOT USED / BLOCKED

Public URL:

Approximate end-to-end latency:

Main limitation:

Deployment:
READY FOR DEMO / NOT READY

Remaining blocker:

Required action from me:

Then STOP.

Do not implement optional bonuses.
Do not add authentication.
Do not add multi-user support.
Do not add autoscaling.
Do not continue experimenting after the deployment is working.
```

### Actions and Commands

- Read `AGENTS.md`, `PROCESS_LOG.md`, `README.md`, and `docs/latency-and-validation.md` before the deployment preflight.
- Ran `command -v gcloud`; observed `gcloud: not installed`.
- Ran a guarded Cloud SDK active-account check that would emit only whether an active account exists, never its identity; it was not run because the `gcloud` executable was absent.
- Ran a guarded `gcloud config get-value project` / active-configuration check; observed `Cloud project cannot be inspected: gcloud not installed`.
- Checked environment variable names prefixed `GOOGLE_`, `GCLOUD_`, `CLOUDSDK_`, or `GCP_` without printing values; none were present.
- Ran `git status --short --branch`; the branch was `main` and clean at preflight start.
- No Google Cloud API call, billing lookup, VM inventory query, zone/machine-type query, resource creation, tool installation, or credential output occurred.

### Result / Blocker

**BLOCKED before provisioning.** With no installed `gcloud` and no Cloud SDK configuration, the account, selected project, billing enablement, existing VM inventory, suitable Intel machine types/zones, and pricing cannot be verified. No cloud resource was created, and no credentials were requested or exposed. Deployment, KVM, emulator, networking, HTTPS, and public browser tests were not performed.

### Required User Action / Next Step

Install the official Google Cloud CLI on this Mac, authenticate it with the Google account that owns the assignment project, set the intended existing Cloud project as the active project, and ensure billing is enabled for that project. Do not send or paste credential material into this chat. Once configured, ask to resume the deployment preflight; the next run must re-check authentication, project, billing, existing VMs, and suitable zone/machine pricing before any provisioning. VM creation will still wait for explicit approval of the reported instance and estimated cost.

No project files other than this append-only process log were changed in this deployment preflight. No commit was created.

## Entry 015 — Investigating Unintended Android Movement

### Time

2026-10-08 19:39 IST (session timestamp)

### User Prompt (verbatim)

```text
Read AGENTS.md and PROCESS_LOG.md first.

We have a working local implementation of the HealthTick "Real-Time Android Device in the Browser" assignment.

Current behavior:
- Real Android Emulator screen is displayed in Chrome.
- Browser tap/swipe/scroll/keyboard input works.
- However, after connecting the device, the Android screen sometimes appears to automatically scroll/move even when the user has not performed any action.

Fix ONLY this unintended automatic movement/input behavior.

Important:
1. Do NOT redesign the architecture.
2. Do NOT switch transports.
3. Do NOT optimize latency.
4. Do NOT modify deployment.
5. Do NOT add features.
6. Do NOT change working tap/swipe/scroll/keyboard behavior unless required to eliminate unintended input.
7. Inspect the existing frontend input/event handlers and backend ADB input handling carefully.
8. Look specifically for:
   - mouse/touch events firing during initialization
   - pointer/touch coordinates being sent without an actual user gesture
   - wheel events
   - pointermove/pointerdown/pointerup handling
   - synthetic events
   - initialization/default coordinates accidentally being interpreted as input
   - browser focus/gesture behavior
   - duplicate or stale input requests
   - timers/intervals that could repeatedly send input
9. The video stream itself must continue working normally. Do NOT stop or artificially freeze the Android video stream.
10. After making the smallest necessary fix, test:
    - Connect/open page → Android screen remains stable without user interaction.
    - Tap still works.
    - Swipe still works.
    - Scroll still works.
    - Keyboard still works.
    - Browser resize still works.
11. If the cause cannot be established confidently, do not make speculative changes. Report what you found instead.
12. Append the work to PROCESS_LOG.md according to the existing mandatory logging instructions.
13. Do not commit or push anything automatically.

At the end, report:
- exact root cause
- files changed
- exact fix
- tests performed
- whether automatic movement stopped
- whether tap/swipe/scroll/keyboard still work.
```

### What AI Did

- Read `AGENTS.md` and the existing `PROCESS_LOG.md` before making changes. Reviewed `frontend/src/App.jsx` pointer, click, wheel, and keyboard handlers; the health polling timer; and `backend/server.py` input routes, which execute ADB only for explicit `/api/input/*` POST requests. The stream startup/capture code does not issue ADB input.
- Reset the real `emulator-5554` Pixel_7 to the Android Settings homepage with `adb -e shell am force-stop com.android.settings` and `adb -e shell am start -W -a android.settings.SETTINGS`. The launch returned `Status: ok` and `com.android.settings/.homepage.SettingsHomepageActivity`.
- Opened `http://127.0.0.1:8000/` in Chrome. The backend reported `emulator-5554`, 1080 × 2400, `video_ready: true`; the displayed stream image was 486 × 1080.
- Installed temporary in-page event/fetch observation (no project file changes). During the first 20-second no-action interval, no pointer, click, wheel, touch, or keyboard events and no `/api/input/*` requests were observed. Two Settings UI hierarchy dumps 10 seconds apart were identical.
- Exercised real browser controls through the existing page: tap opened Android Settings search; browser keyboard typed `wifi`, visible in the actual Android screen; `/api/input/key` Back, `/api/input/scroll`, and `/api/input/swipe` were observed; the swipe was dispatched after a 500 ms gesture, satisfying the frontend's existing >100 ms swipe threshold. A shorter attempted drag did not produce a swipe request because it completed in under that threshold. Resized the browser to 900 × 700 and performed another tap; the app reported `Tap sent · changed frame received`.
- During the extended interaction/browser observation, 14 `/api/input/scroll` POSTs appeared about one second apart while the then-current page's captured DOM event array was empty. The stream image temporarily reported 0 × 0 and the browser reported `ERR_NETWORK_IO_SUSPENDED`. Android was subsequently observed on the bottom portion of Settings rather than at its prior top position. Reloading the page restored the stream. The origin of those scroll POSTs was not traced: the evidence does not distinguish another/stale client, delayed requests, or another browser/tool event source. This is an unresolved anomaly, not proof of a frontend or backend defect.
- For a clean final idle trial, reset Settings to its top and captured its UI hierarchy, reloaded the browser page, and observed for 10 seconds. No browser input events or `/api/input/*` POSTs occurred; the stream remained connected at 486 × 1080; the extracted visible text, bounds, scrollable nodes, and focus state in the Android UI hierarchy were identical before and after the interval.
- Tap, keyboard text, Back key, scroll, and swipe endpoints all produced observed requests during the deliberate control tests. No source-code change was made because the intermittent movement's cause was not established confidently; no synthetic-event guard or other speculative behavior change was introduced.
- Ran `git status --short` and `git diff --check` before appending this entry. No source changes were present at that point. No commit or push was made.

### Errors / Failures / Unresolved Findings

- The automatic movement was not reproduced in the clean final 10-second idle test, but an earlier idle period after deliberate interaction included unexplained repeated scroll POSTs and a changed Android Settings position. The cause remains unconfirmed, so the issue cannot be reported as fixed.
- A brief `ERR_NETWORK_IO_SUSPENDED` / missing MJPEG image occurred during the longer browser interaction test; reloading re-established the real stream. No transport or application changes were made.
- The first drag test was under the frontend's 100 ms swipe dispatch threshold and did not test the swipe route; a subsequent longer drag did dispatch it.
- No Android video/capture code was disabled or changed.

### Files Changed

- `PROCESS_LOG.md` only (this append-only entry). No frontend or backend source was changed.

### User Decision / Next Step

The next decision is whether to authorize a focused follow-up that attributes the intermittent scroll POSTs to their originating browser/client and correlates each POST with a captured trusted DOM event before any code fix is attempted. Until that source is established, no speculative fix is recommended.

## Entry 016 — Focused Scroll-Request Source Trace

### Time

2026-10-08 19:44 IST (session timestamp)

### User Prompt (verbatim)

```text
Yes—trace the request source (Recommended)
```

### What AI Did

- Enumerated the active Playwright browser context; it contained one page at `http://127.0.0.1:8000/`.
- Inspected local processes and port 8000 sockets. The existing Python backend (PID 3540), FFmpeg (PID 3552), and scrcpy (PID 3553) were running. At inspection time, the backend had one established local socket in addition to its listening socket; no second browser page was present in this context.
- Added temporary in-page event and fetch observation, then performed exactly one deliberate browser wheel input over the real Android screen and observed for eight seconds.
- Observed one trusted DOM `wheel` event (`deltaY: 240`) and exactly one `/api/input/scroll` POST. Its JavaScript stack reached the built frontend bundle (`/assets/index-CjHTTkVK.js`); no further input POSTs appeared during the observation. The stream remained connected at 486 × 1080.
- Confirmed in source that the wheel handler is the only frontend call path for `/api/input/scroll`, and it calls `sendInput` for the observed wheel event. No periodic scroll/input timer exists in the reviewed frontend/backend input paths.
- Did not change source code. The prior anomaly (14 scroll POSTs with no corresponding events in the then-current page's temporary capture, followed by a changed Settings position) did not recur and still cannot be attributed to a particular page, delayed request, or browser/tool event. This trace therefore does not establish an exact root cause or justify an input-handler change.

### Errors / Failures / Unresolved Findings

- A single deliberate wheel produced one expected scroll POST; the intermittent repeated POST anomaly was not reproducible. Its original source remains unknown.
- No code fix was made because the user explicitly directed that speculative changes must not be made without a confident cause.

### Files Changed

- `PROCESS_LOG.md` only (this append-only entry).

### User Decision / Next Step

Source attribution remains unresolved. No source change is recommended from the available evidence. The current implementation should remain unchanged unless a further occurrence can be captured with the originating browser event/request and corresponding Android input correlated in real time.

## Entry 017 — Diagnosing the Deployed MJPEG Failure

### Time

2026-10-09 09:12 IST (session timestamp)

### User Prompt (verbatim)

```text
You are working on my HealthTick Android Browser take-home assignment.

THIS IS A REAL DEPLOYMENT BUG AND THE DEADLINE IS TODAY. Work directly on the
existing project and fix the real issue. Do NOT create a mock/fake Android
screen and do NOT replace the real Android streaming architecture.

Project:
~/healthtick-android-browser

Goal:
A real Android Emulator running on the Google Cloud VM must continuously stream
its real screen to the browser and accept browser input through ADB.

Current architecture:

Android Emulator
    ↓
scrcpy
    ↓
FFmpeg
    ↓
MJPEG HTTP stream
    ↓
Browser <img>

Browser input
    ↓
Python backend
    ↓
ADB
    ↓
Android Emulator

Current deployed VM:
- Debian 13
- x86_64
- Google Cloud VM
- 2 vCPU / ~8 GB RAM
- KVM available and working
- Android Emulator API 35 Google APIs x86_64
- AVD: HealthTickDevice
- ADB serial: emulator-5554
- Emulator logical display: 720x1600
- Backend port: 8000
- Public URL:
  http://34.14.173.43:8000

Installed:
- Android SDK
- adb
- emulator
- scrcpy 5.0
- FFmpeg 7.1.5
- Python 3
- Node/npm

Important:
The emulator itself is healthy.

These commands currently work:

adb -s emulator-5554 shell getprop sys.boot_completed
=> 1

adb -s emulator-5554 shell wm size
=> Physical size: 1080x2400
=> Override size: 720x1600

adb devices
=> emulator-5554 device

systemd emulator service:
healthtick-emulator.service
=> active/running

systemd backend service:
healthtick-backend.service
=> active/running

The frontend loads successfully and shows:

Connected: emulator-5554 · 720 × 1600

BUT the actual video area is black / broken.

Current backend logs repeatedly show:

GET /stream.mjpg?... HTTP/1.1" 503
Video pipeline became stale; restarting capture.

Current process check:

pgrep -af "scrcpy|ffmpeg"

shows FFmpeg running, for example:

ffmpeg -hide_banner -loglevel warning -i /tmp/healthtick-stream-.../scrcpy.mkv -an -fps_mode passthrough -c:v mjpeg -q:v 7 -f image2pipe -vcodec mjpeg pipe:1

BUT scrcpy is NOT present.

Therefore the likely failure is:

scrcpy starts and exits immediately OR cannot create/write the recording
FIFO/container, so FFmpeg remains waiting and the backend repeatedly reports a
stale pipeline / 503.

IMPORTANT: Do not assume the cause. Diagnose the actual scrcpy failure from
stderr/logs and reproduce it manually under the same user/environment used by
systemd.

Files already modified during troubleshooting:
- backend/server.py
- frontend/src/App.jsx

The backend was changed to:
- detect stale FFmpeg/scrcpy processes
- use scrcpy:
  --max-size=720
  --max-fps=15
  --video-bit-rate=2M

The frontend was changed to append a unique session query parameter to
/stream.mjpg to avoid stale browser stream reuse.

DO NOT undo these performance improvements unless testing proves they are the
cause.

SYSTEMD SERVICES:

Emulator:
healthtick-emulator.service

Backend:
healthtick-backend.service

Backend environment:
ADB_PATH=/home/rajeswersahani720/android-sdk/platform-tools/adb
ADB_SERIAL=emulator-5554
HOST=0.0.0.0
PORT=8000

Backend runs:
python3 /home/rajeswersahani720/healthtick-android-browser/backend/server.py

WHAT YOU MUST DO:

1. Inspect backend/server.py carefully.

2. Inspect the current VideoPipeline implementation completely, including:
   - start()
   - stop()
   - _read_jpegs()
   - process creation
   - FIFO creation
   - FFmpeg creation
   - scrcpy creation
   - stream.mjpg endpoint
   - stale-pipeline recovery

3. Inspect the actual scrcpy command currently generated by the backend.

4. Run the exact equivalent scrcpy command manually on the VM using the same:
   - user
   - ADB executable
   - ADB serial
   - PATH
   - AVD/emulator

5. Capture and inspect scrcpy stderr. Do not hide the error.

6. Check whether scrcpy 5.0 supports the exact recording arguments currently
   being used.

7. Check whether the FIFO/container recording approach is correct for scrcpy
   5.0 on this Linux VM.

8. Check whether FFmpeg is opening the FIFO correctly.

9. Check whether the problem is:
   - scrcpy binary/path
   - ADB connection
   - scrcpy permissions
   - FIFO permissions
   - MKV output
   - recording format
   - scrcpy command-line incompatibility
   - process lifecycle
   - systemd environment
   - FFmpeg waiting for input
   - stale process cleanup
   - race condition between FFmpeg and scrcpy
   - Android emulator state
   - CPU/resource issue

10. Do NOT just keep restarting the backend. Find the root cause.

11. Fix the implementation so that:
   - scrcpy remains alive
   - FFmpeg receives real Android video
   - backend publishes JPEG frames
   - /stream.mjpg returns 200 and continuously streams frames
   - browser displays the real Android screen
   - browser input continues to work through ADB
   - restarting the backend does not leave orphaned scrcpy/FFmpeg processes
   - stale capture processes are properly cleaned before restart
   - a browser refresh/new tab can establish a fresh stream
   - the implementation remains simple and reliable for one emulator

12. If the current scrcpy → FIFO → FFmpeg approach is fundamentally unreliable
   with scrcpy 5.0, you may replace ONLY the capture implementation with a
   simpler reliable real-device approach, for example:
   scrcpy/device capture → FFmpeg → MJPEG
   but the final implementation MUST still use the real Android Emulator.

13. Do NOT introduce WebRTC unless absolutely necessary. We already tested
   Google's native Emulator WebRTC gateway and it returned UNIMPLEMENTED in our
   environment.

14. Do NOT introduce hosted Android streaming/device-farm services.

15. Do NOT use fake/mock/simulated Android data.

16. Keep the browser frontend simple. The assignment is about real device
   streaming and interaction, not UI polish.

17. Preserve existing working input functionality:
   - tap
   - swipe
   - scroll
   - keyboard/text input
   - coordinate mapping
   - Android Back/Home

18. Run validation after the fix.

REQUIRED VALIDATION:

A. Backend:

curl http://127.0.0.1:8000/api/health

must return HTTP 200.

B. Stream:

curl -I "http://127.0.0.1:8000/stream.mjpg?test=<unique-value>"

must NOT return 503.

C. Processes:

pgrep -af scrcpy
pgrep -af ffmpeg

must show a healthy capture pipeline while the stream is connected.

D. Real frame validation:

Connect to /stream.mjpg and verify that actual JPEG frames are being produced
continuously.

Do not claim this works merely because the HTTP request returns 200.

E. Browser:

Open:

http://34.14.173.43:8000

The actual Android home screen must appear without pressing Android Home first.

F. New-tab test:

Open the URL in a new browser tab.

The Android screen must appear without manually touching the emulator.

G. Input tests:

- tap
- Back
- Home
- swipe
- wheel scroll
- text input

must work.

H. Stability:

Leave the stream open for at least 2–3 minutes and check:

sudo journalctl -u healthtick-backend.service -n 100 --no-pager

There must NOT be a continuous loop of:

Video pipeline became stale; restarting capture.
GET /stream.mjpg ... 503

I. Restart test:

sudo systemctl restart healthtick-backend.service

Then reopen the browser and verify the real Android screen returns.

J. Cleanup:

After stopping/restarting the backend, there must not be accumulating orphaned
scrcpy/FFmpeg processes.

IMPORTANT PROCESS LOG REQUIREMENT:

This project has AGENTS.md and PROCESS_LOG.md.

AGENTS.md requires an append-only PROCESS_LOG.md.

After every meaningful troubleshooting/fix step, append:
- exact user prompt verbatim
- what you did
- errors/failures
- user's decision/next step

Do NOT delete previous entries.
Do NOT rewrite previous history.
Preserve the failed approaches.

Also update documentation only after the implementation is actually verified.

IMPORTANT:
Before making a large architectural change, first reproduce and identify the
actual scrcpy failure.

At the end, report:

1. Root cause.
2. Exact files changed.
3. Exact fix.
4. Commands used to validate it.
5. Actual validation results.
6. Any remaining limitation.
7. Whether the public URL is working with a real Android screen.

Do not say "fixed" unless the browser visibly receives real Android frames and
the process stays healthy.
```

### What AI Did

- Read `AGENTS.md`, the relevant tail of `PROCESS_LOG.md`, the complete local `backend/server.py` lifecycle and stream/input routes, and `frontend/src/App.jsx`.
- Confirmed the available checkout is `/Users/rajeshwer/Desktop/healthtick-android-browse`; the requested `~/healthtick-android-browser` directory does not exist on this host. The checkout is clean at commit `5f36d0e` before this log entry. Its capture implementation does not contain the deployment-reported stale recovery/performance edits: its scrcpy command still uses max-size 1080/max-fps 30 and `SCRCPY` defaults to the bare executable name `"scrcpy"`.
- Probed `GET http://34.14.173.43:8000/api/health`: HTTP 200, reporting emulator-5554 at 720×1600 and `video_ready: true`.
- Probed `HEAD /stream.mjpg`: HTTP 501 because the Python `BaseHTTPRequestHandler` does not implement HEAD. Then performed a bounded real GET to `/stream.mjpg`; it returned HTTP 503 with the explicit error `Could not start screen capture: [Errno 2] No such file or directory: 'scrcpy'`. The response body contained zero JPEG markers and zero MJPEG boundaries.
- This establishes that in the deployed backend process environment, launching the configured program named `scrcpy` fails with executable-not-found before a scrcpy child process can emit stderr, before FFmpeg can receive video, and before FIFO/container compatibility can be tested. It is not evidence of a scrcpy 5.0 option, FIFO, MKV, emulator, CPU, or ADB failure.
- Confirmed `gcloud` is unavailable locally. Attempted non-interactive, public-key-only SSH to the VM with strict host-key verification; SSH refused to connect because this host key has never been verified locally. No host key was added, no credentials were exposed, and no remote command was run.
- Made no source, service, frontend, or deployment changes. The running deployment's source tree and actual service PATH cannot be inspected until a trusted remote access path is available. Its interactive-vs-systemd scrcpy installation location remains unverified.

### Errors / Failures / Blockers

- Public MJPEG GET currently fails with HTTP 503 and the precise executable-not-found error for `'scrcpy'`; no actual JPEG frame is served.
- Public stream HEAD returns 501 (method unsupported), not 503; actual stream status was verified using GET, which is the relevant multipart behavior.
- SSH is blocked at host-key verification (`No ED25519 host key is known ... StrictHostKeyChecking=yes`). Because the VM identity has not been verified, no remote shell or changes were attempted.
- This local checkout is not the specified `~/healthtick-android-browser` project path and does not include the deployment-reported latest code changes.
- No evidence is available yet to manually reproduce under the systemd user/PATH, capture scrcpy stderr, inspect FFmpeg FIFO state or service journal, run process cleanup/restart checks, or perform real browser input on the deployed VM.

### Files Changed

- `PROCESS_LOG.md` only (this append-only entry).

### User Decision / Next Step

The confirmed immediate blocker is that the deployed backend cannot resolve the `scrcpy` executable from its service environment. The smallest next step is to provide a trusted SSH host-key fingerprint (or an already verified SSH/gcloud access path) so the same-user systemd environment, `command -v scrcpy`, exact executable path, service unit/PATH, live process list, and journal can be inspected, then the actual binary can be tested with the backend's exact arguments and visible stderr. Only after that remote diagnosis should the deployment be changed and full frame/browser/restart validation performed.

## Entry 018 — Public Browser Confirmation

### Time

2026-10-09 09:13 IST (session timestamp)

### User Prompt Reference

The full verbatim deployment request is preserved in Entry 017. Relevant instruction: “Do not say "fixed" unless the browser visibly receives real Android frames and the process stays healthy.”

### What AI Did

- Opened the public URL `http://34.14.173.43:8000` in the integrated browser. The page displayed the connected-device label `emulator-5554 · 720 × 1600`, but the Android video area was fully black.
- Correlated this observed browser failure with the public MJPEG GET from Entry 017, which returned 503 and the literal executable-not-found error; no real JPEG frames were returned.

### Errors / Failures

- The deployed browser is not currently displaying the real Android screen. No claim of successful repair or healthy capture is made.

### Files Changed

- `PROCESS_LOG.md` only (this append-only addendum).

### User Decision / Next Step

Remote diagnosis/fix still requires a verified host identity and authorized SSH access (or another trusted remote administration path). No deployment mutation should be attempted before that access is established.

## Entry 020 — Making MJPEG Startup and Recovery Reliable

### Time

2026-10-09 09:40 IST

### User Prompt (verbatim)

```text
We need to finish the HealthTick Software Developer Intern assignment today.

Project:
healthtick-android-browser

Deployment:
Google Cloud VM
Public URL:
http://34.14.173.43:8000

Architecture:
Android Emulator
→ scrcpy
→ FFmpeg
→ MJPEG
→ Python backend
→ browser <img>

Input:
Browser
→ Python backend
→ ADB
→ Android Emulator

IMPORTANT: This is a REAL Android emulator. Do NOT replace anything with fake/mock/demo data.

CURRENT DEPLOYMENT STATUS:

The systemd PATH issue has already been fixed.

The deployed VM now has:

SCRCPY_PATH=/home/rajeshwersahani720/scrcpy-linux-x86_64-v5.0/scrcpy
FFMPEG_PATH=/usr/bin/ffmpeg
ADB_PATH=/home/rajeshwersahani720/android-sdk/platform-tools/adb
ADB_SERIAL=emulator-5554

scrcpy is confirmed working:

scrcpy 5.0

The running process is confirmed with:

/home/rajeshwersahani720/scrcpy-linux-x86_64-v5.0/scrcpy
--no-window
--no-playback
--no-control
--no-audio
--max-size=720
--max-fps=15
--video-bit-rate=2M
--record=.../scrcpy.mkv
--record-format=mkv

FFmpeg is also running.

The deployed backend returns:

GET /stream.mjpg?... HTTP/1.1 200

However, there is still an intermittent BUG:

1. Open the public URL in a fresh browser tab.
2. The UI says:
   Connected: emulator-5554 · 720 × 1600
3. Sometimes the Android screen is visible immediately.
4. Sometimes the video area remains completely black even though /stream.mjpg returns HTTP 200.
5. Reload/reconnect sometimes makes the screen appear.
6. The backend logs show messages such as:
   "Video pipeline became stale; restarting capture."
7. Therefore the remaining problem is NOT simply scrcpy PATH.
8. We need reliable stream startup and recovery.

I need you to inspect the existing implementation rather than blindly rewriting it.

Files to inspect first:

backend/server.py
frontend/src/App.jsx
frontend/src/main.jsx
frontend/src/style.css
README.md
PROCESS_LOG.md
AGENTS.md

KNOWN CURRENT backend design:

VideoPipeline.start():
- connects to the Android emulator
- gets display size
- captures an initial screenshot with:
  adb exec-out screencap -p
- publishes that JPEG
- creates a FIFO
- starts FFmpeg reading the FIFO
- starts scrcpy recording into the FIFO
- starts a reader thread that extracts JPEG frames from FFmpeg
- publishes frames with a sequence counter

/stream.mjpg:
- calls VIDEO.start()
- returns multipart/x-mixed-replace
- waits for frames using the sequence counter

CURRENT stale detection checks whether FFmpeg and scrcpy processes are alive.

IMPORTANT:
The current stale detection is not sufficient if:
- the reader thread dies while FFmpeg/scrcpy remain alive
- FFmpeg remains alive but stops producing frames
- scrcpy remains alive but capture is frozen
- the stream starts before a usable frame is actually available
- a browser reconnect attaches to a stale/dead reader state

TASK:

Make the real video stream reliable.

Requirements:

1. Do NOT change the architecture unnecessarily.
2. Keep scrcpy + FFmpeg + MJPEG.
3. Keep the existing real Android emulator.
4. Keep browser input functionality:
   - tap
   - swipe
   - scroll
   - keyboard/text input
   - Android Back
   - Android Home
5. Keep coordinate mapping accurate at arbitrary browser sizes.
6. Keep 720x1600 Android override and scrcpy:
   --max-size=720
   --max-fps=15
   --video-bit-rate=2M
7. Keep the stream cache-busting session parameter.
8. Do NOT disable YouTube or Google apps as a workaround.
9. Do NOT add fake frames.
10. Do NOT make the browser periodically send fake taps or other input.

ROBUST STREAM REQUIREMENTS:

A. VideoPipeline must track:
- FFmpeg process
- scrcpy process
- reader thread
- last successfully published frame time
- frame sequence

B. Consider the pipeline stale if ANY of these is true:
- FFmpeg has exited
- scrcpy has exited
- reader thread has died
- no frame has been published for a reasonable timeout, e.g. 5 seconds

C. On stale pipeline:
- safely stop the existing FFmpeg/scrcpy/reader resources
- recreate FIFO/resources
- restart capture
- preserve the current Android emulator
- avoid leaking processes/FIFOs/temp directories

D. Stream startup must be reliable:
- do not consider the stream healthy merely because the HTTP connection returned 200
- ensure a real JPEG frame has been published before the stream waits indefinitely
- if startup fails, return a useful 503 instead of an apparently successful black stream

E. Avoid race conditions between multiple browser stream connections.
The implementation should safely handle:
- opening the page
- opening a new tab
- browser reconnect
- image onerror reconnect
- multiple stream requests arriving close together

F. Do not restart the video pipeline for every browser request.
There should be one shared capture pipeline.

G. Do not block the Python HTTP server unnecessarily.

H. Frontend:
- keep the stream session cache-busting
- keep automatic reconnect on image error
- avoid an infinite rapid reconnect loop
- use a small backoff if necessary
- make sure reconnect actually creates a fresh stream request

I. Add enough logging to diagnose:
- pipeline started
- scrcpy PID
- FFmpeg PID
- reader started
- first frame published
- frame timestamps
- pipeline stale reason
- pipeline restart
- pipeline stopped

Do not spam logs every frame. Log only useful state changes.

VALIDATION:

Before saying it is fixed, run:

python3 -m py_compile backend/server.py

cd frontend
npm run build

Then test locally if possible.

Also verify:

grep -n "max-size\|max-fps\|video-bit-rate" backend/server.py

The final source must use:

--max-size=720
--max-fps=15
--video-bit-rate=2M

Then test deployment behavior conceptually against the existing VM setup.

The important acceptance test is:

1. Open http://34.14.173.43:8000 in a fresh tab.
2. Wait without clicking Android Home.
3. Real Android screen must appear.
4. Reload the page.
5. Real Android screen must appear again.
6. Open a second tab.
7. Real Android screen must appear there.
8. Reload again.
9. Screen must recover automatically if the stream is interrupted.
10. Tap Android.
11. Swipe Android.
12. Scroll Android.
13. Open a text field and type text.
14. Verify Android actually responds.
15. Leave the page idle for at least several minutes.
16. Verify the video does not randomly become permanently black.
17. Do NOT use fake/mock behavior to pass these tests.

IMPORTANT:
Do not claim deployment is fixed merely because the HTTP status is 200.

We need actual JPEG frames reaching the browser.

Also inspect the existing PROCESS_LOG.md and AGENTS.md.

The assignment requires PROCESS_LOG.md to remain append-only and each meaningful step must include:
- exact user prompt verbatim
- what AI did
- errors/failures
- user decision next

Append the current work to PROCESS_LOG.md according to AGENTS.md. Do not delete or rewrite previous entries.

At the end give me:

1. Exact files changed.
2. Root cause of the intermittent black stream.
3. Exact fix.
4. Validation commands and their results.
5. Any remaining limitation.
6. Exact deployment commands I need to run on the Google Cloud VM.

Do NOT make unrelated UI changes.
Do NOT rewrite the project from scratch.
Do NOT remove working functionality.
```

### What AI Did

- Read the requested files first: `AGENTS.md`, `PROCESS_LOG.md`, `README.md`, `backend/server.py`, `frontend/src/App.jsx`, `frontend/src/main.jsx`, and `frontend/src/style.css`.
- Inspected the complete local `VideoPipeline` and stream handler. This checkout did not contain the deployment-reported prior stale-process guard; it spawned processes once, published an ADB screenshot before live capture, considered `started` sufficient, and did not track reader failure or frame age. The stream handler returned HTTP 200 before confirming a JPEG from the scrcpy/FFmpeg reader. The last task’s unavailable remote access still applies; no VM source was directly edited.
- Updated `VideoPipeline` to track both child processes, reader/error state, live frame sequence, last successful live-frame monotonic timestamp, lifecycle generation, and serialized startup/recovery. Startup now waits up to 15 seconds for a real JPEG emitted by the scrcpy → FIFO → FFmpeg reader before allowing a 200 stream response; there is no screenshot-only fallback. Startup failures return diagnostic 503 responses with stderr tails.
- Added stale detection for exited FFmpeg, exited scrcpy, stopped/failed reader, or no published live frame for more than five seconds. Each existing MJPEG connection checks/restarts the shared pipeline at one-second intervals, so connected clients can recover without a page refresh; a new tab also checks the shared pipeline. Restarts terminate the owned process groups, join the reader, close logs/pipes, and remove the temporary FIFO directory. Concurrent starts are serialized; failed launches use a two-second retry cooldown.
- Added state-change logging for pipeline start/stop/restart, process IDs, reader start/stop, first JPEG size/time/sequence, stale reason, startup failure, and captured stderr. No per-frame log spam was added.
- Kept the existing scrcpy + FFmpeg + MJPEG architecture, ADB input handlers, coordinate mapping, and required `--max-size=720`, `--max-fps=15`, `--video-bit-rate=2M` settings.
- Updated frontend stream URLs with a per-page session query value and a fresh reconnect query value. Image errors retry with exponential backoff from 1 to 15 seconds; successful image load resets the backoff. No Android input is generated for reconnect.
- Added a `do_HEAD` implementation for `/stream.mjpg` so the requested `curl -I` readiness probe validates live startup rather than always returning Python’s default 501.
- Ran `python3 -m py_compile backend/server.py` successfully. A focused in-process HTTP test without an emulator verified both HEAD and GET return 503 instead of falsely returning 200, and a second attempt during cooldown does not start another capture. A separate state-check harness verified healthy, dead-reader, stale-frame, exited-FFmpeg, and exited-scrcpy determinations. The local ADB reports no connected devices, so live emulator integration could not be tested here.
- Ran `cd frontend && npm run build` successfully (Vite 6.4.4). The first attempted build from repository root failed with `ENOENT` because `package.json` is under `frontend/`; rerunning from the correct directory passed. `git diff --check` passed. `grep` confirmed the required capture flags.
- Probed the public deployment before local code was changed/deployed. Health returned HTTP 200. A public MJPEG GET returned HTTP 200 and repeated samples contained real JPEG SOI/EOI markers (six complete marker pairs in a 10-second bounded sample; curl’s timeout is expected for a long-lived stream). One fresh public tab first rendered black, then displayed the real Android app drawer after approximately 15 seconds without an Android Home press. A decoded sample public JPEG showed that same real device screen. This confirms the existing public endpoint can deliver actual frames, but does not validate the changed local source or several-minute stability. The public HEAD probe still returned 501 because the new `do_HEAD` code has not been deployed.
- No deployment, remote service restart, device input test against the modified code, or several-minute soak test was performed. The deployment is not claimed fixed.

### Errors / Failures / Remaining Findings

- The user-visible production symptom was independently reproduced once: the fresh public page initially showed a black video area, then displayed the real Android app drawer after about 15 seconds. The current deployed HEAD request returned 501. The public curl stream returned real JPEGs, so scrcpy can produce actual frames at least intermittently.
- The local checkout has no connected emulator (`adb devices -l` listed no devices). Live local frames, full input regression against this version, process restart cleanup under a real emulator, and long-duration stability remain unverified.
- The current public VM has not received these local changes. SSH remains unverified/unavailable in this session; no VM restart or source copy was attempted.
- Exact low-level cause for each intermittent production black interval remains unproven. The confirmed code-level reliability defects were premature HTTP success based on an initial screenshot/process startup, absence of reader/frame-age health, and no recovery loop for an already-open stream. These are addressed in the local implementation but require deployment and live verification before describing the deployment as fixed.
- No README changes were made because the modified implementation has not yet been verified on the VM.

### Files Changed

- `backend/server.py`
- `frontend/src/App.jsx`
- `PROCESS_LOG.md` (this append-only entry; previous entries retained)

### User Decision / Next Step

Copy these changes to the existing VM, build the frontend, restart `healthtick-backend.service`, and perform the public live-frame, fresh-tab/reload, interaction, restart-cleanup, and multi-minute soak checks. Do not mark deployment ready until real JPEG frames are observed in the updated browser build and the recovery process remains healthy.

## Entry 019 — User-Selected Remote Access Follow-Up

### Time

2026-10-09 09:14 IST (session timestamp)

### User Decision (verbatim)

> I’ll provide another trusted SSH/gcloud access path

### What AI Did

- Recorded the user's choice of a trusted remote administration path instead of supplying the SSH host-key fingerprint directly.
- Did not retry SSH, alter host trust, access credentials, or modify the VM.

### Errors / Failures

- The trusted access path has not yet been provided, so remote same-user reproduction, fix, restart, and browser validation remain blocked.

### User Decision / Next Step

Wait for the user to provide the trusted SSH/gcloud access path, then continue by inspecting the deployed service environment and scrcpy executable location before changing the VM.

## Entry 021 — HEAD Error Response Semantics Follow-Up

### Time

2026-10-09 09:42 IST

### User Prompt Reference

The exact user prompt for this work is preserved verbatim in Entry 020.

### What AI Did

- Refined the `/stream.mjpg` HEAD error response so it returns diagnostic headers/status without sending a response body, while preserving JSON diagnostics for GET.
- Re-ran `python3 -m py_compile backend/server.py` and `git diff --check`; both passed.
- Ran an in-process HTTP test with no emulator: HEAD returned 503 with zero body bytes; GET returned 503 with an explicit recent-startup diagnostic. This test did not provide or simulate Android video.
- Reconfirmed the final scrcpy flags at `backend/server.py:289-290`.

### Errors / Failures

- The local test environment still has no connected emulator, so the new success path (real frames before HTTP 200) could not be exercised locally.
- The public server remains on the pre-deployment build; its observed `HEAD` response remains 501 until these source changes are copied and restarted on the VM.

### Files Changed

- `backend/server.py`
- `PROCESS_LOG.md` (append-only follow-up)

### User Decision / Next Step

Deploy the source to the existing VM and run the live-frame and stability acceptance tests before describing the public deployment as fixed.
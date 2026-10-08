# HealthTick Android Browser — AI Agent Instructions

## Project Objective

Build the HealthTick take-home assignment:

**Real-Time Android Device in the Browser**

The application must provide a real, interactive Android Emulator inside a web browser.

The core experience must allow a user to:

- See the live Android device screen updating continuously.
- Tap/click the Android device from the browser.
- Swipe.
- Scroll.
- Type using the browser keyboard.
- Have input land at the correct Android screen position regardless of browser window size.
- Measure and report action-to-visible-update latency.
- Run the system from documented local setup steps.
- Deploy the backend/device environment on a real server.
- Provide a publicly accessible deployed version.

The implementation must use real Android/emulator functionality. Do not replace required functionality with mockups, fake Android interfaces, screenshots, prerecorded video, simulated device responses, or hardcoded demonstrations.

---

## Agreed Architecture

The current architecture direction is:

Browser
→ React frontend
→ WebRTC / WebSocket communication
→ Python Gateway
→ gRPC
→ Android Emulator

The Android Emulator and browser communication should use the Google Android Emulator WebRTC/container ecosystem where technically appropriate.

This architecture is subject to validation through experiments. Do not silently replace the architecture with an unrelated approach.

If a major architectural change appears necessary, explain:

1. The problem with the current approach.
2. The alternative.
3. The advantages and disadvantages.
4. The impact on the assignment requirements.
5. Why the change is justified.

Do not make major architecture changes without the user's approval.

---

## Development Principles

### 1. Build the real system

Do not create a fake implementation merely to make the UI look complete.

Every core feature must eventually be connected to the real Android Emulator.

### 2. Validate before expanding

Prefer small, testable milestones:

1. Android Emulator runs.
2. Android screen reaches the browser.
3. Browser can tap the emulator.
4. Swipe works.
5. Scroll works.
6. Keyboard input works.
7. Coordinate mapping works across browser sizes.
8. Latency can be measured.
9. Local system is reliable.
10. Deployment works.
11. Optional bonuses are considered only after core functionality is stable.

Do not build large amounts of unrelated code before validating the highest-risk technical path.

### 3. Do not fabricate results

Never claim that:

- a feature works unless it has actually been tested;
- a deployment works unless it has actually been tested;
- a latency number was measured unless it was actually measured;
- a command succeeded unless its result was observed;
- a library supports a capability unless that has been verified.

If something has not been tested, explicitly state that it has not been tested.

### 4. Research before major implementation

For unfamiliar technologies, inspect authoritative documentation and existing project documentation before making major implementation decisions.

For the Android Emulator/WebRTC stack, prefer official Google documentation and repositories when available.

### 5. Keep the implementation simple

The assignment explicitly values a simple reliable solution over a complex partially finished solution.

Do not introduce unnecessary:

- microservices;
- databases;
- orchestration systems;
- abstractions;
- frameworks;
- dependencies;
- infrastructure.

unless there is a concrete requirement for them.

### 6. Test incrementally

After meaningful implementation changes:

- run the relevant checks;
- inspect errors;
- test the affected behavior;
- report failures honestly.

Do not wait until the end to discover whether the core system works.

### 7. Preserve failed experiments

Failed approaches are valuable for this assignment.

Do not hide or delete failed approaches from the project history or process documentation.

Record meaningful dead ends and abandoned approaches.

### 8. Security

Never commit:

- passwords;
- API keys;
- access tokens;
- private keys;
- cloud credentials;
- personal secrets.

Use environment variables or appropriate secret-management mechanisms.

### 9. Git discipline

Make focused commits at meaningful milestones.

Do not make one giant final commit containing the entire project.

### 10. Documentation

Keep documentation aligned with the actual implementation.

Do not document planned functionality as if it already exists.

---

## AI Process Logging — Mandatory Assignment Instruction

Maintain a file called PROCESS_LOG.md in the project root throughout this
work. After each meaningful step, append an entry with: the time, the
user's exact prompt (verbatim, not summarised), what you did in response,
any errors or failures you hit, and what the user decided next. Record
dead ends and abandoned approaches as well as successes. Never rewrite or
delete earlier entries. Keep the file up to date as you go, not at the
end.

---

## PROCESS_LOG Rules

The AI agent must follow the mandatory logging instruction above.

Whenever a meaningful AI-assisted development step is completed:

1. Append a new entry to `PROCESS_LOG.md`.
2. Preserve the user's exact prompt verbatim.
3. Record what the AI actually did.
4. Record errors, failures, dead ends, and abandoned approaches.
5. Record the user's resulting decision or next step.
6. Never modify previous entries.
7. Never delete previous entries.
8. Never rewrite the history to make it look cleaner.
9. Do not postpone logging until the end.

If the AI cannot determine something required for the log, it must explicitly state that information is unavailable rather than inventing it.

---

## User Decision Authority

The AI is an implementation and research assistant.

The user makes the final decisions about:

- architecture;
- technology choices;
- scope;
- accepting or rejecting alternatives;
- whether a feature is considered complete;
- whether a failed approach should be abandoned.

When a major decision is required, explain the trade-offs and ask the user before proceeding.

---

## Assignment Constraints

The core device and streaming solution must use free or open-source software.

Do not use a paid hosted Android device-streaming/device-farm service or commercial streaming SDK as the core solution.

Hosting may be free or paid generic infrastructure, subject to the assignment requirements.

The deployed backend/device environment must run on a server and must not depend on the user's personal computer being online.

---

## Current Development Status

The project has only completed its repository/foundation setup.

No Android streaming implementation has been accepted yet.

The next technical milestone is to validate the local Android Emulator → Google Emulator WebRTC → Python Gateway → React/browser path before building additional application functionality.

Do not assume this path works until it has been experimentally verified.
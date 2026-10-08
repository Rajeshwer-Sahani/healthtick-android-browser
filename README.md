# HealthTick — Real-Time Android Device in the Browser

A take-home assignment implementation that provides a live, interactive
Android Emulator inside a web browser.

## Project Status

🚧 Early development — repository and development workflow setup complete.

## Planned Architecture

```text
Browser
  ↓
React Frontend
  ↓
WebRTC / WebSocket
  ↓
Python Gateway
  ↓
gRPC
  ↓
Android Emulator
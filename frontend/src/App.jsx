import { useCallback, useEffect, useRef, useState } from "react";

const API = "/api";
const STREAM_URL = import.meta.env.DEV
  ? "http://127.0.0.1:8000/stream.mjpg"
  : "/stream.mjpg";

export default function App() {
  const imageRef = useRef(null);
  const pointerRef = useRef(null);
  const screenRef = useRef(null);
  const suppressClickRef = useRef(false);
  const inputQueueRef = useRef(Promise.resolve());
  const wheelHandlerRef = useRef(null);
  const keyboardReadyAtRef = useRef(0);
  const [health, setHealth] = useState(null);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("Connecting to emulator…");
  const [busy, setBusy] = useState(false);
  const [latency, setLatency] = useState(null);

  useEffect(() => {
    let active = true;
    async function pollHealth() {
      try {
        const response = await fetch(`${API}/health`, { cache: "no-store" });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Emulator unavailable");
        if (active) {
          setHealth(data);
          setError("");
          setStatus(`Connected: ${data.device} · ${data.width} × ${data.height}`);
        }
      } catch (cause) {
        if (active) {
          setHealth(null);
          setError(cause.message);
          setStatus("Waiting for Android Emulator");
        }
      }
    }
    pollHealth();
    const timer = window.setInterval(pollHealth, 2500);
    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, []);

  const screenPoint = useCallback((clientX, clientY) => {
    const image = imageRef.current;
    if (!image || !image.naturalWidth || !image.naturalHeight) return null;
    const rect = image.getBoundingClientRect();
    const scale = Math.min(
      rect.width / image.naturalWidth,
      rect.height / image.naturalHeight,
    );
    const contentWidth = image.naturalWidth * scale;
    const contentHeight = image.naturalHeight * scale;
    const left = rect.left + (rect.width - contentWidth) / 2;
    const top = rect.top + (rect.height - contentHeight) / 2;
    const x = clientX - left;
    const y = clientY - top;
    if (x < 0 || y < 0 || x >= contentWidth || y >= contentHeight) return null;
    return {
      x: x / contentWidth,
      y: y / contentHeight,
      frameWidth: image.naturalWidth,
      frameHeight: image.naturalHeight,
    };
  }, []);

  function sendInput(endpoint, payload, label, waitForFrame = true, notBefore = 0) {
    const actionStarted = performance.now();
    const operation = inputQueueRef.current.then(async () => {
      const delay = Math.max(0, notBefore - performance.now());
      if (delay > 0) {
        await new Promise((resolve) => window.setTimeout(resolve, delay));
      }
      setBusy(true);
      setError("");
      setStatus(`Sending ${label}…`);
      setLatency(null);
      try {
        const beforeResponse = await fetch(`${API}/metrics`, { cache: "no-store" });
        const before = await beforeResponse.json();
        const response = await fetch(`${API}/input/${endpoint}`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        });
        const result = await response.json();
        if (!response.ok) throw new Error(result.error || `${label} failed`);
        const inputMs = performance.now() - actionStarted;
        const sequence = result.frame_sequence_before ?? before.frame_sequence;
        let frameMs = null;
        if (waitForFrame) {
          for (let attempt = 0; attempt < 30; attempt += 1) {
            await new Promise((resolve) => window.setTimeout(resolve, 100));
            const metricsResponse = await fetch(`${API}/metrics`, { cache: "no-store" });
            const metrics = await metricsResponse.json();
            if (metrics.frame_sequence > sequence) {
              frameMs = performance.now() - actionStarted;
              break;
            }
          }
        }
        setLatency({
          backendToAdb: result.backend_to_adb_ms,
          adbDuration: result.adb_duration_ms,
          clickToResponse: Math.round(inputMs),
          clickToChangedFrame: !waitForFrame
            ? "Streaming continuously"
            : frameMs === null ? "No changed frame detected" : `${Math.round(frameMs)} ms`,
        });
        setStatus(frameMs === null ? `${label} sent` : `${label} sent · changed frame received`);
      } catch (cause) {
        setError(cause.message);
        setStatus("Input failed");
      } finally {
        setBusy(false);
      }
    });
    inputQueueRef.current = operation.catch(() => {});
    return operation;
  }

  function onPointerDown(event) {
    if (event.button !== 0) return;
    const point = screenPoint(event.clientX, event.clientY);
    if (!point) return;
    event.currentTarget.focus();
    event.currentTarget.setPointerCapture(event.pointerId);
    pointerRef.current = { pointerId: event.pointerId, points: [point], startedAt: performance.now() };
  }

  function onPointerMove(event) {
    const gesture = pointerRef.current;
    if (!gesture || gesture.pointerId !== event.pointerId) return;
    const point = screenPoint(event.clientX, event.clientY);
    if (!point) return;
    const previous = gesture.points.at(-1);
    if (Math.hypot(point.x - previous.x, point.y - previous.y) > 0.003) {
      gesture.points.push(point);
    }
  }

  function onPointerUp(event) {
    const gesture = pointerRef.current;
    if (!gesture || gesture.pointerId !== event.pointerId) return;
    const finalPoint = screenPoint(event.clientX, event.clientY);
    if (finalPoint) gesture.points.push(finalPoint);
    pointerRef.current = null;
    if (gesture.points.length > 2 && performance.now() - gesture.startedAt > 100) {
      suppressClickRef.current = true;
      void sendInput("swipe", {
        points: [gesture.points[0], gesture.points.at(-1)],
        duration_ms: Math.max(100, Math.min(2000, Math.round(performance.now() - gesture.startedAt))),
      }, "Swipe");
    }
  }

  function onClick(event) {
    if (suppressClickRef.current) {
      suppressClickRef.current = false;
      return;
    }
    const point = screenPoint(event.clientX, event.clientY);
    if (!point) return;
    keyboardReadyAtRef.current = performance.now() + 1000;
    void sendInput("tap", point, "Tap");
  }

  wheelHandlerRef.current = (event) => {
    event.preventDefault();
    void sendInput("scroll", { delta_x: event.deltaX, delta_y: event.deltaY }, "Scroll");
  };

  useEffect(() => {
    const screen = screenRef.current;
    if (!screen) return undefined;
    const handleWheel = (event) => wheelHandlerRef.current?.(event);
    screen.addEventListener("wheel", handleWheel, { passive: false });
    return () => screen.removeEventListener("wheel", handleWheel);
  }, [Boolean(health)]);

  function onKeyDown(event) {
    if (event.metaKey || event.ctrlKey || event.altKey) return;
    if (event.key.length === 1 && event.key !== " ") {
      event.preventDefault();
      const notBefore = keyboardReadyAtRef.current;
      keyboardReadyAtRef.current = 0;
      void sendInput("text", { text: event.key }, "Text", false, notBefore);
    } else {
      const supported = new Set([
        "Backspace", "Enter", " ", "Tab", "Escape",
        "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight",
        "Home", "Delete",
      ]);
      if (!supported.has(event.key)) return;
      event.preventDefault();
      const notBefore = keyboardReadyAtRef.current;
      keyboardReadyAtRef.current = 0;
      void sendInput("key", { key: event.key }, "Key", true, notBefore);
    }
  }

  function onStreamError() {
    window.setTimeout(() => {
      if (imageRef.current) {
        imageRef.current.src = `${STREAM_URL}?reconnect=${Date.now()}`;
      }
    }, 1000);
  }

  return (
    <main className="app">
      <header className="topbar">
        <div>
          <h1>HealthTick Android Browser</h1>
          <p>Real Pixel_7 emulator · local experiment</p>
        </div>
        <div className={`connection ${health ? "online" : "offline"}`}>
          <span className="dot" /> {status}
        </div>
      </header>
      <section className="workspace">
        <div className="device-panel">
          {health ? (
            <div
              ref={screenRef}
              className="screen"
              tabIndex={0}
              aria-label="Interactive Android screen. Click, swipe, scroll, or type."
              onPointerDown={onPointerDown}
              onPointerMove={onPointerMove}
              onPointerUp={onPointerUp}
              onPointerCancel={() => { pointerRef.current = null; }}
              onClick={onClick}
              onKeyDown={onKeyDown}
            >
              <img
                ref={imageRef}
                src={STREAM_URL}
                alt="Live Android Emulator screen"
                onError={onStreamError}
                draggable="false"
              />
            </div>
          ) : (
            <div className="placeholder">{error || "Start the Pixel_7 emulator and backend."}</div>
          )}
        </div>
        <aside className="controls">
          <h2>Device controls</h2>
          <p>Click to tap. Drag to swipe. Use the mouse wheel to scroll. Click a text field on Android, then type here.</p>
          <p className="hint">For keyboard entry, keep the Android screen focused after clicking the target field.</p>
          <div className="actions">
            <button disabled={busy || !health} onClick={() => void sendInput("key", { key: "Back" }, "Back")}>Android Back</button>
            <button disabled={busy || !health} onClick={() => void sendInput("key", { key: "Home" }, "Home")}>Android Home</button>
          </div>
          <div className="status-box" aria-live="polite">
            <strong>{status}</strong>
            {error && <p className="error">{error}</p>}
            {latency && (
              <dl>
                <dt>Backend → ADB</dt><dd>{latency.backendToAdb} ms</dd>
                <dt>ADB command</dt><dd>{latency.adbDuration} ms</dd>
                <dt>Input response</dt><dd>{latency.clickToResponse} ms</dd>
                <dt>Changed frame</dt><dd>{latency.clickToChangedFrame}</dd>
              </dl>
            )}
          </div>
          <small>Tap the screen to focus it before using keyboard input. All gestures are sent to Android through the Python backend and ADB.</small>
        </aside>
      </section>
    </main>
  );
}

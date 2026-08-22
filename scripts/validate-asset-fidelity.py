#!/usr/bin/env python3
"""Validate an approved Design Arc asset set in source and a running browser."""

from __future__ import annotations

import argparse
import base64
from contextlib import contextmanager
import functools
import hashlib
from http.server import BaseHTTPRequestHandler, SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time
from typing import Iterator
from urllib.parse import urlparse
from urllib.request import urlopen
import zlib


SCHEMA = "design-arc.asset-fidelity/v1"
RASTER_TYPES = {
    "image/png",
    "image/jpeg",
    "image/gif",
    "image/webp",
    "image/bmp",
    "image/tiff",
}
SEMANTIC_KINDS = {"control", "label", "navigation", "state", "status"}
FIXED_VIEWPORTS = {"desktop": (1280, 720), "mobile": (390, 844)}
NATIVE_ELEMENTS = {
    "control": {"button", "input", "select", "textarea", "a"},
    "label": {"label"},
    "navigation": {"nav"},
    "state": {"input", "select"},
    "status": {"output"},
}


class ValidationError(Exception):
    """A user-actionable asset-fidelity failure."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def object_value(value: object, label: str) -> dict[str, object]:
    require(isinstance(value, dict), f"{label} must be an object")
    return value


def list_value(value: object, label: str) -> list[object]:
    require(isinstance(value, list), f"{label} must be a list")
    return value


def text_value(value: object, label: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), f"{label} must be non-empty text")
    return value


def safe_file(root: Path, relative: object, label: str) -> tuple[str, Path]:
    name = text_value(relative, label)
    candidate = (root / name).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ValidationError(f"{label} must stay inside the application root") from exc
    return name, candidate


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def discover_browser() -> Path:
    configured = os.environ.get("DESIGN_ARC_BROWSER")
    if configured is not None:
        candidate = Path(configured).expanduser()
        require(
            candidate.is_file() and os.access(candidate, os.X_OK),
            "DESIGN_ARC_BROWSER does not name an executable Chrome or Chromium browser",
        )
        return candidate.resolve()

    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ]
    for executable in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome"):
        found = shutil.which(executable)
        if found:
            candidates.append(found)
    for name in candidates:
        candidate = Path(name)
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate.resolve()
    raise ValidationError(
        "no supported Chrome or Chromium browser found; install one or set DESIGN_ARC_BROWSER"
    )


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, _format: str, *_args: object) -> None:
        return


@contextmanager
def serve(root: Path) -> Iterator[str]:
    handler = functools.partial(QuietHandler, directory=str(root))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address[:2]
        yield f"http://{host}:{port}/index.html"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def reference_handler(
    assets: dict[str, tuple[bytes, str, str]],
) -> type[BaseHTTPRequestHandler]:
    class TrustedReferenceHandler(BaseHTTPRequestHandler):
        def log_message(self, _format: str, *_args: object) -> None:
            return

        def do_GET(self) -> None:
            path = urlparse(self.path).path
            if path == "/reference.html":
                body = b"<!doctype html><meta charset=utf-8><title>Design Arc trusted raster reference</title>"
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header(
                    "Content-Security-Policy",
                    "default-src 'none'; img-src 'self'; script-src 'none'; worker-src 'none'; connect-src 'none'",
                )
            elif path.startswith("/asset/") and path.removeprefix("/asset/") in assets:
                asset_key = path.removeprefix("/asset/")
                body, media_type, approved_hash = assets[asset_key]
                self.send_response(200)
                self.send_header("Content-Type", media_type)
                self.send_header("X-Design-Arc-Approved-SHA256", approved_hash)
            else:
                body = b"not found"
                self.send_response(404)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return TrustedReferenceHandler


@contextmanager
def serve_reference_assets(
    assets: dict[str, tuple[bytes, str, str]],
) -> Iterator[str]:
    """Serve approved bytes from an origin that exposes no application content."""
    server = ThreadingHTTPServer(("127.0.0.1", 0), reference_handler(assets))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address[:2]
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        return int(listener.getsockname()[1])


def recv_exact(connection: socket.socket, length: int) -> bytes:
    chunks: list[bytes] = []
    remaining = length
    while remaining:
        chunk = connection.recv(remaining)
        if not chunk:
            raise ValidationError("browser DevTools connection closed unexpectedly")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


class WebSocket:
    """Small RFC 6455 client sufficient for local Chrome DevTools messages."""

    def __init__(self, url: str) -> None:
        parsed = urlparse(url)
        require(parsed.scheme == "ws" and parsed.hostname is not None, "invalid browser DevTools URL")
        self.connection = socket.create_connection((parsed.hostname, parsed.port or 80), timeout=10)
        self.connection.settimeout(10)
        key = base64.b64encode(os.urandom(16)).decode("ascii")
        path = parsed.path or "/"
        if parsed.query:
            path += "?" + parsed.query
        request = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {parsed.hostname}:{parsed.port or 80}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n"
            "Origin: http://127.0.0.1\r\n\r\n"
        )
        self.connection.sendall(request.encode("ascii"))
        response = b""
        while b"\r\n\r\n" not in response:
            response += self.connection.recv(4096)
            require(len(response) < 65536, "browser DevTools handshake was too large")
        require(response.startswith(b"HTTP/1.1 101"), "browser rejected the DevTools connection")

    def close(self) -> None:
        try:
            self.connection.close()
        except OSError:
            pass

    def send_text(self, text: str) -> None:
        payload = text.encode("utf-8")
        mask = os.urandom(4)
        length = len(payload)
        header = bytearray([0x81])
        if length < 126:
            header.append(0x80 | length)
        elif length < 65536:
            header.append(0x80 | 126)
            header.extend(struct.pack(">H", length))
        else:
            header.append(0x80 | 127)
            header.extend(struct.pack(">Q", length))
        masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
        self.connection.sendall(bytes(header) + mask + masked)

    def receive_text(self) -> str:
        fragments: list[bytes] = []
        while True:
            first, second = recv_exact(self.connection, 2)
            final = bool(first & 0x80)
            opcode = first & 0x0F
            masked = bool(second & 0x80)
            length = second & 0x7F
            if length == 126:
                length = struct.unpack(">H", recv_exact(self.connection, 2))[0]
            elif length == 127:
                length = struct.unpack(">Q", recv_exact(self.connection, 8))[0]
            mask = recv_exact(self.connection, 4) if masked else b""
            payload = recv_exact(self.connection, length)
            if masked:
                payload = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
            if opcode == 0x8:
                raise ValidationError("browser closed the DevTools connection")
            if opcode == 0x9:
                self._send_control(0xA, payload)
                continue
            if opcode in (0x0, 0x1):
                fragments.append(payload)
                if final:
                    return b"".join(fragments).decode("utf-8")

    def _send_control(self, opcode: int, payload: bytes) -> None:
        mask = os.urandom(4)
        require(len(payload) < 126, "unsupported browser control frame")
        masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
        self.connection.sendall(bytes([0x80 | opcode, 0x80 | len(payload)]) + mask + masked)


class ChromeSession:
    def __init__(self, browser: Path) -> None:
        self.browser = browser
        self.process: subprocess.Popen[bytes] | None = None
        self.socket: WebSocket | None = None
        self.message_id = 0
        self.events: list[dict[str, object]] = []
        self.profile: tempfile.TemporaryDirectory[str] | None = None

    def __enter__(self) -> "ChromeSession":
        try:
            port = free_port()
            self.profile = tempfile.TemporaryDirectory(prefix="design-arc-chrome-")
            command = [
                str(self.browser),
                "--headless=new",
                "--disable-background-networking",
                "--disable-component-update",
                "--disable-default-apps",
                "--disable-extensions",
                "--disable-gpu",
                "--hide-scrollbars",
                "--no-default-browser-check",
                "--no-first-run",
                "--remote-allow-origins=*",
                f"--remote-debugging-port={port}",
                f"--user-data-dir={self.profile.name}",
                "about:blank",
            ]
            if hasattr(os, "geteuid") and os.geteuid() == 0:
                command.insert(1, "--no-sandbox")
            self.process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            pages: list[dict[str, object]] | None = None
            deadline = time.monotonic() + 12
            while time.monotonic() < deadline:
                if self.process.poll() is not None:
                    raise ValidationError("supported browser exited before DevTools became ready")
                try:
                    with urlopen(f"http://127.0.0.1:{port}/json/list", timeout=1) as response:
                        value = json.load(response)
                    if isinstance(value, list) and value:
                        pages = value
                        break
                except (OSError, ValueError):
                    time.sleep(0.1)
            require(pages is not None, "supported browser did not expose DevTools within 12 seconds")
            page = next((item for item in pages if item.get("type") == "page"), None)
            require(isinstance(page, dict), "supported browser did not expose a page target")
            websocket_url = page.get("webSocketDebuggerUrl")
            require(isinstance(websocket_url, str), "supported browser omitted its page DevTools URL")
            self.socket = WebSocket(websocket_url)
            self.call("Page.enable")
            self.call("Runtime.enable")
            return self
        except BaseException:
            self._cleanup()
            raise

    def __exit__(self, _type: object, _value: object, _traceback: object) -> None:
        self._cleanup()

    def _cleanup(self) -> None:
        if self.socket is not None:
            self.socket.close()
            self.socket = None
        if self.process is not None:
            if self.process.poll() is None:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait(timeout=5)
            self.process = None
        if self.profile is not None:
            self.profile.cleanup()
            self.profile = None

    def call(self, method: str, params: dict[str, object] | None = None) -> dict[str, object]:
        require(self.socket is not None, "browser DevTools is not connected")
        self.message_id += 1
        request_id = self.message_id
        self.socket.send_text(json.dumps({"id": request_id, "method": method, "params": params or {}}))
        while True:
            message = json.loads(self.socket.receive_text())
            if message.get("id") == request_id:
                require("error" not in message, f"browser DevTools {method} failed: {message.get('error')}")
                result = message.get("result", {})
                require(isinstance(result, dict), f"browser DevTools {method} returned an invalid result")
                return result
            if "method" in message:
                self.events.append(message)

    def wait_event(self, method: str) -> None:
        require(self.socket is not None, "browser DevTools is not connected")
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            for index, event in enumerate(self.events):
                if event.get("method") == method:
                    self.events.pop(index)
                    return
            message = json.loads(self.socket.receive_text())
            if message.get("method") == method:
                return
            if "method" in message:
                self.events.append(message)
        raise ValidationError(f"browser did not emit {method}")


PROBE_FUNCTION = r"""
(async (spec) => {
  if (document.fonts && document.fonts.ready) await document.fonts.ready;
  await new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  const accessibleName = element => {
    const aria = element.getAttribute('aria-label');
    if (aria) return aria.trim();
    if (element.labels && element.labels.length) {
      return Array.from(element.labels).map(label => label.textContent.trim()).join(' ').trim();
    }
    const alt = element.getAttribute('alt');
    if (alt) return alt.trim();
    return (element.textContent || '').trim();
  };
  const isInteractive = element => {
    const tag = element.tagName.toLowerCase();
    if (tag === 'a') return element.hasAttribute('href');
    if (tag === 'button' || tag === 'select' || tag === 'textarea') return !element.disabled;
    if (tag === 'input') return element.type !== 'hidden' && !element.disabled;
    return false;
  };
  const canFocus = element => {
    const previous = document.activeElement;
    element.focus({preventScroll: true});
    const focused = document.activeElement === element;
    if (previous && previous.focus) previous.focus({preventScroll: true});
    return focused;
  };
  const assets = spec.assets.map(expected => {
    const element = document.querySelector(expected.selector);
    if (!element) return {id: expected.id, found: false};
    const style = getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    const x = Math.max(0, Math.min(innerWidth - 1, rect.left + rect.width / 2));
    const y = Math.max(0, Math.min(innerHeight - 1, rect.top + rect.height / 2));
    const hit = rect.width > 0 && rect.height > 0 ? document.elementFromPoint(x, y) : null;
    return {
      id: expected.id,
      found: true,
      tag: element.tagName.toLowerCase(),
      src: element.currentSrc || element.src || '',
      complete: element.complete === true,
      naturalWidth: Number(element.naturalWidth || 0),
      naturalHeight: Number(element.naturalHeight || 0),
      x: rect.left,
      y: rect.top,
      width: rect.width,
      height: rect.height,
      alt: element.getAttribute('alt') || '',
      visible: style.display !== 'none' && style.visibility !== 'hidden' &&
        Number(style.opacity) > 0 && rect.width > 0 && rect.height > 0 &&
        rect.right > 0 && rect.bottom > 0 && rect.left < innerWidth && rect.top < innerHeight &&
        (hit === element || element.contains(hit)),
    };
  });
  const semantics = spec.semantics.map(expected => {
    const element = document.querySelector(expected.selector);
    if (!element) return {selector: expected.selector, found: false};
    const navigationTargets = Array.from(element.querySelectorAll(
      'a[href], button:not([disabled]), input:not([disabled]):not([type="hidden"]), select:not([disabled]), textarea:not([disabled])'
    ));
    const labelTarget = element.tagName.toLowerCase() === 'label'
      ? (element.htmlFor ? document.getElementById(element.htmlFor) : element.querySelector('input, select, textarea, button'))
      : null;
    return {
      selector: expected.selector,
      found: true,
      tag: element.tagName.toLowerCase(),
      role: element.getAttribute('role') || '',
      name: accessibleName(element),
      interactive: isInteractive(element),
      focusable: canFocus(element),
      labelAssociated: Boolean(labelTarget),
      navigationFocusable: navigationTargets.some(target => isInteractive(target) && canFocus(target)),
    };
  });
  return {viewport: {width: innerWidth, height: innerHeight}, assets, semantics};
})
"""


REFERENCE_FUNCTION = r"""
(async (spec) => {
  const image = new Image();
  image.decoding = 'sync';
  image.src = spec.assetUrl;
  await image.decode();
  const canvas = document.createElement('canvas');
  canvas.width = Math.max(1, Math.round(spec.width));
  canvas.height = Math.max(1, Math.round(spec.height));
  const context = canvas.getContext('2d', {willReadFrequently: true});
  if (!context) throw new Error('trusted 2D canvas is unavailable');
  context.drawImage(image, 0, 0, canvas.width, canvas.height);
  const samples = [];
  for (let row = 0; row < 10; row += 1) {
    const vertical = (row + 0.5) / 10;
    const canvasY = Math.min(canvas.height - 1, Math.floor(vertical * canvas.height));
    for (let column = 0; column < 20; column += 1) {
      const horizontal = (column + 0.5) / 20;
      const canvasX = Math.min(canvas.width - 1, Math.floor(horizontal * canvas.width));
      samples.push({
        screenX: Math.floor(spec.x + horizontal * spec.width),
        screenY: Math.floor(spec.y + vertical * spec.height),
        rgba: Array.from(context.getImageData(canvasX, canvasY, 1, 1).data),
      });
    }
  }
  return {
    src: image.currentSrc || image.src,
    naturalWidth: image.naturalWidth,
    naturalHeight: image.naturalHeight,
    samples,
  };
})
"""


def screenshot_dimensions(data: bytes) -> tuple[int, int]:
    require(data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24, "browser screenshot is not a PNG")
    return struct.unpack(">II", data[16:24])


def paeth(left: int, above: int, upper_left: int) -> int:
    estimate = left + above - upper_left
    left_distance = abs(estimate - left)
    above_distance = abs(estimate - above)
    upper_left_distance = abs(estimate - upper_left)
    if left_distance <= above_distance and left_distance <= upper_left_distance:
        return left
    if above_distance <= upper_left_distance:
        return above
    return upper_left


def decode_png(data: bytes, label: str) -> tuple[int, int, bytes]:
    """Decode an 8-bit, non-interlaced RGB/RGBA PNG into RGBA bytes."""
    require(data.startswith(b"\x89PNG\r\n\x1a\n"), f"{label} is not a PNG")
    offset = 8
    width = height = bit_depth = color_type = interlace = None
    compressed = bytearray()
    while offset + 12 <= len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        kind = data[offset + 4 : offset + 8]
        body = data[offset + 8 : offset + 8 + length]
        require(offset + 12 + length <= len(data), f"{label} has a truncated PNG chunk")
        if kind == b"IHDR":
            width, height, bit_depth, color_type, _compression, _filter, interlace = struct.unpack(
                ">IIBBBBB", body
            )
        elif kind == b"IDAT":
            compressed.extend(body)
        elif kind == b"IEND":
            break
        offset += 12 + length
    require(
        isinstance(width, int) and isinstance(height, int) and width > 0 and height > 0,
        f"{label} has no valid PNG dimensions",
    )
    require(bit_depth == 8 and color_type in {2, 6} and interlace == 0, f"{label} must be an 8-bit non-interlaced RGB/RGBA PNG")
    channels = 3 if color_type == 2 else 4
    stride = width * channels
    try:
        raw = zlib.decompress(bytes(compressed))
    except zlib.error as exc:
        raise ValidationError(f"{label} PNG pixels are corrupt") from exc
    require(len(raw) == height * (stride + 1), f"{label} PNG scanline length is invalid")
    rows: list[bytearray] = []
    cursor = 0
    previous = bytearray(stride)
    for _row in range(height):
        filter_type = raw[cursor]
        cursor += 1
        encoded = raw[cursor : cursor + stride]
        cursor += stride
        reconstructed = bytearray(stride)
        for index, value in enumerate(encoded):
            left = reconstructed[index - channels] if index >= channels else 0
            above = previous[index]
            upper_left = previous[index - channels] if index >= channels else 0
            if filter_type == 0:
                prediction = 0
            elif filter_type == 1:
                prediction = left
            elif filter_type == 2:
                prediction = above
            elif filter_type == 3:
                prediction = (left + above) // 2
            elif filter_type == 4:
                prediction = paeth(left, above, upper_left)
            else:
                raise ValidationError(f"{label} uses unsupported PNG filter {filter_type}")
            reconstructed[index] = (value + prediction) & 0xFF
        rows.append(reconstructed)
        previous = reconstructed
    rgba = bytearray(width * height * 4)
    destination = 0
    for row in rows:
        for source in range(0, len(row), channels):
            rgba[destination : destination + 3] = row[source : source + 3]
            rgba[destination + 3] = row[source + 3] if channels == 4 else 255
            destination += 4
    return width, height, bytes(rgba)


def rgba_pixel(pixels: bytes, width: int, x: int, y: int) -> tuple[int, int, int, int]:
    offset = (y * width + x) * 4
    return tuple(pixels[offset : offset + 4])  # type: ignore[return-value]


def screenshot_asset_coverage(
    screenshot: bytes,
    reference_samples: object,
) -> float:
    screen_width, screen_height, screen_pixels = decode_png(screenshot, "browser screenshot")
    matches = 0
    compared = 0
    samples = list_value(reference_samples, "browser-native asset reference samples")
    require(len(samples) == 200, "browser-native asset reference sampling must cover 200 points")
    for index, raw_sample in enumerate(samples):
        sample = object_value(raw_sample, f"browser-native asset reference sample {index}")
        screen_x = sample.get("screenX")
        screen_y = sample.get("screenY")
        require(
            isinstance(screen_x, int) and 0 <= screen_x < screen_width,
            f"browser-native asset reference sample {index} has an invalid x coordinate",
        )
        require(
            isinstance(screen_y, int) and 0 <= screen_y < screen_height,
            f"browser-native asset reference sample {index} has an invalid y coordinate",
        )
        rgba = list_value(sample.get("rgba"), f"browser-native asset reference sample {index} rgba")
        require(
            len(rgba) == 4 and all(isinstance(channel, int) and 0 <= channel <= 255 for channel in rgba),
            f"browser-native asset reference sample {index} has invalid color data",
        )
        if rgba[3] < 250:
            continue
        actual = rgba_pixel(screen_pixels, screen_width, screen_x, screen_y)
        compared += 1
        if max(abs(actual[channel] - rgba[channel]) for channel in range(3)) <= 16:
            matches += 1
    require(compared >= 100, "approved asset has insufficient opaque pixel coverage for screenshot proof")
    return matches / compared


def inspect_viewport(
    chrome: ChromeSession,
    url: str,
    viewport_name: str,
    viewport: dict[str, object],
    selected_assets: list[dict[str, object]],
    semantics: list[dict[str, object]],
) -> tuple[dict[str, object], bytes]:
    width = viewport.get("width")
    height = viewport.get("height")
    require(isinstance(width, int) and width >= 320, f"{viewport_name} viewport width must be at least 320")
    require(isinstance(height, int) and height >= 320, f"{viewport_name} viewport height must be at least 320")
    chrome.call(
        "Emulation.setDeviceMetricsOverride",
        {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": viewport_name == "mobile"},
    )
    chrome.call("Page.navigate", {"url": f"{url}?viewport={viewport_name}"})
    chrome.wait_event("Page.loadEventFired")
    spec = {
        "assets": [
            {"id": asset["id"], "selector": asset["selector"]}
            for asset in selected_assets
        ],
        "semantics": [
            {"selector": requirement["selector"]}
            for requirement in semantics
        ],
    }
    expression = f"{PROBE_FUNCTION}({json.dumps(spec)})"
    evaluation = chrome.call(
        "Runtime.evaluate",
        {"expression": expression, "awaitPromise": True, "returnByValue": True},
    )
    require("exceptionDetails" not in evaluation, "browser runtime probe threw an exception")
    remote = object_value(evaluation.get("result"), "browser runtime result")
    result = object_value(remote.get("value"), "browser runtime value")
    screenshot_result = chrome.call(
        "Page.captureScreenshot",
        {"format": "png", "fromSurface": True, "captureBeyondViewport": False},
    )
    encoded = text_value(screenshot_result.get("data"), "browser screenshot")
    screenshot = base64.b64decode(encoded, validate=True)
    require(
        screenshot_dimensions(screenshot) == (width, height),
        f"browser {viewport_name} screenshot must be {width}x{height}",
    )
    return result, screenshot


def trusted_reference_samples(
    chrome: ChromeSession,
    reference_origin: str,
    asset_key: str,
    viewport_name: str,
    viewport: dict[str, object],
    rectangle: dict[str, object],
) -> list[object]:
    """Decode approved bytes in a clean profile and non-application origin."""
    width = viewport["width"]
    height = viewport["height"]
    chrome.call(
        "Emulation.setDeviceMetricsOverride",
        {"width": width, "height": height, "deviceScaleFactor": 1, "mobile": viewport_name == "mobile"},
    )
    reference_page = f"{reference_origin}/reference.html?viewport={viewport_name}&asset={asset_key}"
    asset_url = f"{reference_origin}/asset/{asset_key}"
    chrome.call("Page.navigate", {"url": reference_page})
    chrome.wait_event("Page.loadEventFired")
    spec = {
        "assetUrl": asset_url,
        "x": rectangle["x"],
        "y": rectangle["y"],
        "width": rectangle["width"],
        "height": rectangle["height"],
    }
    evaluation = chrome.call(
        "Runtime.evaluate",
        {
            "expression": f"{REFERENCE_FUNCTION}({json.dumps(spec)})",
            "awaitPromise": True,
            "returnByValue": True,
        },
    )
    require("exceptionDetails" not in evaluation, "trusted browser-native reference sampling failed")
    remote = object_value(evaluation.get("result"), "trusted browser runtime result")
    result = object_value(remote.get("value"), "trusted browser runtime value")
    require(result.get("src") == asset_url, "trusted reference loaded an unexpected asset URL")
    require(
        int(result.get("naturalWidth", 0)) > 0 and int(result.get("naturalHeight", 0)) > 0,
        "trusted reference asset did not decode",
    )
    return list_value(result.get("samples"), "trusted browser-native asset reference samples")


def validate_manifest(manifest_path: Path, evidence_output: Path | None = None) -> None:
    require(manifest_path.is_file(), f"manifest is unavailable: {manifest_path}")
    root = manifest_path.resolve().parent
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"manifest is not valid JSON: {exc}") from exc
    manifest = object_value(manifest, "manifest")
    require(manifest.get("schema") == SCHEMA, f"manifest schema must be {SCHEMA}")

    platform = object_value(manifest.get("active_platform"), "active_platform")
    platform_name = text_value(platform.get("name"), "active_platform.name")
    native_images = platform.get("native_image_generation")
    require(isinstance(native_images, bool), "active_platform.native_image_generation must be true or false")

    asset_sets = object_value(manifest.get("asset_sets"), "asset_sets")
    parsed_sets: dict[str, list[dict[str, object]]] = {}
    assets_by_id: dict[str, tuple[str, dict[str, object]]] = {}
    for set_name in ("platform", "stitch"):
        raw_assets = list_value(asset_sets.get(set_name), f"asset_sets.{set_name}")
        parsed: list[dict[str, object]] = []
        for index, raw_asset in enumerate(raw_assets):
            asset = object_value(raw_asset, f"asset_sets.{set_name}[{index}]")
            asset_id = text_value(asset.get("id"), f"asset_sets.{set_name}[{index}].id")
            require(asset_id.startswith(set_name + "."), f"asset {asset_id} must retain {set_name} provenance")
            require(asset_id not in assets_by_id, f"asset ID is duplicated: {asset_id}")
            assets_by_id[asset_id] = (set_name, asset)
            parsed.append(asset)
        parsed_sets[set_name] = parsed
    require(bool(parsed_sets["platform"]), "active platform must provide a baseline platform asset set")
    if manifest.get("stitch_invoked") is True:
        require(bool(parsed_sets["stitch"]), "Stitch invocation requires a preserved Stitch asset set")

    selection = object_value(manifest.get("selection"), "selection")
    design = selection.get("design")
    require(design in {"platform", "stitch", "hybrid"}, "selection.design must be platform, stitch, or hybrid")
    selected_ids = [text_value(value, "selection.asset_ids item") for value in list_value(selection.get("asset_ids"), "selection.asset_ids")]
    require(bool(selected_ids) and len(selected_ids) == len(set(selected_ids)), "selection.asset_ids must be unique and non-empty")
    for asset_id in selected_ids:
        require(asset_id in assets_by_id, f"selected asset is absent from its provenance set: {asset_id}")
    selected_sets = {assets_by_id[asset_id][0] for asset_id in selected_ids}
    if design == "platform":
        require(selected_sets == {"platform"}, "platform selection may use only platform assets")
    elif design == "stitch":
        require(selected_sets == {"stitch"}, "stitch selection may use only stitch assets")
        require(bool(parsed_sets["stitch"]), "stitch selection requires exported Stitch assets")
    else:
        require(selection.get("hybrid_approved") is True, "hybrid selection requires explicit approval")
        require(selected_sets == {"platform", "stitch"}, "approved hybrid must identify assets from both provenance sets")

    required_selected = {
        asset["id"]
        for set_name in selected_sets
        for asset in parsed_sets[set_name]
        if asset.get("required") is True
    }
    missing_required = sorted(required_selected - set(selected_ids))
    if missing_required:
        if design == "hybrid":
            raise ValidationError(f"hybrid selection omits a required asset: {missing_required[0]}")
        raise ValidationError(f"selection omits a required asset from the selected design: {missing_required[0]}")

    implementation_sources = [
        safe_file(root, value, "implementation_sources item")
        for value in list_value(manifest.get("implementation_sources"), "implementation_sources")
    ]
    require(bool(implementation_sources), "implementation_sources must not be empty")
    source_text: dict[str, str] = {}
    for name, path in implementation_sources:
        require(path.is_file(), f"implementation source is unavailable: {name}")
        source_text[name] = path.read_text(encoding="utf-8")

    for set_name, assets in parsed_sets.items():
        for asset in assets:
            asset_id = text_value(asset.get("id"), "asset.id")
            relative, path = safe_file(root, asset.get("path"), f"asset {asset_id} path")
            if not path.is_file():
                if asset_id in selected_ids:
                    raise ValidationError(f"required selected asset is unavailable: {asset_id}")
                raise ValidationError(f"preserved {set_name} asset is unavailable: {asset_id}")
            expected_hash = text_value(asset.get("sha256"), f"asset {asset_id} sha256")
            require(len(expected_hash) == 64, f"asset {asset_id} sha256 must contain 64 hexadecimal characters")
            if file_sha256(path) != expected_hash.lower():
                if asset_id in selected_ids:
                    raise ValidationError(f"selected asset hash does not match approved asset: {asset_id}")
                raise ValidationError(f"preserved {set_name} asset hash does not match: {asset_id}")
            media_type = text_value(asset.get("media_type"), f"asset {asset_id} media_type")
            if set_name == "platform" and asset.get("required") is True and media_type in RASTER_TYPES and not native_images:
                raise ValidationError(
                    f"required raster asset is blocked because {platform_name} lacks native image generation: {asset_id}"
                )
            if asset_id in selected_ids:
                references = [
                    text_value(value, f"asset {asset_id} source_references item")
                    for value in list_value(asset.get("source_references"), f"asset {asset_id} source_references")
                ]
                require(bool(references), f"selected asset has no implementation source reference: {asset_id}")
                require(all(name in source_text for name in references), f"selected asset references an undeclared implementation source: {asset_id}")
                if not any(relative in source_text[name] for name in references):
                    raise ValidationError(f"selected asset is not referenced by implementation source: {asset_id}")
                text_value(asset.get("selector"), f"asset {asset_id} selector")
                text_value(asset.get("alt"), f"asset {asset_id} alt")
            elif any(relative in text for text in source_text.values()):
                raise ValidationError(f"unselected {set_name} asset is referenced by implementation source: {asset_id}")

    semantics = [
        object_value(value, f"semantic_requirements[{index}]")
        for index, value in enumerate(list_value(manifest.get("semantic_requirements"), "semantic_requirements"))
    ]
    kinds = {requirement.get("kind") for requirement in semantics}
    require(SEMANTIC_KINDS <= kinds, "semantic requirements must cover controls, labels, navigation, state, and status")
    for requirement in semantics:
        kind = requirement.get("kind")
        require(kind in SEMANTIC_KINDS, f"unsupported semantic requirement kind: {kind}")
        selector = text_value(requirement.get("selector"), f"semantic {kind} selector")
        element = text_value(requirement.get("element"), f"semantic {kind} element").lower()
        require(element in NATIVE_ELEMENTS[str(kind)], f"semantic {kind} {selector} must use a native {kind} element")
        text_value(requirement.get("name"), f"semantic {kind} name")

    viewports = object_value(manifest.get("viewports"), "viewports")
    for viewport_name, expected_dimensions in FIXED_VIEWPORTS.items():
        viewport = object_value(viewports.get(viewport_name), f"viewports.{viewport_name}")
        actual_dimensions = (viewport.get("width"), viewport.get("height"))
        require(
            actual_dimensions == expected_dimensions,
            f"{viewport_name} viewport must be exactly {expected_dimensions[0]}x{expected_dimensions[1]}",
        )
    selected_assets = [assets_by_id[asset_id][1] for asset_id in selected_ids]
    reference_payloads: dict[str, tuple[bytes, str, str]] = {}
    reference_keys: dict[str, str] = {}
    for asset in selected_assets:
        render = object_value(asset.get("render"), f"asset {asset['id']} render")
        require({"desktop", "mobile"} <= set(render), f"asset {asset['id']} requires desktop and mobile render expectations")
        asset_id = str(asset["id"])
        approved_hash = str(asset["sha256"])
        asset_key = hashlib.sha256(f"{asset_id}\0{approved_hash}".encode("utf-8")).hexdigest()
        approved_path = safe_file(root, asset.get("path"), f"asset {asset_id} path")[1]
        reference_payloads[asset_key] = (
            approved_path.read_bytes(),
            str(asset["media_type"]),
            approved_hash,
        )
        reference_keys[asset_id] = asset_key

    browser = discover_browser()
    proof: dict[str, object] = {
        "schema": "design-arc.asset-fidelity-proof/v1",
        "manifest_sha256": file_sha256(manifest_path),
        "selected_design": design,
        "selected_asset_ids": selected_ids,
        "viewports": {},
    }
    with (
        serve(root) as url,
        serve_reference_assets(reference_payloads) as reference_origin,
        ChromeSession(browser) as chrome,
        ChromeSession(browser) as reference_chrome,
    ):
        approved_origin = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        proof["reference_trust_boundary"] = {
            "origin": reference_origin,
            "separate_application_origin": reference_origin != approved_origin,
            "independent_browser_profile": True,
            "application_content_served": False,
        }
        for viewport_name in ("desktop", "mobile"):
            viewport = object_value(viewports.get(viewport_name), f"viewports.{viewport_name}")
            result, screenshot = inspect_viewport(chrome, url, viewport_name, viewport, selected_assets, semantics)
            viewport_proof: dict[str, object] = {
                "width": viewport["width"],
                "height": viewport["height"],
                "screenshot_sha256": hashlib.sha256(screenshot).hexdigest(),
                "assets": {},
            }
            print(
                f"PASS: {viewport_name} screenshot sha256 "
                f"{viewport_proof['screenshot_sha256']}"
            )
            actual_assets = {
                item.get("id"): item
                for item in list_value(result.get("assets"), f"browser {viewport_name} assets")
                if isinstance(item, dict)
            }
            for asset in selected_assets:
                asset_id = str(asset["id"])
                actual = object_value(actual_assets.get(asset_id), f"browser asset {asset_id}")
                require(actual.get("found") is True, f"selected {asset_id} is absent from running application at {viewport_name}")
                require(actual.get("tag") == "img", f"selected {asset_id} must render as an image at {viewport_name}")
                actual_src = text_value(actual.get("src"), f"selected {asset_id} browser source")
                expected_path = str(asset["path"])
                parsed_source = urlparse(actual_src)
                require(
                    f"{parsed_source.scheme}://{parsed_source.netloc}" == approved_origin,
                    f"selected {asset_id} loaded from an unapproved origin at {viewport_name}",
                )
                require(
                    parsed_source.path.lstrip("/") == expected_path,
                    f"selected {asset_id} is substituted in the running application at {viewport_name}",
                )
                require(
                    actual.get("complete") is True and int(actual.get("naturalWidth", 0)) > 0 and int(actual.get("naturalHeight", 0)) > 0,
                    f"selected {asset_id} is broken in the running application at {viewport_name}",
                )
                require(actual.get("alt") == asset.get("alt"), f"selected {asset_id} accessible description drifted at {viewport_name}")
                require(actual.get("visible") is True, f"selected {asset_id} is not visibly rendered at {viewport_name}")
                expected_render = object_value(
                    object_value(asset.get("render"), f"asset {asset_id} render").get(viewport_name),
                    f"asset {asset_id} {viewport_name} render",
                )
                tolerance = expected_render.get("tolerance", 0)
                require(isinstance(tolerance, (int, float)) and tolerance >= 0, f"asset {asset_id} render tolerance must be non-negative")
                for dimension in ("x", "y", "width", "height"):
                    expected = expected_render.get(dimension)
                    actual_dimension = actual.get(dimension)
                    minimum = 0 if dimension in {"x", "y"} else 0.000001
                    require(isinstance(expected, (int, float)) and expected >= minimum, f"asset {asset_id} expected {dimension} is invalid")
                    require(isinstance(actual_dimension, (int, float)), f"asset {asset_id} browser {dimension} is invalid")
                    require(
                        abs(actual_dimension - expected) <= tolerance,
                        f"selected {asset_id} {dimension} does not match approved proposal at {viewport_name}",
                    )
                reference_samples = trusted_reference_samples(
                    reference_chrome,
                    reference_origin,
                    reference_keys[asset_id],
                    viewport_name,
                    viewport,
                    actual,
                )
                coverage = screenshot_asset_coverage(screenshot, reference_samples)
                require(
                    coverage >= 0.9,
                    f"selected {asset_id} screenshot coverage is below 90% at {viewport_name}",
                )
                object_value(viewport_proof["assets"], "viewport proof assets")[asset_id] = {
                    "approved_sha256": asset["sha256"],
                    "loaded_url": actual_src,
                    "rectangle": {
                        dimension: actual[dimension] for dimension in ("x", "y", "width", "height")
                    },
                    "pixel_coverage": round(coverage, 6),
                    "reference_sample_count": len(reference_samples),
                    "reference_origin": reference_origin,
                }
                print(f"PASS: selected {asset_id} rendered at {viewport_name}")

            actual_semantics = {
                item.get("selector"): item
                for item in list_value(result.get("semantics"), f"browser {viewport_name} semantics")
                if isinstance(item, dict)
            }
            for requirement in semantics:
                selector = str(requirement["selector"])
                kind = str(requirement["kind"])
                actual = object_value(actual_semantics.get(selector), f"semantic {kind} {selector}")
                require(actual.get("found") is True, f"semantic {kind} {selector} is absent at {viewport_name}")
                expected_element = str(requirement["element"]).lower()
                require(
                    actual.get("tag") == expected_element,
                    f"semantic {kind} {selector} must render as {expected_element}",
                )
                require(actual.get("name") == requirement.get("name"), f"semantic {kind} {selector} has no matching accessible name")
                if kind == "control":
                    require(
                        actual.get("interactive") is True and actual.get("focusable") is True,
                        f"semantic control {selector} must be an interactive native control",
                    )
                elif kind == "state":
                    require(
                        actual.get("interactive") is True and actual.get("focusable") is True,
                        f"semantic state {selector} must be an interactive focusable native state",
                    )
                elif kind == "navigation":
                    require(
                        actual.get("navigationFocusable") is True,
                        f"semantic navigation {selector} has no focusable navigation target at {viewport_name}",
                    )
                elif kind == "label":
                    require(
                        actual.get("labelAssociated") is True,
                        f"semantic label {selector} is not associated with a native control at {viewport_name}",
                    )
                if requirement.get("focusable") is True and kind not in {"control", "state"}:
                    require(actual.get("focusable") is True, f"semantic {kind} {selector} is not focusable at {viewport_name}")
            object_value(proof["viewports"], "proof viewports")[viewport_name] = viewport_proof

    if evidence_output is not None:
        evidence_output.parent.mkdir(parents=True, exist_ok=True)
        evidence_output.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("PASS: asset fidelity matches approved proposal at desktop and mobile viewports")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate source integration and desktop/mobile browser fidelity for a selected Design Arc asset set."
    )
    parser.add_argument("manifest", type=Path, help="Path to design-arc.asset-fidelity/v1 JSON manifest")
    parser.add_argument(
        "--evidence-output",
        type=Path,
        help="Optional path for screenshot hashes, approved hashes, rectangles, and pixel coverage proof",
    )
    return parser.parse_args()


def main() -> int:
    try:
        args = parse_args()
        validate_manifest(
            args.manifest.resolve(),
            args.evidence_output.resolve() if args.evidence_output is not None else None,
        )
    except (ValidationError, OSError, ValueError, TypeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

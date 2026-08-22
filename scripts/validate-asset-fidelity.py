#!/usr/bin/env python3
"""Validate an approved Design Arc asset set in source and a running browser."""

from __future__ import annotations

import argparse
import base64
from contextlib import contextmanager
import functools
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
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
NATIVE_ELEMENTS = {
    "control": {"button", "input", "select", "textarea", "a"},
    "label": {"label"},
    "navigation": {"nav"},
    "state": {"input", "select", "details", "progress", "meter"},
    "status": {"output", "status"},
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

    def __exit__(self, _type: object, _value: object, _traceback: object) -> None:
        if self.socket is not None:
            self.socket.close()
        if self.process is not None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
        if self.profile is not None:
            self.profile.cleanup()

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
    const previous = document.activeElement;
    element.focus({preventScroll: true});
    const focusable = document.activeElement === element;
    if (previous && previous.focus) previous.focus({preventScroll: true});
    return {
      selector: expected.selector,
      found: true,
      tag: element.tagName.toLowerCase(),
      role: element.getAttribute('role') || '',
      name: accessibleName(element),
      focusable,
    };
  });
  return {viewport: {width: innerWidth, height: innerHeight}, assets, semantics};
})
"""


def screenshot_dimensions(data: bytes) -> tuple[int, int]:
    require(data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24, "browser screenshot is not a PNG")
    return struct.unpack(">II", data[16:24])


def inspect_viewport(
    chrome: ChromeSession,
    url: str,
    viewport_name: str,
    viewport: dict[str, object],
    selected_assets: list[dict[str, object]],
    semantics: list[dict[str, object]],
) -> dict[str, object]:
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
    return result


def validate_manifest(manifest_path: Path) -> None:
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
    if design != "hybrid":
        require(required_selected <= set(selected_ids), "selection omits a required asset from the selected design")

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
    selected_assets = [assets_by_id[asset_id][1] for asset_id in selected_ids]
    for asset in selected_assets:
        render = object_value(asset.get("render"), f"asset {asset['id']} render")
        require({"desktop", "mobile"} <= set(render), f"asset {asset['id']} requires desktop and mobile render expectations")

    browser = discover_browser()
    with serve(root) as url, ChromeSession(browser) as chrome:
        for viewport_name in ("desktop", "mobile"):
            viewport = object_value(viewports.get(viewport_name), f"viewports.{viewport_name}")
            result = inspect_viewport(chrome, url, viewport_name, viewport, selected_assets, semantics)
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
                require(
                    urlparse(actual_src).path.lstrip("/") == expected_path,
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
                for dimension in ("width", "height"):
                    expected = expected_render.get(dimension)
                    actual_dimension = actual.get(dimension)
                    require(isinstance(expected, (int, float)) and expected > 0, f"asset {asset_id} expected {dimension} must be positive")
                    require(isinstance(actual_dimension, (int, float)), f"asset {asset_id} browser {dimension} is invalid")
                    require(
                        abs(actual_dimension - expected) <= tolerance,
                        f"selected {asset_id} {dimension} does not match approved proposal at {viewport_name}",
                    )
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
                if requirement.get("focusable") is True:
                    require(actual.get("focusable") is True, f"semantic {kind} {selector} is not focusable at {viewport_name}")

    print("PASS: asset fidelity matches approved proposal at desktop and mobile viewports")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate source integration and desktop/mobile browser fidelity for a selected Design Arc asset set."
    )
    parser.add_argument("manifest", type=Path, help="Path to design-arc.asset-fidelity/v1 JSON manifest")
    return parser.parse_args()


def main() -> int:
    try:
        validate_manifest(parse_args().manifest.resolve())
    except (ValidationError, OSError, ValueError, TypeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

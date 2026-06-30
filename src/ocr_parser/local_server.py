from __future__ import annotations

import argparse
import base64
import json
import re
import subprocess
import tempfile
import uuid
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse


WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
INDEX_HTML = WORKSPACE_ROOT / "index.html"
EXPORT_SCRIPT = WORKSPACE_ROOT / "tools" / "export_ppt_slides.ps1"
DOWNLOADS_DIR = WORKSPACE_ROOT / "downloads"
DEFAULT_HTML_DIR = DOWNLOADS_DIR / "HTML"
DEFAULT_MD_DIR = DOWNLOADS_DIR / "MD"
ALLOWED_EXTENSIONS = {".ppt", ".pptx", ".pptm"}


class LocalParserHandler(BaseHTTPRequestHandler):
    server_version = "OCRLocalParser/0.1"

    def do_OPTIONS(self) -> None:
        self._send_empty(HTTPStatus.NO_CONTENT)

    def do_GET(self) -> None:
        path = urlparse(self.path).path

        if path == "/health":
            self._send_json({"ok": True, "service": "ocr-local-parser"})
            return

        if path == "/api/settings":
            self._send_json(
                {
                    "ok": True,
                    "workspace": str(WORKSPACE_ROOT),
                    "htmlDir": str(DEFAULT_HTML_DIR),
                    "mdDir": str(DEFAULT_MD_DIR),
                }
            )
            return

        if path in {"/", "/index.html"}:
            self._send_file(INDEX_HTML, "text/html; charset=utf-8")
            return

        self._send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        path = urlparse(self.path).path

        if path == "/api/codex/save":
            try:
                payload = self._read_json_body()
                result = save_codex_html_package(payload)
            except ValueError as error:
                self._send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
                return
            except RuntimeError as error:
                self._send_json({"error": str(error)}, HTTPStatus.INTERNAL_SERVER_ERROR)
                return

            self._send_json(result)
            return

        if path == "/api/markdown/save":
            try:
                payload = self._read_json_body()
                result = save_markdown_file(payload)
            except ValueError as error:
                self._send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
                return
            except RuntimeError as error:
                self._send_json({"error": str(error)}, HTTPStatus.INTERNAL_SERVER_ERROR)
                return

            self._send_json(result)
            return

        if path == "/api/downloads/open":
            try:
                payload = self._read_optional_json_body()
                result = open_directory(payload.get("directory") or str(DEFAULT_HTML_DIR))
            except ValueError as error:
                self._send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
                return
            except RuntimeError as error:
                self._send_json({"error": str(error)}, HTTPStatus.INTERNAL_SERVER_ERROR)
                return

            self._send_json(result)
            return

        if path == "/api/folder/open":
            try:
                payload = self._read_json_body()
                result = open_directory(str(payload.get("directory") or ""))
            except ValueError as error:
                self._send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
                return
            except RuntimeError as error:
                self._send_json({"error": str(error)}, HTTPStatus.INTERNAL_SERVER_ERROR)
                return

            self._send_json(result)
            return

        if path == "/api/folder/select":
            try:
                payload = self._read_json_body()
                result = select_directory(payload)
            except ValueError as error:
                self._send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
                return
            except RuntimeError as error:
                self._send_json({"error": str(error)}, HTTPStatus.INTERNAL_SERVER_ERROR)
                return

            self._send_json(result)
            return

        if path != "/api/ppt/convert":
            self._send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
            return

        try:
            upload = self._read_ppt_upload()
            slides = convert_ppt_to_slide_payloads(upload["filename"], upload["content"])
        except ValueError as error:
            self._send_json({"error": str(error)}, HTTPStatus.BAD_REQUEST)
            return
        except RuntimeError as error:
            self._send_json({"error": str(error)}, HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        self._send_json({"slides": slides})

    def log_message(self, format: str, *args) -> None:
        return

    def _read_ppt_upload(self) -> dict[str, bytes | str]:
        content_type = self.headers.get("Content-Type", "")
        match = re.search(r"boundary=(?P<boundary>[^;]+)", content_type)

        if "multipart/form-data" not in content_type or not match:
            raise ValueError("Expected multipart/form-data upload.")

        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            raise ValueError("No PPT file was uploaded.")
        if length > 80 * 1024 * 1024:
            raise ValueError("PPT file is too large. Limit is 80 MB.")

        body = self.rfile.read(length)
        boundary = ("--" + match.group("boundary").strip('"')).encode("utf-8")

        for part in body.split(boundary):
            if b"Content-Disposition:" not in part or b'name="ppt"' not in part:
                continue

            header_blob, _, content = part.partition(b"\r\n\r\n")
            if not content:
                continue

            content = content.removesuffix(b"\r\n")
            content = content.removesuffix(b"--")
            filename_match = re.search(
                rb'filename="(?P<filename>[^"]+)"',
                header_blob,
            )
            filename = filename_match.group("filename").decode("utf-8", errors="replace") if filename_match else "slides.pptx"
            extension = Path(filename).suffix.lower()

            if extension not in ALLOWED_EXTENSIONS:
                raise ValueError("Select a .ppt, .pptx, or .pptm file.")

            return {"filename": filename, "content": content}

        raise ValueError("PPT file field was not found.")

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            raise ValueError("Request body is empty.")
        if length > 300 * 1024 * 1024:
            raise ValueError("Request body is too large. Limit is 300 MB.")

        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except json.JSONDecodeError as error:
            raise ValueError("Request body must be JSON.") from error

    def _read_optional_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}

        if length > 300 * 1024 * 1024:
            raise ValueError("Request body is too large. Limit is 300 MB.")

        try:
            return json.loads(self.rfile.read(length).decode("utf-8"))
        except json.JSONDecodeError as error:
            raise ValueError("Request body must be JSON.") from error

    def _send_empty(self, status: HTTPStatus) -> None:
        self.send_response(status)
        self._send_cors_headers()
        self.end_headers()

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self._send_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_file(self, path: Path, content_type: str) -> None:
        if not path.exists():
            self._send_json({"error": "File not found"}, HTTPStatus.NOT_FOUND)
            return

        encoded = path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self._send_cors_headers()
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_cors_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Private-Network", "true")


def convert_ppt_to_slide_payloads(filename: str, content: bytes) -> list[dict[str, str | int]]:
    if not EXPORT_SCRIPT.exists():
        raise RuntimeError(f"Missing export script: {EXPORT_SCRIPT}")

    safe_name = Path(filename).name or "slides.pptx"

    with tempfile.TemporaryDirectory(prefix="ocr-ppt-") as temp_root:
        temp_path = Path(temp_root)
        input_path = temp_path / safe_name
        output_dir = temp_path / ("slides-" + uuid.uuid4().hex)
        input_path.write_bytes(content)
        output_dir.mkdir(parents=True, exist_ok=True)

        command = [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(EXPORT_SCRIPT),
            "-InputPath",
            str(input_path),
            "-OutputDir",
            str(output_dir),
        ]
        result = subprocess.run(command, capture_output=True, text=True, timeout=180)

        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "PowerPoint slide export failed.").strip()
            raise RuntimeError(detail)

        image_paths = sorted(
            output_dir.glob("*.PNG"),
            key=lambda path: natural_slide_sort_key(path.name),
        )
        if not image_paths:
            image_paths = sorted(
                output_dir.glob("*.png"),
                key=lambda path: natural_slide_sort_key(path.name),
            )

        if not image_paths:
            raise RuntimeError("No slide images were exported. Check that PowerPoint is installed and the file opens correctly.")

        slides = []
        for index, image_path in enumerate(image_paths, start=1):
            image_bytes = image_path.read_bytes()
            slides.append(
                {
                    "number": index,
                    "name": image_path.name,
                    "type": "image/png",
                    "dataUrl": "data:image/png;base64," + base64.b64encode(image_bytes).decode("ascii"),
                }
            )

        return slides


def natural_slide_sort_key(name: str) -> tuple[int, str]:
    match = re.search(r"(\d+)", name)
    return (int(match.group(1)) if match else 0, name.lower())


def save_codex_html_package(payload: dict) -> dict[str, str | bool]:
    filename = sanitize_download_filename(str(payload.get("filename") or "codex_vision_package.html"))
    html = str(payload.get("html") or "")
    target_dir = resolve_user_directory(payload.get("directory"), DEFAULT_HTML_DIR)

    if not filename.lower().endswith(".html"):
        filename += ".html"
    if not html.strip():
        raise ValueError("HTML package content is empty.")

    target_dir.mkdir(parents=True, exist_ok=True)
    output_path = (target_dir / filename).resolve()
    output_path.write_text(html, encoding="utf-8")

    return {
        "saved": True,
        "path": str(output_path),
        "filename": filename,
    }


def save_markdown_file(payload: dict) -> dict[str, str | bool]:
    filename = sanitize_download_filename(str(payload.get("filename") or "rag_markdown.md"))
    markdown = str(payload.get("markdown") or "")
    target_dir = resolve_user_directory(payload.get("directory"), DEFAULT_MD_DIR)

    if not filename.lower().endswith(".md"):
        filename += ".md"
    if not markdown.strip():
        raise ValueError("Markdown content is empty.")

    target_dir.mkdir(parents=True, exist_ok=True)
    output_path = (target_dir / filename).resolve()
    output_path.write_text(markdown, encoding="utf-8")

    return {
        "saved": True,
        "path": str(output_path),
        "filename": filename,
    }


def resolve_user_directory(value: object, default: Path) -> Path:
    raw_value = str(value or "").strip()
    if not raw_value:
        return default.resolve()

    path = Path(raw_value).expanduser()
    if not path.is_absolute():
        path = WORKSPACE_ROOT / path

    return path.resolve()


def open_directory(directory: object) -> dict[str, str | bool]:
    target_dir = resolve_user_directory(directory, DEFAULT_HTML_DIR)
    target_dir.mkdir(parents=True, exist_ok=True)

    try:
        subprocess.Popen(["explorer", str(target_dir)])
    except OSError as error:
        raise RuntimeError(f"Could not open downloads directory: {error}") from error

    return {
        "opened": True,
        "path": str(target_dir),
    }


def select_directory(payload: dict) -> dict[str, str | bool]:
    title = str(payload.get("title") or "Select save folder")
    current = resolve_user_directory(payload.get("current"), DEFAULT_HTML_DIR)
    current.mkdir(parents=True, exist_ok=True)

    escaped_title = title.replace("'", "''")
    escaped_current = str(current).replace("'", "''")
    command = (
        "Add-Type -AssemblyName System.Windows.Forms; "
        "$owner = New-Object System.Windows.Forms.Form; "
        "$owner.StartPosition = 'CenterScreen'; "
        "$owner.Width = 1; "
        "$owner.Height = 1; "
        "$owner.ShowInTaskbar = $false; "
        "$owner.TopMost = $true; "
        "$owner.Opacity = 0; "
        "$owner.Show(); "
        "$owner.Activate(); "
        "$dialog = New-Object System.Windows.Forms.FolderBrowserDialog; "
        "$dialog.Description = '" + escaped_title + "'; "
        "$dialog.SelectedPath = '" + escaped_current + "'; "
        "$dialog.ShowNewFolderButton = $true; "
        "try { "
        "if ($dialog.ShowDialog($owner) -eq [System.Windows.Forms.DialogResult]::OK) "
        "{ [Console]::OutputEncoding = [System.Text.Encoding]::UTF8; Write-Output $dialog.SelectedPath } "
        "} finally { $owner.Close(); $owner.Dispose(); }"
    )

    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-STA", "-Command", command],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except OSError as error:
        raise RuntimeError(f"Could not open folder picker: {error}") from error
    except subprocess.TimeoutExpired as error:
        raise RuntimeError("Folder picker timed out.") from error

    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "Folder picker failed.").strip()
        raise RuntimeError(detail)

    selected = result.stdout.strip()
    if not selected:
        return {"selected": False, "path": ""}

    return {"selected": True, "path": selected}


def sanitize_download_filename(value: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1F]', "", value.strip())
    cleaned = re.sub(r"\s+", "_", cleaned)
    cleaned = re.sub(r"_+", "_", cleaned).strip("._ ")
    return cleaned[:120] or "codex_vision_package.html"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the local OCR parser helper server.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8765, type=int)
    args = parser.parse_args(argv)

    server = ThreadingHTTPServer((args.host, args.port), LocalParserHandler)
    print(f"OCR local parser server listening on http://{args.host}:{args.port}")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

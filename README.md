# OCR Markdown Parser

OCR text and slide images are collected, normalized, and prepared as Markdown that can be reviewed by Codex Vision.

## Start The App

Use the system launcher:

```powershell
cd "C:\Users\user\Documents\My Works\OCR"
.\start_ocr_app.cmd
```

The launcher starts the local parser service in a visible terminal window and opens the parser UI at `http://127.0.0.1:8765/`. Keep the service window open while using save or PPT automation features.

The local parser service is required for:

- Saving Codex Vision HTML packages directly to `C:\Users\user\Documents\My Works\OCR\downloads`
- PPT auto parsing from `.ppt`, `.pptx`, or `.pptm` files

Do not open `index.html` alone when testing save or PPT automation. Use the local service URL so the app and helper run as one system.

If the browser says the connection was refused:

- Run `.\start_ocr_app.cmd` again.
- Keep the `OCR Local Parser Service` terminal window open.
- Use `http://127.0.0.1:8765/`, not `file:///.../index.html`.

## Project Map

```text
.
|-- index.html                  # Browser UI
|-- start_ocr_app.cmd            # Main launcher
|-- start_ocr_app.ps1            # PowerShell launcher implementation
|-- start_local_parser.ps1       # Internal local parser service launcher
|-- docs/
|   |-- ui-rules.md              # UI behavior and design rules
|   `-- project-map.md           # Engineering map
|-- src/ocr_parser/
|   |-- cli.py                   # ocr-parse command
|   |-- local_server.py          # Local PPT export and HTML save service
|   |-- models.py                # ParsedDocument dataclass
|   `-- parser.py                # OCR text field extraction
|-- tools/
|   |-- export_ppt_slides.ps1    # PowerPoint slide image export
|   |-- remove-legacy-ocr-workspace.ps1
|   `-- use-my-works-workspace.ps1
|-- tests/
|   `-- test_parser.py
|-- data/
|   |-- input/
|   `-- output/
`-- downloads/                   # Codex Vision packages and local logs
```

## Codex Vision Package Save

`Codex 보정 보내기` saves HTML packages through the local parser service only. A save is considered successful only when the file is written to:

```text
C:\Users\user\Documents\My Works\OCR\downloads
```

If the local service is not running, the app shows an error instead of pretending the package was saved.

`Save path` copies the downloads path. If browser clipboard permission is denied, the app shows the path in the status area.

## PPT Auto Parsing

`자동 파싱` lets the user select a `.ppt`, `.pptx`, or `.pptm` file. The local parser service exports each slide as a PNG image with PowerPoint, then sends those slide images back to the browser OCR queue.

Requirements:

- Windows PowerPoint must be installed.
- Launch through `.\start_ocr_app.cmd`.
- Keep the launched local service running while using the browser app.

## Parser CLI

Parse a UTF-8 text file:

```powershell
ocr-parse data\input\sample.txt --pretty
```

Parse stdin:

```powershell
"거래일자: 2026-06-27 합계: 12,300원 contact buyer@example.com" | ocr-parse --pretty
```

Write JSON output:

```powershell
ocr-parse data\input\sample.txt --output data\output\parsed.json
```

## Tests

```powershell
python -m pytest
```

## Working Notes

- Keep generated files under `downloads/` or `data/output/`.
- Keep OCR samples under `data/input/`; only `.gitkeep` is tracked there by default.
- `docs/ui-rules.md` is the source of truth for browser UI behavior before editing `index.html`.

# Project Map

## Main Surfaces

- `index.html`: primary OCR Markdown browser app. It contains styles, markup, and client-side JavaScript in one file.
- `docs/ui-rules.md`: design and behavior requirements for the browser app. Read this before changing `index.html`.
- `src/ocr_parser`: Python parser package for structured extraction from OCR text.
- `tests`: parser regression tests.

## Python Parser Flow

```text
ocr_parser.cli
  -> reads file or stdin
  -> OCRTextParser.parse(text)
  -> ParsedDocument.to_dict()
  -> prints or writes JSON
```

`OCRTextParser` currently extracts:

- dates
- amounts
- email addresses
- phone numbers
- Korean business registration numbers
- line and character counts

## Browser App Flow

```text
image input
  -> local Tesseract OCR A/B/C pass
  -> Markdown draft generation
  -> quality inspector repair
  -> HTML Codex Vision package export
```

The browser app is intentionally single-file for quick local use. Keep edits localized and consult `docs/ui-rules.md` for behavior that must not regress.

## Local Generated Data

- `downloads/`: generated Vision packages and workspace cleanup logs.
- `data/input/`: local OCR text samples.
- `data/output/`: parser JSON outputs.

These folders are ignored except for `.gitkeep` placeholders.

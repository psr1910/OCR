# OCR Parser UI Rules

## Workspace Control

- Canonical local workspace: `C:\Users\user\Documents\My Works\OCR`.
- Runtime downloads for Codex Vision packages belong under `C:\Users\user\Documents\My Works\OCR\downloads`.
- Do not keep, recreate, or use `C:\Users\user\Documents\OCR` as a secondary workspace.
- Use `tools/remove-legacy-ocr-workspace.ps1` to delete the legacy path safely after closing any process that locks it. The script compares file hashes before removal and refuses to delete if the workspaces differ.
- Git commit, push, and deployment actions are performed only when the user explicitly asks for Git reflection or deployment.

## Layout Balance

- The markdown editor is the primary work area. It should be wider than the image preview.
- The app should use nearly the full viewport, not a centered narrow page.
- The page shell must not grow taller than the viewport during normal desktop tool use.
- Overflow belongs inside work panels, not on the document body.
- Default desktop app width: 100% minus 24px page gutters.
- Default desktop split: source image 36%, markdown workspace 64%.
- The source image preview is for verification, not full-screen inspection.
- Image intake controls must stay compact so they do not compete with the preview.
- The markdown quality panel belongs in a right-side inspector, not above the editor.

## Source Preview

- Preview area is a reference pane, not the dominant left-side area.
- Desktop preview target height: 500px.
- Avoid viewport-filling image preview unless the user explicitly requests focus mode.
- Captured Images history should use the extra vertical space on the left side.
- Captured Images history must scroll internally when entries overflow.
- Captured images are independent from Markdown clearing.
- Each captured image must support rerunning OCR back into Markdown and removing the capture from history.
- Captured image item actions belong beside the image metadata, not below the item.
- Captured image action buttons should sit left/right in one row so they do not increase item height.
- Captured image action buttons should use equal compact dimensions, 30px height, and short labels.
- Captured image history must preserve slide order from top to bottom; Slide 1 should stay above later slides.
- Clicking a captured image history item should keep the preview behavior and also jump the Markdown editor to the matching slide block. Match by captureId first; Slide number is only a fallback/display hint.

## Markdown Quality Inspector

- Use detailed inspector cards that show the actual detected value.
- Default inspector width target: 300px.
- Validate accumulated markdown at the slide-block level, not only at the whole-document level.
- Markdown slide blocks must be inserted in ascending slide order, even when multiple OCR jobs complete at different times.
- New Markdown output must use the department heading `# [개발품질그룹]` by default, with Report Type, Source(PPT url), Method, and Status fields.
- New Markdown output must use the English slide header format `### ■ Slide N`.
- Legacy Korean slide headers may be parsed for compatibility, but the UI and new generated Markdown should display `Slide`.
- Known encoding-damaged fixed templates such as `# [媛쒕컻?덉쭏洹몃９]` and `### ??Slide N` must be repaired back to `# [개발품질그룹]` and `### ■ Slide N` before validation, Codex prompt copy, HTML handoff, or final download. Do not apply broad OCR-body character guessing.
- The document header is global, but slide identifiers and required slide content are per-slide checks.
- The final gate passes only when the global header passes and every parsed slide block passes required checks.
- The summary card is the only validation area that carries the pass/fail container treatment and it must wrap the child rule cards.
- The summary card border color stays fixed; only the top color bar changes between PASS and FAIL.
- Empty/default inspector state should be STANDBY, not FAIL.
- Do not show missing-rule repair messages in STANDBY.
- In STANDBY, use the same card structure as the loaded validation state. Keep child rule cards, value blocks, and repair inputs visible; only the status text stays STANDBY/CHECK.
- The Markdown quality summary card must size to its content, not stretch to fill the sidebar height. Extra vertical room stays blank below the card; overflow continues to scroll in the validation area.
- Do not use colored bars on individual rule cards.
- Required rule cards should use a simple `*` mark beside the title, not a red card treatment.
- The inspector header should keep `MD 품질 점검` and `*는 필수 규칙입니다.` on one line, with the required-rule note right aligned.
- The inspector should read as both an alert area and a workspace: the summary card reports state, and child rule cards expose the repair targets/actions.
- Do not combine colored bars, colored backgrounds, blinking, and multiple text colors in one card.
- Content insets should be consistent across working areas: the left image preview surface and the right Markdown quality validation area both use a 10px parent-to-card inset.
- Required missing fields must block markdown download.
- Users must be able to manually enter missing values and apply them back into the markdown.
- Avoid blinking warnings. Warnings should be visible without visual noise.
- The final gate status belongs at the top of the Markdown quality inspector as a summary card representing the child rule group, not as a detached badge.
- The inspector should use the same enterprise panel language as the rest of the app: white cards, thin borders, subtle shadows, restrained typography.
- The Status divider and child card layout must not change between STANDBY and loaded validation state.
- Rule cards should show a compact PASS/FAIL state pill, the detected value, and the manual repair action in that order.
- Rule card order and labels should be short English function names: Header, Source(PPT url), Metadata.
- Rule cards should use PASS/FAIL/CHECK as the only visible status labels. Do not add duplicate OK/Missing labels inside slide rows.
- Header quality checks and handoff filenames must use the first Markdown heading bracket text, e.g. `# [개발품질그룹]`.
- Header repair controls manage three independent lines: Department updates the first heading bracket `# [Department]`, Report Type updates `**Report Type:**`, and Failure Mode updates `**Failure Mode:**`.
- Department defaults to `개발품질그룹`.
- Report Type is a separate metadata field again and defaults to `Reliability Failure Report`.
- Reliability failure report metadata is required for final Markdown: `Report Type`, `Product`, `Project`, `Failure Mode`, `Test Type`, `Occurrence Date`, `Author`, `Method`, and `Status`.
- Do not show `Confirm` as a separate quality rule card. Confirm is the required value of `Metadata > Status`, so the Metadata card should display and validate it.
- `Source(PPT url)` is the second independent quality card, not an editor nested under Header, and it is a required rule.
- The Source card updates only the global Markdown metadata line `**Source(PPT url):**`.
- The Source card input placeholder should read `PPT EDM url`.
- `Source(PPT url)` is required metadata for the original PPT file name or PPT EDM URL. Use `TBD` as the default placeholder, and block final download while it is still `TBD`.
- Do not generate or require a separate `**Source:**` metadata line. Source handling belongs only to the `Source(PPT url)` card.
- The Metadata card must not show source fields because source handling is managed by the separate Source card.
- The Metadata card must not show Status as body text. Document status belongs in the Status summary card's top-right pill as Review or Confirm.
- The Metadata card must not show Method as an editable field. Method is a system/finalization field managed by the OCR parser and Codex refinement step.
- Metadata fields editable inside the Metadata card are Product, Project, Test Type, Occurrence Date, and Author, with one input and one compact Apply button per field.
- Method remains in the Markdown metadata, but Confirm output must keep only the final adopted extraction/correction method. Review drafts may contain multiple OCR passes or candidates, but unselected candidates must not remain in the final Method field.
- Manual repair Apply actions must preserve the Markdown editor scroll position. Applying Header, Source, Metadata, or Table changes must not jump the editor to the bottom.
- Download Markdown must remain locked unless Status is `Confirm`. `Review` is treated as a draft/intermediate state and must not be downloadable as final `.md`.
- Table quality checking is not required. Remove the Table quality card; table creation is a manual toolbar action only.
- Manual Markdown tables should use `| Item | Value | Status |`.
- Manual Slide creation, renaming, and deletion controls are removed. OCR-generated slides with capture-id comments are the only trusted slide blocks because Vision handoff matches captured images by captureId, not by user-edited slide numbers.

## Controls

- `자동 파싱` means PPT file automation: the user selects a `.ppt`, `.pptx`, or `.pptm` file, the local parser service exports each slide as an image, and the browser app enqueues those slide images into the existing OCR flow in slide order.
- Clipboard image reading is only a fallback intake path. Do not define `자동 파싱` as clipboard-only behavior.
- The app must be launched through `start_ocr_app.cmd` or `start_ocr_app.ps1`, which starts the local parser service at `http://127.0.0.1:8765` and opens the parser UI from that same service URL.
- The local parser service should run in a visible terminal window. Users must keep that window open while using save or PPT automation features.
- Save and PPT automation testing must use `http://127.0.0.1:8765/`, not `file:///.../index.html`.
- If the browser reports connection refused, the local parser service is not running or its terminal window was closed; relaunch with `start_ocr_app.cmd`.
- The UI must monitor the local parser service health and show helper availability with a compact checkbox treatment matching the Codex export check style.
- The helper checkbox is a read-only service state indicator: checked only when `http://127.0.0.1:8765/health` is reachable, unchecked when it is offline.
- The Status card should place the helper checkbox and compact `Helper` button in the top-right corner of the card, separate from the glossary metadata line so long glossary filenames cannot overlap it.
- The `Helper` button must not copy commands. It checks helper health first; when offline, it calls the registered local protocol `ocr-parser://launch` and then polls health again.
- GitHub Pages can launch the helper only after the local protocol has been registered once with `tools/register-ocr-protocol.ps1`.
- Helper guidance belongs behind a compact `?` guide button beside `Helper`, not inside the main status text and not as an automatic popup on every Helper launch.
- The helper guide popup must be written in Korean for end users and explain the exact order: download `OCR_Helper_Setup.zip`, unzip it, run `install_helper_protocol.cmd` once, return to the page, press `Helper`, keep the local parser window open, and read the checkbox state.
- The helper guide popup should include a direct download link for `OCR_Helper_Setup.zip`.
- PPT automation requires the local parser service; if it is unavailable, the UI must show a clear status message and keep paste/drop/select image intake available.
- Header and Slide insertion controls are not shown in the Markdown output toolbar. Header metadata is repaired from the quality inspector, and slides are created only by OCR capture.
- Table insertion belongs in the Markdown output toolbar for manual supplemental data. It inserts at the editor cursor and does not create, select, rename, or delete slide blocks.
- Markdown copy handoff belongs in the Codex card, not the Markdown output toolbar.
- Do not duplicate global Markdown action buttons inside the quality inspector.
- Markdown output toolbar buttons should look actionable with subtle shadow, restrained hover lift, and consistent weight.
- Markdown output toolbar hover should stay restrained: use a subtle slate border/background lift, not strong blue emphasis.
- Panel header action buttons, including `자동 파싱`, must use the same neutral button treatment and hover behavior as Markdown output toolbar utility buttons.
- Panel header action labels must keep enough horizontal breathing room from their buttons; do not place label text tightly against the action button.
- Button transitions are global: border, text color, background, shadow, transform, and opacity use the same short easing.
- Codex card buttons must use the same restrained hover behavior as the rest of the app: no strong blue hover state, only subtle slate lift/background.
- Helper card buttons, including the compact `?` guide button, use the same restrained hover group as Codex card buttons; do not create a separate helper-only hover treatment.
- Button purpose styles are shared: primary for final/save actions, secondary for neutral utility actions, danger for destructive removal actions, compact for small repeated list actions.
- In rule repair rows, Apply should keep a consistent 58px width and 28px height across Header, Metadata, and Source rules.
- Markdown quality inspector repair buttons should be lower than main toolbar buttons, using a compact 28px height.
- Markdown quality inspector inputs should use 11px text, keep the existing text color, and use restrained placeholder styling so fields blend into the card rather than dominating it.
- Disabled buttons must look inactive. They should not change border, color, background, shadow, or transform on hover or active states.
- Codex correction handoff is always HTML-package based. Do not split the UI by Codex access.
- The Codex card keeps a fixed checked checkbox as a visual signal and one action button labeled `Codex 보정 보내기`.
- The single Codex action saves one HTML Vision Package containing Markdown, manifest, glossary context, and captured images.
- The Codex card should show a small `Save path` button before the send button, not a long inline path label.
- The `Save path` button stays disabled until a Codex Vision Package is successfully saved through the local parser service. After success, it asks the local parser service to open `C:\Users\user\Documents\My Works\OCR\downloads` directly in Explorer.
- Clearing Markdown resets `Save path` to disabled so users do not mistake the path button for a new successful save.
- Codex Vision Package save is considered successful only when the local parser service at `http://127.0.0.1:8765` writes the HTML file directly to `C:\Users\user\Documents\My Works\OCR\downloads`.
- Do not report browser download fallback or File System Access picker fallback as a successful Codex package save to the managed downloads folder.
- If the local parser service is unavailable, show a clear error telling the user to launch the system with `start_ocr_app.cmd`; do not pretend the HTML package was saved.
- A Codex Vision Package must contain at least one captured slide image. If captured images are missing or markdown capture ids cannot be matched to embedded images, block package saving and show an error instead of creating a text-only package.
- OCR completion prepares the accumulated Markdown for that HTML Codex handoff.
- Do not auto-copy after async OCR; browser clipboard permission can reject non-click writes.
- The HTML package prompt should use the full accumulated Markdown refinement prompt first, and fall back to the latest raw OCR prompt only when no Markdown exists.
- The HTML package prompt must keep explicit RAG refinement rules even when images are available: preserve source evidence, avoid guessing, convert visible tables/flows, enforce glossary terms, verify image manifest, and output Markdown only.
- Plain text fallback and clipboard copy are not the primary flow. The saved HTML Vision Package is the authoritative handoff because some receiving chat surfaces preserve only one pasted image.
- The prompt should recommend a near-0.0 temperature when that setting is available.
- Codex cleanup prompts must preserve the original language mix. Do not force Korean, English, Chinese characters, abbreviations, product names, model names, test names, proper nouns, or technical terms into one language.
- Codex cleanup prompts should correct only unambiguous OCR errors and preserve uncertain text rather than guessing or translating.
- Codex cleanup prompts must instruct Codex to change document metadata Status from `Review` to `Confirm` in the refined output.
- OCR should run a local multi-pipeline A/B/C pass when possible: Engine A grayscale, Engine B binary threshold, and Engine C inverted high contrast. The parser may score the three results with glossary keywords only when a `quality_team_glossary_YYMMDD.md` or `quality_team_glossary.md` file is loaded. Do not hardcode example keywords into scoring.
- When no glossary file is loaded, keyword scoring must be skipped; the parser may still use neutral fallback signals such as OCR noise and text preservation to choose one OCR context.
- Codex cleanup prompts must be Vision-first: include parser-captured slide images in the saved HTML package, treat those images as the primary source, and use the selected OCR text only as supporting context.
- For multiple captured slides, the app copies one combined Vision package containing the Markdown draft plus all captured images ordered by captureId-backed slide order.
- If a chat surface cannot read pasted rich images or the exported HTML package, the prompt should tell Codex to report image ingestion failure rather than silently relying on OCR text only.
- Every Vision package must include an explicit image manifest with expected image count and expected Slide list. Codex instructions must require verifying this manifest before refinement; if any expected image is missing or unreadable, the only valid output is `IMAGE_INGESTION_FAILED` plus missing Slide number(s).
- Slide number is not a stable image identity. Every captured image must receive a unique `captureId`, and OCR-generated Markdown slide blocks must embed that id as `<!-- capture-id: ... -->`. Vision package image matching must use captureId first, with Slide number only as a display/order hint.
- The draft Method should describe the scoring and Vision handoff path, e.g. `Client-side Tesseract OCR scoring (kor+eng, A/B/C) + Codex Vision review`.
- Do not add local captured-image trace comments or `Source(PPT url)` lines to new slide Markdown. Source is global metadata only because per-slide source duplication is noisy and can become inconsistent.
- If `quality_team_glossary.md` exists beside `index.html`, Codex prompts must include it as an authoritative Quality Team Glossary section. Matching From/synonym/slang/OCR-typo terms should be force-replaced with the specified To term and exact capitalization.
- Versioned glossary files such as `quality_team_glossary_260628.md` are preferred. The app should try recent dated glossary files first, then fall back to `quality_team_glossary.md`.
- The Status card should show a compact glossary line below the main status: `Glossary: none` when no file is loaded, or `Glossary: <filename>` when a glossary file is loaded.
- The glossary line belongs to the bottom row of the Status card and must not move when status/error text changes. Reserve a fixed message area above it and clamp long status messages.
- Status/error text inside the fixed message area should be top-aligned, not vertically centered.
- If `quality_team_glossary.md` is missing or blocked by the browser, continue with the normal Codex prompt without showing a blocking error.
- All users use the same handoff path: generate a `.html` Codex Vision package containing the refinement prompt, current draft, and captured images, not a `.md` file, so draft requests are not confused with completed RAG Markdown.
- HTML handoff filenames should use the document header name from the first Markdown line's bracket text, e.g. `# [개발품질그룹]` -> `개발품질그룹_codex_vision_package_YYMMDD_HHMMSS.html`. Replace whitespace with underscores.
- Empty Codex handoff actions should use the same status message: `OCR or Markdown is required.`
- Status and error messages shown in the status card must be English only. Do not mix Korean in runtime error/status messages.
- The browser app cannot directly reuse a user's Codex product session or entitlement.
- Do not show Gateway, model, token, or Run OCR controls unless a real internal gateway feature is reintroduced.
- Download remains disabled until all required markdown checks pass.
- Download disabled state should explain STANDBY versus rule-lock conditions without showing repair errors in STANDBY.

## Visual Style

- Keep a restrained enterprise dashboard tone.
- Use consistent 6-8px radii, 1px borders, and slate/blue accents.
- Text hierarchy should be consistent: 16px panel headings, 13-14px controls, 12px metadata.
- Footer ownership metadata should use the same footnote style as the existing privacy/runtime note and align to the far right on desktop.
- Do not make new floating decorative sections.
- Prefer dense, scan-friendly panels over large empty areas.

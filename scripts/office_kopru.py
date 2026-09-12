#!/usr/bin/env python3
"""office_kopru.py — Microsoft Office (PowerPoint / Word) bridge through PowerShell COM.

Plugin-root script owned by no skill; called by journalsunum-s-pptx, journalsunum-s-poster,
journalstyle and journal-s-zotero. Needs no pip package: the COM work runs inside Windows
PowerShell 5.1, sent as an -EncodedCommand (no .ps1 on disk).

Subcommands (one JSON object on stdout, exit 0 / 1 / 2):
  probe   [--app powerpoint|word]                      is the app there, which version
  check   <file> [--out-dir DIR]                       open invisible + read-only, structural facts
  render  <file> [--out-dir DIR] [--width N] [--cols N] [--per-sheet N]
                                                       PNG per slide (or page) + labelled grid jpg(s)
  pdf     <file> [--out PATH] [--force]                PDF beside the file (PowerPoint SaveAs / Word Export)
  open    <file> [--pane designer|accessibility|none] [--slide N]
                                                       VISIBLE hand-off, leaves the app open
  fields  <file> [--update] [--out PATH]               Word only: ADDIN field census (ZOTERO_*)
  hunt    --app powerpoint|word [--out-dir DIR]        capture every visible top-level window (modal)
  close   --pid N                                      close a window/pid this bridge started

Exit 2 = {"error": "no_office"} (ProgID missing / not Windows) — the plugin's no_zotero contract.
Exit 1 = modal_detected | timeout | com_error | unsafe_input | bad_args.

Process hygiene: PowerPoint is single-instance — New-Object attaches to a running user
instance — so `owned_instance` is decided from Get-Process BEFORE the COM call, and a
non-owned instance is never Quit (only the presentation the bridge opened is closed).
DisplayAlerts is never touched unless --quiet-alerts is given, and then the JSON says so.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import time
import zipfile
from pathlib import Path

# ---------------------------------------------------------------- constants (no pywin32)
MSO_TRUE = -1
MSO_FALSE = 0
PP_SAVEAS_PDF = 32            # PpSaveAsFileType.ppSaveAsPDF
WD_EXPORT_FORMAT_PDF = 17     # WdExportFormat.wdExportFormatPDF
WD_EXPORT_OPTIMIZE_PRINT = 0  # WdExportOptimizeFor.wdExportOptimizeForPrint
WD_FIELD_ADDIN = 81           # WdFieldType.wdFieldAddin
WD_FORMAT_XML_DOCUMENT = 16   # WdSaveFormat.wdFormatXMLDocument
WD_STAT_PAGES = 2             # WdStatistic.wdStatisticPages

APPS = {
    "powerpoint": {"progid": "PowerPoint.Application", "process": "POWERPNT"},
    "word": {"progid": "Word.Application", "process": "WINWORD"},
}
EXT_APP = {
    ".pptx": "powerpoint", ".potx": "powerpoint", ".ppsx": "powerpoint", ".ppt": "powerpoint",
    ".docx": "word", ".docm": "word", ".doc": "word", ".dotx": "word",
}
PANE_IDS = {
    # Verified on this machine 2026-09-12 (PowerPoint 16.0.20326): GetEnabledMso('DesignerPane')
    # = True; 'DesignIdeas' and 'DesignIdeasPane' raise "value out of range".
    "designer": ["DesignerPane", "DesignIdeas", "DesignIdeasPane"],
    "accessibility": ["AccessibilityChecker"],
    "none": [],
}
STATE_FILE = ".office_kopru_last.json"
MAX_FILE_BYTES = 512 * 1024 * 1024


# ---------------------------------------------------------------- output helpers
def _utf8_stdout() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def emit(payload: dict, code: int = 0) -> int:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    sys.stdout.flush()
    return code


def fail(error: str, code: int = 1, **extra) -> int:
    payload = {"error": error}
    payload.update(extra)
    return emit(payload, code)


# ---------------------------------------------------------------- input safety (copied from
# journalsunum_ortak.checked_input_file — deliberately NOT imported: a plugin-root script
# depends on no skill)
def checked_input_file(raw: str) -> Path:
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = Path.cwd() / path
    path = path.resolve(strict=False)
    if path.is_symlink():
        raise ValueError(f"symlink refused: {path}")
    if not path.is_file():
        raise ValueError(f"not a regular file: {path}")
    size = path.stat().st_size
    if size == 0 or size > MAX_FILE_BYTES:
        raise ValueError(f"file size out of bounds ({size} bytes): {path}")
    if path.suffix.lower() not in EXT_APP:
        raise ValueError(f"unsupported extension: {path.suffix}")
    return path


def app_for(path: Path | None, override: str | None) -> str:
    if override:
        return override
    if path is None:
        raise ValueError("--app required without a file")
    return EXT_APP[path.suffix.lower()]


def under_input_dir(path: Path) -> bool:
    return "input" in {p.lower() for p in path.parts[:-1]}


# ---------------------------------------------------------------- office presence (winreg,
# before any PowerShell is spawned)
def office_present(app: str) -> tuple[bool, str]:
    if os.name != "nt":
        return False, "not Windows"
    import winreg  # noqa: PLC0415 — Windows only

    key = f"{APPS[app]['progid']}\\CLSID"
    try:
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, key):
            return True, f"HKCR\\{key}"
    except OSError:
        return False, f"HKCR\\{key}"


# ---------------------------------------------------------------- PowerShell runner
def ps_quote(s: str) -> str:
    return "'" + str(s).replace("'", "''") + "'"


PROLOGUE = r"""
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = 'Stop'
$t0 = Get-Date
$procName = __PROC__
$pre = @(Get-Process $procName -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id)
$owned = ($pre.Count -eq 0)
$R = [ordered]@{ ok = $false; app = __PROGID__; owned_instance = $owned; pre_pids = @($pre) }
function Emit { param($obj, $code)
  $obj.post_pids = @(Get-Process $procName -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id)
  $obj.elapsed_s = [math]::Round(((Get-Date) - $t0).TotalSeconds, 2)
  Write-Output ('JSON:' + ($obj | ConvertTo-Json -Compress -Depth 8))
  exit $code
}
try { $app = New-Object -ComObject __PROGID__ } catch {
  $R.error = 'com_error'; $R.message = $_.Exception.Message; Emit $R 1
}
$R.app_version = [string]$app.Version
"""

EPILOGUE_INVISIBLE = r"""
if ($doc -ne $null) { try { $doc.Close(__CLOSE_ARG__) } catch { $R.close_error = $_.Exception.Message } }
if ($owned) { try { $app.Quit() } catch { $R.quit_error = $_.Exception.Message } }
[void][Runtime.InteropServices.Marshal]::ReleaseComObject($app)
[GC]::Collect(); [GC]::WaitForPendingFinalizers()
Start-Sleep -Milliseconds 400
$R.ok = ($R.error -eq $null)
Emit $R $(if ($R.ok) { 0 } else { 1 })
"""


def run_ps(script: str, timeout: float) -> tuple[dict | None, str, int, bool]:
    """Returns (json_or_None, raw_output, returncode, timed_out)."""
    encoded = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
    cmd = ["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
           "-EncodedCommand", encoded]
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        out = (exc.stdout or b"").decode("utf-8", "replace")
        return None, out, -1, True
    except FileNotFoundError:
        return None, "powershell.exe not found", -2, False
    out = proc.stdout.decode("utf-8", "replace") + proc.stderr.decode("utf-8", "replace")
    result = None
    for line in reversed(out.splitlines()):
        if line.startswith("JSON:"):
            try:
                result = json.loads(line[5:])
            except json.JSONDecodeError:
                result = None
            break
    return result, out, proc.returncode, False


CATCH = r"""
} catch {
  $R.error = 'com_error'; $R.message = $_.Exception.Message
  $R.at_line = $_.InvocationInfo.ScriptLineNumber
  __ON_ERROR__
}
"""


def build(app: str, body: str, close_arg: str = "", handoff: bool = False, **tokens) -> str:
    # Every COM call runs inside one try: a thrown HRESULT (a file PowerPoint refuses, a
    # locked document) must still reach the epilogue (close / quit / JSON), never die as
    # CLIXML noise on stderr.
    on_error = "Emit $R 1" if handoff else ""
    script = (PROLOGUE + "\n$doc = $null\ntry {\n" + body + CATCH.replace("__ON_ERROR__", on_error)
              + ("" if handoff else EPILOGUE_INVISIBLE))
    tokens.setdefault("PROC", ps_quote(APPS[app]["process"]))
    tokens.setdefault("PROGID", ps_quote(APPS[app]["progid"]))
    tokens.setdefault("CLOSE_ARG", close_arg)
    for key, value in tokens.items():
        script = script.replace(f"__{key}__", str(value))
    return script


def finish(app: str, result: dict | None, raw: str, rc: int, timed_out: bool,
           out_dir: Path | None, stem: str, kill_on_modal: bool) -> int:
    """Common post-processing: timeout → hunt, missing JSON → com_error."""
    if timed_out:
        hunt = do_hunt(app, out_dir, stem, kill=kill_on_modal)
        if hunt.get("windows"):
            return fail("modal_detected", app=app, modal_png=[w["png"] for w in hunt["windows"]],
                        windows=hunt["windows"], killed=hunt.get("killed", []))
        return fail("timeout", app=app, windows=[], hint="no visible window found; raise --timeout")
    if result is None:
        return fail("com_error", app=app, returncode=rc, output=raw[-2000:])
    if result.get("error"):
        return emit(result, 1)
    return emit(result, 0)


# ---------------------------------------------------------------- zip/xml font census
def fonts_from_package(path: Path) -> list[str]:
    pattern = re.compile(r'(?:typeface|w:ascii|w:hAnsi)="([^"]+)"')
    fonts: set[str] = set()
    try:
        with zipfile.ZipFile(path) as zf:
            for name in zf.namelist():
                if not name.endswith(".xml"):
                    continue
                # Slide/body XML only: the theme's font scheme lists dozens of script fonts
                # that never render, and fontTable.xml is a declaration, not a use.
                if not (name.startswith("ppt/slides/slide") or name in ("word/document.xml", "word/styles.xml")):
                    continue
                if zf.getinfo(name).file_size > 20 * 1024 * 1024:
                    continue
                text = zf.read(name).decode("utf-8", "replace")
                for m in pattern.finditer(text):
                    face = m.group(1)
                    if face.startswith("+"):  # theme placeholders (+mn-lt, +mj-lt)
                        continue
                    fonts.add(face)
    except (zipfile.BadZipFile, OSError):
        return []
    return sorted(fonts)


def ps_font_list(fonts: list[str]) -> str:
    return "@(" + ",".join(ps_quote(f) for f in fonts) + ")"


# ---------------------------------------------------------------- subcommand: probe
def cmd_probe(args) -> int:
    app = args.app or "powerpoint"
    present, probed = office_present(app)
    if not present:
        return fail("no_office", 2, app=APPS[app]["progid"], probed=probed)
    body = "\n$doc = $null\n"
    script = build(app, body)
    result, raw, rc, timed_out = run_ps(script, args.timeout)
    if result is not None and not result.get("error"):
        result["quit"] = bool(result.get("owned_instance"))
    return finish(app, result, raw, rc, timed_out, None, "probe", args.kill_on_modal)


# ---------------------------------------------------------------- subcommand: check
CHECK_PPT = r"""
if (__QUIET__) { $app.DisplayAlerts = 1; $R.display_alerts_suppressed = $true }
$doc = $app.Presentations.Open(__PATH__, -1, 0, 0)
$R.file = __PATH__
$R.opened_readonly = $true
$R.repair_prompt = $false
$R.protected_view = ($app.ProtectedViewWindows.Count -gt 0)
$R.slide_count = $doc.Slides.Count
$R.slide_size_in = @{ w = [math]::Round($doc.PageSetup.SlideWidth / 72, 2); h = [math]::Round($doc.PageSetup.SlideHeight / 72, 2) }
$withNotes = 0
foreach ($s in $doc.Slides) {
  try { $t = $s.NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text } catch { $t = '' }
  if ($t.Trim().Length -gt 0) { $withNotes++ }
}
$R.has_notes = "$withNotes/$($doc.Slides.Count)"
$R.final = [bool]$doc.Final
Add-Type -AssemblyName System.Drawing
$installed = (New-Object System.Drawing.Text.InstalledFontCollection).Families | ForEach-Object { $_.Name }
$used = __FONTS__
$R.fonts_used = @($used)
$R.fonts_missing = @($used | Where-Object { $installed -notcontains $_ })
"""

CHECK_WORD = r"""
$app.Visible = $false
if (__QUIET__) { $app.DisplayAlerts = 0; $R.display_alerts_suppressed = $true }
$doc = $app.Documents.Open(__PATH__, $false, $true, $false)
$R.file = __PATH__
$R.opened_readonly = $true
$R.repair_prompt = $false
$R.protected_view = ($app.ProtectedViewWindows.Count -gt 0)
$R.page_count = $doc.ComputeStatistics(2)
$R.page_size_in = @{ w = [math]::Round($doc.PageSetup.PageWidth / 72, 2); h = [math]::Round($doc.PageSetup.PageHeight / 72, 2) }
$R.compat_mode = $doc.CompatibilityMode
$R.final = [bool]$doc.Final
$R.read_only = [bool]$doc.ReadOnly
$R.fields_total = $doc.Fields.Count
Add-Type -AssemblyName System.Drawing
$installed = (New-Object System.Drawing.Text.InstalledFontCollection).Families | ForEach-Object { $_.Name }
$used = __FONTS__
$R.fonts_used = @($used)
$R.fonts_missing = @($used | Where-Object { $installed -notcontains $_ })
"""


def cmd_check(args) -> int:
    try:
        path = checked_input_file(args.file)
        app = app_for(path, args.app)
    except ValueError as exc:
        return fail("unsafe_input", message=str(exc))
    present, probed = office_present(app)
    if not present:
        return fail("no_office", 2, app=APPS[app]["progid"], probed=probed)
    fonts = fonts_from_package(path)
    body = CHECK_PPT if app == "powerpoint" else CHECK_WORD
    script = build(app, body, close_arg="" if app == "powerpoint" else "0",
                   PATH=ps_quote(str(path)), FONTS=ps_font_list(fonts),
                   QUIET="$true" if args.quiet_alerts else "$false")
    result, raw, rc, timed_out = run_ps(script, args.timeout)
    out_dir = Path(args.out_dir) if args.out_dir else path.parent
    return finish(app, result, raw, rc, timed_out, out_dir, path.stem, args.kill_on_modal)


# ---------------------------------------------------------------- subcommand: render
RENDER_PPT = r"""
if (__QUIET__) { $app.DisplayAlerts = 1; $R.display_alerts_suppressed = $true }
$doc = $app.Presentations.Open(__PATH__, -1, 0, 0)
$R.file = __PATH__
$W = __WIDTH__
$H = [int]([math]::Round($W * $doc.PageSetup.SlideHeight / $doc.PageSetup.SlideWidth))
$R.width_px = $W; $R.height_px = $H
$R.slide_count = $doc.Slides.Count
$pngs = @()
$i = 0
foreach ($s in $doc.Slides) {
  $i++
  $png = Join-Path __OUTDIR__ (__STEM__ + '-s' + $i.ToString('00') + '.png')
  $s.Export($png, 'PNG', $W, $H)
  $pngs += $png
}
$R.pngs = @($pngs)
$R.backend = 'powerpoint'
"""


def make_grid(pngs: list[str], out_dir: Path, stem: str, cols: int, per_sheet: int,
              labels: list[str] | None = None) -> tuple[list[str], list[str]]:
    """Contact sheet(s) with Pillow. Returns (grid paths, warnings)."""
    warnings: list[str] = []
    try:
        from PIL import Image, ImageDraw, ImageFont  # noqa: PLC0415
    except ImportError:
        return [], ["Pillow not installed: per-slide PNGs written, no grid"]
    grids: list[str] = []
    sheets = [pngs[i:i + per_sheet] for i in range(0, len(pngs), per_sheet)] or [[]]
    try:
        font = ImageFont.truetype("arial.ttf", 22)
    except OSError:
        font = ImageFont.load_default()
    thumb_w = 640
    for n, sheet in enumerate(sheets, start=1):
        if not sheet:
            continue
        images = []
        for p in sheet:
            try:
                im = Image.open(p).convert("RGB")
            except OSError as exc:
                warnings.append(f"{p}: {exc}")
                continue
            ratio = thumb_w / im.width
            images.append(im.resize((thumb_w, max(1, int(im.height * ratio)))))
        if not images:
            continue
        thumb_h = max(im.height for im in images)
        label_h = 34
        pad = 16
        rows = (len(images) + cols - 1) // cols
        sheet_img = Image.new("RGB", (cols * (thumb_w + pad) + pad, rows * (thumb_h + label_h + pad) + pad),
                              (245, 245, 245))
        draw = ImageDraw.Draw(sheet_img)
        for idx, im in enumerate(images):
            r, c = divmod(idx, cols)
            x = pad + c * (thumb_w + pad)
            y = pad + r * (thumb_h + label_h + pad)
            global_idx = (n - 1) * per_sheet + idx
            text = labels[global_idx] if labels and global_idx < len(labels) else f"slide {global_idx + 1}"
            draw.text((x, y), text, fill=(20, 20, 20), font=font)
            sheet_img.paste(im, (x, y + label_h))
            draw.rectangle([x - 1, y + label_h - 1, x + im.width, y + label_h + im.height], outline=(160, 160, 160))
        name = f"{stem}-grid.jpg" if len(sheets) == 1 else f"{stem}-grid-{n}.jpg"
        target = out_dir / name
        sheet_img.save(target, "JPEG", quality=85)
        grids.append(str(target))
    return grids, warnings


def png_sizes(pngs: list[str]) -> list[dict]:
    try:
        from PIL import Image  # noqa: PLC0415
    except ImportError:
        return []
    sizes = []
    for p in pngs:
        try:
            with Image.open(p) as im:
                sizes.append({"png": p, "w": im.width, "h": im.height})
        except OSError:
            sizes.append({"png": p, "error": "unreadable"})
    return sizes


def cmd_render(args) -> int:
    try:
        path = checked_input_file(args.file)
        app = app_for(path, args.app)
    except ValueError as exc:
        return fail("unsafe_input", message=str(exc))
    present, probed = office_present(app)
    if not present:
        return fail("no_office", 2, app=APPS[app]["progid"], probed=probed)
    out_dir = Path(args.out_dir).resolve() if args.out_dir else path.parent
    if under_input_dir(path) and out_dir == path.parent:
        return fail("unsafe_input", message="file is under input/; pass --out-dir outside it")
    out_dir.mkdir(parents=True, exist_ok=True)
    stem = path.stem
    if app == "powerpoint":
        script = build(app, RENDER_PPT, PATH=ps_quote(str(path)), OUTDIR=ps_quote(str(out_dir)),
                       STEM=ps_quote(stem), WIDTH=int(args.width),
                       QUIET="$true" if args.quiet_alerts else "$false")
        result, raw, rc, timed_out = run_ps(script, args.timeout)
        if timed_out or result is None or result.get("error"):
            return finish(app, result, raw, rc, timed_out, out_dir, stem, args.kill_on_modal)
        pngs = list(result.get("pngs") or [])
    else:
        # Word: PDF first, then Poppler rasterises it.
        pdf_path = out_dir / f"{stem}.pdf"
        code = _word_pdf(path, pdf_path, args, force=True, quiet=False)
        if code is not None:
            return code
        pngs = _pdftoppm(pdf_path, out_dir, stem, int(args.width))
        if pngs is None:
            return fail("com_error", app=app, message="pdftoppm not found on PATH; PDF written",
                        pdf=str(pdf_path))
        result = {"ok": True, "app": APPS[app]["progid"], "file": str(path), "pdf": str(pdf_path),
                  "pngs": pngs, "backend": "word+pdftoppm", "width_px": int(args.width)}
    grids, warnings = make_grid(pngs, out_dir, stem, int(args.cols), int(args.per_sheet))
    result["grid"] = grids
    result["png_sizes"] = png_sizes(pngs)
    result["cols"] = int(args.cols)
    result["warnings"] = warnings
    return emit(result, 0)


def _pdftoppm(pdf: Path, out_dir: Path, stem: str, width: int) -> list[str] | None:
    try:
        subprocess.run(["pdftoppm", "-png", "-scale-to-x", str(width), "-scale-to-y", "-1",
                        str(pdf), str(out_dir / f"{stem}-s")], capture_output=True, timeout=180, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return None
    pngs = sorted(str(p) for p in out_dir.glob(f"{stem}-s*.png"))
    return pngs


# ---------------------------------------------------------------- subcommand: pdf
PDF_PPT = r"""
if (__QUIET__) { $app.DisplayAlerts = 1; $R.display_alerts_suppressed = $true }
$doc = $app.Presentations.Open(__PATH__, -1, 0, 0)
$R.file = __PATH__
$doc.SaveCopyAs(__PDF__, 32)
$R.pdf = __PDF__
$R.quality = 'standard'
$R.bytes = (Get-Item __PDF__).Length
"""

PDF_WORD = r"""
$app.Visible = $false
if (__QUIET__) { $app.DisplayAlerts = 0; $R.display_alerts_suppressed = $true }
$doc = $app.Documents.Open(__PATH__, $false, $true, $false)
$R.file = __PATH__
$doc.ExportAsFixedFormat(__PDF__, 17, $false, 0, 0, 1, 1, 0, $true, $true, 1, $true, $true, $false)
$R.pdf = __PDF__
$R.quality = 'print'
$R.bytes = (Get-Item __PDF__).Length
"""


def _pdf_pages(pdf: Path) -> int | None:
    for mod in ("pypdf", "PyPDF2"):
        try:
            lib = __import__(mod)
            return len(lib.PdfReader(str(pdf)).pages)
        except Exception:  # noqa: BLE001 — optional dependency, any failure means "unknown"
            continue
    return None


def _word_pdf(path: Path, pdf_path: Path, args, force: bool, quiet: bool) -> int | None:
    """Runs the Word export. Returns an exit code on failure, None on success."""
    if pdf_path.exists() and not force:
        return fail("unsafe_input", message=f"PDF exists, pass --force: {pdf_path}")
    script = build("word", PDF_WORD, close_arg="0", PATH=ps_quote(str(path)), PDF=ps_quote(str(pdf_path)),
                   QUIET="$true" if quiet else "$false")
    result, raw, rc, timed_out = run_ps(script, args.timeout)
    if timed_out or result is None or result.get("error"):
        return finish("word", result, raw, rc, timed_out, pdf_path.parent, path.stem, args.kill_on_modal)
    return None


def cmd_pdf(args) -> int:
    try:
        path = checked_input_file(args.file)
        app = app_for(path, args.app)
    except ValueError as exc:
        return fail("unsafe_input", message=str(exc))
    present, probed = office_present(app)
    if not present:
        return fail("no_office", 2, app=APPS[app]["progid"], probed=probed)
    pdf_path = Path(args.out).resolve() if args.out else path.with_suffix(".pdf")
    if under_input_dir(pdf_path):
        return fail("unsafe_input", message="refusing to write under input/; pass --out")
    if pdf_path.exists() and not args.force:
        return fail("unsafe_input", message=f"PDF exists, pass --force: {pdf_path}")
    if app == "word":
        code = _word_pdf(path, pdf_path, args, force=True, quiet=args.quiet_alerts)
        if code is not None:
            return code
        result = {"ok": True, "app": APPS[app]["progid"], "file": str(path), "pdf": str(pdf_path),
                  "quality": "print", "bytes": pdf_path.stat().st_size}
    else:
        script = build(app, PDF_PPT, PATH=ps_quote(str(path)), PDF=ps_quote(str(pdf_path)),
                       QUIET="$true" if args.quiet_alerts else "$false")
        result, raw, rc, timed_out = run_ps(script, args.timeout)
        if timed_out or result is None or result.get("error"):
            return finish(app, result, raw, rc, timed_out, pdf_path.parent, path.stem, args.kill_on_modal)
    result["pages"] = _pdf_pages(pdf_path)
    return emit(result, 0)


# ---------------------------------------------------------------- subcommand: open (visible hand-off)
OPEN_PPT = r"""
$app.Visible = -1
$doc = $app.Presentations.Open(__PATH__, 0, 0, -1)
$R.file = __PATH__
$R.visible = $true
try { $app.ActiveWindow.View.GotoSlide(__SLIDE__) } catch { $R.goto_error = $_.Exception.Message }
try { $app.Activate() } catch { }
$R.hwnd = [int64]$app.HWND
$R.pid = $null
foreach ($p in (Get-Process $procName -ErrorAction SilentlyContinue)) { if ($pre -notcontains $p.Id) { $R.pid = $p.Id } }
if ($R.pid -eq $null -and $pre.Count -gt 0) { $R.pid = $pre[0] }
$R.pane = [ordered]@{ requested = __PANEREQ__; probes = @() }
foreach ($id in __PANEIDS__) {
  $pr = [ordered]@{ mso_id = $id }
  try { $pr.enabled = [bool]$app.CommandBars.GetEnabledMso($id) } catch { $pr.enabled = $null; $pr.enabled_error = $_.Exception.Message }
  if ($pr.enabled) {
    try { $app.CommandBars.ExecuteMso($id); $pr.executed = $true } catch { $pr.executed = $false; $pr.error = $_.Exception.Message }
  } else { $pr.executed = $false }
  $R.pane.probes += $pr
  if ($pr.executed) { $R.pane.mso_id = $id; $R.pane.executed = $true; break }
}
if (-not $R.pane.executed) { $R.pane.executed = $false }
$R.left_open = $true
$R.ok = $true
Emit $R 0
"""

OPEN_WORD = r"""
$app.Visible = $true
$doc = $app.Documents.Open(__PATH__, $false, $false, $false)
$R.file = __PATH__
$R.visible = $true
try { $app.Activate() } catch { }
$R.hwnd = $null
$R.pid = $null
foreach ($p in (Get-Process $procName -ErrorAction SilentlyContinue)) { if ($pre -notcontains $p.Id) { $R.pid = $p.Id } }
$R.pane = [ordered]@{ requested = __PANEREQ__; probes = @() }
foreach ($id in __PANEIDS__) {
  $pr = [ordered]@{ mso_id = $id }
  try { $pr.enabled = [bool]$app.CommandBars.GetEnabledMso($id) } catch { $pr.enabled = $null; $pr.enabled_error = $_.Exception.Message }
  if ($pr.enabled) {
    try { $app.CommandBars.ExecuteMso($id); $pr.executed = $true } catch { $pr.executed = $false; $pr.error = $_.Exception.Message }
  } else { $pr.executed = $false }
  $R.pane.probes += $pr
  if ($pr.executed) { $R.pane.mso_id = $id; $R.pane.executed = $true; break }
}
if (-not $R.pane.executed) { $R.pane.executed = $false }
$R.left_open = $true
$R.ok = $true
Emit $R 0
"""


def cmd_open(args) -> int:
    try:
        path = checked_input_file(args.file)
        app = app_for(path, args.app)
    except ValueError as exc:
        return fail("unsafe_input", message=str(exc))
    present, probed = office_present(app)
    if not present:
        return fail("no_office", 2, app=APPS[app]["progid"], probed=probed)
    if args.pane == "designer" and app == "word":
        return fail("bad_args", message="designer pane exists only in PowerPoint")
    ids = PANE_IDS[args.pane]
    body = OPEN_PPT if app == "powerpoint" else OPEN_WORD
    script = build(app, body, handoff=True, PATH=ps_quote(str(path)), SLIDE=int(args.slide),
                   PANEREQ=ps_quote(args.pane), PANEIDS=ps_font_list(ids))
    result, raw, rc, timed_out = run_ps(script, args.timeout)
    out_dir = path.parent
    if timed_out or result is None or result.get("error"):
        return finish(app, result, raw, rc, timed_out, out_dir, path.stem, args.kill_on_modal)
    # Proof of the hand-off: capture the window that carries this file's name (PrintWindow),
    # so the caller can Read it and see whether the requested pane actually appeared.
    if not args.no_proof:
        time.sleep(1.5)
        hunt = do_hunt(app, out_dir, path.stem + "_handoff")
        proof = [w for w in hunt.get("windows", []) if w.get("title", "").lower().startswith(path.stem.lower())]
        result["proof_png"] = proof[0]["png"] if proof else None
        result["windows"] = [{"title": w["title"], "pid": w["pid"]} for w in hunt.get("windows", [])]
    state = {"app": app, "pid": result.get("pid"), "pre_pids": result.get("pre_pids", []),
             "file": str(path), "opened_at": time.time()}
    try:
        (out_dir / STATE_FILE).write_text(json.dumps(state), encoding="utf-8")
        result["state_file"] = str(out_dir / STATE_FILE)
    except OSError as exc:
        result.setdefault("warnings", []).append(f"state file not written: {exc}")
    return emit(result, 0)


# ---------------------------------------------------------------- subcommand: fields (Word)
FIELDS_WORD = r"""
$app.Visible = $false
if (__QUIET__) { $app.DisplayAlerts = 0; $R.display_alerts_suppressed = $true }
$doc = $app.Documents.Open(__PATH__, $false, $true, $false)
$R.file = __PATH__
$R.repair_prompt = $false
$R.fields_total = $doc.Fields.Count
$z = [ordered]@{ ZOTERO_ITEM = 0; ZOTERO_BIBL = 0; ZOTERO_TEMP = 0 }
$foreign = @()
$addin = 0
foreach ($f in $doc.Fields) {
  if ($f.Type -ne 81) { continue }
  $addin++
  $code = $f.Code.Text.Trim()
  if ($code -match '^ADDIN\s+ZOTERO_ITEM') { $z.ZOTERO_ITEM++ }
  elseif ($code -match '^ADDIN\s+ZOTERO_BIBL') { $z.ZOTERO_BIBL++ }
  elseif ($code -match '^ADDIN\s+ZOTERO_TEMP') { $z.ZOTERO_TEMP++ }
  elseif ($foreign.Count -lt 5) { $foreign += ($code.Substring(0, [math]::Min(60, $code.Length))) }
}
$R.addin_total = $addin
$R.zotero = $z
$R.foreign_addin = @($foreign)
$R.zotero_pref_property = $false
foreach ($p in $doc.CustomDocumentProperties) { if ($p.Name -like 'ZOTERO_PREF*') { $R.zotero_pref_property = $true; break } }
$R.updated = $null
if (__UPDATE__) {
  $doc.Close(0); $doc = $null
  $doc2 = $app.Documents.Open(__PATH__, $false, $false, $false)
  $rc = $doc2.Fields.Update()
  $doc2.SaveAs2(__OUT__, 16)
  $doc2.Close(0)
  $R.updated = [ordered]@{ return_code = $rc; out = __OUT__ }
}
"""


def cmd_fields(args) -> int:
    try:
        path = checked_input_file(args.file)
    except ValueError as exc:
        return fail("unsafe_input", message=str(exc))
    if EXT_APP[path.suffix.lower()] != "word":
        return fail("bad_args", message="fields is a Word-only subcommand")
    present, probed = office_present("word")
    if not present:
        return fail("no_office", 2, app=APPS["word"]["progid"], probed=probed)
    if args.update and not args.out:
        return fail("bad_args", message="--update requires --out (the source is never written)")
    out = Path(args.out).resolve() if args.out else None
    if out is not None and (out == path or under_input_dir(out)):
        return fail("unsafe_input", message="--out must be a new file outside input/")
    script = build("word", FIELDS_WORD, close_arg="0", PATH=ps_quote(str(path)),
                   UPDATE="$true" if args.update else "$false",
                   OUT=ps_quote(str(out)) if out else "$null",
                   QUIET="$true" if args.quiet_alerts else "$false")
    result, raw, rc, timed_out = run_ps(script, args.timeout)
    return finish("word", result, raw, rc, timed_out, path.parent, path.stem, args.kill_on_modal)


# ---------------------------------------------------------------- subcommand: hunt (modal capture)
HUNT_PS = r"""
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System; using System.Text; using System.Runtime.InteropServices; using System.Collections.Generic;
public static class WinCap {
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc p, IntPtr l);
  [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr h, int x, int y, int w, int hh, bool rep);
  [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr dc, uint f);
  [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
  public static List<IntPtr> Windows(uint pid) {
    var list = new List<IntPtr>();
    EnumWindows((h, l) => { uint p; GetWindowThreadProcessId(h, out p); if (p == pid && IsWindowVisible(h)) list.Add(h); return true; }, IntPtr.Zero);
    return list;
  }
}
"@
[void][WinCap]::SetProcessDPIAware()   # otherwise GetWindowRect is scaled and the capture is cropped
$procName = __PROC__
$out = @()
$n = 0
foreach ($p in (Get-Process $procName -ErrorAction SilentlyContinue)) {
  foreach ($h in [WinCap]::Windows([uint32]$p.Id)) {
    $sb = New-Object System.Text.StringBuilder 512; [void][WinCap]::GetWindowText($h, $sb, 512)
    $cb = New-Object System.Text.StringBuilder 256; [void][WinCap]::GetClassName($h, $cb, 256)
    $r = New-Object WinCap+RECT; [void][WinCap]::GetWindowRect($h, [ref]$r)
    $w = $r.R - $r.L; $hh = $r.B - $r.T
    if ($w -lt 600) { [void][WinCap]::MoveWindow($h, $r.L, $r.T, 600, [math]::Max($hh, 200), $true); [void][WinCap]::GetWindowRect($h, [ref]$r); $w = $r.R - $r.L; $hh = $r.B - $r.T }
    $png = $null
    if ($w -gt 0 -and $hh -gt 0) {
      $n++
      $png = Join-Path __OUTDIR__ (__STEM__ + '_modal-' + $n + '.png')
      $bmp = New-Object System.Drawing.Bitmap $w, $hh
      $g = [System.Drawing.Graphics]::FromImage($bmp)
      $dc = $g.GetHdc(); [void][WinCap]::PrintWindow($h, $dc, 2); $g.ReleaseHdc($dc)
      $bmp.Save($png, [System.Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $bmp.Dispose()
    }
    $out += [ordered]@{ pid = $p.Id; hwnd = [int64]$h; title = $sb.ToString(); class = $cb.ToString(); w = $w; h = $hh; png = $png }
  }
}
$killed = @()
if (__KILL__) { foreach ($p in (Get-Process $procName -ErrorAction SilentlyContinue)) { if (@(__PREPIDS__) -notcontains $p.Id) { Stop-Process -Id $p.Id -Force; $killed += $p.Id } } }
Write-Output ('JSON:' + ([ordered]@{ ok = $true; windows = @($out); killed = @($killed) } | ConvertTo-Json -Compress -Depth 6))
"""


def do_hunt(app: str, out_dir: Path | None, stem: str, kill: bool = False,
            pre_pids: list[int] | None = None) -> dict:
    out_dir = out_dir or Path.cwd()
    out_dir.mkdir(parents=True, exist_ok=True)
    script = HUNT_PS.replace("__PROC__", ps_quote(APPS[app]["process"])) \
        .replace("__OUTDIR__", ps_quote(str(out_dir))).replace("__STEM__", ps_quote(stem)) \
        .replace("__KILL__", "$true" if kill else "$false") \
        .replace("__PREPIDS__", ",".join(str(p) for p in (pre_pids or [])) or "-1")
    result, raw, rc, timed_out = run_ps(script, 60)
    if result is None:
        return {"ok": False, "windows": [], "error": "hunt_failed", "output": raw[-1000:]}
    return result


def cmd_hunt(args) -> int:
    app = args.app or "powerpoint"
    out_dir = Path(args.out_dir).resolve() if args.out_dir else Path.cwd()
    result = do_hunt(app, out_dir, args.stem or app, kill=args.kill_on_modal)
    result["app"] = app
    return emit(result, 0 if result.get("ok") else 1)


# ---------------------------------------------------------------- subcommand: close
def cmd_close(args) -> int:
    state_path = Path(args.state_dir).resolve() / STATE_FILE if args.state_dir else Path.cwd() / STATE_FILE
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return fail("bad_args", message=f"no state file at {state_path}; close only closes what open started")
    pid = int(args.pid)
    if state.get("pid") != pid:
        return fail("bad_args", message=f"pid {pid} is not the one open recorded ({state.get('pid')})")
    shared = pid in (state.get("pre_pids") or [])  # the user's own instance: close our file, never Quit
    app = state["app"]
    body = r"""
$doc = $null
$R.shared_instance = __SHARED__
$R.open_before = @($app.__COLL__ | ForEach-Object { $_.FullName })
foreach ($p in @($app.__COLL__)) {
  if (($p.FullName -ieq __PATH__) -or ($p.Name -ieq __NAME__)) {
    $full = $p.FullName
    try { $p.Close(__CLOSEARG__); $R.closed_file = $full } catch { $R.close_error = $_.Exception.Message }
  }
}
$remaining = $app.__COLL__.Count
$R.remaining_documents = $remaining
if ($remaining -eq 0 -and -not __SHARED__) { try { $app.Quit(); $R.quit = $true } catch { $R.quit_error = $_.Exception.Message } } else { $R.quit = $false }
[void][Runtime.InteropServices.Marshal]::ReleaseComObject($app)
Start-Sleep -Milliseconds 600
$R.still_running = ((Get-Process -Id __PID__ -ErrorAction SilentlyContinue) -ne $null)
$R.ok = $true
Emit $R 0
"""
    script = build(app, body, handoff=True, COLL="Presentations" if app == "powerpoint" else "Documents",
                   PATH=ps_quote(state["file"]), NAME=ps_quote(Path(state["file"]).name),
                   CLOSEARG="" if app == "powerpoint" else "0", PID=pid,
                   SHARED="$true" if shared else "$false")
    result, raw, rc, timed_out = run_ps(script, args.timeout)
    if timed_out or result is None:
        return finish(app, result, raw, rc, timed_out, state_path.parent, "close", args.kill_on_modal)
    if result.get("closed_file"):
        try:
            state_path.unlink()
        except OSError:
            pass
    return emit(result, 0 if result.get("closed_file") else 1)


# ---------------------------------------------------------------- CLI
def main(argv: list[str] | None = None) -> int:
    _utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--timeout", type=float, default=90.0, help="seconds before the PowerShell child is killed and a modal hunt runs")
    parser.add_argument("--kill-on-modal", action="store_true", help="after a timeout, kill instances the bridge started (never a pre-existing one)")
    parser.add_argument("--quiet-alerts", action="store_true", help="suppress DisplayAlerts (never on a first attempt; echoed in the JSON)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("probe"); p.add_argument("--app", choices=APPS); p.set_defaults(fn=cmd_probe)
    p = sub.add_parser("check"); p.add_argument("file"); p.add_argument("--app", choices=APPS); p.add_argument("--out-dir"); p.set_defaults(fn=cmd_check)
    p = sub.add_parser("render"); p.add_argument("file"); p.add_argument("--app", choices=APPS); p.add_argument("--out-dir")
    p.add_argument("--width", type=int, default=1600); p.add_argument("--cols", type=int, default=3); p.add_argument("--per-sheet", type=int, default=12)
    p.set_defaults(fn=cmd_render)
    p = sub.add_parser("pdf"); p.add_argument("file"); p.add_argument("--app", choices=APPS); p.add_argument("--out"); p.add_argument("--force", action="store_true"); p.set_defaults(fn=cmd_pdf)
    p = sub.add_parser("open"); p.add_argument("file"); p.add_argument("--app", choices=APPS)
    p.add_argument("--pane", choices=PANE_IDS, default="none"); p.add_argument("--slide", type=int, default=1)
    p.add_argument("--no-proof", action="store_true", help="skip the PrintWindow proof capture after opening"); p.set_defaults(fn=cmd_open)
    p = sub.add_parser("fields"); p.add_argument("file"); p.add_argument("--update", action="store_true"); p.add_argument("--out"); p.set_defaults(fn=cmd_fields)
    p = sub.add_parser("hunt"); p.add_argument("--app", choices=APPS, required=True); p.add_argument("--out-dir"); p.add_argument("--stem"); p.set_defaults(fn=cmd_hunt)
    p = sub.add_parser("close"); p.add_argument("--pid", type=int, required=True); p.add_argument("--state-dir", help="folder holding .office_kopru_last.json (default: cwd)"); p.set_defaults(fn=cmd_close)

    args = parser.parse_args(argv)
    if os.name != "nt":
        return fail("no_office", 2, app="any", probed="not Windows")
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())

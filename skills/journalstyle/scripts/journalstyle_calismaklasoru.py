#!/usr/bin/env python3
"""Bir çalışmanın (study) workspace klasörünü çözer ve iskelesini kurar.

Bu script tek doğruluk kaynağıdır: journalstyle, journalwriter ve journalpeerreview skill'leri workspace
yollarını buradan alır (prose'da yol tekrar etmemek için). İki kip vardır (JSON'daki `mode`):

- **plugin-home** (1.17.0): kaynak dosya plugin checkout'unun `input/` klasörü altındaysa
  workspace = checkout kökü; hammadde `input/`, çıktılar `output/`, dergi PDF'leri ve profiller
  `input/yayinstili/` + `input/authorguidelines/`. Kök, plugin-kökü `scripts/hammadde_kokcoz.py`
  ile çözülür (env `JOURNAL_PLUGIN_HOME` → cwd manifesti → `CLAUDE_PLUGIN_ROOT`).
- **docx-folder** (1.16.x davranışı, aynen): kaynak başka bir yerdeyse workspace = kaynak .docx'in
  klasörü; `yayinstili/`, `authorguidelines/`, `ciktilar/` + README iskelesi.

Kullanım:
    python journalstyle_calismaklasoru.py <makale.docx | klasör> [--slug <slug>] [--no-scaffold]

Davranış:
- workspace = verilen .docx'in dizini (dosya) ya da verilen klasörün kendisi; plugin-home kipinde
  checkout kökü. Var olmayan çıplak bir dosya adı `<home>/input/<ad>` olarak da denenir.
- Varsayılan (--scaffold açık): docx-folder kipinde eksik `yayinstili/`, `authorguidelines/`,
  `ciktilar/` klasörlerini ve yoksa bir `README.md` yer tutucuyu; plugin-home kipinde `output/`,
  `input/yayinstili/`, `input/authorguidelines/` klasörlerini (README yok — kökte plugin'in kendi
  README'si durur) oluşturur.
  Zaten varsa dokunmaz (idempotent). --no-scaffold verilirse yalnız yol çözer, oluşturmaz.
- --slug verilirse `yayinstili/<slug>/` ve `authorguidelines/<slug>/` alt klasörlerini de
  kurar ve içlerindeki PDF'leri listeler (skill'in "yerel kaynak var mı" kararı için).
- Her profil KAYNAĞININ yanında durur: kural profili `authorguidelines/<slug>.json`,
  fiili yayın stili `yayinstili/<slug>.yayinstili.json`. Ayrı bir profil klasörü yoktur.
- stdout'a YALNIZ JSON basar (parse edilebilir); bilgi/uyarılar stderr'e gider.

Telif/veri notu: bu script yalnız klasör oluşturur ve PDF adlarını listeler; içerik okumaz.
"""
import sys
import os
import json
import argparse

# Windows konsolu cp1254'te ﬁ/ç/ı gibi karakterlerde patlar; stdout/stderr'i utf-8'e sabitle.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Plugin-kökü çözücü: skills/journalstyle/scripts → üç üst dizin = checkout kökü → scripts/.
# Eski bir kurulu kopyada (1.16.x cache) dosya yoksa import düşer ve yalnız docx-folder kipi çalışır.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))), "scripts"))
try:
    from hammadde_kokcoz import resolve_home, InputRootNotFound
except ImportError:  # pragma: no cover
    resolve_home = None
    InputRootNotFound = Exception

SUBDIRS = ["yayinstili", "authorguidelines", "ciktilar"]
HOME_SUBDIRS = ["output", os.path.join("input", "yayinstili"),
                os.path.join("input", "authorguidelines")]
# plugin-home kipinde kök düzeyinde kalmış eski çalışma klasörleri (bir docx bir zamanlar kökte
# durmuş olabilir): taşınmaz, yalnız bildirilir.
HOME_LEGACY_SUBDIRS = ["ciktilar", "yayinstili", "authorguidelines"]

# 1.16.0 öncesi düzen: PDF klasörlerinin adında "-pdf" vardı ve iki profil ayrı bir
# `journal-profiles/` klasöründe toplanıyordu. Artık her profil kaynağının yanında durur.
# Eski klasörler OTOMATİK TAŞINMAZ (içerik kaybı riski) — yalnız uyarılır ve JSON'da
# `legacy_dirs` olarak bildirilir; taşıma kararı kullanıcınındır.
LEGACY_SUBDIRS = ["yayinstili-pdf", "authorguidelines-pdf", "journal-profiles"]

README_TEXT = """# Çalışma workspace'i (plugin-journal)

Bu klasör bir **çalışmanın** workspace'idir. plugin-journal skill'leri (journalstyle, journalwriter,
journalpeerreview) buradaki kaynak `.docx` üzerinden çalışır ve alt klasörleri kullanır:

- `yayinstili/<dergi-slug>/`          — hedef dergiden örnek yayınlanmış makale PDF'leri (yayın
                                        stili analizinin BİRİNCİL kaynağı). Sen koyarsın; boşsa
                                        plugin web'e düşer.
- `yayinstili/<dergi-slug>.yayinstili.json`
                                      — plugin'in bu PDF'lerden çıkardığı fiili yayın stili.
                                        Elle düzenleme gerekmez.
- `authorguidelines/<dergi-slug>/`    — derginin "Author Guidelines" PDF'i. Sen koyarsın. Plugin
                                        her durumda web araması da yapar; birleştirme kararını sana
                                        sorar.
- `authorguidelines/<dergi-slug>.json`
                                      — plugin'in ürettiği resmi kural profili. Elle düzenleme
                                        gerekmez.
- `ciktilar/`                         — formatlanmış çıktı `.docx` dosyaları.

Her profil, çıkarıldığı KAYNAĞIN yanında durur — ayrı bir profil klasörü yoktur.

`<dergi-slug>` örn.: The Spine Journal → `thespinejournal`.
Bu README ve alt klasörler yoksa plugin bunları otomatik oluşturur.

Alternatif (1.17.0, "plugin-home" kipi): hammaddeyi plugin checkout'unun `input/` klasörüne
koyarsan workspace o checkout'un kökü olur — kaynaklar `input/`, çıktılar `output/`, dergi
PDF'leri `input/yayinstili/<slug>/` ve `input/authorguidelines/<slug>/`. Bu README o kipte yazılmaz.
"""


def resolve_workspace(target):
    """target bir .docx (veya dosya) ise dizinini, klasör ise kendisini döndürür."""
    target = os.path.abspath(target)
    if os.path.isdir(target):
        return target
    # Dosya (var ya da henüz yok): workspace = üst dizini.
    return os.path.dirname(target)


def pdf_paths(folder):
    """Full paths of the PDFs in `folder` — case-insensitive, so `.PDF` counts too.

    (`glob("*.pdf")` is case-insensitive on Windows but not on Linux/macOS; this is
    the one listing both journalstyle_calismaklasoru.py and journalstyle_pdfmetincikar.py go through.)
    """
    if not os.path.isdir(folder):
        return []
    return sorted(os.path.join(folder, f) for f in os.listdir(folder)
                  if f.lower().endswith(".pdf") and os.path.isfile(os.path.join(folder, f)))


def legacy_dirs(workspace, extra=()):
    """1.16.0 öncesi düzenden kalan klasörler (varsa) — taşınmaz, yalnız bildirilir."""
    return [d for d in list(LEGACY_SUBDIRS) + list(extra)
            if os.path.isdir(os.path.join(workspace, d))]


def _inside(path, parent):
    """path, parent'ın altında mı (aynı dizin dahil)."""
    try:
        return os.path.commonpath([os.path.abspath(path), os.path.abspath(parent)]) == \
            os.path.abspath(parent)
    except ValueError:  # farklı sürücü
        return False


def detect_home(target):
    """Hedef `<home>/input/` altındaysa hammadde_kokcoz sonucunu, değilse None döndürür.

    Var olmayan çıplak bir ad `<home>/input/<ad>` olarak da denenir; bulunursa (home, yeni_hedef).
    """
    if resolve_home is None:
        return None, target
    try:
        home = resolve_home(scaffold=False)
    except InputRootNotFound:
        return None, target
    input_dir = home["input_dir"]
    if _inside(target, input_dir):
        return home, target
    if not os.path.exists(target) and not os.path.isabs(target):
        cand = os.path.join(input_dir, target)
        if os.path.exists(cand):
            return home, cand
    return None, target


def list_pdfs(folder):
    return [os.path.basename(p) for p in pdf_paths(folder)]


def main():
    ap = argparse.ArgumentParser(description="plugin-journal workspace çözümleyici/iskele kurucu")
    ap.add_argument("target", help="Kaynak .docx dosyası veya workspace klasörü")
    ap.add_argument("--slug", default=None, help="Dergi slug'ı (yayinstili/authorguidelines alt klasörünü kurar)")
    ap.add_argument("--no-scaffold", action="store_true", help="Sadece yol çöz, klasör/README oluşturma")
    a = ap.parse_args()

    home, target = detect_home(a.target)
    mode = "plugin-home" if home else "docx-folder"
    workspace = home["home"] if home else resolve_workspace(target)
    scaffolded = False

    # Yanlış yazılmış bir yol sessizce yeni bir workspace kurmasın: hedef dosya
    # yoksa uyar (iskele yine kurulur, ama kullanıcı yazım hatasını görür).
    target_missing = not os.path.exists(target)
    if target_missing:
        sys.stderr.write(
            f"UYARI: '{a.target}' bulunamadı. Workspace olarak '{workspace}' kullanılıyor; "
            "yol yanlış yazılmışsa boş bir iskele kuruluyor olabilir.\n")

    if not a.no_scaffold:
        os.makedirs(workspace, exist_ok=True)
        for sub in (HOME_SUBDIRS if home else SUBDIRS):
            path = os.path.join(workspace, sub)
            if not os.path.isdir(path):
                os.makedirs(path, exist_ok=True)
                scaffolded = True
        if not home:
            readme = os.path.join(workspace, "README.md")
            if not os.path.exists(readme):
                with open(readme, "w", encoding="utf-8") as f:
                    f.write(README_TEXT)
                scaffolded = True

    if home:
        sources_dir = home["input_dir"]
        yayinstili_dir = home["yayinstili_dir"]
        authorguidelines_dir = home["authorguidelines_dir"]
        outputs_dir = home["output_dir"]
        eski = legacy_dirs(workspace, HOME_LEGACY_SUBDIRS)
        sys.stderr.write(f"BILGI: plugin-home kipi — home={workspace} ({home['source']})\n")
    else:
        sources_dir = workspace
        yayinstili_dir = os.path.join(workspace, "yayinstili")
        authorguidelines_dir = os.path.join(workspace, "authorguidelines")
        outputs_dir = os.path.join(workspace, "ciktilar")
        eski = legacy_dirs(workspace)
    if eski:
        sys.stderr.write(
            "UYARI: eski düzen klasör(leri) duruyor: " + ", ".join(eski) + ". Yeni düzende "
            "PDF'ler 'yayinstili/<slug>/' ve 'authorguidelines/<slug>/', profiller "
            "'authorguidelines/<slug>.json' ve 'yayinstili/<slug>.yayinstili.json'. İçerik "
            "kaybı olmasın diye otomatik taşınmadı — elle taşınmalı.\n")

    yayinstili_slug_dir = None
    authorguidelines_slug_dir = None
    yayinstili_pdfs = []
    authorguidelines_pdfs = []

    if a.slug:
        yayinstili_slug_dir = os.path.join(yayinstili_dir, a.slug)
        authorguidelines_slug_dir = os.path.join(authorguidelines_dir, a.slug)
        if not a.no_scaffold:
            for path in (yayinstili_slug_dir, authorguidelines_slug_dir):
                if not os.path.isdir(path):
                    os.makedirs(path, exist_ok=True)
                    scaffolded = True
        yayinstili_pdfs = list_pdfs(yayinstili_slug_dir)
        authorguidelines_pdfs = list_pdfs(authorguidelines_slug_dir)

    result = {
        "workspace": workspace,
        "mode": mode,
        "home": workspace if home else None,
        "sources_dir": sources_dir,
        "slug": a.slug,
        "yayinstili_dir": yayinstili_dir,
        "authorguidelines_dir": authorguidelines_dir,
        "outputs_dir": outputs_dir,
        "yayinstili_slug_dir": yayinstili_slug_dir,
        "authorguidelines_slug_dir": authorguidelines_slug_dir,
        "yayinstili_pdfs": yayinstili_pdfs,
        "authorguidelines_pdfs": authorguidelines_pdfs,
        "scaffolded": scaffolded,
        "legacy_dirs": eski,
        "target_exists": not target_missing,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

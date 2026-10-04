#!/usr/bin/env python3
"""Bir çalışmanın (study) workspace klasörünü çözer ve iskelesini kurar.

Bu script tek doğruluk kaynağıdır: journalstyle, journalwriter ve journalpeerreview skill'leri workspace
yollarını buradan alır (prose'da yol tekrar etmemek için). İki kip vardır (JSON'daki `mode`):

- **plugin-home** (1.17.0): kaynak dosya plugin checkout'unun `input/` (ya da kendi `output/`) klasörü altındaysa
  workspace = checkout kökü; hammadde `input/`, çıktılar `output/`, dergi PDF'leri ve profiller
  `input/yayinstili/` + `input/authorguidelines/`. Kök, plugin-kökü `scripts/hammadde_kokcoz.py`
  ile çözülür (env `JOURNAL_PLUGIN_HOME` → cwd manifesti → `CLAUDE_PLUGIN_ROOT`).
- **plugin-home-job** (1.28.0): kaynak `<home>/input/<iş>/` (ya da `output/<iş>/`) altındaysa ve
  `input/<iş>/` bir klasörse bir iş = bir klasör: `sources_dir = input/<iş>`, `outputs_dir =
  output/<iş>` (iskele kurar), `output_layout: "flat"` — çıktılar uzantı alt klasörü OLMADAN
  düz durur (`cikti_yolcoz.py --duz`), `yedekler/` o klasörün altında. JSON'da `job`.
  1.30.0: iş klasörünün adı son güncelleme damgasıyla başlar (`20261004 2152 Tez C2`, Stop hook'u
  `isklasoru_addamgala.py` yeniler); iş DAMGASIZ adla (`job_id`) bulunur, input ve output
  damgaları ayrıdır. `job` gerçek input klasör adıdır. Eski damgalı bir yol kimlikle düzeltilir.
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
- 1.22.0: JSON'daki `stamp` (`YYYYMMDD HHMM`, bu çağrının anı = işin başlangıcı) ve
  `output_layout: "ext-subdir"` çıktı düzenini bildirir — her çıktı `<outputs_dir>/<uzantı>/<ad>
  <stamp>.<uzantı>` olarak plugin-kökü `scripts/cikti_yolcoz.py` ile adlandırılır; çağıran
  taraf aynı damgayı işin bütün dosyalarına verir. Uzantı klasörleri önceden kurulmaz.

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
try:
    from cikti_yolcoz import damga as _damga
except ImportError:  # pragma: no cover
    _damga = None
try:  # 1.30.0: job folders carry a leading last-update stamp; a job is found by its identity
    from cikti_yolcoz import damga_ayir, is_klasoru_bul, yol_tazele
except ImportError:  # pragma: no cover
    damga_ayir = lambda ad: (None, ad)  # noqa: E731
    is_klasoru_bul = lambda kok, k: os.path.join(kok, k) if os.path.isdir(os.path.join(kok, k)) else None  # noqa: E731
    yol_tazele = lambda p: p  # noqa: E731

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
- `ciktilar/<uzantı>/`                — plugin'in ürettiği her dosya, uzantısına göre alt klasörde ve
                                        adının sonunda iş damgasıyla: `docx/<ad>_<slug> YYYYMMDD HHMM.docx`.

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
    """Hedef `<home>/input/` ya da `<home>/output/` altındaysa hammadde_kokcoz sonucunu, değilse None döndürür.

    Var olmayan çıplak bir ad `<home>/input/<ad>` olarak da denenir; bulunursa (home, yeni_hedef).
    `output/` da workspace'tir: bir revizyon turu önceki turun `output/docx/` dosyasını okur; aksi halde
    docx-folder kipi `output/docx/ciktilar/` açardı (2026-09-28).
    """
    if resolve_home is None:
        return None, target
    try:
        home = resolve_home(scaffold=False)
    except InputRootNotFound:
        return None, target
    input_dir = home["input_dir"]
    target = yol_tazele(target)  # 1.30.0: a path from before the job folder was re-stamped
    if _inside(target, input_dir) or _inside(target, home["output_dir"]):
        return home, target
    if not os.path.exists(target) and not os.path.isabs(target):
        cand = os.path.join(input_dir, target)
        if os.path.exists(cand):
            return home, cand
    return None, target


JOB_EXCLUDED = ("yayinstili", "authorguidelines")


def detect_job(home, target):
    """1.28.0 — iş klasörü: hedef `<home>/input/<iş>/…` ya da `<home>/output/<iş>/…` altındaysa ve
    `input/<iş>/` gerçek bir klasörse `<iş>` adını, değilse None döndürür (bir iş = bir klasör;
    çıktılar `output/<iş>/` altında DÜZ durur — kullanıcı kuralı, 2026-10-03). `yayinstili/` ve
    `authorguidelines/` iş değildir; `output/docx/` gibi bir uzantı klasörü de değildir, çünkü
    `input/docx/` yoktur."""
    for kok in (home["input_dir"], home["output_dir"]):
        if not _inside(target, kok):
            continue
        rel = os.path.relpath(os.path.abspath(target), os.path.abspath(kok))
        parcalar = rel.split(os.sep)
        if len(parcalar) < 2 or parcalar[0] in JOB_EXCLUDED or parcalar[0].startswith("."):
            return None
        # 1.30.0: `20261004 2152 Tez C2` → identity `Tez C2`; input and output stamps differ
        kimlik = damga_ayir(parcalar[0])[1]
        if is_klasoru_bul(home["input_dir"], kimlik):
            return kimlik
    return None


def list_pdfs(folder):
    return [os.path.basename(p) for p in pdf_paths(folder)]


def main():
    ap = argparse.ArgumentParser(description="plugin-journal workspace çözümleyici/iskele kurucu")
    ap.add_argument("target", help="Kaynak .docx dosyası veya workspace klasörü")
    ap.add_argument("--slug", default=None, help="Dergi slug'ı (yayinstili/authorguidelines alt klasörünü kurar)")
    ap.add_argument("--no-scaffold", action="store_true", help="Sadece yol çöz, klasör/README oluşturma")
    a = ap.parse_args()

    home, target = detect_home(a.target)
    job = detect_job(home, target) if home else None
    mode = "plugin-home-job" if job else ("plugin-home" if home else "docx-folder")
    workspace = home["home"] if home else resolve_workspace(target)
    scaffolded = False

    # Yanlış yazılmış bir yol sessizce yeni bir workspace kurmasın: hedef dosya
    # yoksa uyar (iskele yine kurulur, ama kullanıcı yazım hatasını görür).
    target_missing = not os.path.exists(target)
    if target_missing:
        sys.stderr.write(
            f"UYARI: '{a.target}' bulunamadı. Workspace olarak '{workspace}' kullanılıyor; "
            "yol yanlış yazılmışsa boş bir iskele kuruluyor olabilir.\n")

    job_in = job_out = None
    if job:
        job_in = is_klasoru_bul(home["input_dir"], job)
        job_out = is_klasoru_bul(home["output_dir"], job) or os.path.join(
            home["output_dir"], f"{_damga()} {job}" if _damga else job)

    if not a.no_scaffold:
        os.makedirs(workspace, exist_ok=True)
        for sub in (HOME_SUBDIRS if home else SUBDIRS) + ([job_out] if job else []):
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
        if job:
            sources_dir, outputs_dir = job_in, job_out
        eski = legacy_dirs(workspace, HOME_LEGACY_SUBDIRS)
        sys.stderr.write(f"BILGI: {mode} kipi — home={workspace} ({home['source']})"
                         + (f" iş={job}" if job else "") + "\n")
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
        # 1.30.0: `job` = the input folder's real name (with its stamp), `job_id` = the identity
        "job": os.path.basename(job_in) if job else None,
        "job_id": job,
        "sources_dir": sources_dir,
        "slug": a.slug,
        "yayinstili_dir": yayinstili_dir,
        "authorguidelines_dir": authorguidelines_dir,
        "outputs_dir": outputs_dir,
        # 1.28.0: "flat" = iş klasörü (cikti_yolcoz.py --duz); eski 1.16 cache'te (damga yok) de "flat"
        "output_layout": "flat" if (job or not _damga) else "ext-subdir",
        "stamp": _damga() if _damga else None,
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

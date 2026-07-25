#!/usr/bin/env python3
"""Bir çalışmanın (study) workspace klasörünü çözer ve iskelesini kurar.

plugin-journal artık her çalışmayı **kaynak .docx'in bulunduğu klasör** üzerinden yürütür.
Bu script tek doğruluk kaynağıdır: journalstyle, writer ve peerreview skill'leri workspace
yollarını buradan alır (prose'da yol tekrar etmemek için).

Kullanım:
    python workspace.py <makale.docx | klasör> [--slug <slug>] [--no-scaffold]

Davranış:
- workspace = verilen .docx'in dizini (dosya) ya da verilen klasörün kendisi.
- Varsayılan (--scaffold açık): eksik `yayinstili-pdf/`, `authorguidelines-pdf/`,
  `journal-profiles/`, `ciktilar/` klasörlerini ve yoksa bir `README.md` yer tutucuyu oluşturur.
  Zaten varsa dokunmaz (idempotent). --no-scaffold verilirse yalnız yol çözer, oluşturmaz.
- --slug verilirse `yayinstili-pdf/<slug>/` ve `authorguidelines-pdf/<slug>/` alt klasörlerini de
  kurar ve içlerindeki PDF'leri listeler (skill'in "yerel kaynak var mı" kararı için).
- stdout'a YALNIZ JSON basar (parse edilebilir); bilgi/uyarılar stderr'e gider.

Telif/veri notu: bu script yalnız klasör oluşturur ve PDF adlarını listeler; içerik okumaz.
"""
import sys
import os
import json
import glob
import argparse

# Windows konsolu cp1254'te ﬁ/ç/ı gibi karakterlerde patlar; stdout/stderr'i utf-8'e sabitle.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

SUBDIRS = ["yayinstili-pdf", "authorguidelines-pdf", "journal-profiles", "ciktilar"]

README_TEXT = """# Çalışma workspace'i (plugin-journal)

Bu klasör bir **çalışmanın** workspace'idir. plugin-journal skill'leri (journalstyle, writer,
peerreview) buradaki kaynak `.docx` üzerinden çalışır ve alt klasörleri kullanır:

- `yayinstili-pdf/<dergi-slug>/`      — hedef dergiden örnek yayınlanmış makale PDF'leri (yayın
                                        stili analizinin BİRİNCİL kaynağı). Sen koyarsın; boşsa
                                        plugin web'e düşer.
- `authorguidelines-pdf/<dergi-slug>/` — derginin "Author Guidelines" PDF'i. Sen koyarsın. Plugin
                                        her durumda web araması da yapar; birleştirme kararını sana
                                        sorar.
- `journal-profiles/`                 — plugin'in ürettiği profil önbelleği (`<slug>.json`,
                                        `<slug>.yayinstili.json`). Elle düzenleme gerekmez.
- `ciktilar/`                         — formatlanmış çıktı `.docx` dosyaları.

`<dergi-slug>` örn.: The Spine Journal → `thespinejournal`.
Bu README ve alt klasörler yoksa plugin bunları otomatik oluşturur.
"""


def resolve_workspace(target):
    """target bir .docx (veya dosya) ise dizinini, klasör ise kendisini döndürür."""
    target = os.path.abspath(target)
    if os.path.isdir(target):
        return target
    # Dosya (var ya da henüz yok): workspace = üst dizini.
    return os.path.dirname(target)


def list_pdfs(folder):
    if not os.path.isdir(folder):
        return []
    return sorted(os.path.basename(p) for p in glob.glob(os.path.join(folder, "*.pdf")))


def main():
    ap = argparse.ArgumentParser(description="plugin-journal workspace çözümleyici/iskele kurucu")
    ap.add_argument("target", help="Kaynak .docx dosyası veya workspace klasörü")
    ap.add_argument("--slug", default=None, help="Dergi slug'ı (yayinstili/authorguidelines alt klasörünü kurar)")
    ap.add_argument("--no-scaffold", action="store_true", help="Sadece yol çöz, klasör/README oluşturma")
    a = ap.parse_args()

    workspace = resolve_workspace(a.target)
    scaffolded = False

    if not a.no_scaffold:
        os.makedirs(workspace, exist_ok=True)
        for sub in SUBDIRS:
            path = os.path.join(workspace, sub)
            if not os.path.isdir(path):
                os.makedirs(path, exist_ok=True)
                scaffolded = True
        readme = os.path.join(workspace, "README.md")
        if not os.path.exists(readme):
            with open(readme, "w", encoding="utf-8") as f:
                f.write(README_TEXT)
            scaffolded = True

    yayinstili_dir = os.path.join(workspace, "yayinstili-pdf")
    authorguidelines_dir = os.path.join(workspace, "authorguidelines-pdf")
    profiles_dir = os.path.join(workspace, "journal-profiles")
    outputs_dir = os.path.join(workspace, "ciktilar")

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
        "slug": a.slug,
        "yayinstili_dir": yayinstili_dir,
        "authorguidelines_dir": authorguidelines_dir,
        "profiles_dir": profiles_dir,
        "outputs_dir": outputs_dir,
        "yayinstili_slug_dir": yayinstili_slug_dir,
        "authorguidelines_slug_dir": authorguidelines_slug_dir,
        "yayinstili_pdfs": yayinstili_pdfs,
        "authorguidelines_pdfs": authorguidelines_pdfs,
        "scaffolded": scaffolded,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

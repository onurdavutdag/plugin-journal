#!/usr/bin/env python3
"""Yayın stili analizi için yerel PDF metni + temel yapısal ipuçları çıkarır.

Kullanım:
    python journalstyle_extract_pdf_text.py <klasör-veya-pdf> [--full] [--max-chars N]

`journal-s-yayinstili` agent'ı, WORKSPACE'teki `yayinstili-pdf/<slug>/` klasöründe (kaynak
`.docx` ile aynı yerde) duran örnek makalelerden fiili yayın geleneklerini (tablo/şekil sayısı,
referans sayısı, bölüm başlıkları, cümle uzunluğu, atıf biçimi) çıkarmak için bunu Bash ile
çağırır. Yolu `journalstyle_workspace.py`'nin bastığı `yayinstili_slug_dir` alanından alır — plugin ağacının
içinde PDF tutulmaz.

- Varsayılan: her PDF için ÖZET (sayfa sayısı, Table/Figure geçiş sayısı, referans satırı
  tahmini, kelime sayısı, ilk ~1500 karakter önizleme).
- `--full`: her PDF'in TAM metnini döker (cümle uzunluğu / edilgen oran analizi için).

pymupdf (fitz) yoksa pypdf'e düşer. Windows cp1254 UnicodeEncodeError'a karşı stdout utf-8.
Telif notu: script yalnız metin döker; agent buradan VERBATIM cümle/caption kopyalamaz,
yalnız sayısal/yapısal örüntü çıkarır.
"""
import sys
import os
import re
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from journalstyle_workspace import pdf_paths as list_pdfs  # noqa: E402 — tek ortak PDF listeleyici

# Windows konsolu cp1254 -> ﬁ/§ gibi karakterlerde patlar; utf-8'e sabitle.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def load_pages(path):
    """PDF sayfa metinlerini liste olarak döndürür (pymupdf, yoksa pypdf).

    Backend YOKLUĞU (ImportError) ile dosya BOZUKLUĞU ayrı ele alınır: şifreli/bozuk
    bir PDF `fitz.open()` içinde ImportError değil RuntimeError/FileDataError fırlatır.
    Eskiden yakalanmıyordu ve 5 PDF'lik bir klasörde ilk bozuk dosya tüm analizi
    düşürüyordu; artık okuma hatası çağırana bırakılır, o dosyayı atlar (bkz. emit()).
    """
    try:
        import fitz  # pymupdf
    except ImportError:
        fitz = None
    if fitz is not None:
        doc = fitz.open(path)
        try:
            return [doc[i].get_text() for i in range(len(doc))]
        finally:
            doc.close()
    try:
        from pypdf import PdfReader
    except ImportError:
        sys.stderr.write("HATA: pymupdf veya pypdf gerekli (pip install pymupdf).\n")
        sys.exit(2)
    r = PdfReader(path)
    return [(p.extract_text() or "") for p in r.pages]


def analyze(pages):
    text = "\n".join(pages)
    words = re.findall(r"\b[\w'-]+\b", text)
    # Metinde geçen benzersiz Table N / Figure N etiketleri (numaralama biçimini gözlemlemek için)
    tables = sorted(set(re.findall(r"\bTables?\s+(\d+)", text)), key=int) if re.search(r"\bTables?\s+\d+", text) else []
    figures = sorted(set(re.findall(r"\bFig(?:ure|\.)?\s+(\d+)", text)), key=int) if re.search(r"\bFig(?:ure|\.)?\s+\d+", text) else []
    # Kaynakça: "References" başlığından sonra numaralı satır tahmini
    ref_est = None
    m = re.search(r"\bReferences\b", text)
    if m:
        tail = text[m.end():]
        seen = {int(n) for n in re.findall(r"(?m)^\s*\[?(\d{1,3})[\].\s]", tail) if int(n) <= 250}
        # En büyük n; ardışıklık şartı (n-1 de var) tek-atımlık sayı/yıl gürültüsünü eler.
        seq = [n for n in seen if (n - 1) in seen or n == 1]
        if seq:
            ref_est = max(seq)
    return {
        "pages": len(pages),
        "word_count": len(words),
        "table_labels": tables,
        "figure_labels": figures,
        "reference_count_est": ref_est,
    }


def emit(path, full, max_chars):
    name = os.path.basename(path)
    try:
        pages = load_pages(path)
    except SystemExit:
        raise                      # "backend kurulu değil" gerçek bir durma sebebi
    except Exception as e:         # şifreli/bozuk PDF — atla, kalanları analiz et
        print("=" * 78)
        print(f"PDF: {name}")
        print(f"  ATLANDI — okunamadı: {type(e).__name__}: {e}")
        print()
        sys.stderr.write(f"UYARI: '{name}' okunamadı ({type(e).__name__}: {e}) — atlandı.\n")
        return
    info = analyze(pages)
    print("=" * 78)
    print(f"PDF: {name}")
    print(f"  pages={info['pages']}  words={info['word_count']}  "
          f"tables_seen={info['table_labels']}  figures_seen={info['figure_labels']}  "
          f"reference_count_est={info['reference_count_est']}")
    print("-" * 78)
    body = "\n".join(pages)
    # --full de sınırlıdır: 5 PDF'lik bir klasör aksi halde tek başına agent
    # context'ini doldurur. Sınırı büyütmek için --max-chars verilir.
    out = body[:max_chars]
    if len(body) > max_chars:
        out += (f"\n...[kısaltıldı: {len(body)} karakterin ilk {max_chars}'i; "
                "daha fazlası için --max-chars N]")
    print(out)
    print()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target", help="PDF dosyası veya PDF içeren klasör")
    ap.add_argument("--full", action="store_true",
                    help="Tam metni dök (özet yerine) — yine de --max-chars ile sınırlıdır")
    ap.add_argument("--max-chars", type=int, default=None,
                    help="Karakter sınırı (varsayılan: özet 1500, --full 20000)")
    a = ap.parse_args()
    max_chars = a.max_chars if a.max_chars is not None else (20000 if a.full else 1500)

    if os.path.isdir(a.target):
        pdfs = list_pdfs(a.target)
        if not pdfs:
            print(f"BILGI: {a.target} altında PDF yok — web yedeğine düşülmeli.")
            return
    elif os.path.isfile(a.target):
        pdfs = [a.target]
    elif not a.target.lower().endswith(".pdf"):
        # Olmayan slug klasörü = yerel PDF yok; hata değil, web yedeğine düş sinyali.
        print(f"BILGI: {a.target} yok — yerel PDF yok, web yedeğine düşülmeli.")
        return
    else:
        sys.stderr.write(f"HATA: bulunamadı: {a.target}\n")
        sys.exit(2)

    print(f"{len(pdfs)} PDF bulundu.\n")
    for p in pdfs:
        emit(p, a.full, max_chars)


if __name__ == "__main__":
    main()

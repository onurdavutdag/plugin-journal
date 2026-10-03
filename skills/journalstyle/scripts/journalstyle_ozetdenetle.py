#!/usr/bin/env python3
"""Bir kongre bildiri özetini (abstract) gönderim kurallarına göre DENETLER — yalnız ölçer, karar vermez.

journalstyle skill'i (ve /journal yönlendirmesi) bir kongre özetini forma yapıştırmadan önce
burayı çağırır: kelime sınırı, zorunlu başlıklar ve sıraları, başlıkta kısaltma, yazar
satırında unvan / büyük-küçük harf, numaralı kaynak listesi ile metin-içi (n) atıflarının
eşleşmesi. Ağırlık (uyarı mı, engel mi) ÇAĞIRANIN kararıdır; script yalnız bulguyu bildirir.

Kullanım:
    python journalstyle_ozetdenetle.py <ozet.docx | ozet.md | ozet.txt>
        [--sinir 250]
        [--basliklar "Amaç,Materyal ve Metot,Bulgular,Sonuç,Referanslar"]
        [--referans-baslik Referanslar] [--yazar-satiri 2] [--kurum-satiri 3]

Girdi:
- .docx: python-docx varsa onunla, yoksa zip + word/document.xml ile (hammadde_oku.py'nin
  yaklaşımı; bağımlılık yok). Her paragraf bir satırdır; tablolar gövde sırasında okunur.
- .md: bir ```text çitli blok varsa özet o bloğun içeriğidir (forma yapıştırılacak metin);
  yoksa dosyanın tamamı.
- .txt: dosyanın tamamı.

Satır modeli (boş satırlar atılır): 1 = başlık, --yazar-satiri = yazarlar, --kurum-satiri = kurum,
sonrası gövde; `--referans-baslik` ile başlayan satırdan itibaren kaynak listesi.

Çıktı: stdout'a YALNIZ JSON (çıkış 0). Okunamayan dosya → {"error": "unreadable"} ve çıkış 2
(journalstyle_calismaklasoru.py / hammadde_kokcoz.py sözleşmesi). Bilgi/uyarılar stderr'e gider.

Telif/veri notu: script içerik üretmez, dosyaya yazmaz; yalnız sayar ve eşleştirir.
"""
import sys
import os
import re
import json
import argparse
import zipfile
import xml.etree.ElementTree as ET

# Windows konsolu cp1254'te ﬁ/ç/ı gibi karakterlerde patlar; stdout/stderr'i utf-8'e sabitle.
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

DEFAULT_SINIR = 250
DEFAULT_BASLIKLAR = "Amaç,Materyal ve Metot,Bulgular,Sonuç,Referanslar"
DEFAULT_REFERANS_BASLIK = "Referanslar"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"

# Türkçe büyük harfler dahil; Romen rakamları ve tek harf dışarıda bırakılır.
UPPER_TR = "A-ZÇĞİÖŞÜ"
ABBR_RE = re.compile(r"^[%s]{2,6}$" % UPPER_TR)
ROMAN_RE = re.compile(r"^[IVXLCDM]+$")
# Unvanlar: noktalı Türkçe kısaltmalar + noktasız MD / PhD.
UNVAN_RE = re.compile(r"\b(?:Dr|Prof|Doç|Uzm|Op|Öğr|Arş)\.|\b(?:MD|PhD)\b")
# Metin-içi atıf: (1), (1,2), (1-3), (1–3); "(2,5×16×22 cm)" gibi ölçüler eşleşmez.
ATIF_RE = re.compile(r"\((\d{1,3}(?:\s*[,;–-]\s*\d{1,3})*)\)")
# Kaynak listesi satırı: "1. …", "1) …", "[1] …"
KAYNAK_SATIR_RE = re.compile(r"^\s*(?:\[?(\d{1,3})\]?[.)]?)\s+\S")


# ----------------------------------------------------------------------------- okuma
def _w(tag):
    return "{%s}%s" % (W_NS, tag)


def _ptext(p):
    """Paragraf metni belge sırasında: w:t, w:tab → boşluk, w:br/w:cr → satır sonu.

    w:instrText (alan kodu) ve w:delText (izlenen silme) w:t değildir, metne girmez —
    bir Zotero alanının kodu kelime sayısına karışmaz.
    """
    out = []
    for r in p.iter(_w("r")):
        for c in r:
            if c.tag == _w("t"):
                out.append(c.text or "")
            elif c.tag == _w("tab"):
                out.append(" ")
            elif c.tag in (_w("br"), _w("cr")):
                out.append("\n")
    return "".join(out)


def _body_lines(body):
    """Gövdedeki paragraf ve tablo hücrelerini belge sırasında satırlara çevirir."""
    lines = []
    for el in list(body):
        if el.tag == _w("tbl"):
            for tr in el.iter(_w("tr")):
                for tc in tr.findall(_w("tc")):
                    for p in tc.iter(_w("p")):
                        lines.extend(_ptext(p).split("\n"))
        elif el.tag == _w("p"):
            lines.extend(_ptext(el).split("\n"))
    return lines


def read_docx(path, warnings):
    """(backend, satırlar). python-docx varsa onun gövde elemanı, yoksa zip/XML."""
    try:
        import docx  # python-docx
        d = docx.Document(path)
        return "python-docx", _body_lines(d.element.body)
    except ImportError:
        warnings.append("python-docx kurulu değil — zip/XML ile okundu")
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    body = root.find(_w("body"))
    if body is None:
        raise ValueError("word/document.xml gövdesi yok")
    return "zipxml", _body_lines(body)


def read_md(path, warnings):
    with open(path, encoding="utf-8-sig") as f:
        text = f.read()
    m = re.search(r"^```text[ \t]*\n(.*?)^```[ \t]*$", text, re.S | re.M)
    if m:
        return "md-fence", m.group(1).split("\n")
    warnings.append("```text çitli blok yok — dosyanın tamamı özet sayıldı")
    return "md-full", text.split("\n")


def read_txt(path, warnings):
    with open(path, encoding="utf-8-sig") as f:
        return "txt", f.read().split("\n")


def read_lines(path, warnings):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".docx":
        backend, lines = read_docx(path, warnings)
    elif ext == ".md":
        backend, lines = read_md(path, warnings)
    elif ext == ".txt":
        backend, lines = read_txt(path, warnings)
    else:
        raise ValueError("desteklenmeyen uzantı: %s" % ext)
    return backend, [ln.strip() for ln in lines if ln.strip()]


# ----------------------------------------------------------------------------- ölçüm
def kelime(text):
    return len(text.split())


def _norm(s):
    return re.sub(r"\s+", " ", s).strip().casefold()


def baslik_bul(line, basliklar):
    """Satır "<Başlık>:" ile başlıyorsa o başlığı (beklenen yazımıyla) döndürür."""
    n = _norm(line)
    for b in basliklar:
        if n.startswith(_norm(b) + ":"):
            return b
    return None


def atif_numaralari(text):
    nums = set()
    for m in ATIF_RE.finditer(text):
        for part in re.split(r"[,;]", m.group(1)):
            part = part.strip()
            rng = re.split(r"\s*[–-]\s*", part)
            if len(rng) == 2 and rng[0].isdigit() and rng[1].isdigit():
                a, b = int(rng[0]), int(rng[1])
                if a <= b and b - a <= 50:
                    nums.update(range(a, b + 1))
                    continue
            if part.isdigit():
                nums.add(int(part))
    return nums


def kisaltmalar(title):
    out = []
    for tok in title.split():
        t = re.sub(r"^[^\w]+|[^\w]+$", "", tok)
        if ABBR_RE.match(t) and not ROMAN_RE.match(t) and t not in out:
            out.append(t)
    return out


def yazar_denetle(line):
    unvan = [m.group(0) for m in UNVAN_RE.finditer(line)]
    sorun = []
    temiz = UNVAN_RE.sub(" ", line)
    for tok in re.split(r"[,;]| ve | and ", temiz):
        for w in tok.split():
            w = re.sub(r"^[^\w]+|[^\w\.]+$", "", w).rstrip(".")
            if not w or not any(ch.isalpha() for ch in w):
                continue
            if w.isdigit():
                continue
            if not w[0].isupper() or (len(w) > 1 and w.isupper() and not ROMAN_RE.match(w)):
                sorun.append(w)
    return unvan, sorun


def denetle(lines, a):
    basliklar = [b.strip() for b in a.basliklar.split(",") if b.strip()]
    ref_baslik = a.referans_baslik.strip()
    uyarilar = []

    if not lines:
        raise ValueError("boş belge")

    # --- satır modeli
    title = lines[0]
    yi = a.yazar_satiri - 1
    ki = a.kurum_satiri - 1
    yazar_satir = lines[yi] if 0 <= yi < len(lines) else ""
    kurum_satir = lines[ki] if 0 <= ki < len(lines) else ""
    govde_basi = max(yi, ki, 0) + 1

    # --- kaynak bölümü
    ref_i = None
    for i in range(govde_basi, len(lines)):
        if _norm(lines[i]).startswith(_norm(ref_baslik)):
            ref_i = i
            break
    govde = lines[govde_basi:ref_i] if ref_i is not None else lines[govde_basi:]
    ref_lines = lines[ref_i + 1:] if ref_i is not None else []
    # "Referanslar: 1. …" tek satırda ise başlık satırının kalanı da listeye girer
    if ref_i is not None:
        rest = lines[ref_i][len(ref_baslik):].lstrip(" :").strip()
        if rest:
            ref_lines = [rest] + ref_lines

    # --- kelime
    toplam = kelime(" ".join(lines))
    ref_kelime = kelime(" ".join(lines[ref_i:])) if ref_i is not None else 0
    referans_haric = toplam - ref_kelime

    # --- başlıklar (belge sırasında; başlık satırı "<Başlık>:" ile başlar)
    bulunan = []
    for ln in lines[govde_basi:]:
        b = baslik_bul(ln, basliklar)
        if b and b not in bulunan:
            bulunan.append(b)
    eksik = [b for b in basliklar if b not in bulunan]
    beklenen_sira = [b for b in basliklar if b in bulunan]
    sira_dogru = bulunan == beklenen_sira

    # --- başlık (title)
    kis = kisaltmalar(title)

    # --- yazarlar
    unvan, buyuk = yazar_denetle(yazar_satir)

    # --- referanslar
    liste_no = []
    for ln in ref_lines:
        m = KAYNAK_SATIR_RE.match(ln)
        if m:
            liste_no.append(int(m.group(1)))
    metin_ici = sorted(atif_numaralari(" ".join(govde)))
    eksik_atif = sorted(n for n in liste_no if n not in metin_ici)
    tanimsiz = sorted(n for n in metin_ici if n not in liste_no)

    # --- uyarılar (ağırlık çağıranın)
    if toplam > a.sinir:
        uyarilar.append("kelime sınırı aşıldı: %d > %d (referanslar dahil)" % (toplam, a.sinir))
    if referans_haric > a.sinir:
        uyarilar.append("kelime sınırı referanslar hariç de aşıldı: %d > %d" % (referans_haric, a.sinir))
    if eksik:
        uyarilar.append("eksik başlık: " + ", ".join(eksik))
    if not sira_dogru:
        uyarilar.append("başlık sırası beklenenden farklı: " + " → ".join(bulunan))
    if kis:
        uyarilar.append("başlıkta kısaltma: " + ", ".join(kis))
    if unvan:
        uyarilar.append("yazar satırında unvan: " + ", ".join(unvan))
    if buyuk:
        uyarilar.append("yazar adında büyük/küçük harf sorunu: " + ", ".join(buyuk))
    if ref_i is None:
        uyarilar.append("kaynak başlığı yok: " + ref_baslik)
    if eksik_atif:
        uyarilar.append("listede olup metinde atıf verilmeyen kaynak: " + ", ".join(map(str, eksik_atif)))
    if tanimsiz:
        uyarilar.append("metinde atıf verilip listede olmayan kaynak: " + ", ".join(map(str, tanimsiz)))
    if ref_i is not None and not liste_no:
        uyarilar.append("kaynak başlığı var, numaralı satır yok")

    return {
        "kelime": {
            "toplam": toplam,
            "referans_haric": referans_haric,
            "sinir": a.sinir,
            "sinir_asildi": toplam > a.sinir,
            "sinir_asildi_referans_haric": referans_haric > a.sinir,
        },
        "basliklar": {
            "beklenen": basliklar,
            "bulunan": bulunan,
            "eksik": eksik,
            "sira_dogru": sira_dogru,
        },
        "baslik": {"metin": title, "kisaltma": kis, "kelime": kelime(title)},
        "yazarlar": {"metin": yazar_satir, "unvan": unvan, "buyuk_harf_sorunu": buyuk},
        "kurum": kurum_satir,
        "referanslar": {
            "sayi": len(liste_no),
            "metin_ici": metin_ici,
            "eksik_atif": eksik_atif,
            "tanimsiz_atif": tanimsiz,
        },
        "uyarilar": uyarilar,
    }


def main():
    ap = argparse.ArgumentParser(description="plugin-journal kongre özeti denetleyici")
    ap.add_argument("file", help="Özet dosyası (.docx / .md / .txt)")
    ap.add_argument("--sinir", type=int, default=DEFAULT_SINIR, help="Kelime sınırı (varsayılan 250)")
    ap.add_argument("--basliklar", default=DEFAULT_BASLIKLAR,
                    help="Virgülle ayrılmış beklenen başlıklar, sırayla")
    ap.add_argument("--referans-baslik", default=DEFAULT_REFERANS_BASLIK,
                    help="Kaynak listesini başlatan başlık")
    ap.add_argument("--yazar-satiri", type=int, default=2, help="Yazar satırının sırası (1 = başlık)")
    ap.add_argument("--kurum-satiri", type=int, default=3, help="Kurum satırının sırası")
    a = ap.parse_args()

    path = os.path.abspath(a.file)
    warnings = []
    try:
        backend, lines = read_lines(path, warnings)
        result = denetle(lines, a)
    except Exception as e:  # okunamayan/boş dosya, bozuk zip, yanlış uzantı
        sys.stderr.write("HATA: %s\n" % e)
        print(json.dumps({"error": "unreadable", "file": path, "detail": str(e)}, ensure_ascii=False))
        sys.exit(2)

    for w in warnings:
        sys.stderr.write("BILGI: %s\n" % w)
    out = {"file": path, "backend": backend}
    out.update(result)
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

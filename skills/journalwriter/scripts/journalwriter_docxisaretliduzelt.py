#!/usr/bin/env python3
"""
Onaylanmış düzeltmeleri MEVCUT bir .docx'e İŞARETLİ olarak uygular: çıkan metin
üstü çizilir (asla silinmez), giren metin renkli yazılır, yeni atıflar belgenin
kendi ZOTERO_ITEM alanlarından klonlanan gerçek Zotero alanlarıdır.

journalwriter'ın betiği. Tez/makale düzeltme turlarında her oturum bu motoru geçici
klasörlerde yeniden kuruyordu (gözlem #380: 7, 26, 27, 28 Eyl 2026); motor buraya
taşındı. Atıf numarası/kaynakça yine journal-s-zotero'nun ve kullanıcının
Word → Zotero → Refresh adımının işidir: bu betik yalnız belgede ZATEN bulunan
anahtarların alanlarını klonlar ve görünen numarayı belgedeki tek-anahtarlı
alanlardan okur; kütüphaneye dokunmaz, kaynakça yazmaz.

Kullanım:
    python -B journalwriter_docxisaretliduzelt.py <girdi.docx> <islemler.json> <cikti.docx>
        [--apply] [--renk RRGGBB] [--ustune-yaz]

Varsayılan KURU çalışmadır: her işlem bellekte uygulanır, ne yapacağı yazdırılır,
dosya yazılmaz. `--apply` aynı işlemleri uygular ve <cikti.docx>'i yazar. Girdi
dosyası hiçbir durumda üzerine yazılmaz (çıktı = girdi → hata). Var olan bir
çıktının üzerine yalnız `--ustune-yaz` ile yazılır. Çıktı yolu
`scripts/cikti_yolcoz.py --uzanti docx --damga "<damga>"` ile alınır, elle kurulmaz.

Bir işlem eşleşmezse (paragraf bulunamadı / birden çok, çapa yok / birden çok,
alan yok ...) hiçbir şey yazılmaz; hangi işlemin neden düştüğü stderr'e basılır,
çıkış kodu 2. Biçim hatası (JSON, seçici, bilinmeyen op) çıkış kodu 1.

İşlem dosyası (UTF-8 JSON) — ya yalnız işlem listesi ya da şu nesne:
    {
      "renk": "FF0000",                      # isteğe bağlı; giren metnin rengi
      "numara_esleme": {"LYXQCQ2X": "10"},   # isteğe bağlı; tek başına alanı olmayan anahtarın numarası
      "govde_baslangici": "GİRİŞ VE AMAÇ",   # isteğe bağlı; "govde": true seçicilerin arama başlangıcı
      "islemler": [
        {"p": "^Amaç: C2 vertebrası", "op": "rep", "args": ["eski metin", "yeni metin"]},
        {"p": "=Şekil 5: Ligamentler", "govde": true, "op": "fmt", "args": ["Şekil 5:", "Şekil 5."]}
      ]
    }

Paragraf seçicisi `p`: "^metin" = paragrafın görünen metni bununla BAŞLAR,
"=metin" = paragrafın görünen metni tam olarak budur (baştaki/sondaki boşluk
kırpılır). Seçici tek paragrafa denk gelmelidir. Seçici ilk kullanımda
belleğe alınır: paragrafın ilk düzeltmesi metni değiştirse de sonraki işlemler
aynı paragrafı bulur (28 Eyl 2026 hatası).

Görünen metinde her alan tek bir "§" karakteriyle temsil edilir; bir alanın hemen
arkasına çapa vermek için çapaya "§" yazılır ("bildirilmektedir §").

İşlemler (args sırasıyla):
    strike   [eski]                 eski metni üstü çizer
    ins      [capa, metin]          çapanın arkasına renkli metin ekler
    rep      [eski, yeni]           eskiyi üstü çizer, arkasına renkli yeniyi ekler
    field    [capa, [ANAHTAR,..]]   çapanın arkasına klon ZOTERO_ITEM alanı ekler
    delfield [[ANAHTAR,..]]         tam bu anahtar kümesini taşıyan alanı kaldırır
    relink   [[ESKI,..], [YENI,..]] alanın anahtar kümesini değiştirir (var olan
                                    öğe korunur, yenisi belgedeki alandan klonlanır)
    pre      [metin]                paragrafın başına renkli metin ekler
    fmt      [eski, yeni]           İŞARETSİZ doğrudan değişiklik (başlık noktalaması,
                                    şekil/tablo etiketi gibi; kullanıcı istediyse)
    head     [yeni]                 başlığın görünen metnini İŞARETSİZ değiştirir

Renk önceliği: --renk > JSON "renk" > FF0000 (plugin'in kırmızı düzeltme kuralı).
Kullanıcı belgede başka bir renk istediyse (C2 tezi: 0070C0 mavi) onu verir.
"""
import argparse
import copy
import json
import os
import random
import re
import string
import sys
import tempfile
import zipfile

from lxml import etree

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
XML_NS = "http://www.w3.org/XML/1998/namespace"
FLD = "§"          # görünen metinde bir alanın yer tutucusu
VARSAYILAN_RENK = "FF0000"


def q(t):
    return "{%s}%s" % (W, t)


class OpHatasi(Exception):
    """Bir işlem belgeyle eşleşmedi; hiçbir şey yazılmaz."""


class BicimHatasi(Exception):
    """İşlem dosyası ya da komut satırı hatalı."""


def sart(kosul, mesaj):
    # assert yerine: python -O altında da çalışsın
    if not kosul:
        raise OpHatasi(mesaj)


def utf8_stdout():
    """Windows'ta yönlendirilen çıktıda Türkçe karakterleri koru."""
    for akis in (sys.stdout, sys.stderr):
        try:
            akis.reconfigure(encoding="utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            pass


# ---------- paragraf modeli ----------
def runs_of(p):
    """p'nin üst düzey run'ları (alanlar bu düzeyde run dizisi olarak durur)."""
    return [r for r in p if r.tag == q("r")]


def segments(p):
    """(tür, nesne) listesi. 't' = metin run'ı, 'f' = alan (run listesi)."""
    segs, cur = [], None
    for r in runs_of(p):
        fc = r.find(q("fldChar"))
        if fc is not None and fc.get(q("fldCharType")) == "begin":
            cur = [r]
            continue
        if cur is not None:
            cur.append(r)
            if fc is not None and fc.get(q("fldCharType")) == "end":
                segs.append(("f", cur))
                cur = None
            continue
        segs.append(("t", r))
    return segs


def run_text(r):
    out = []
    for ch in r:
        if ch.tag == q("t"):
            out.append(ch.text or "")
        elif ch.tag == q("tab"):
            out.append("\t")
    return "".join(out)


def composite(p):
    """Görünen metin (alan = FLD) ve her parçanın [baş, son) aralığı."""
    s, spans = [], []
    pos = 0
    for kind, obj in segments(p):
        t = FLD if kind == "f" else run_text(obj)
        spans.append((pos, pos + len(t), kind, obj))
        s.append(t)
        pos += len(t)
    return "".join(s), spans


def field_keys(runs):
    instr = "".join((it.text or "") for r in runs for it in r.iter(q("instrText")))
    if "ZOTERO_ITEM" not in instr:
        return None, None
    js = json.loads(instr[instr.index("{"):])
    keys = [ci["uris"][0].rsplit("/", 1)[-1] for ci in js["citationItems"]]
    return keys, js


def set_text(r, text):
    ts = r.findall(q("t"))
    sart(len(ts) == 1 and r.find(q("tab")) is None,
         "run biçimi beklenmedik (birden çok w:t ya da sekme): %r" % run_text(r))
    ts[0].text = text
    ts[0].set("{%s}space" % XML_NS, "preserve")


def split_run(r, k):
    """Metin run'ı r'yi k. karakterde böler; (sol, sağ) döner. k 1..len-1."""
    t = run_text(r)
    right = copy.deepcopy(r)
    set_text(r, t[:k])
    set_text(right, t[k:])
    r.addnext(right)
    return r, right


def cut_at(p, pos):
    """Görünen metindeki pos konumunda run sınırı olmasını sağla (alan içinde değil)."""
    _, spans = composite(p)
    for a, b, kind, obj in spans:
        if a < pos < b:
            sart(kind == "t", "kesim noktası bir alanın içinde (konum %d)" % pos)
            split_run(obj, pos - a)
            return
    # zaten sınır


def find_unique(p, needle):
    s, _ = composite(p)
    i = s.find(needle)
    sart(i >= 0, "çapa bulunamadı: %r" % needle)
    sart(s.find(needle, i + 1) < 0, "çapa tek değil: %r" % needle)
    return i


def rpr_set(r, strike=None, color=None, drop_highlight=False):
    rpr = r.find(q("rPr"))
    if rpr is None:
        rpr = etree.SubElement(r, q("rPr"))
        r.remove(rpr)
        r.insert(0, rpr)
    if strike is not None:
        for e in rpr.findall(q("strike")):
            rpr.remove(e)
        if strike:
            etree.SubElement(rpr, q("strike"))
    if color is not None:
        for e in rpr.findall(q("color")):
            rpr.remove(e)
        c = etree.SubElement(rpr, q("color"))
        c.set(q("val"), color)
    if drop_highlight:
        for e in rpr.findall(q("highlight")):
            rpr.remove(e)
    # şema sırası: Word ekleme sırasını tolere ediyor
    return r


def text_runs_between(p, a, b):
    _, spans = composite(p)
    out = []
    for s0, s1, kind, obj in spans:
        if s0 >= a and s1 <= b and s1 > s0:
            sart(kind == "t", "üstü çizilecek/değişecek aralıkta bir alan var")
            out.append(obj)
    return out


def template_run(p, pos):
    """pos'tan önceki son metin run'ı: biçim buradan kopyalanır."""
    _, spans = composite(p)
    prev = None
    for a, b, kind, obj in spans:
        if b <= pos and kind == "t":
            prev = obj
    sart(prev is not None, "konum %d öncesinde biçim alınacak metin run'ı yok" % pos)
    return prev


def element_before(p, pos):
    """pos'ta biten son öğe (run ya da alanın son run'ı)."""
    _, spans = composite(p)
    last = None
    for a, b, kind, obj in spans:
        if b == pos:
            last = obj[-1] if kind == "f" else obj
    sart(last is not None, "konum %d'de biten öğe yok" % pos)
    return last


# ---------- belge durumu ----------
class Belge:
    """Belgenin alan dizini + işlem bağlamı."""

    def __init__(self, root, renk, numara_esleme):
        self.root = root
        self.body = root.find(q("body"))
        self.renk = renk
        self.numara_esleme = dict(numara_esleme or {})
        self.alanlar = {}       # anahtar -> (citationItem, görünen numara | None)
        self.sablon = None      # (alan run'ları, json) — klon kalıbı
        self.ac, self.kapa, self.ayrac = "(", ")", ","
        self._alanlari_dizinle()

    def _alanlari_dizinle(self):
        for p in self.body.iter(q("p")):
            for kind, obj in segments(p):
                if kind != "f":
                    continue
                keys, js = field_keys(obj)
                if not keys:
                    continue
                disp = "".join(run_text(r) for r in obj if r.find(q("instrText")) is None
                               and r.find(q("fldChar")) is None)
                if self.sablon is None:
                    self.sablon = (obj, js)
                    d = disp.strip()
                    # görünen biçimi belgenin ilk alanından al: (n) ya da [n], "," ya da ", "
                    if d.startswith("["):
                        self.ac, self.kapa = "[", "]"
                    if ", " in d:
                        self.ayrac = ", "
                for ci in js["citationItems"]:
                    k = ci["uris"][0].rsplit("/", 1)[-1]
                    if len(keys) == 1 and (k not in self.alanlar or self.alanlar[k][1] is None):
                        self.alanlar[k] = (ci, disp.strip("()[] "))
                for ci in js["citationItems"]:
                    k = ci["uris"][0].rsplit("/", 1)[-1]
                    self.alanlar.setdefault(k, (ci, None))

    def numara(self, k):
        sart(k in self.alanlar or k in self.numara_esleme,
             "anahtar %s belgede hiçbir alanda yok (önce journal-s-zotero ile işaretleyip render edin)" % k)
        n = self.numara_esleme.get(k) or self.alanlar[k][1]
        sart(n and str(n).isdigit(),
             "%s için tek anahtarlı alan yok, numara okunamadı; numara_esleme ile verin" % k)
        return int(n)

    def gorunen(self, keys):
        return self.ac + self.ayrac.join(str(self.numara(k)) for k in keys) + self.kapa

    def yeni_metin_run(self, p, pos, text):
        tpl = template_run(p, pos)
        r = copy.deepcopy(tpl)
        for ch in list(r):
            if ch.tag != q("rPr"):
                r.remove(ch)
        t = etree.SubElement(r, q("t"))
        t.text = text
        t.set("{%s}space" % XML_NS, "preserve")
        rpr_set(r, strike=False, color=self.renk, drop_highlight=True)
        return r

    def alan_kur(self, p, pos, keys):
        sart(self.sablon is not None, "belgede klonlanacak ZOTERO_ITEM alanı yok")
        _, tpl_js = self.sablon
        keys = sorted(keys, key=self.numara)
        for k in keys:
            sart(k in self.alanlar, "anahtar %s belgede hiçbir alanda yok, klonlanamaz" % k)
        disp = self.gorunen(keys)
        js = copy.deepcopy(tpl_js)
        js["citationID"] = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
        js["citationItems"] = [copy.deepcopy(self.alanlar[k][0]) for k in keys]
        js["properties"] = {"formattedCitation": disp, "plainCitation": disp, "noteIndex": 0}
        instr = " ADDIN ZOTERO_ITEM CSL_CITATION " + json.dumps(js, ensure_ascii=False) + " "
        base = self.yeni_metin_run(p, pos, "")
        for ch in list(base):
            if ch.tag != q("rPr"):
                base.remove(ch)
        out = []
        for typ in ("begin", None, "separate", "result", "end"):
            r = copy.deepcopy(base)
            if typ in ("begin", "separate", "end"):
                fc = etree.SubElement(r, q("fldChar"))
                fc.set(q("fldCharType"), typ)
            elif typ is None:
                it = etree.SubElement(r, q("instrText"))
                it.text = instr
                it.set("{%s}space" % XML_NS, "preserve")
            else:
                t = etree.SubElement(r, q("t"))
                t.text = disp
            out.append(r)
        return out


def find_field(p, keyset):
    hits = []
    for kind, obj in segments(p):
        if kind == "f":
            keys, js = field_keys(obj)
            if keys and set(keys) == set(keyset):
                hits.append((obj, js))
    sart(len(hits) == 1, "anahtar kümesi %s olan alan sayısı %d (1 olmalı)" % (sorted(keyset), len(hits)))
    return hits[0]


# ---------- işlemler ----------
def op_strike(B, p, old):
    i = find_unique(p, old)
    cut_at(p, i)
    cut_at(p, i + len(old))
    for r in text_runs_between(p, i, i + len(old)):
        rpr_set(r, strike=True)
    return i + len(old)


def op_insert(B, p, anchor, text):
    i = find_unique(p, anchor)
    pos = i + len(anchor)
    cut_at(p, pos)
    r = B.yeni_metin_run(p, pos, text)
    element_before(p, pos).addnext(r)


def op_replace(B, p, old, new):
    end = op_strike(B, p, old)
    r = B.yeni_metin_run(p, end, new)
    element_before(p, end).addnext(r)


def op_field(B, p, anchor, keys):
    i = find_unique(p, anchor)
    pos = i + len(anchor)
    cut_at(p, pos)
    runs = B.alan_kur(p, pos, keys)
    anchor_el = element_before(p, pos)
    for r in reversed(runs):
        anchor_el.addnext(r)


def op_delfield(B, p, keyset):
    runs, _ = find_field(p, keyset)
    prev = runs[0].getprevious()
    for r in runs:
        p.remove(r)
    # önceki atıfla arasındaki tek boşluğu da kaldır
    if prev is not None and prev.tag == q("r") and run_text(prev).endswith(" ") \
            and prev.find(q("fldChar")) is None:
        set_text(prev, run_text(prev)[:-1])


def op_relink(B, p, keyset, newkeys):
    runs, js = find_field(p, keyset)
    newkeys = sorted(newkeys, key=B.numara)
    eldeki = {ci["uris"][0].rsplit("/", 1)[-1]: ci for ci in js["citationItems"]}
    items = []
    for k in newkeys:
        if k in eldeki:
            items.append(eldeki[k])          # sayfa/önek bilgisi korunur
        else:
            sart(k in B.alanlar, "anahtar %s belgede hiçbir alanda yok, eklenemez" % k)
            items.append(copy.deepcopy(B.alanlar[k][0]))
    disp = B.gorunen(newkeys)
    js["citationItems"] = items
    js.setdefault("properties", {})
    js["properties"]["formattedCitation"] = disp
    js["properties"]["plainCitation"] = disp
    its = [it for r in runs for it in r.iter(q("instrText"))]
    its[0].text = " ADDIN ZOTERO_ITEM CSL_CITATION " + json.dumps(js, ensure_ascii=False) + " "
    for it in its[1:]:
        it.text = ""
    res = [r for r in runs if r.find(q("t")) is not None]
    sart(res, "alanın görünen sonucu yok")
    set_text(res[0], disp)
    for r in res[1:]:
        set_text(r, "")


def op_pre(B, p, text):
    _, spans = composite(p)
    first = next((obj for a, b, kind, obj in spans if kind == "t" and b > a), None)
    sart(first is not None, "paragrafta metin run'ı yok")
    r = copy.deepcopy(first)
    for ch in list(r):
        if ch.tag != q("rPr"):
            r.remove(ch)
    t = etree.SubElement(r, q("t"))
    t.text = text
    t.set("{%s}space" % XML_NS, "preserve")
    rpr_set(r, strike=False, color=B.renk, drop_highlight=True)
    first.addprevious(r)


def op_fmt(B, p, old, new):
    """İşaretsiz doğrudan değişiklik; aralık birden çok metin run'ını geçebilir, alanı geçemez."""
    i = find_unique(p, old)
    cut_at(p, i)
    cut_at(p, i + len(old))
    runs = text_runs_between(p, i, i + len(old))
    sart(runs, "fmt: aralıkta run yok")
    set_text(runs[0], new)
    for r in runs[1:]:
        set_text(r, "")


def op_head(B, p, new):
    """Başlığın görünen metnini doğrudan değiştirir; sekme/alanlara dokunmaz."""
    runs = [obj for kind, obj in segments(p) if kind == "t" and run_text(obj)]
    ts = [t for r in runs for t in r.findall(q("t"))]
    sart(ts, "head: metin yok")
    ts[0].text = new
    for t in ts[1:]:
        t.text = ""


OPS = {  # op adı -> (fonksiyon, beklenen args sayısı)
    "strike": (op_strike, 1), "ins": (op_insert, 2), "rep": (op_replace, 2),
    "field": (op_field, 2), "delfield": (op_delfield, 1), "relink": (op_relink, 2),
    "pre": (op_pre, 1), "fmt": (op_fmt, 2), "head": (op_head, 1),
}


# ---------- işlem dosyası ----------
def islemleri_oku(yol):
    try:
        with open(yol, encoding="utf-8-sig") as f:
            veri = json.load(f)
    except (OSError, ValueError) as e:
        raise BicimHatasi("işlem dosyası okunamadı: %s" % e)
    if isinstance(veri, list):
        veri = {"islemler": veri}
    if not isinstance(veri, dict) or not isinstance(veri.get("islemler"), list):
        raise BicimHatasi("işlem dosyası bir liste ya da 'islemler' listesi taşıyan nesne olmalı")
    for n, e in enumerate(veri["islemler"], 1):
        if not isinstance(e, dict):
            raise BicimHatasi("#%d: işlem bir nesne olmalı" % n)
        sel, op, args = e.get("p"), e.get("op"), e.get("args", [])
        if not isinstance(sel, str) or len(sel) < 2 or sel[0] not in "^=":
            raise BicimHatasi("#%d: 'p' seçicisi '^metin' ya da '=metin' olmalı: %r" % (n, sel))
        if op not in OPS:
            raise BicimHatasi("#%d: bilinmeyen op %r (geçerli: %s)" % (n, op, ", ".join(OPS)))
        if not isinstance(args, list) or len(args) != OPS[op][1]:
            raise BicimHatasi("#%d: %s %d argüman bekler, %r verildi" % (n, op, OPS[op][1], args))
        if e.get("govde") and not veri.get("govde_baslangici"):
            raise BicimHatasi("#%d: 'govde': true için üst düzeyde 'govde_baslangici' gerekli" % n)
    renk = veri.get("renk")
    if renk is not None and not re.fullmatch(r"[0-9A-Fa-f]{6}", str(renk)):
        raise BicimHatasi("'renk' RRGGBB olmalı: %r" % renk)
    return veri


def kisa(x, n=60):
    s = x if isinstance(x, str) else json.dumps(x, ensure_ascii=False)
    s = s.replace("\n", " ")
    return s if len(s) <= n else s[:n - 1] + "…"


def uygula(root, veri, renk):
    B = Belge(root, renk, veri.get("numara_esleme"))
    tum = list(B.body.iter(q("p")))
    govde = tum
    if veri.get("govde_baslangici"):
        hedef = veri["govde_baslangici"]
        gi = next((i for i, p in enumerate(tum) if composite(p)[0].strip() == hedef), None)
        sart(gi is not None, "govde_baslangici paragrafı bulunamadı: %r" % hedef)
        govde = tum[gi:]
    memo = {}   # seçici ilk kullanımda sabitlenir (ilk düzeltmeden sonra da aynı paragraf)

    def bul(sel, govde_mi):
        anahtar = (sel, bool(govde_mi))
        if anahtar in memo:
            return memo[anahtar]
        mod, metin = sel[0], sel[1:]
        ps = govde if govde_mi else tum
        if mod == "=":
            hits = [p for p in ps if composite(p)[0].strip() == metin]
        else:
            hits = [p for p in ps if composite(p)[0].strip().startswith(metin)]
        sart(len(hits) == 1, "paragraf %r eşleşme sayısı %d (1 olmalı)" % (sel, len(hits)))
        memo[anahtar] = hits[0]
        return hits[0]

    satirlar = []
    for n, e in enumerate(veri["islemler"], 1):
        try:
            p = bul(e["p"], e.get("govde"))
            fn = OPS[e["op"]][0]
            args = [set(a) if (e["op"] in ("delfield", "relink") and i == 0) else a
                    for i, a in enumerate(e["args"])]
            fn(B, p, *args)
        except OpHatasi as ex:
            raise OpHatasi("#%d %s [%s] %s → %s" % (n, e["op"], kisa(e["p"], 40),
                                                   kisa(e["args"]), ex))
        satirlar.append("#%d %-8s %s | %s" % (n, e["op"], kisa(e["p"], 40), kisa(e["args"], 90)))
    return satirlar


def ayni_dosya(a, b):
    if os.path.exists(a) and os.path.exists(b):
        return os.path.samefile(a, b)
    return os.path.normcase(os.path.abspath(a)) == os.path.normcase(os.path.abspath(b))


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description="Onaylı düzeltmeleri mevcut bir docx'e işaretli uygular.")
    ap.add_argument("girdi")
    ap.add_argument("islemler")
    ap.add_argument("cikti")
    ap.add_argument("--apply", action="store_true", help="yaz (varsayılan: kuru çalışma)")
    ap.add_argument("--renk", help="giren metnin rengi RRGGBB (JSON 'renk' ve FF0000 üstünde)")
    ap.add_argument("--ustune-yaz", action="store_true", help="var olan ÇIKTININ üzerine yaz")
    a = ap.parse_args()

    try:
        if ayni_dosya(a.girdi, a.cikti):
            raise BicimHatasi("çıktı girdiyle aynı dosya; girdi asla üzerine yazılmaz")
        if not os.path.isfile(a.girdi):
            raise BicimHatasi("girdi yok: %s" % a.girdi)
        if a.renk is not None and not re.fullmatch(r"[0-9A-Fa-f]{6}", a.renk):
            raise BicimHatasi("--renk RRGGBB olmalı: %r" % a.renk)
        if a.apply and os.path.exists(a.cikti) and not a.ustune_yaz:
            raise BicimHatasi("çıktı zaten var: %s (bilerek yazılacaksa --ustune-yaz)" % a.cikti)
        veri = islemleri_oku(a.islemler)
    except BicimHatasi as ex:
        sys.stderr.write("HATA: %s\n" % ex)
        return 1

    renk = (a.renk or veri.get("renk") or VARSAYILAN_RENK).upper()
    with zipfile.ZipFile(a.girdi) as zin:
        root = etree.fromstring(zin.read("word/document.xml"))
        try:
            satirlar = uygula(root, veri, renk)
        except OpHatasi as ex:
            sys.stderr.write("HATA: işlem eşleşmedi, hiçbir şey yazılmadı: %s\n" % ex)
            return 2
        for s in satirlar:
            print(s)
        print("işlem sayısı: %d · renk: %s" % (len(satirlar), renk))
        if not a.apply:
            print("KURU çalışma — yazılmadı. Yazmak için --apply.")
            return 0
        new_xml = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
        hedef_klasor = os.path.dirname(os.path.abspath(a.cikti))
        os.makedirs(hedef_klasor, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix="journalwriter_docxisaretliduzelt_", suffix=".docx",
                                   dir=hedef_klasor)
        os.close(fd)
        try:
            with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
                for it in zin.infolist():
                    zout.writestr(it, new_xml if it.filename == "word/document.xml"
                                  else zin.read(it.filename))
            os.replace(tmp, a.cikti)
        except BaseException:
            if os.path.exists(tmp):
                os.remove(tmp)
            raise
    print("yazıldı: %s" % a.cikti)
    return 0


if __name__ == "__main__":
    sys.exit(main())

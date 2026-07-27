#!/usr/bin/env python3
"""
Bir dergi profili (JSON) alır ve bir .docx dosyasına mekanik biçimlendirme
kurallarını (yazı tipi, boyut, satır aralığı, kenar boşlukları, sayfa boyutu)
uygular. Kaynakça/atıf stili bu betikte yapılmaz ve bu plugin'de yalnızca
`journal-s-zotero` ajanının yetkisindedir (zotero_cite.py). Bölüm sırası gibi diğer
anlamsal kontroller journalstyle akışının kalanında ele alınır.

Kullanım:
    python apply_profile.py <girdi.docx> <profil.json> <cikti.docx>
"""
import os
import sys
import json
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_LINE_SPACING

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from docx_util import iter_paragraphs, iter_runs, to_float, utf8_stdout  # noqa: E402

WARNINGS = []


def warn(msg):
    WARNINGS.append(msg)
    sys.stderr.write("UYARI: " + msg + "\n")


_MARGIN_ATTRS = {"top": "top_margin", "bottom": "bottom_margin",
                 "left": "left_margin", "right": "right_margin"}


def apply_page_setup(doc, fmt):
    margins = fmt.get("margins_cm") or {}
    page_size = fmt.get("page_size")
    missing = [k for k in _MARGIN_ATTRS if margins and margins.get(k) is None]
    if missing:
        warn(f"margins_cm eksik alan(lar): {', '.join(sorted(missing))} — bu kenar "
             "boşlukları belgede olduğu gibi bırakıldı.")
    bad = []
    for section in doc.sections:
        for key, attr in _MARGIN_ATTRS.items():
            value = margins.get(key)
            if value is None:
                continue
            cm = to_float(value)          # "2,5" (Türkçe ondalık) da kabul edilir
            if cm is None:
                if key not in bad:
                    bad.append(key)
                continue
            setattr(section, attr, Cm(cm))
    for key in bad:
        warn(f"margins_cm.{key} = '{margins.get(key)}' sayıya çevrilemedi — bu kenar "
             "boşluğu belgede olduğu gibi bırakıldı.")
        if page_size == "A4":
            section.page_width = Cm(21.0)
            section.page_height = Cm(29.7)
        elif page_size == "Letter":
            section.page_width = Cm(21.59)
            section.page_height = Cm(27.94)
        elif page_size:
            warn(f"page_size '{page_size}' tanınmadı (A4/Letter bekleniyor) — sayfa "
                 "boyutuna dokunulmadı.")


_SPACING_MAP = {
    "single": WD_LINE_SPACING.SINGLE,
    "double": WD_LINE_SPACING.DOUBLE,
    "1.5": WD_LINE_SPACING.ONE_POINT_FIVE,
}


def _spacing_setter(spacing):
    """Return a function that applies `spacing` to a paragraph_format, or None.

    Accepts both the named forms ("single"/"double"/"1.5") and a raw number
    (2, 1.5, "2,0") — a profile written from author guidelines may carry either.
    """
    if spacing is None:
        return None
    key = str(spacing).strip().lower()
    if key in _SPACING_MAP:
        rule = _SPACING_MAP[key]
        def _apply(pf):
            pf.line_spacing_rule = rule
        return _apply
    try:
        value = float(key.replace(",", "."))
    except ValueError:
        warn(f"line_spacing '{spacing}' tanınmadı (single/double/1.5 veya sayı "
             "bekleniyor) — satır aralığına dokunulmadı.")
        return None
    if value <= 0:
        warn(f"line_spacing '{spacing}' geçersiz — satır aralığına dokunulmadı.")
        return None
    def _apply(pf):
        pf.line_spacing = value
    return _apply


def apply_font_and_spacing(doc, fmt):
    font_family = fmt.get("font_family")
    font_size = fmt.get("font_size_pt")
    set_spacing = _spacing_setter(fmt.get("line_spacing"))

    # Normal stilini güncelle (çoğu run buradan miras alır)
    normal_style = doc.styles["Normal"]
    if font_family:
        normal_style.font.name = font_family
    if font_size:
        normal_style.font.size = Pt(font_size)
    if set_spacing:
        set_spacing(normal_style.paragraph_format)

    # Gövde + tablo hücreleri + üstbilgi/altbilgi: doğrudan (run-level) biçimlendirme
    # stilden miras almadığı için her paragraf ve run'a açıkça uygulanır.
    # iter_runs(): köprü (<w:hyperlink>) içindeki run'lar da dâhil — `Paragraph.runs`
    # yalnız doğrudan çocukları görür ve kaynakçadaki DOI köprüleri eski fontta kalırdı.
    for para in iter_paragraphs(doc):
        if set_spacing:
            set_spacing(para.paragraph_format)
        for run in iter_runs(para):
            if font_family:
                run.font.name = font_family
            if font_size:
                run.font.size = Pt(font_size)


def report_unapplied(profile):
    """Bu betiğin OTOMATİK uygulamadığı, manuel/agent gerektiren alanları listeler."""
    manual_items = []
    if profile.get("citation_style"):
        manual_items.append(
            f"Kaynakça/atıf stili '{profile['citation_style'].get('name')}' -> `journal-s-zotero` ajanı (zotero_cite.py) ile uygulanmalı."
        )
    if profile.get("required_sections"):
        manual_items.append(
            f"Zorunlu bölümler kontrol edilmeli: {', '.join(profile['required_sections'])}"
        )
    if profile.get("section_order"):
        manual_items.append("Bölüm sırası otomatik yeniden düzenlenmedi, manuel/skill seviyesinde kontrol gerekir.")
    if profile.get("notes"):
        manual_items.append(f"Not: {profile['notes']}")
    return manual_items


def main():
    utf8_stdout()
    if len(sys.argv) != 4:
        print("Kullanım: python apply_profile.py <girdi.docx> <profil.json> <cikti.docx>")
        sys.exit(1)

    input_path, profile_path, output_path = sys.argv[1:4]

    with open(profile_path, "r", encoding="utf-8") as f:
        profile = json.load(f)

    doc = Document(input_path)
    fmt = profile.get("formatting", {})

    apply_page_setup(doc, fmt)
    apply_font_and_spacing(doc, fmt)

    doc.save(output_path)

    print(f"Kaydedildi: {output_path}")
    if WARNINGS:
        print("\n--- Uygulanamayan Profil Alanları ---")
        for w in WARNINGS:
            print(f"- {w}")
    manual_items = report_unapplied(profile)
    if manual_items:
        print("\n--- Manuel/Agent Kontrolü Gereken Maddeler ---")
        for item in manual_items:
            print(f"- {item}")


if __name__ == "__main__":
    main()

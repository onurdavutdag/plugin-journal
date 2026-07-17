#!/usr/bin/env python3
"""
Bir dergi profili (JSON) alır ve bir .docx dosyasına mekanik biçimlendirme
kurallarını (yazı tipi, boyut, satır aralığı, kenar boşlukları, sayfa boyutu)
uygular. Kaynakça/atıf stili bu betikte yapılmaz ve bu plugin'de yalnızca
`zotero` skill'inin yetkisindedir (zotero_cite.py). Bölüm sırası gibi diğer
anlamsal kontroller journalstyle akışının kalanında ele alınır.

Kullanım:
    python apply_profile.py <girdi.docx> <profil.json> <cikti.docx>
"""
import sys
import json
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_LINE_SPACING


CM_TO_TWIPS = lambda cm: Cm(cm)  # python-docx handles conversion internally


def apply_page_setup(doc, fmt):
    margins = fmt.get("margins_cm")
    page_size = fmt.get("page_size")
    for section in doc.sections:
        if margins:
            section.top_margin = Cm(margins["top"])
            section.bottom_margin = Cm(margins["bottom"])
            section.left_margin = Cm(margins["left"])
            section.right_margin = Cm(margins["right"])
        if page_size == "A4":
            section.page_width = Cm(21.0)
            section.page_height = Cm(29.7)
        elif page_size == "Letter":
            section.page_width = Cm(21.59)
            section.page_height = Cm(27.94)


def apply_font_and_spacing(doc, fmt):
    font_family = fmt.get("font_family")
    font_size = fmt.get("font_size_pt")
    spacing = fmt.get("line_spacing")

    spacing_map = {
        "single": WD_LINE_SPACING.SINGLE,
        "double": WD_LINE_SPACING.DOUBLE,
        "1.5": WD_LINE_SPACING.ONE_POINT_FIVE,
    }

    # Normal stilini güncelle (çoğu run buradan miras alır)
    normal_style = doc.styles["Normal"]
    if font_family:
        normal_style.font.name = font_family
    if font_size:
        normal_style.font.size = Pt(font_size)
    if spacing in spacing_map:
        normal_style.paragraph_format.line_spacing_rule = spacing_map[spacing]

    # Belge içindeki tüm paragraf ve run'lara da açıkça uygula
    # (bazı Word şablonlarında doğrudan run-level override olabilir)
    for para in doc.paragraphs:
        if spacing in spacing_map:
            para.paragraph_format.line_spacing_rule = spacing_map[spacing]
        for run in para.runs:
            if font_family:
                run.font.name = font_family
            if font_size:
                run.font.size = Pt(font_size)


def report_unapplied(profile):
    """Bu betiğin OTOMATİK uygulamadığı, manuel/agent gerektiren alanları listeler."""
    manual_items = []
    if profile.get("citation_style"):
        manual_items.append(
            f"Kaynakça/atıf stili '{profile['citation_style'].get('name')}' -> `zotero` skill'i (zotero_cite.py) ile uygulanmalı."
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
    manual_items = report_unapplied(profile)
    if manual_items:
        print("\n--- Manuel/Agent Kontrolü Gereken Maddeler ---")
        for item in manual_items:
            print(f"- {item}")


if __name__ == "__main__":
    main()

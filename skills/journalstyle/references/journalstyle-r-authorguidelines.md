# Dergi Profili Şeması

`journalstyle-s-authorguidelines` agent'ının üretmesi, `journalstyle` skill'inin okuması gereken JSON yapısı budur. Bilinmeyen/doğrulanamayan alanlar `null` bırakılır, uydurulmaz.

```json
{
  "journal_name": "Journal of Example Research",
  "publisher": "Elsevier",
  "source_url": "https://www.elsevier.com/journals/.../guide-for-authors",
  "last_verified": "2026-07-05",
  "guidelines_source": "web",
  "article_types": ["research article", "review"],
  "word_limit": {
    "value": 8000,
    "excludes": ["references", "abstract", "figure captions"]
  },
  "abstract": {
    "max_words": 250,
    "structured": false,
    "keywords_min": 4,
    "keywords_max": 6
  },
  "formatting": {
    "font_family": "Times New Roman",
    "font_size_pt": 12,
    "line_spacing": "double",
    "margins_cm": {"top": 2.5, "bottom": 2.5, "left": 2.5, "right": 2.5},
    "page_size": "A4",
    "heading_style": "numbered",
    "line_numbers": true
  },
  "section_order": [
    "Title Page", "Abstract", "Keywords", "Introduction", "Methods",
    "Results", "Discussion", "Conclusion", "Declarations",
    "References", "Tables", "Figures"
  ],
  "required_sections": [
    "Declaration of Competing Interest", "Data Availability Statement",
    "Author Contributions", "Funding"
  ],
  "citation_style": {
    "name": "Vancouver",
    "in_text": "numbered",
    "reference_list_style": "numbered-order-of-appearance"
  },
  "figures_tables": {
    "placement": "end-of-manuscript",
    "numbering": "Figure 1, Figure 2 ...",
    "caption_position": "below-figure-above-table"
  },
  "file_format": {
    "accepted": [".docx", ".tex"],
    "figure_formats": [".tiff", ".eps", ".png (min 300dpi)"]
  },
  "notes": "Doğrulanamayan veya belirsiz kalan noktalar için serbest metin."
}
```

## Doldurma kuralları

- `source_url` mutlaka gerçek "Author Guidelines" sayfası olmalı; genel dergi ana sayfası kabul edilmez.
- `last_verified` her araştırmada güncellenir; skill 6 aydan eski profillerde kullanıcıya yeniden doğrulama önerir.
- Sayısal olmayan/karmaşık kurallar (örn. "şekil telif izni gerekiyorsa ek belge") `notes` alanına yazılır, `apply_profile.py` bunları otomatik uygulamaz — kullanıcıya manuel adım olarak raporlanır.
- **`guidelines_source`** kuralın kaynağını gösterir: `"web"` = yalnız web araması; `"user-pdf"` =
  yalnız workspace'teki `authorguidelines-pdf/<slug>/` PDF'i; `"both-merged"` = kullanıcı checkpoint'te
  web + PDF'i birleştirmeyi seçti; `"both-unmerged"` = agent'ın döndürdüğü **taslak** aşama (henüz
  birleştirilmedi).
- **Web + PDF akışı (checkpoint):** `journalstyle-s-authorguidelines` agent'ı **her zaman web araması**
  yapar; workspace'te PDF varsa ondan da **ayrıca** çıkarır ve **iki ayrı set** döndürür:
  `web_findings` + `pdf_findings` (+ kısa `web_ozet`). Agent bunları **birleştirmez** ve final
  `<slug>.json`'ı yazmaz. Skill, `web_ozet`'i kullanıcıya gösterip *birleştir / sadece web / sadece
  PDF / manuel* kararını alır, sonra final tek profili `<profiles_dir>/<slug>.json`'a yazar ve
  `guidelines_source`'u karara göre ayarlar. Çelişkiler (web vs PDF) `notes`'a yazılır.

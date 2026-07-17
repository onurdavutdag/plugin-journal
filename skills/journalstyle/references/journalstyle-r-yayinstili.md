# Yayın Stili Şeması (Published Style)

`journalstyle-s-yayinstili` agent'ının üretmesi, `journalstyle` skill'inin okuması gereken
JSON yapısı budur. Bu dosya, resmi kural profilinden (`journalstyle-r-authorguidelines.md`) **ayrıdır**: resmi
kural değil, dergide **yayınlanmış gerçek makalelerden gözlemlenen fiili gelenekleri** tutar.
Bilinmeyen/erişilemeyen alanlar `null` bırakılır, uydurulmaz.

**Birincil kaynak = yerel yüklenen PDF'ler.** Kullanıcı hedef dergiye ait örnek makaleleri
**workspace'teki** `yayinstili-pdf/<slug>/` klasörüne PDF olarak koyar (slug, `journal-profiles/*.json`
ile aynı; workspace = kaynak `.docx`'in klasörü, skill `workspace.py` ile çözer). Agent stili
**önce bu PDF'lerden** (`extract_pdf_text.py` ile) çıkarır ve `style_source: "user-pdf"` yazar;
bu klasör yok/boşsa web aramasına düşer (`journal-auto`).

```json
{
  "journal_name": "The Spine Journal (TSJ)",
  "slug": "thespinejournal",
  "last_analyzed": "2026-07-11",
  "draft_topic_keywords": ["lumbar fusion", "spondylolisthesis", "PROMs"],
  "style_source": "user-pdf",
  "sample_selection": "yerel yüklenen PDF'ler (workspace: yayinstili-pdf/<slug>/); yoksa web: konu-benzeri, son 5 yıl, açık erişim",
  "sample_urls": [
    "2025 Ardelt. Risk factors ... The Spine Journal.pdf",
    "2025 Huybregts. Hounsfield unit ... The Spine Journal.pdf"
  ],
  "sample_n": 5,
  "structure": {
    "tables_per_article": {"median": 3, "range": [1, 6]},
    "table_numbering": "Table 1, Table 2 ... (metinde geçiş sırası)",
    "table_caption_position": "above-table",
    "table_notes_style": "tablo altında dipnot, sembollerle (*, †, ‡)",
    "figures_per_article": {"median": 2, "range": [0, 5]},
    "figure_numbering": "Figure 1, Figure 2 ...",
    "figure_panel_labeling": "A, B, C alt panel",
    "figure_caption_position": "below-figure",
    "caption_format": "'Table N.' + kalın kısa başlık + açıklayıcı cümle; kısaltmalar dipnotta (KURAL — verbatim caption metni DEĞİL)",
    "reference_count": {"median": 35, "range": [20, 60]},
    "de_facto_headings": ["Introduction", "Methods", "Results", "Discussion", "Conclusion"],
    "section_order": ["Introduction", "Methods", "Results", "Discussion", "Conclusion"],
    "abstract_de_facto": {
      "structured": true,
      "heading_count": 4,
      "headings": ["Background", "Methods", "Results", "Conclusions"],
      "word_count": {"median": 248, "range": [220, 265]}
    },
    "article_word_count": {"median": 3200, "range": [2600, 4100]}
  },
  "text_style": {
    "tense_by_section": {
      "introduction": "present+past",
      "methods": "past",
      "results": "past",
      "discussion": "present+past (genel doğrular present)"
    },
    "passive_voice_ratio": "~%60 edilgen (Methods yoğun)",
    "first_person_usage": "'we' kullanılıyor (Methods & Discussion)",
    "avg_sentence_length": {"median_words": 22, "range": [18, 28]},
    "in_text_citation_format": "numaralı superscript [1,2]",
    "citation_density": "~1 atıf / 2-3 cümle; Giriş ve Tartışma yoğun",
    "stats_presentation": "mean ± SD, %95 CI parantez içinde, p<0.001 biçimi"
  },
  "notes": "Erişim/paywall kısıtları, konu-benzeri örnek bulunamadıysa fallback bilgisi ve resmi kuralla çelişkiler serbest metin olarak buraya yazılır."
}
```

## Doldurma kuralları

- `style_source`:
  - `"user-pdf"` = stil workspace'teki `yayinstili-pdf/<slug>/` altındaki **yerel yüklenen PDF'lerden**
    çıkarıldı (birincil, varsayılan yol).
  - `"journal-auto"` = yerel PDF yoktu, dergiden **web** otomatik seçimine düşüldü (yedek).
  - `"user-supplied"` = yalnız `user_reference_article` ile verilen tek makale.
  - `"both"` = yerel PDF/kullanıcı makalesi + web dergi örnekleri birlikte.
- Her sayısal metrik (`tables_per_article`, `figures_per_article`, `reference_count`) kaç
  kaynaktan hesaplandıysa `sample_n` bunu yansıtır; incelenen kaynaklar `sample_urls` altında
  listelenir — **yerel PDF'lerde URL yerine dosya adları** yazılır (kullanıcı makalesi verildiyse
  o da bu listeye dahildir). Kaynağın yerel PDF olduğu `notes`'a düşülür.
- Erişilemeyen (paywall) veya tek örnekten güvenilir çıkarılamayan alanlar `null` bırakılır ve
  nedeni `notes`'a yazılır — tahmin üretilmez.
- `avg_sentence_length` ve `passive_voice_ratio` yalnızca **tam metin** fetch edildiyse hesaplanır;
  abstract-only erişimde ilgili alan `null` bırakılır ve nedeni `notes`'a yazılır.
- `article_word_count` fiili yayın uzunluğu **gözlemidir**, kelime LİMİTİ değildir; resmi limit
  `<slug>.json`'dadır. `in_text_citation_format` gözlemlenen atıf biçimidir; resmi `citation_style`
  yine `<slug>.json`'dadır, çelişirse `notes`'a düşülür.
- **Telif:** profile örnek makalelerden **hiçbir cümle, caption veya abstract metni verbatim
  kopyalanmaz**; yalnızca sayısal metrik ve **kural olarak ifade edilen** yapısal örüntü tutulur
  (ör. `caption_format` gerçek caption metni değil, biçim kuralıdır).
- Şema büyüdüğünde eski önbellek JSON'larında bulunmayan yeni alanlar `null` kabul edilir; sonraki
  çalıştırma doldurur.
- Bu dosya resmi profildeki (`<slug>.json`) `formatting`/`figures_tables` kurallarını **ezmez**;
  onlarla çelişirse çelişki `notes`'ta belirtilir (gözlem typeset son hâlden gelebilir).
- `last_analyzed` her çalıştırmada güncellenir; skill tazeliği kontrol edip gerekirse yeniden
  çalıştırmayı kullanıcıya sorar.

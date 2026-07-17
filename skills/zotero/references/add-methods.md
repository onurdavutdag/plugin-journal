# Kaynak ekleme — Zotero'nun 5 yöntemi

Hepsi aynı sonuca varır: **doğrulanmış** bir CSL kaydı. Uydurma künye asla —
her alan ya kaynağın kendisinden ya PubMed/CrossRef doğrulamasından gelir.

## 1. Kimlik ile (Add by Identifier) — DOI / PMID / ISBN / arXiv

- **PMID** → `mcp__claude_ai_PubMed__get_article_metadata` ile künyeyi çek.
- **DOI** → `mcp__claude_ai_PubMed__convert_article_ids` ile PMID'ye çevir,
  sonra metadata çek; PubMed'de yoksa DOI'yi `https://doi.org/<doi>` üzerinden
  WebFetch ile çöz (CrossRef içeriği döner).
- **ISBN** (kitap) → WebSearch ile yayıncı/WorldCat künyesi; emin değilsen
  kullanıcıya alanları onaylat.
- **arXiv** → `https://arxiv.org/abs/<id>` sayfasından künye.

## 2. Veritabanı / tarayıcı çıktısı

Kullanıcı PubMed/Scopus sayfası veya künye metni yapıştırır → ayrıştır →
başlık+yazar+yıl ile `mcp__claude_ai_PubMed__lookup_article_by_citation`
çağırıp DOI/PMID doğrula.

## 3. PDF'den (sürükle-bırak karşılığı)

1. PDF'in ilk sayfasını Read ile aç (veya `search_pdfs.py` ile tara) —
   başlık, yazarlar, dergi, DOI genelde ilk sayfada/altbilgide.
2. Eksik DOI/PMID → `lookup_article_by_citation` (başlık+yazar+yıl) ile kurtar.
3. Doğrulanamayan alanları boş bırak, kullanıcıya bildir.

## 4. Manuel giriş

Kullanıcı alanları verir. Zorunlu asgari: başlık, yazar(lar), yıl, kaynak türü.
Dergi makalesinde DOI/PMID'yi PubMed'den doğrulamayı **her zaman** dene.

## 5. İçe aktarma (.ris / .bib)

- `.ris`: `TY`, `AU`, `TI`, `T2/JO`, `PY`, `VL`, `IS`, `SP-EP`, `DO` etiketleri.
- `.bib`: `@article{...}` alanları (`author`, `title`, `journal`, `year`,
  `volume`, `number`, `pages`, `doi`).
- Her kaydı ayrıştır → de-duplikasyon kontrolü (aynı DOI/PMID = aynı makale,
  bkz. `references/citation-format.md`) → doğrula.

## Gerçek kütüphaneye yazma — yalnız canlı API

Zotero **açıkken** (`zotero_lib.py --status` → `live_api: true`):

```
POST http://127.0.0.1:23119/connector/saveItems
Content-Type: application/json

{"items": [{"itemType": "journalArticle", "title": "...",
            "creators": [{"firstName": "...", "lastName": "...", "creatorType": "author"}],
            "date": "2016", "publicationTitle": "...", "volume": "...",
            "issue": "...", "pages": "...", "DOI": "...",
            "extra": "PMID: 27542303"}],
 "uri": "http://localhost/claude-zotero-skill"}
```

- PMID `extra` alanına `PMID: <n>` biçiminde yazılır (Zotero geleneği).
- Yanıt 201 → kayıt kullanıcının kütüphanesine düştü; `zotero_lib.py --search`
  ile teyit et.
- Zotero kapalıysa: kaydı JSON olarak hazırla, kullanıcıya göster,
  "Zotero'yu açınca ekleyeyim" de. **sqlite'a asla doğrudan yazma.**
- Eklemeden önce de-duplikasyon: `zotero_lib.py --search "<doi veya başlık>"` —
  aynı DOI/PMID varsa ekleme, mevcut item'ın anahtarını kullan.

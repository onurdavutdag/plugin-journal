---
name: zotero
description: >-
  Kullanıcının bilgisayarındaki GERÇEK Zotero kütüphanesine bağlanan referans
  yöneticisi. Zotero'nun iş akışını taklit eder: kütüphaneyi/dermeleri listeler,
  kimlik (DOI/PMID/ISBN/arXiv) ile kaynak ekler, Word (.docx) içine metin-içi
  atıf ve otomatik kaynakça basar, stil değişince yeniden numaralar (Refresh),
  atıfları sabitler (Unlink). Tetikleyiciler: "zotero", "kütüphaneme ekle",
  "kütüphanemde ne var", "referans ekle", "kaynakça oluştur", "atıf ekle",
  "DOI ile ekle", "PMID ile ekle", "Word'e kaynakça bas", "atıf stilini
  değiştir", "dermelerimi listele", "Zotero'daki makalelerim". Kullanıcı
  Zotero'daki kaynaklarına dayalı herhangi bir atıf/kaynakça işi istediğinde
  bu skili kullan. Keywords: Zotero, reference manager, kaynakça, atıf,
  bibliography, citation, collection, derme, DOI, PMID, RIS, BibTeX.
---

# zotero — Gerçek Zotero'ya bağlı referans yöneticisi

Kullanıcının kurulu Zotero'suna bağlanırsın (veri dizini: `$ZOTERO_DATA_DIR`
yoksa `~/Zotero`). Zotero'nun yaptığı işi yaparsın: toplama, düzenleme, atıf.

## Tek-sahip kuralı — docx kaynakçası yalnız burada

**Bir `.docx` içinde metin-içi atıf ve kaynakça listesinin eklenmesi, çıkarılması,
güncellenmesi ve stil dönüşümü YALNIZCA bu skill'in yetkisindedir.** Başka hiçbir
skill/agent (writer, journalstyle, research) kaynakçaya dokunmaz; onlar kaynağı
bulur/doğrular (research), metni yazar (writer, `{{zref:KEY}}` işaretçisi basar),
mekanik biçim uygular (journalstyle) — atıf/kaynakça mekaniğini bu skile devreder.
Kanonik biçim tanımı: `references/citation-format.md`.

## Ana kural — research'ten miras

**Hiçbir künyeyi uydurma.** Her kayıt ya kullanıcının gerçek Zotero item'ından
gelir ya da doğrulanmış DOI/PMID'den (PubMed MCP / `research` skill'i ile).
Doğrulanamayan kaynak eklenmez; bu durumda açıkça söylenir.

## Bağlantı katmanı

```
python scripts/zotero_lib.py --status              # backend durumu
python scripts/zotero_lib.py --list-collections    # dermeler
python scripts/zotero_lib.py --items [--collection "tez c2"] [--limit N]
python scripts/zotero_lib.py --get ITEMKEY
python scripts/zotero_lib.py --search "terim"
```

- **sqlite (birincil):** `zotero.sqlite` kopyalanıp okunur — Zotero **kapalıyken
  de çalışır**. Çıktı CSL-JSON benzeri; `attachments` alanı gerçek
  `storage\` PDF yollarını verir.
- **Canlı yerel API (ikincil):** Zotero 7 açıkken `http://127.0.0.1:23119`.
  Kütüphaneye **yazma** (yeni kayıt ekleme) yalnız bu yolla yapılır — bkz.
  `references/add-methods.md`. sqlite'a asla doğrudan yazma (kütüphaneyi bozar).
- Zotero kapalı + yazma istendi → kaydı hazırla, kullanıcıya "Zotero'yu aç"
  de, açılınca gönder.

## Zotero kavram eşlemesi

| Zotero | Bu skill |
|---|---|
| Collections (Dermeler) | `--list-collections`, `--collection` filtresi |
| Add by Identifier | `references/add-methods.md` yöntem 1 (DOI/PMID/ISBN/arXiv) |
| PDF sürükle-bırak | yöntem 3 (metadata çıkarımı + PubMed doğrulama) |
| .ris/.bib içe aktarma | yöntem 5 |
| Add/Edit Citation | `zotero_cite.py` işaretçi: `{{zref:ITEMKEY}}` veya `[@ITEMKEY]` |
| Add/Edit Bibliography | `zotero_cite.py --action refresh` (sona "Kaynaklar" basar) |
| Refresh (akıllı metin) | her `refresh` çağrısı yeniden numaralar + kaynakçayı günceller |
| Unlink Citations | `--action unlink` (dergi istemedikçe önerme — geri dönüşü yok) |
| Style Repository | `references/styles.md` (yerel CSL → Style Repository; biçimi zotero uygular) |

## Word akışı (Add/Edit Citation + Bibliography)

1. Kullanıcının metnindeki atıf noktalarına işaretçi koy/koydur:
   `{{zref:ITEMKEY}}` — anahtar `zotero_lib.py --search` ile bulunur. Gramerin tam tanımı
   (gruplu `{{zref:KEY1;KEY2}}`, `[@ITEMKEY]` alias, eksik anahtar davranışı):
   `references/zref-protocol.md`.
2. Çalıştır:
   ```
   python scripts/zotero_cite.py --docx makale.docx [--style vancouver|author-date]
                                 [--mode field|text] [--out cikti.docx]
                                 [--heading "References"] [--no-red]
   ```
   - Numaralı stilde geçiş sırasına göre `[1]`, `[2]`…; yazar-yıl stilinde
     `(Yazar, Yıl)`; kaynakça otomatik.
   - **`--mode field` (varsayılan): çıktı GERÇEK Zotero alan kodudur**
     (`ADDIN ZOTERO_ITEM CSL_CITATION` + `ZOTERO_PREF` + `ZOTERO_BIBL`).
     Kullanıcının Zotero uygulaması bu atıfları **tanır**: Word'de Zotero
     sekmesi → Refresh yeniden numaralar, Document Preferences ile stil
     değiştirilebilir (kullanıcının Zotero 7 + Word kurulumunda doğrulandı).
     Tekrarlanan script çağrısı yalnız YENİ işaretçileri alana çevirir; mevcut
     `ZOTERO_*` alanlarına asla dokunmaz — onların sahibi artık Zotero'dur.
   - **`--mode text`**: eski statik metin davranışı. Tekrarlanan çağrı =
     Refresh: yeniden numaralar, kaynakçayı yeniden yazar (idempotent —
     işaretçiler belgede kalır). Zotero uygulaması bu atıfları görmez;
     güncelleme yalnız bu skill üzerinden.
   - **Mevcut** docx güncellenirken eklenen metin **kırmızı** (global kural);
     sıfırdan üretilen belgede `--no-red`.
3. Dergiye özel ince stil → `references/styles.md` akışı (yerel CSL → Style
   Repository); biçimi **bu skill** uygular, başka agent/skill'e devretme.
   Field modunda kullanıcı stili doğrudan Zotero uygulamasından da değiştirebilir.
4. Teslimden önce (dergi isterse) sabitle: field modunda Zotero'nun kendi
   **Unlink Citations** düğmesi; text modunda `--action unlink`.

## Kanıt köprüsü

Kullanıcının Zotero `storage\` klasöründeki PDF'ler, `research`/`writer` için
tier-2 kanıt kaynağıdır — bkz. `references/storage-bridge.md`.

## Rapor künyesi (zorunlu)

Kullanıcıya sunulan her rapor/işlem özeti, başlığın hemen altında şu künye bloğuyla başlar; o
çalışmada **fiilen** okunan reference'lar listelenir (subagent yok → `—`; kullanılmayan `—`):

```
Skill: zotero
Subagent: —
References: <okunanlar: add-methods.md / styles.md / storage-bridge.md / citation-format.md>
---
```

## Referans dosyaları

- `references/zref-protocol.md` — `{{zref:ITEMKEY}}` işaretçi grameri (writer↔zotero devir sözleşmesi).
- `references/citation-format.md` — metin-içi atıf + kaynakça biçimi (Vancouver taban), de-duplikasyon.
- `references/add-methods.md` — 5 ekleme yöntemi + kütüphaneye yazma (saveItems).
- `references/styles.md` — Vancouver taban, dergiye özel stil çözümleme sırası.
- `references/storage-bridge.md` — storage PDF'lerini kanıt aramasına katma.

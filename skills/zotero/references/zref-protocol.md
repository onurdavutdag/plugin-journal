# zref devir protokolü — SAHİBİ: zotero

Metin yazan skill (`writer`) ile atıf/kaynakça basan skill (`zotero`) arasındaki **tek işaretçi
sözleşmesi** burada tanımlıdır. `writer`/`research`/`journalstyle` yalnızca işaretçi **basar**;
işaretçiyi görünür atıfa ve kaynakçaya çeviren tek yetkili `zotero`'dur (`zotero_cite.py`).
Metin-içi atıf/kaynakça **biçimi** için: `citation-format.md`. İşaretçi **grameri** için: bu dosya.

## Gramer (koddan doğrulanmıştır)

`zotero_cite.py` işaretçileri şu regex ile ayrıştırır:

```
MARKER_RE = re.compile(r"\{\{zref:([A-Z0-9;\s]+)\}\}|\[@([A-Z0-9;\s]+)\]")
```

Yani iki eşdeğer biçim desteklenir:

| Biçim | Tekli | Gruplu (aynı cümlede birden çok kaynak) |
|---|---|---|
| **Kanonik** (bunu bas) | `{{zref:ITEMKEY}}` | `{{zref:KEY1;KEY2}}` |
| Kabul edilen alias (Pandoc) | `[@ITEMKEY]` | `[@KEY1;KEY2]` |

- **`ITEMKEY`** = 8 haneli büyük-harf/rakam Zotero item anahtarı (ör. `F5RI4K5K`).
  `zotero_lib.py --search "terim"` ile bulunur.
- Gruplu atıfta anahtarlar **noktalı virgülle** (`;`) ayrılır; araya boşluk konabilir.
- **Yazan skill her zaman kanonik biçimi (`{{zref:ITEMKEY}}`) basar.** `[@...]` biçimi geriye
  dönük uyumluluk için ayrıştırılır (ör. Pandoc'tan gelen metin); yeni metinde kullanma.

## Kim ne basar

- **writer / research / journalstyle:** cümlenin desteklendiği tam yere `{{zref:ITEMKEY}}` koyar.
  Ham sayı (`[1]`), `(Yazar, Yıl)` veya kaynakça listesi **yazmaz** — o zotero'nun işi.
  Anahtarı olmayan kaynak için: önce `add-methods.md` ile kütüphaneye eklet, anahtarı al, sonra bas.
- **zotero (`zotero_cite.py`):** her işaretçiyi seçilen stilde metin-içi atıfa çevirir, geçiş
  sırasına göre numaralar ve kaynakçayı sona yazar.

## Render davranışı (net sözleşme)

- **Field modu (varsayılan, `--mode field`):** her işaretçi gerçek Zotero Word alanı olur
  (`ADDIN ZOTERO_ITEM CSL_CITATION` + `ZOTERO_PREF` + `ZOTERO_BIBL`). Kullanıcının Zotero
  uygulaması tanır; yeniden numaralama/stil değişimi Word'deki Zotero sekmesinden yapılır.
  Tekrar çağrı **yalnız YENİ işaretçileri** alana çevirir; mevcut `ZOTERO_*` alanlarına dokunmaz.
- **Text modu (`--mode text`):** statik metin; tekrar çağrı = Refresh (yeniden numaralar,
  kaynakçayı yeniden yazar). Script içinde **idempotent** — işaretçiler belgede kalır.
- **Eksik anahtar:** kütüphanede bulunamayan anahtar **uydurulmaz**; `zotero_cite.py` çıktısındaki
  JSON raporunda `unknown_keys` altında listelenir. Yazan skill bu anahtarı düzeltir veya
  kaynağı `add-methods.md` ile ekler.
- **Mükerrer kaynak:** aynı DOI/PMID = aynı makale; de-duplikasyon **render sırasında** yapılır
  (bkz. `citation-format.md` → "De-duplikasyon"). Aynı kaynağa her yerde **aynı** anahtarı bas.
- **Kırmızı revizyon:** mevcut docx güncellenirken eklenen atıf/kaynakça metni kırmızıdır
  (global kural); sıfırdan belgede `--no-red`.

## Özet kural

Tek kanonik işaretçi `{{zref:ITEMKEY}}`; gramer bu dosyada, biçim `citation-format.md`'de,
kütüphaneye ekleme `add-methods.md`'de. Başka hiçbir skill atıf/kaynakça biçimlemez.

# Atıf stilleri — çözümleme sırası (Style Repository mantığı)

Docx atıf/kaynakça biçimi **yalnızca zotero'nun yetkisinde.** Kanonik biçim tanımı bu skill'in
`references/citation-format.md` dosyası. Varsayılan: **Vancouver** (numaralı; 6 yazar + et al.,
NLM dergi kısaltması, DOI+PMID). `zotero_cite.py --style vancouver` bu tabanı üretir;
`--style author-date` APA-vari taban üretir. Diğer skiller bu işi yapmaz, zotero'ya devreder.

## Dergiye özel stil istendiğinde

Kullanıcı hedef dergi adı verdiğinde ("AJNR stilinde", "Spine için") sırayla:

1. **Yerel Zotero CSL deposu:** `~/Zotero/styles/*.csl` içinde dergi adını ara
   (Glob + Grep `<title>` etiketi). Kullanıcının Zotero'suna kurduğu stiller
   burada — varsa kurallarını (numaralı mı yazar-yıl mı, `et-al-min`,
   noktalama) CSL XML'inden oku.
2. **Zotero Style Repository (web):** yoksa
   `https://www.zotero.org/styles?q=<dergi>` üzerinden stili bul; CSL dosyasını
   WebFetch ile çek ve kuralları çıkar.
3. **journalstyle profili:** journalstyle skill'i o dergi için profil
   önbelleklemişse (`citation_style` alanı) onu kullan — çelişkide profil kazanır
   (dergi kılavuzundan türetilmiştir).

## Uygulama

- Taban seçimi: stil numaralıysa `zotero_cite.py --style vancouver`,
  yazar-yıl ise `--style author-date` ile belgeyi üret/refresh et.
- İnce ayrıntılar (üst-simge numara, köşeli/parantez farkı, et-al eşiği,
  italikler, "References" başlık adı) **zotero'nun kendi sorumluluğunda** —
  yerel CSL/Style Repository'den okunan kuralı `zotero_cite.py` parametreleriyle
  (`--heading`, stil seçimi) ve gerekiyorsa çıktı üzerinde hedeflenmiş düzeltmeyle
  uygula. Bu işi başka bir agent/skill'e devretme; yetki tek elde kalır.
- Stil değişikliği sonrası her zaman `zotero_cite.py` refresh çalıştırılmış
  bir belge üzerinde çalışılır — işaretçiler belgede durduğu için stil geçişi
  kayıpsızdır (Vancouver ⇄ author-date arası geçiş test edilmiştir).
- **Stil değişiminin iki yolu** (çelişki yok):
  1. **Zotero uygulamasından** — `--mode field` (varsayılan) çıktısındaki canlı
     alanlar Zotero'nundur: Word'de Zotero sekmesi → Document Preferences →
     stil seç → Refresh. Tüm CSL stilleri (Style Repository) kullanılabilir.
  2. **Bu skill'den** — `zotero_cite.py --style ...` yeni işaretçi basımında
     taban stili belirler; text-mode belgelerde tek yol budur.

## De-duplikasyon ve dil

- Aynı DOI/PMID = aynı makale — kaynakçaya ikinci kez girmez
  (`citation-format.md` kuralı).
- Türkçe belge çıktısında kaynakça başlığı "Kaynaklar"; İngilizce belgede
  `--heading "References"`. Sayı/yüzde biçimi global CLAUDE.md dil kuralına tabi.

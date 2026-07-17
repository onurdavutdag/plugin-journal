# Kanıt köprüsü — Zotero storage PDF'leri research/writer için

Kullanıcının gerçek Zotero kütüphanesindeki ekli PDF'ler
(`<ZOTERO_DATA_DIR>/storage/<KEY>/*.pdf`) tier-2 kanıt kaynağıdır — research
skill'inin "Uploaded PDF" katmanıyla aynı öncelik.

## Akış

1. `research` (veya writer üzerinden) bir iddiaya kanıt ararken, `pdflerim/`
   ve workspace taramasına **ek olarak** Zotero storage'ı da tara:

   ```
   python <research-skill-dir>/scripts/search_pdfs.py --dir "C:/Users/onurd/Zotero/storage" --terms "kavram" "anahtar kelime"
   ```

2. İsabet gelen PDF'in hangi Zotero item'ına ait olduğunu bul: dosya yolundaki
   `storage/<ATTACHMENT_KEY>/` klasör adı attachment anahtarıdır; asıl künye için

   ```
   python <zotero-skill-dir>/scripts/zotero_lib.py --items
   ```

   çıktısındaki `attachments` alanıyla eşleştir (tam yol eşleşmesi). Eşleşen
   item'ın `key, title, DOI, PMID` alanları hazır künyedir — **uydurma yok,
   künye kullanıcının kendi kütüphanesinden gelir.**

3. İsabeti research kuralına göre doğrula: PDF'i Read ile o sayfada aç,
   pasajın iddiayı gerçekten desteklediğini teyit et (anahtar kelime çakışması
   destek değildir). Sayfa numarası + bölüm başlığı raporlanır.

4. Çıktıda `Source: Uploaded PDF` kullan; gerekçede "Zotero kütüphanesi"
   alt-kaynağını belirt. DOI/PMID item kaydından alınır; eksikse PubMed
   `lookup_article_by_citation` ile kurtarılır.

5. Atıf yazımı: item zaten kütüphanede olduğundan Word tarafında doğrudan
   `{{zref:ITEMKEY}}` işaretçisi kullanılabilir — writer akışıyla entegre.

## Not

- Storage klasöründe yüzlerce PDF olabilir; `--terms` spesifik tut, gerekirse
  önce `zotero_lib.py --search` ile aday item'ları daralt, sonra yalnız o
  attachment yollarını tara.
- Silinmiş (çöpteki) item'ların PDF'leri storage'da kalabilir; `zotero_lib.py`
  çıktısında görünmeyen bir attachment'a denk gelirsen künyesiz kullanma.

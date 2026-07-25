<!-- Oluşturma: 20260725 2140 -->
# Tuzaklar, yasaklar ve ⚠️ belirsizlik envanteri

> İşaretler: ⚔️ kaynaklar ayrışıyor · ⚠️ videoda net değildi, kesin konuşma · 🔴 veri kaybı riski · ⭐ ders notları dışı
> Bir Zotero sorununda **önce buraya** bakılır.

## 🔴 1. Word'de elle düzeltme yapma

Metin içi atıfta ya da kaynakçada hata görülünce doğrudan Word'de düzeltmek en yaygın hatadır.

**Ne olur:** Refresh'e basıldığında ya da yeni bir atıf eklendiğinde Zotero *"alıntıyı oluşturduktan sonra bir değişiklik yapmışsınız, kabul edeyim mi?"* diye sorar. **Hayır** denince elle yapılan düzeltme silinir, Zotero'daki (hatalı) veri geri gelir.

**Doğru akış:** hata **Zotero ana programındaki sağ panelden** düzeltilir → Word'de **Refresh**. Belgedeki o kaynağa ait bütün atıflar tek seferde düzelir.

⚔️ **Tek istisna:** Isnat'ta ikinci ve sonraki **kısa dipnotlardaki** fazlalıkların elle silinmesi. Kuralı net: çalışma tamamen bittikten, artık yenileme ihtiyacı kalmadıktan sonra yapılır; yapılacaklar bir kenara not edilir, en sona bırakılır.

## 🔴 2. Yanlış kaydı silip yeniden ekleme

**Ne olur:** Zotero aynı isimli iki kaydın aynı kitap olduğunu anlamaz. İkinci ve sonraki atıflarda — normalde yalnız soyadı + kısa eser adı gelmesi gerekirken — bu iki "farklı" kitabı ayırt etmek için parantez içinde basım yılı gibi ek bilgi basmaya başlar.

⚠️ Kaynaklarda ayrıca "hayalet kayıt" sorunu anlatılıyor: yanlış kayıt silinip çöp sepeti boşaltılsa bile Zotero bazen o kaydı hatırlamaya devam edip atıf biçimini bozabiliyor. Bu davranışın teknik sebebi videoda açıklanmıyor.

**Doğru akış:** mevcut kaydı **düzenle**. Zaten mükerrer oluştuysa *Yenilenmiş Eserler → Eserleri Birleştir* (`zotero-r-organizasyon.md`).

## 3. Büyük belgelerde performans

- 80–100 sayfayı geçen, binlerce dipnotlu belgelerde Word yavaşlar.
- 300 sayfa civarında tek bir atıf eklemek 10–20 saniye sürebilir.
- **Strateji:** tez gibi uzun çalışmalarda her bölüm (Giriş, 1. Bölüm, 2. Bölüm…) ayrı Word dosyasında yazılır; en sonda birleştirilir ve bir kez **Refresh** yapılır.
- Kütüphane tarafında: gereksiz PDF ekleri temizlenir, çalışma başına ayrı derme kullanılır.

## 🔴 4. Unlink Citations

Geri dönüşü yoktur. Atıflar ve kaynakça düz metne döner, belgenin kütüphaneyle bağı tamamen kopar; kaynakça bir daha yeniden kurulamaz.

**Ne zaman:** yalnız en son sürümde, tüm düzeltmeler bittikten sonra, yayınevine/matbaaya/redaktöre göndermeden hemen önce. Kaynaklarda "çok nadir kullanılır, hiç gerekmeyebilir" deniyor.

**Önce:** belgenin Zotero-bağlantılı hâli **Farklı Kaydet** ile ayrı bir dosyaya saklanır.

## 5. Sürüm yükseltmesi

⚔️ Zotero 6 → 7/8 geçişinde eklentilerin güncellendiğinden emin olunmalı; aksi hâlde Word sekmesindeki komutlar çalışmayabilir. Güncelleme yolu: **Yardım → Güncellemeleri denetle**.

## 6. Veri kaybı

Bilgisayar arızasına karşı hesap açılıp bulut senkronu kurulur; ayrıca **Dosya → Kitaplığı dışarı aktar → Zotero RDF** ile düzenli yerel yedek alınır (`zotero-r-eklenti-senkron.md`).

---

## ⚠️ Belirsizlik envanteri — kaynaklarda NET OLMAYAN konular

Aşağıdaki konularda **kesin konuşulmaz**; "videoda net değildi / kaynakta geçmiyordu" denir ve gerekiyorsa ⭐ etiketli genel bilgi verilir. Liste NotebookLM `zotero` defterine ayrıca sorularak doğrulandı.

| Konu | Durum |
|---|---|
| **Zotero 8 "seçili ögeyi küçültme"** | Anlatıcı *"şöyle üzerine tıklayıp şöyle küçülttüğüm zaman"* diyor; hangi buton/menü olduğu söylenmiyor, ekranda gösteriliyor. Bilinen: tek eser seçiliyken çalışıyor, 2-3 eserde çalışmıyor |
| **Sihirli değnek ikonunun tam konumu** | İki kaynak "artı ikonunun hemen yanında / üst panelde yeşil artı simgesinin yanında" diyor. Ekran koordinatı yok — tarif ederken bu ölçüde kal |
| **Mobil uygulama (iOS/Android)** | Hiç geçmiyor. Kaynaklar yalnız "farklı cihaz/bilgisayardan bulut üzerinden erişim"den söz ediyor. Zotero'nun resmî mobil uygulaması konusunda ders notu yok |
| **300 MB kota dolunca** | Kota var deniyor, dolduğunda ne yapılacağı (ek alan satın alma, fiyat, WebDAV, alternatif) anlatılmıyor. Tek öneri: PDF eklerini elle silmek |
| **Veri klasörü (data directory) yedeği** | Klasör yolu ve Zotero kapalıyken kopyalama yöntemi kaynaklarda yok. Kaynaklardaki yedek yolu **RDF dışa aktarma** |
| **Veri ↔ dosya senkronizasyonu ayrımı** | Yok. PDF'leri senkron dışı bırakma ayarı anlatılmıyor |
| **Word'de Zotero sekmesi kaybolursa onarım** | Onarım adımı yok. Yalnız 32-bit/64-bit uyuşmazlığı uyarısı var |
| **Mükerrer birleştirmede ana kayıt seçimi** | Birleştirme anlatılıyor, "master item" seçimi anlatılmıyor |
| **YÖK Tez numarasıyla otomatik ekleme** | Anlatıcı denemiş, çalışmamış; sebebi açıklanmıyor |
| **Bazı ISBN'lerin bulunamaması** | "Bazen bulamayabiliyor" deniyor, teknik sebebi yok |
| **Yazma eser künyesi** | Yalnız değinilerek geçiyor, adım adım tarif yok |
| **Tezde Tez No / Arşivdeki yeri** | ⚔️ İki video çelişiyor — ayrıntı ve karar `zotero-r-ilahiyat.md`'de |

## Belirti → dosya

| Belirti | Önce bakılacak |
|---|---|
| Düzeltme kayboluyor, eski hâline dönüyor | Bu dosya, madde 1 |
| İkinci dipnot uzun geliyor / parantezde fazladan bilgi | Bu dosya, madde 2 + `zotero-r-organizasyon.md` |
| Word donuyor, atıf 10-20 saniye sürüyor | Bu dosya, madde 3 |
| ISBN/DOI sonuç vermiyor | `zotero-r-kaynak-ekleme.md` |
| Connector ikonu görünmüyor | `zotero-r-eklenti-senkron.md` |
| Kaynakça sıralaması Arapça isimlerde bozuk | `zotero-r-ilahiyat.md` |
| Stil listesinde İsnat yok | `zotero-r-atif-stilleri.md` |
| Kütüphane başka bilgisayarda görünmüyor | `zotero-r-eklenti-senkron.md` |

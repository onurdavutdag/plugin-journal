<!-- Oluşturma: 20260725 2140 -->
# Kurulum, Connector, senkronizasyon, depolama ve YEDEKLEME

> İşaretler: ⚔️ kaynaklar ayrışıyor · ⚠️ videoda net değildi, kesin konuşma · 🔴 veri kaybı riski · ⭐ ders notları dışı

## Kurulum

1. Google'a `zotero indir` yazılır, çıkan ilk sayfaya girilir → **Download**.
2. İşletim sistemi seçilir (Windows / Mac / Linux). ⚠️ Mac kullanıcıları kendi sürümünü seçmeli; Windows'ta 32-bit ↔ 64-bit ayrımına dikkat (*Bilgisayarım → sağ tık → Özellikler → Sistem türü*).
3. Kurulum biter bitmez **Word eklentisi de otomatik yüklenir** — Word açılınca üst şeritte **Zotero** sekmesi görünür.
4. Ayrıca indirme sayfasından **Zotero Connector** tarayıcıya kurulur.

## Zotero Connector

- Chrome, Firefox, Safari, Opera desteklenir.
- **Sabitleme:** adres çubuğunun yanındaki **puzzle** ikonu → Connector'ün yanındaki sabitleme (pin) işareti. Yoksa ikon her açılışta gizlenir.
- İkon, sayfadaki kaynağın türüne göre şekil değiştirir (kitap / kağıt / oynatıcı / web sayfası).
- Kayıt, Zotero'da o an **seçili dermeye** düşer; açılan pencereden hedef derme değiştirilebilir.

Ayrıntı ve çalıştığı siteler → `zotero-r-kaynak-ekleme.md`.

## Hesap açma

1. zotero.org → **Register for a free account**.
2. Kullanıcı adı, e-posta, şifre girilir.
3. ⚠️ **E-posta doğrulaması şart** — gelen linke tıklanmadan hesap aktifleşmez.
4. Web arayüzünde *Kütüphanem · Gruplar · Dokümanlar* bölümleri görünür.

## Senkronizasyon (eşitleme)

⚔️ **Menü yolu kaynaklarda üç farklı adla geçiyor** — arayüz dili ve sürüme göre değişiyor. Kullanıcıya üçünü de söyle:

| Kaynak | Yol |
|---|---|
| Aklan & Salih, Koç | **Düzen → Ayarlar → Eşitle** (Koç: *"Ayarlar → Hesabı eşitle"*) |
| Gömek | **Düzen → Tercihler** (ya da Ayarlar) → **Eşitle** |
| Grad Coach (Mac) | **Settings → Sync** |

Kullanıcı adı + şifre girilir, "eşitlemeyi kur" denir. Bir kere yapılır.

Aynı ekranda **hesabı ilişkisizlendir** (unlink account) seçeneği vardır — 🔴 basılırsa hesap bağlantısı kopar, önce yedek al.

**Ne kazandırır:**
- Veriler buluta yedeklenir — Grad Coach'un deyimiyle "dizüstüne kahve döküldüğünde" işe yarar.
- Başka bir şehirde, başka bir bilgisayarda Zotero açılıp hesaba girilince tüm kütüphane kendiliğinden iner. O bilgisayarda çalışıyor olmak gerekmez.

⚠️ **Kaynaklarda anlatılmayanlar:** "veri senkronizasyonu ↔ dosya senkronizasyonu" ayrımı, PDF eklerini senkron dışı bırakma ayarı, WebDAV. Bu sorulara "videolarda geçmiyordu" de.

## Depolama kotası — 300 MB

- Zotero **300 MB'a kadar ücretsiz** depolama verir.
- Yalnız künye (metin) verisi tutuluyorsa fazlasıyla yeterlidir.
- **PDF ekleri** kotayı hızla doldurur.
- Anlatıcının kota yönetimi: künye oluştuktan sonra **ataş işaretinden** PDF eki seçilir → *sağ tık → Eseri çöp sepetine gönder*. Künye kalır, yalnız PDF gider. 🔴 PDF'in başka bir yerde durduğu doğrulanmadan yapılmaz.
- İkinci öneri: her makale/tez için ayrı bir derme açıp yalnız o çalışmanın kaynaklarını tutmak.

⚠️ **Kota dolduğunda ne yapılacağı kaynaklarda YOK.** Ek alan satın alma adımları, fiyat, alternatif depolama anlatılmıyor. Bu soruda sınırı açıkça söyle, ⭐ etiketiyle genel bilgi ver.

## 🔴 YEDEKLEME — veri kaybı riskli her işlemden önce

Kaynaklarda **iki** yedekleme yolu geçiyor:

**1. Kitaplığı dışarı aktarma (RDF) — asıl yol**

1. **Dosya → Kitaplığı dışarı aktar** (tek derme için: derme üzerinde sağ tık → *Derlemeyi dışarı aktar*).
2. Biçim: **Zotero RDF**. "Notları dışarı aktar" kutusu isteğe bağlı.
3. Kaydedilecek yer seçilir (masaüstü olur).
4. Oluşan dosya, geri yüklemede çift tıklanır → *"içeri aktarmak istiyor musunuz?"* → Tamam. Eserler yeni bir dermeye gelir.

Aynı dosya kütüphaneyi başka bir bilgisayara taşımak ya da bir arkadaşa göndermek için de kullanılır (anlatıcı 2264 eseri böyle aktarıyor).

**2. Bulut eşitlemesi** — hesap açıp senkronu kurmak, kendiliğinden bir yedektir.

⚠️ **Kaynaklarda geçmeyen:** Zotero **veri klasörünün** (data directory) yolu ve Zotero kapalıyken klasörü kopyalama yöntemi anlatılmıyor. Bu yöntemi önerirsen ⭐ ile etiketle.

### Yedek şart olan işlemler

Aşağıdakilerden **hiçbiri**, kullanıcı yedeğini aldığını söylemeden başlatılmaz:

| İşlem | Risk |
|---|---|
| Toplu silme, çöp sepetini boşaltma | Künye geri gelmez |
| PDF eklerini kota için silme | Ek dosya kaybolur |
| Mükerrer kayıtları birleştirme | Birleşme geri alınamaz |
| Senkronu sıfırlama / hesabı ilişkisizlendirme | Yerel ↔ bulut çakışması |
| **Unlink Citations** | Belge-kütüphane bağı kopar, geri dönüşü yok |
| Sürüm yükseltme öncesi | Eklenti/uyumluluk sorunu |
| RDF içeri aktarma (büyük kütüphaneye) | Mükerrer yığını |

Word tarafında ayrıca: **Unlink öncesi belgenin Zotero-bağlantılı hâli Farklı Kaydet ile ayrı saklanır.**

## Sık hatalar

- E-posta doğrulamasını atlayıp senkronun çalışmamasına şaşırmak.
- Connector'ü sabitlemeyip "ikon yok" sanmak.
- PDF yığınını sürükleyip kotayı doldurmak.
- Tek yedek olarak buluta güvenmek — yerelde bir hata buluta da eşitlenir; RDF dışa aktarması ayrıca alınır.

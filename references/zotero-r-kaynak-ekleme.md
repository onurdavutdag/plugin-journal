<!-- Oluşturma: 20260725 2140 -->
# Zotero'ya kaynak ekleme — 4 kanal + toplu aktarım

> İşaretler: ⚔️ kaynaklar ayrışıyor · ⚠️ videoda net değildi, kesin konuşma · 🔴 veri kaybı riski · ⭐ ders notları dışı
> Kaynak: 6 video transkripti (Aklan & Salih · Türkel & Ateş · Grad Coach · Gömek · Koç ders 11 · Koç & Tekno Akademi), NotebookLM `zotero` defteriyle doğrulandı.

## Karar kuralı — hangi kanal?

| Elindeki | Kanal | Neden |
|---|---|---|
| DOI / ISBN / PMID numarası | **Sihirli değnek** | En yüksek doğruluk, saniyeler sürer |
| Açık bir akademik web sayfası (DergiPark, İSAM, Kitapyurdu, Google Books, YouTube) | **Connector** | Künye + varsa PDF/snapshot birlikte gelir |
| Fiziksel kitap, çok eski eser, tanımlayıcısı tutmayan kaynak | **Manuel giriş** | Tek seçenek |
| Bilgisayarda duran PDF yığını | **Sürükle-bırak** | Üst veriyi kendi okur |
| Bir sayfadaki onlarca künye, Şamile/İSAM/YÖK listesi | **AI → BibTeX → Panodan içeri aktar** | Tek tek girmek saatler alır |

---

## 1. Manuel giriş

1. Kütüphane panelinin üstündeki **yeşil artı (+)** ikonuna tıklanır.
2. Eser türü seçilir: Kitap · Makale · Kitap Bölümü · Tez · Ansiklopedi Maddesi · Web Sayfası.
3. Sağ panelde alanlar doldurulur: başlık, yazar (ad / soyad ayrı kutular), yayıncı, yayın yeri, tarih (yalnız **yıl**), cilt sayısı.

**Başlık biçimi:** cümle biçimi ya da başlık biçimi seçilebilir; başlık biçiminde bağlaç ve edatlar (*ve*, *ile*, *fi*, *el-*) küçük kalır.

**Çok ciltli eserde** sağ paneldeki **Cilt Sayısı** alanına toplam cilt (ör. `10`) yazılır — kaynakçada eserin kaç ciltten oluştuğu böyle görünür.

## 2. Sihirli değnek (Add Item by Identifier)

⚠️ **Konum:** iki kaynak da "artı ikonunun hemen yanında / üst panelde yeşil artı simgesinin yanında" diyor; anlatıcılar ekranda gösterdiği için tam koordinat metinden çıkmıyor. Kullanıcıya *"üst araç çubuğunda, yeni kayıt (+) butonunun bitişiğinde bir sihirli değnek ikonu"* diye tarif et, ekran koordinatı verme.

- Açılan kutuya **ISBN** (tireler **yazılmadan**, düz sayı dizisi), **DOI** veya **PMID** girilip Enter'a basılır.
- DOI için makale sayfasındaki numarayı komple kopyalayıp yapıştırmak yeterli.
- Bilgiler geldikten sonra **sağ panel mutlaka kontrol edilir** — yayın yeri eksik gelebilir, başlık tamamen büyük harf gelebilir.

⚠️ **Bulamayabilir.** Anlatıcı bazı ISBN'lerin sonuç vermediğini söylüyor ("bazen bulamayabiliyor"), teknik sebebi videoda açıklanmıyor. Bulamazsa manuel girişe geçilir.
⚠️ YÖK Tez'deki **tez numarası** sihirli değnekte çalışmıyor — anlatıcı denediğini ve olmadığını söylüyor.

## 3. Zotero Connector (tarayıcı)

1. Zotero indirme sayfasından tarayıcıya (Chrome, Firefox, Safari, Opera) kurulur.
2. **Sabitleme:** adres çubuğunun yanındaki **puzzle** ikonuna tıklanır, Connector'ün yanındaki sabitleme işareti açılır — yoksa ikon her açılışta gizli kalır.
3. Kaydedilecek sayfada ikona tıklanır. İkon kaynak türüne göre **şekil değiştirir**: kitap → kitap, makale → kağıt/dosya, video → oynatıcı, diğer → web sayfası.
4. Kayıt, o an Zotero'da **seçili olan dermeye** düşer; açılan küçük pencereden hedef derme değiştirilebilir.

Çalıştığı doğrulanmış siteler: DergiPark, İSAM kataloğu ve ilahiyat makaleler veri tabanı, Kitapyurdu, Google Books, YouTube (başlık + tarih + link, "web sayfası" olarak).

⚠️ 32-bit / 64-bit uyuşmazlığı: indirme sayfasında doğru sürüm seçilmelidir (Windows'ta *Bilgisayarım → sağ tık → Özellikler → Sistem türü*).

## 4. PDF sürükle-bırak

PDF dosyası (ya da klasördeki onlarca PDF birden) Zotero'nun **orta paneline** sürüklenir; Zotero üst veriden künyeyi kendi oluşturur.

🔴 **Kota tuzağı:** bu yöntem PDF'i de eke koyar ve 300 MB'lık ücretsiz alanı hızla doldurur. Anlatıcının önerisi: künye oluştuktan sonra **ataş işaretinden** PDF eki seçilip *sağ tık → Eseri çöp sepetine gönder* denir — **künye silinmez, yalnız PDF eki silinir.** Silmeden önce PDF'in başka bir yerde durduğundan emin ol.

## 5. Yapay zeka ile toplu aktarım (BibTeX)

Kaynaklarda en çok vakit kazandıran yöntem.

1. Sayfadaki künye listesi (İSAM, YÖK Tez, Şamile "Bitaqa", ekran görüntüsü de olur) kopyalanır.
2. ChatGPT'ye yapıştırılıp komut verilir. Kaynaklarda geçen üç kalıp:
   - `Bu eserleri zotero formatına getir`
   - `Bu künye bilgilerini isnat 2'ye göre bibtex formatına çevir`
   - `Bu künyeyi latinize zotero formatına getir`
   Arapça eserlerde ek talimatlar: *"Latin alfabesine göre değil Türk alfabesine göre transfer et"*, *"gereksiz uzantıları yazma, sadece dipnot olarak ver"*.
3. Çıktının **kodu kopyala** butonuna basılır.
4. Zotero'da **Dosya → Panodan İçeri Aktar** seçilir. Eserler tek seferde kütüphaneye düşer.

⭐ AI çıktısı doğrulanmadan güvenilmez: uydurma yıl/yayıncı üretebilir. İçeri aktarıldıktan sonra en az bir kaydın künyesi kaynakla karşılaştırılır.

## 6. İçeri/dışarı aktarma (RDF) — grup kütüphaneleri ve yedek

- **Dışa:** *Dosya → Kitaplığı dışarı aktar* (ya da bir derme üzerinde sağ tık → *Derlemeyi dışarı aktar*) → biçim **Zotero RDF** → kaydet. "Notları dışarı aktar" kutusu isteğe bağlıdır.
- **İçe:** oluşan `.rdf` dosyasına çift tıklanır, "içeri aktarmak istiyor musunuz?" sorusuna Tamam denir — eserler **yeni bir dermeye** eklenir.
- Aynı akış DİA ve Şamile grup kütüphanelerinden eser çekmenin de yoludur → `zotero-r-ilahiyat.md`.
- Aynı akış **yedekleme**nin de kaynaklarda geçen tek yoludur → `zotero-r-eklenti-senkron.md`.

## Sık hatalar

- Sihirli değnekten gelen künyeyi kontrol etmeden bırakmak (eksik yayın yeri, büyük harf başlık).
- ISBN'i tireli girmek.
- PDF sürükleyip kotayı doldurmak, sonra Zotero'nun kastığından şikâyet etmek.
- Yanlış girilen kaydı **silip yeniden eklemek** — atıf sistemini bozar, bkz. `zotero-r-tuzaklar.md`.
- AI çıktısını doğrulamadan içeri aktarmak.

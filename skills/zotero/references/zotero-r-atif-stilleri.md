<!-- Oluşturma: 20260725 2140 -->
# Word / Google Docs atıf akışı ve atıf stilleri

> İşaretler: ⚔️ kaynaklar ayrışıyor · ⚠️ videoda net değildi, kesin konuşma · 🔴 veri kaybı riski · ⭐ ders notları dışı
> Bu dosya **kullanıcının kendi elleriyle Word/Google Docs içinde** yaptığı işi anlatır. Claude'un docx'e programatik atıf basması ayrı iştir → `SKILL.md` + `zotero-r-citation-format.md`.

## Zotero sekmesi nereden gelir

- Word eklentisi Zotero kurulumuyla **otomatik** yüklenir; Word açıldığında üst şeritte **Zotero** sekmesi belirir.
- Google Docs'ta Connector kuruluysa menü çubuğunda **Zotero** başlığı çıkar. İlk kullanımda Docs, Zotero'ya belgeyi düzenleme izni sorar.
- LibreOffice de desteklenir.

⚠️ **Sekme görünmüyorsa:** kaynaklarda bir onarım yolu (Ayarlar → Cite → eklentiyi yeniden yükle gibi) **anlatılmıyor**. Yalnız 32-bit/64-bit uyuşmazlığına dikkat edilmesi söyleniyor. Bu soruda "videoda onarım adımı geçmiyordu" de, ⭐ etiketiyle genel öneri ver.

## Atıf ekleme — Add/Edit Citation

1. İmleç dipnotun/atıfın gireceği yere konur.
2. Zotero sekmesi → **Add/Edit Citation**.
3. **İlk kullanımda bir kez** stil seçme penceresi çıkar (bkz. aşağıdaki stil kurulumu). Bir daha sormaz.
4. Arama kutusuna yazar ya da eser adı yazılır, eser seçilir.
5. Seçilen eserin **üzerine tıklanınca** detay kutusu açılır: **Sayfa**, **Ön ek (prefix)**, **Son ek (suffix)**.
6. Enter → Enter ile atıf yazılır.

**Aynı cümleye birden çok atıf:** Enter'a basmadan aramaya devam edilip ikinci, üçüncü eser de seçilir. Ya da var olan atıfa tıklanıp *Edit with Zotero* ile yenisi eklenir.

**Ön ek / son ek kullanımı:** son eke *"ayrıntılı bilgi için bakınız"* gibi ibareler yazılır; dipnotun sonunda görünür. Kaynaklarda sık kullanılan bir kolaylık olarak anlatılıyor.

**Dipnot sırası:** verilmiş atıfların yerleri, atıf kutusunda **sürüklenerek** değiştirilebilir (vefat tarihine göre sıralama gibi) — silip yeniden yazmaya gerek yok.

### ⚔️ Sürümler arası fark

| Sürüm | Atıf ekleme penceresi |
|---|---|
| **Zotero 6 ve öncesi** | Arama için **kırmızı bir bar (Red Bar)** çıkar |
| **Zotero 7** | Arayüz yenilendi; **en son uğraşılan eser** pencerede otomatik en üstte önerilir |
| **Zotero 8** | En güncel sürüm. ⚠️ Zotero ana ekranında bir eser seçili bırakılıp pencere "küçültüldüğünde" o eser atıf penceresine **seçili öge** olarak gelir. Anlatıcı bu hareketi *"şöyle üzerine tıklayıp şöyle küçülttüğüm zaman"* diye tarif ediyor — hangi buton/menü olduğu videoda söylenmiyor, ekranda gösteriliyor. Kesin konuşma. Yalnız **tek** eser seçiliyken çalışıyor; 2-3 eser seçilince çalışmıyor |

**Güncelleme yolu:** Yardım → *Güncellemeleri denetle*. (⚠️ Anlatıcı önce "Düzen → Ayarlar" deyip hemen düzeltiyor: doğrusu **Yardım**.)

### Klasik Görünüm (Classic View)

Add/Edit Citation kutusunun yanındaki **aşağı oka** tıklanır → **Klasik Görünüm**. Zotero'nun asıl arayüzüne benzeyen, dermelerin klasör hâlinde göründüğü pencere açılır. Arama yerine listeden seçmeyi tercih edenler içindir.

## Cilt ve sayfa numarası

Her şey tek bir **Sayfa** kutusuna yazılır — Zotero'ya ayrı cilt alanı girmeye gerek yoktur.

| Durum | Yazılış |
|---|---|
| Tek sayfa | `45` |
| Aynı eserden birden çok sayfa | `125, 150, 350` (virgülden sonra **boşluk**) |
| Çok ciltli eser, 9. cildin 320. sayfası | `9/320` — eğik çizgi |
| 5. cildin 235. sayfası | `5/235` |

⚔️ **Cilt bilgisi nereye?** Anlatıcı iki yolu da deniyor: (a) sağ paneldeki **Cilt** alanına yazmak, (b) atıf anında **Sayfa** kutusuna `cilt/sayfa` biçiminde vermek. Tercihi (b): *"cilt bilgisini sonradan, sayfa bilgisi üzerinden veriyorum; tek kitap olarak gördüğü için fazlalıklar ortaya çıkmıyor."* ⚠️ Uyarı: bu yöntem Isnat gibi stillere göre kurgulanmıştır, **başka bir stile geçilince biçim bozulabilir**.

## Kaynakça — Add/Edit Bibliography

İmleç kaynakçanın gireceği yere konur → Zotero sekmesi → **Add/Edit Bibliography**. Kullanılan tüm eserler seçilen stile göre, alfabetik ve otomatik listelenir.

⭐ Satır aralığı/girinti gibi biçim ayarları Zotero'nun işi değildir; kurumun şablonuna göre elle ayarlanır.

## Atıf stili kurulumu ve değiştirme

**Isnat 2 (İSNAD) kurulumu — tam yol:**

1. Word → Zotero sekmesi → **Document Preferences**.
2. Listede yoksa alttaki **Stilleri Yönet** (Manage Styles).
3. Açılan pencerede **Ek stilleri indir** (Get additional styles).
4. Arama kutusuna `isnat` yazılır. Üç edisyon listelenir — **1. edisyon seçilmez**, en güncel olan 2. edisyon alınır.
5. Tam adlar: **İsnat Atıf Sistemi 2. Edisyon (Dipnotlu)** ve **İsnat Atıf Sistemi 2. Edisyon (Metin İçi)**. Danışman/enstitü/dergi hangisini istiyorsa o seçilir; ilahiyatta yaygın olan **dipnotlu**dur.
6. Çift tıklanınca Word'e eklenir; bu bir kereye mahsustur.

**Üniversitenin kendi `.csl` dosyası varsa:** Zotero masaüstü uygulaması → Ayarlar → **Cite (Alıntı yap)** sekmesi → **+** butonu ile içeri aktarılır. (Kaynaklarda Bursa Uludağ Üniversitesi'nin enstitü bazlı ayrı stilleri örnek veriliyor; anlatıcının notu: *"artık İsnat varken gerek yok."*)

**Stil değiştirme:** Zotero sekmesi → **Document Preferences** → yeni stil → Tamam. Tüm dipnotlar ve kaynakça tek tuşla dönüşür.

Kaynaklarda geçen somut senaryo: makale İsnat isteyen dergiye gönderilir, kabul edilmez; APA isteyen başka dergiye gönderilecektir — Document Preferences'tan APA seçilir, dipnotlar ve kaynakça anında APA olur. Aynı şekilde Isnat *dipnotlu* ↔ *metin içi* arasında da geçilir.

⚠️ Arapça eserlerde harf-i tarif için uygulanan çift-alan tekniği (`zotero-r-ilahiyat.md`) stil değişiminde **sorun çıkarabilir** — anlatıcı bunu açıkça söylüyor.

## Refresh (Yenile)

Şu durumlarda basılır: Zotero'da bir künye düzeltildiğinde, belgeye yeni atıf eklendikten sonra kaynakçayı güncellemek için.

🔴 **Word içinde elle yapılan düzeltme kalıcı değildir.** Refresh'e basıldığında Zotero *"alıntıyı oluşturduktan sonra bir değişiklik yapmışsınız, kabul edeyim mi?"* diye sorar:

- **Hayır** → elle yapılan düzeltme silinir, Zotero'daki veri geri gelir. **Varsayılan doğru cevap budur** — hata Zotero'da düzeltilir, Word'de değil.
- **Evet** → değişiklik korunur, o atıf artık Zotero'dan güncellenmez.

⚔️ Anlatıcıların bir istisnası var: Isnat'ta ikinci ve sonraki **kısa dipnotlardaki** fazlalıkları elle silmek bazen gerekiyor. Bunun kuralı net: **çalışma tamamen bittikten, artık yenileme ihtiyacı kalmadıktan sonra** yapılır, bir kenara not edilir, en sona bırakılır.

## Unlink Citations (bağlantıyı kesme)

Zotero sekmesi → **Unlink Citations**. Tüm atıflar ve kaynakça **düz metne** dönüşür, belgenin Zotero kütüphanesiyle bağı tamamen kopar.

🔴 **Geri dönüşü yoktur.** Anlatıcılar: *"Yanlışlıkla da basmayın, basarsanız bağlantısı kalmaz"*, *"bunu yaptıktan sonra kaynakçayı yeniden kuramazsınız."*

Ne zaman: yalnız **en son sürümde**, tüm düzeltmeler bittikten sonra, yayınevine/matbaaya/redaktöre göndermeden hemen önce — uyumluluk sorunu ya da bağlantının kopma riski olmasın diye. Kaynaklarda "çok nadir kullanılır, hiç gerekmeyebilir" deniyor.

🔴 **Önce yedek:** işlemden önce belgenin Zotero-bağlantılı hâli **Farklı Kaydet** ile ayrı bir dosyaya saklanır. Bu adım atlanmadan devam edilmez.

## Sık hatalar

- Word'de elle düzeltip Refresh'e basmak → düzeltme uçar.
- Isnat 2 yerine 1. edisyonu seçmek.
- Unlink'e çalışmanın ortasında basmak.
- Cilt bilgisini hem sağ panele hem sayfa kutusuna girip çift göstermek.
- Kaynakçayı ekleyip sonradan atıf ekleyip Refresh'i unutmak.

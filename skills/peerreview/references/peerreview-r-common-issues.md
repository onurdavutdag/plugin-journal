# Sık Görülen Metodolojik ve İstatistiksel Hatalar — Hakem Kontrol Kataloğu

Bu dosya, hakem incelemesinde **sık karşılaşılan** sorunları kategoriye göre listeler. `peerreview`
skill'i Aşama 3'te bunu okur; her maddeyi taslakla eşleştirip **fiilen** görülen sorunu major/minor
olarak işaretler. Her madde üç parça: **Sık görülen sorun · Nasıl saptanır · Ne önerilir**.
Örnek sayı biçimi Türkçe kurala göre (virgül) verilmiştir; İngilizce raporda noktaya çevir.

> Kural: burada listelenen bir sorunu **taslakta gerçekten yoksa uydurma**. Emin değilsen "yazara
> soru" olarak yaz. Düzeltmeyi hakem yapmaz; sorumlu takım üyesine devreder (bkz. SKILL.md tek-sahip kuralı).

---

## İstatistiksel sorunlar

### 1. p-değeri kötüye kullanımı ve yanlış yorumu
- **Sorun:** p-hacking (yalnız anlamlıları raporlama), düzeltmesiz çoklu test, anlamsızlığı "etki yok"
  kanıtı sayma, etki büyüklüğü olmadan yalnız p, sürekli p'yi eşikte ikileştirme (p=0,049 ≠ p=0,051),
  istatistiksel anlamlılığı klinik anlamlılıkla karıştırma.
- **Nasıl saptanır:** 0,05 hemen altında yığılan p'ler; çok test ama düzeltme yok; "fark bulunmadı"
  ifadesi anlamsız sonuçtan; etki büyüklüğü/GA yok.
- **Ne önerilir:** etki büyüklüğü + %95 GA raporla; uygun çoklu test düzeltmesi (Bonferroni, FDR,
  Holm); anlamsızlığı temkinli yorumla (kanıt yokluğu ≠ yokluğun kanıtı); "fark yok" için eşdeğerlik testi.

### 2. Yanlış istatistiksel test seçimi
- **Sorun:** varsayım ihlalinde parametrik test (non-normal, eşit olmayan varyans); eşleştirilmiş
  veriye bağımsız test; çok grupta ANOVA yerine tekrarlı t-testi; ordinal veriyi sürekli sayma;
  tekrarlı ölçüm yapısını yok sayma.
- **Nasıl saptanır:** varsayım kontrolü anılmıyor; küçük örneklemde parametrik; ANOVA yerine çoklu
  ikili t; Likert'i t-testiyle; tekrarlı ölçüm dikkate alınmadan.
- **Ne önerilir:** varsayımları açıkça kontrol et (normallik testi, Q-Q); uygunsa non-parametrik;
  ANOVA sonrası uygun post-hoc düzeltme; tekrarlı ölçümde karma etkili model; ordinal için ordinal regresyon.

### 3. Örneklem büyüklüğü ve güç
- **Sorun:** güç analizi/gerekçe yok; yetersiz güçle "etki yok" iddiası; post-hoc güç (bilgi vermez);
  durdurma kuralı ön-tanımsız; gerekçesiz eşit olmayan grup.
- **Nasıl saptanır:** küçük n (tipik tasarımda grup başına n<30); metotta güç analizi yok; post-hoc
  güç ifadesi; geniş GA; büyük p + küçük n ile "etki yok".
- **Ne önerilir:** beklenen etkiye dayalı a priori güç analizi; ulaşılan güç/kesinliği (GA genişliği)
  raporla; yetersiz güçlüyse kabul et; yorumda etki büyüklüğü + GA; örneklem ve durdurma kuralını ön-kaydet.

### 4. Eksik veri
- **Sorun:** gerekçesiz tam-vaka analizi (listwise silme); eksikliğin miktar/örüntüsü raporlanmaz;
  MCAR test edilmeden varsayılır; uygunsuz imputasyon; duyarlılık analizi yok.
- **Nasıl saptanır:** analizler arası farklı n açıklamasız; eksik veri tartışılmaz; katılımcı
  "analizden çıkarıldı"; basit ortalama imputasyonu; duyarlılık analizi yok.
- **Ne önerilir:** eksikliğin miktar/örüntüsünü raporla; MCAR'ı test et (Little); uygun yöntem
  (çoklu imputasyon, maksimum olabilirlik); duyarlılık analizi; çalışmalarda tedavi-niyeti (ITT) analizi.

### 5. Dairesel analiz ve çift-daldırma (double-dipping)
- **Sorun:** seçim ve çıkarım için aynı veri; kontrasta göre ROI tanımlayıp aynı ROI'de o kontrastı
  test; aykırı seçip sonra fark testi; post-hoc alt grubu planlıymış gibi sunma; HARKing.
- **Nasıl saptanır:** sonuca göre seçilen ROI/özellik; beklenmedik alt grup analizi; keşifsel diye
  etiketlenmemiş post-hoc; veriden bağımsız doğrulama yok.
- **Ne önerilir:** seçim ve test için bağımsız veri seti; analiz/hipotez ön-kaydı; doğrulayıcı ve
  keşifsel analizi net ayır; çapraz doğrulama/hold-out; seçim yanlılığını düzelt.

### 6. Sözde-replikasyon (pseudoreplication)
- **Sorun:** teknik replikayı biyolojik replika sayma; aynı denekten çok ölçümü bağımsız sayma;
  kümelenmiş veriyi kümelenmeyi hesaba katmadan analiz; uzamsal/zamansal bağımlılık.
- **Nasıl saptanır:** n = ölçüm sayısı (biyolojik birim değil); aynı hayvandan çok hücre bağımsız
  sayılmış; tekrarlı ölçüm anılmamış; rastgele etki/kümelenme yok.
- **Ne önerilir:** n'i biyolojik replika (hayvan/hasta/bağımsız örnek) tanımla; iç içe/kümeli veride
  karma etkili model; tekrarlı ölçümü açıkça hesapla; teknik replikaları önce ortala.

---

## Deney tasarımı sorunları

### 7. Uygun kontrol eksikliği
- **Sorun:** negatif/pozitif kontrol yok; ilaç çalışmasında vehikül kontrol yok; boylamsalda
  zaman-eşli kontrol yok; batch kontrol yok.
- **Nasıl saptanır:** metotta yalnız deney grupları; şekillerde kontrol yok; baz/referans koşul belirsiz.
- **Ne önerilir:** özgüllük için negatif, yöntem doğrulaması için pozitif kontrol; eşli vehikül;
  cerrahi girişimde sham; batch karşılaştırmalarında batch kontrolü.

### 8. Karıştırıcı değişkenler (confounding)
- **Sorun:** gruplar girişim dışında sistematik farklı; kontrol edilmemiş batch etkisi; sıra etkisi;
  günün saati etkisi; körlenmemiş deneyci etkisi.
- **Nasıl saptanır:** gruplar birden çok özellikte farklı; örnekler gruba göre farklı batch'te;
  işlem sırası randomize değil; körleme yok; baz özellikler gruplar arası farklı.
- **Ne önerilir:** birimleri koşullara randomize et; bilinen karıştırıcıya göre blokla; örnek işleme
  sırasını randomize et; körle; gerekiyorsa batch düzeltmesi; baz farkları raporla ve düzelt.

### 9. Yetersiz replikasyon
- **Sorun:** replikasyonsuz tek deney; teknik replikayı biyolojik sanma; "alanda tipik" diye küçük n;
  bağımsız doğrulama yok; temsili örnek seçme.
- **Nasıl saptanır:** "deney bir kez yapıldı"; gerekçesiz n=3; "temsili görsel"; anahtar iddia tek
  deneye dayalı; bağımsız veri setinde doğrulama yok.
- **Ne önerilir:** bağımsız biyolojik replika (tipik ≥3); anahtar bulguyu bağımsız kohortta doğrula;
  yalnız temsili değil tüm replikaları raporla; güç analiziyle örneklemi gerekçelendir; bireysel veri noktalarını göster.

---

## Tekrarlanabilirlik sorunları

### 10. Yetersiz metot ayrıntısı
- **Sorun:** replikasyona yetmeyen metot; anahtar reaktif belirtilmemiş (firma/katalog no); yazılım
  sürüm/parametre yok; antikor doğrulanmamış; hücre hattı kimliği doğrulanmamış.
- **Nasıl saptanır:** muğlak ("standart protokoller kullanıldı"); reaktif kaynağı yok; jenerik
  yazılım sürümsüz; antikor doğrulama bilgisi yok.
- **Ne önerilir:** ayrıntılı protokol ver/atıfla; reaktif firma-katalog-lot; yazılım sürüm+parametre;
  antikor doğrulaması; hücre hattı kimlik yöntemi (STR); protokolleri erişilebilir yap (protocols.io).

### 11. Veri ve kod erişilebilirliği
- **Sorun:** veri erişim beyanı yok; "istek üzerine" (çoğu yerine getirilmez); analiz kodu yok;
  özel yazılım paylaşılmamış; dokümantasyon yok.
- **Nasıl saptanır:** erişim beyanı eksik; repository accession no yok; hesaplamalı yöntem kodsuz;
  özel pipeline erişimsiz; README yok.
- **Ne önerilir:** ham veriyi uygun repository'ye (GEO, SRA, Dryad, Zenodo) yatır; kodu GitHub'da
  paylaş; README/dokümantasyon; ortam dosyası (requirements.txt); kalıcı atıf için DOI.

### 12. Yöntem doğrulaması eksikliği
- **Sorun:** yeni yöntem altın standarda karşı doğrulanmamış; özgüllük/duyarlılık/doğrusallık test
  edilmemiş; spike-in yok; çapraz reaktivite test edilmemiş; saptama limiti belirlenmemiş.
- **Nasıl saptanır:** yeni assay doğrulamasız; mevcut yöntemle karşılaştırma yok; pozitif/negatif
  kontrol gösterilmemiş; kanıtsız özgüllük iddiası; standart eğri yok.
- **Ne önerilir:** yerleşik yaklaşımlara karşı doğrula; özgüllüğü göster (knockdown/knockout);
  doğrusallık & dinamik aralık; pozitif/negatif kontrol; saptama/miktar limiti; operatörler arası tekrarlanabilirlik.

---

## Yorumlama sorunları

### 13. Sonuçların abartılması
- **Sorun:** korelasyonel veriye nedensel dil; mekanizma kanıtı olmadan mekanizma iddiası; veriyi
  aşan ekstrapolasyon (tür/koşul/popülasyon); iyi literatür taraması olmadan "ilk gösteren" iddiası;
  sınırlı örnekten aşırı genelleme.
- **Nasıl saptanır:** gözlemsel veriden "X, Y'ye neden olur"; test edilmemiş mekanizma; fare verisi
  insana çekince olmadan uygulanmış; atıf eksiğiyle özgünlük iddiası.
- **Ne önerilir:** uygun dil ("ile ilişkili" vs "neden oldu"); korelasyon-nedensellik ayrımı; model
  sistem kısıtını kabul et; kapsamlı literatür bağlamı; genellenebilirlikte özgül ol; mekanizmayı hipotez olarak sun.

### 14. Kiraz toplama ve seçici raporlama
- **Sorun:** yalnız anlamlıları raporlama; tipik olmayabilecek "temsili" görsel; gerekçesiz aykırı
  dışlama; negatif/çelişen bulguyu raporlamama; farklı istatistik yaklaşımları arasında geçiş.
- **Nasıl saptanır:** raporlanan tüm sonuçlar anlamlı; "3 deneyin temsili" ama nicelik yok; veri
  dışlaması bulgularda var metotta yok; ek veri ana bulguyla çelişiyor.
- **Ne önerilir:** sonuçtan bağımsız tüm planlı analizleri raporla; replikalar arası değişkenliği
  göster; aykırı ölçütünü ön-tanımla; negatif sonuçları dahil et; analiz planını ön-kaydet.

### 15. Alternatif açıklamaları göz ardı etme
- **Sorun:** alternatif düşünülmeden tercih edilen açıklama; çelişen kanıtı tartışmadan reddetme;
  hedef-dışı etki düşünülmemiş; karıştırıcı kabul edilmemiş; kısıt bölümü zayıf/yok.
- **Nasıl saptanır:** tek yorum gerçekmiş gibi; önceki çelişen bulgu anılmıyor; alternatif mekanizma
  yok; kısıt tartışması yok; kontrolsüz özgüllük varsayımı.
- **Ne önerilir:** alternatif açıklamaları tartış; literatürdeki çelişen bulguları ele al; özgüllük
  kontrolleri; kısıtları etraflıca tartış; alternatif hipotezleri test et.

---

## Şekil ve veri sunumu sorunları

### 16. Uygunsuz veri görselleştirme
- **Sorun:** sürekli veri için bar grafik (dağılımı gizler); tanımsız/eksik hata çubuğu; kırpılmış
  y-ekseni farkı abartır; çift y-ekseni yanıltır; aşırı anlamlı basamak; renk körü uyumsuz renk.
- **Nasıl saptanır:** az veriyle bar; hata çubuğu ne (SD/SEM/GA?) belirsiz; oran/yüzde verisinde
  y sıfırdan başlamıyor; iki farklı ölçekli y; aşırı hassas değer (p=0,04562); kırmızı-yeşil şema.
- **Ne önerilir:** bireysel noktalar (scatter/box/violin); hata çubuğunu tanımla (SD/SEM/%95 GA);
  y'yi sıfırdan başlat ya da kırığı belirt; çift y yerine ayrı panel; uygun basamak; renk körü uyumlu
  palet (viridis, colorbrewer); legend'da örneklem sayısı.

### 17. Görüntü manipülasyonu şüphesi
- **Sorun:** aşırı kontrast/parlaklık; belirtilmeden birleştirilmiş (splice) jel/görsel; kopya
  panel; blot'ta eşit olmayan arka plan; seçici kırpma; aşırı işlenmiş mikroskopi.
- **Nasıl saptanır:** şüpheli örüntü/süreksizlik; arka plansız çok yüksek kontrast; farklı panelde
  benzer öğe; splice düşündüren düz çizgi; tutarsız arka plan.
- **Ne önerilir:** ayarları tüm görsele tekdüze uygula; splice'ı ayırıcı çizgiyle belirt; ek dosyada
  tam/kırpılmamış görsel; istenirse orijinal; dergi görüntü bütünlük politikasına uy.

---

## Çalışma tasarımı sorunları

### 18. Kötü tanımlı hipotez ve sonlanım
- **Sorun:** net hipotez yok; birincil sonlanım belirtilmemiş; düzeltmesiz çoklu sonlanım; veri
  sonrası değişen sonlanım; "olta atma"nın hipotez-güdümlü gibi sunulması.
- **Nasıl saptanır:** giriş net test edilebilir hipotez vermiyor; hiyerarşisi belirsiz çok sonlanım;
  bulgulardaki sonlanım metottakiyle uyuşmuyor; keşifsel çalışma doğrulayıcı gibi.
- **Ne önerilir:** net, test edilebilir hipotez; a priori birincil/ikincil sonlanım; mümkünse
  ön-kayıt; çoklu sonlanım için düzeltme; keşifsel/doğrulayıcı ayrımı; tüm ön-tanımlı sonlanımları raporla.

### 19. Baz dengesizliği ve seçim yanlılığı
- **Sorun:** gruplar bazda farklı; seçim ölçütü farklı uygulanmış; sağlıklı gönüllü yanlılığı;
  survivorship (hayatta kalan) yanlılığı; gözlemselde endikasyon yanlılığı.
- **Nasıl saptanır:** Tablo 1'de anlamlı baz farkı; gruplar arası farklı dahil ölçütü; yanıt oranı
  <%50 analizsiz; yalnız tamamlayanlar; randomize yerine kendi kendine seçilmiş gruplar.
- **Ne önerilir:** baz özellikleri Tablo 1'de raporla; dengeyi randomizasyonla sağla; analizde baz
  farkını düzelt; yanıt oranını raporla; gözlemsel veride propensity skor eşleme; ITT analizi.

### 20. Zamansal ve batch etkileri
- **Sorun:** örnekler koşula göre batch'lenmiş; zamansal eğilim hesaba katılmamış; cihaz kayması;
  gruplar için farklı operatör; gruplar arası reaktif lot değişimi.
- **Nasıl saptanır:** tüm tedavi örnekleri aynı gün; kontroller farklı dönemden; batch/zaman etkisi
  anılmıyor; gruplar için farklı teknisyen; uzun süre, zamansal analiz yok.
- **Ne önerilir:** örnekleri batch/zamana randomize et; batch'i kovaryat olarak ekle; batch düzeltmesi
  (ComBat, limma); batch'ler arası kalite kontrol örneği; zamansal eğilimi test et; operatörleri dengele.

---

## Raporlama sorunları

### 21. Eksik istatistiksel raporlama
- **Sorun:** test istatistiği yok; serbestlik derecesi eksik; kesin p yerine eşitsizlik (p<0,05);
  GA yok; etki büyüklüğü yok; grup başına n raporlanmamış.
- **Nasıl saptanır:** yalnız p, test istatistiği yok; p<0,05 (kesin değer değil); belirsizlik ölçüsü
  yok; etki büyüklüğü belirsiz; n toplam için var grup için yok.
- **Ne önerilir:** tam test istatistiği (t, F, χ² vb. + df); kesin p (p<0,001 hariç); %95 GA; etki
  büyüklüğü (Cohen d, OR, korelasyon katsayısı); her analizde grup başına n; CONSORT tarzı akış şeması.

### 22. Metot–Bulgular uyumsuzluğu
- **Sorun:** metotta olup yapılmayan analiz; metotta olmayıp bulgularda olan analiz; metot ve
  bulgularda farklı örneklem; metotta anılıp gösterilmeyen kontrol; yapılana uymayan istatistik.
- **Nasıl saptanır:** bulgularda metot açıklaması olmayan analiz; metotta bulgularda olmayan deney;
  bölümler arası uyumsuz sayı; anılan ama gösterilmeyen kontrol; kullanılandan farklı yazılım.
- **Ne önerilir:** metot–bulgular tam uyumu sağla; yapılan tüm analizleri metotta tanımla;
  yapılmayanı çıkar; tüm sayıları tutarlı doğrula; metodu fiili analizlere göre güncelle.

---

## Bu referans nasıl kullanılır

Makale değerlendirirken: (1) metot ve bulguları sistematik oku, (2) her kategoride bu maddeleri
tara, (3) belirli sorunu **kanıtıyla** not et, (4) yapıcı iyileştirme öner, (5) major (geçerliliği
etkiler) ve minor (açıklığı etkiler) ayır, (6) tekrarlanabilirlik ve şeffaflığı önceliklendir.

Bu liste tüketici değildir; en sık görülenleri kapsar. Her zaman disiplin ve bağlamı gözet.
Bir sorunu **taslakta fiilen görmüyorsan işaretleme.**

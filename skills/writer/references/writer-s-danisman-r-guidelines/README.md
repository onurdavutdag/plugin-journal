# Raporlama Kılavuzları — Madde Düzeyi Paket

Bu dizin, EQUATOR Network (www.equator-network.org) raporlama kılavuzlarının **madde-düzeyi,
IMRaD bölümüne göre gruplu, damıtılmış** özetlerini tutar. `writer-s-danisman` agent'ı, çalışma
tipini belirledikten sonra **eşleşen dosyayı Read eder** ve o bölüm için ilgili maddeleri
yazım rehberliğine katar.

`writer-s-danisman-r-bilgi.md` §5 kılavuzları yalnız **adlandırır**; madde içeriği burada.

## Çalışma tipi → kılavuz dosyası

| Çalışma tipi | Kılavuz | Dosya | Kaynak |
|---|---|---|---|
| Randomize kontrollü çalışma (RKÇ) | CONSORT | `CONSORT.md` | resmi checklist (CONSORT 2010, BMJ) |
| Gözlemsel (kohort / vaka-kontrol / kesitsel) | STROBE | `STROBE.md` | resmi checklist (STROBE v4, 3 varyant) |
| Sistematik derleme & meta-analiz | PRISMA | `PRISMA.md` | hafıza (EQUATOR ile doğrula) |
| Olgu sunumu / olgu serisi | CARE | `CARE.md` | resmi checklist (CARE 2013) + 2 Türkçe editör rehberi |
| Tanısal doğruluk çalışması | STARD | `STARD.md` | resmi checklist (STARD 2015) |
| Prognostik / prediksiyon modeli | TRIPOD | `STARD.md` içinde kısa not | hafıza (EQUATOR ile doğrula) |
| Deneysel hayvan çalışması | ARRIVE | `ARRIVE.md` | hafıza (EQUATOR ile doğrula) |

**Kaynak sütunu:** `resmi checklist` = ilgili EQUATOR kılavuzunun resmi checklist'inden birebir
türetildi; `hafıza` = damıtılmış özet — submission öncesi EQUATOR resmi checklist ile doğrula.

## Kurallar

- **Dosyada olmayan bir kılavuz istenirse uydurma.** Kullanıcıya "bu kılavuzun madde detayı
  pakette yok" de; genel `bilgi.md` §5 eşlemesiyle yetin veya kullanıcıdan kaynak iste.
- Bu özetler kılavuzların **resmi kopyası değildir**; kendi sözcüklerimizle damıtılmış
  uygulama notlarıdır. Submission öncesi resmi checklist (EQUATOR) ile son kontrol önerilir.
- Madde numaraları resmi kılavuzun numarasıyla hizalıdır ki yazar checklist doldururken
  eşleştirebilsin.

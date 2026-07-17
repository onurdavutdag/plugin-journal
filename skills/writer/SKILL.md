---
name: writer
description: >-
  Bir akademik makalenin bir bölümünü (Tartışma/Discussion, Giriş/Introduction,
  Sonuç, Özet/Abstract vb.) hedef derginin yazar kurallarına ve kullanıcının kaynak
  şablonuna uygun şekilde YAZMAK için kullan. Tetikleyiciler; "tartışma bölümünü yaz",
  "giriş yaz", "sonuç bölümünü yaz", "bu dergi için özet yaz", "makale metni oluştur",
  "şu bölümü [dergi adı] stiline göre yaz" gibi ifadeler. Kullanıcı bir makale bölümü
  YAZDIRMAK istediğinde bunu kullan (yalnızca biçimlendirme/format istediğinde
  journalstyle kullanılır — o farklıdır). Bu skill metni yazarken, kanıt gerektiren
  ve kullanıcının atıf vermediği her bilimsel/klinik iddia için OTOMATİK olarak `research`
  skill'ini çağırıp gerçek, doğrulanabilir alıntılar (DOI/PMID) ekler.
---

# Writer — Bölüm Yazımı + Otomatik Alıntı

Kullanıcının tezinden/verisinden ve gönderdiği şablondan yola çıkarak, hedef derginin
stilinde bir makale bölümü yazarsın. Yazdığın metinde kanıt gerektiren her cümle için
`research` skill'ini tetikleyip **gerçek** alıntı önerirsin. Uydurma atıf asla.

## Akış

### 1. Hedefi netleştir
Kullanıcıdan al (konuşmada zaten varsa oradan çıkar, tekrar sorma):
- **Hangi bölüm?** (Tartışma, Giriş, Sonuç, Özet, Metot vb.)
- **Hedef dergi** (ve makale türü: research article, case report vb.)
- **Kaynak dosya(lar)**: kullanıcının gönderdiği şablon/taslak `.docx`, tez, ve
  Sonuçlar/tablolar/istatistik çıktıları (Tartışma yazmak için bulgular şart).
- **Dil**: kaynak metnin dili (Türkçe → Türkçe yaz, İngilizce → İngilizce). Belirsizse sor.

### 2. Hedef dergi profilini al (journalstyle altyapısını yeniden kullan)
- **Workspace'i çöz.** Profiller artık plugin içinde değil, **çalışmanın workspace'inde** (kaynak
  `.docx`'in klasörü) `journal-profiles/` altında tutulur. Kaynak `.docx` yolundan çöz:
  `PYTHONIOENCODING=utf-8 python "${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/journalstyle/scripts/workspace.py" "<kaynak.docx>" --slug <slug>`
  Dönen JSON'daki `profiles_dir`, `yayinstili_slug_dir`, `authorguidelines_slug_dir` yollarını kullan.
- Önce `<profiles_dir>/<dergi-slug>.json` dosyasına bak.
- Yoksa **journalstyle-s-authorguidelines** subagent'ını çağır (aynı plugin'de) ve profili oluştur/önbelleğe al (`<profiles_dir>` altına). authorguidelines web+PDF checkpoint'i için journalstyle akışıyla aynı kural geçerli (web özeti kullanıcıya gösterilir).
- Profilden şunları kullan: `word_limit`, `section_order`, `abstract` kuralları,
  `citation_style` (Vancouver/APA/IEEE — bu bilgiyi `zotero`'ya aktar; atıf biçimini/kaynakçayı
  `zotero` uygular, sen yalnız `{{zref:KEY}}` işaretçisi basarsın), dil ve stil ipuçları.
- Emin olunamayan kural `null`'sa uydurma; kullanıcıyı uyar.

### 3. Kaynağı ve bulguları analiz et
- Kullanıcının şablon/taslak `.docx`'ini `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/journalstyle/scripts/extract_docx_structure.py`
  ile incele (mevcut başlıklar, ton, uzunluk, atıf stili). Yazım stilini buna uydur —
  kullanıcının sesini taklit et, kendi jenerik akademik tonunu dayatma.
- Tartışma/Sonuç için bulguları (tablolar, p-değerleri, etki büyüklükleri) kaynaktan al.
  **Sayı/yüzde/p-değeri biçimini kullanıcının global kuralına göre** yaz: Türkçe'de virgül
  ve `%` sayının önünde (ör. `%73,5`, `p=0,028`); İngilizce'de nokta ve `%` sonda
  (ör. `73.5%`, `p=0.028`). İstatistik testleri kullanıcının sembol standardıyla dipnotla.

### 3b. Yazım rehberliğini al — `writer-s-danisman`'ı otomatik çağır
Bölümü yazmadan **önce**, aynı plugin'deki `writer-s-danisman`'ı **Agent aracıyla otomatik
çağır** (onay bekleme). Ona şu bağlamı ver: hangi bölüm (Giriş/Metot/Bulgular/Tartışma/
Özet/Sonuç), çalışma tipi (RKÇ, kohort, vaka-kontrol, kesitsel, tanısal, olgu sunumu…),
PICO/hipotez ve varsa mevcut taslak. Subagent damıtılmış makale-yazımı bilgisinden
(`references/writer-s-danisman-r-bilgi.md`) şunları döndürür:
- o bölümün **IMRaD-temelli iskeleti** (paragraf/alt başlık yapısı),
- her parçada ne olması gerektiği (uzunluk, sonlanım sırası, Tablo 1/akış şeması, Bulgularda
  yorum yasağı, %95 GA'lı sayısal sunum, Tartışmada kısıt paragrafı vb.),
- çalışma tipine uygun **raporlama kılavuzu** (STROBE/CONSORT/STARD/CARE/PRISMA) istekleri,
- bölüme özgü **sık hatalar / kontrol listesi**.
Bu iskeleti ve ölçütleri yazımın çatısı olarak kullan. Not: `writer-s-danisman` **atıf
üretmez** — kaynak bulma işi §5'teki `research`'ündür.

### 3c. Yayın/örnek stilini incele — `journalstyle-s-yayinstili`'yi otomatik çağır
Bölümü yazmadan **önce**, aynı plugin'deki **journalstyle-s-yayinstili** agent'ını Agent
aracıyla **otomatik çağır** (onay bekleme). Ver: hedef dergi + slug + kaynak taslağın
konusu/anahtar kelimeleri + **workspace yolları** (`yayinstili_slug_dir`, `profiles_dir`) +
**(kullanıcı belirli bir örnek makale verdiyse — "şu makaleye göre yaz", dosya/URL/DOI)**
`user_reference_article`. Agent `<profiles_dir>/<slug>.yayinstili.json` üretir/okur (varsa taze
olanı yeniden üretmeden kullan). Dönen **fiili stili** §4 yazımının stil çatısı olarak kullan
(§3b danışmanın IMRaD iskeletiyle birlikte):
- baskın **zaman/ses** (past/present, edilgen/etken),
- **atıf yoğunluğu** (hangi bölümde ne sıklıkta — §5 research çağrılarını buna göre ayarla),
- fiili **bölüm başlıkları** ve abstract yapısı,
- **istatistik sunum biçimi** (mean ± SD, %95 CI, p gösterimi) — kullanıcının global sayı/p
  biçim kuralıyla çelişmez, onunla birlikte uygulanır.
Not: bu agent yalnız **gözlem** verir; atıf üretmez (o §5 `research`'ün işi), metni yazan sensin.
Kullanıcı örnek makale vermediyse agent dergiden otomatik benzer örnekleri seçer.

### 3d. Tartışma için literatür tartışması — NotebookLM (yalnızca Tartışma/Discussion yazılırken)
Kullanıcının NotebookLM'deki literatür havuzu, Tartışma'nın "literatürle karşılaştırma"
paragraflarının hammadde kaynağıdır. `notebooklm-mcp` MCP sunucusunun araçlarını kullan
(`mcp__notebooklm-mcp__*`): `notebook_list`, `notebook_describe`, `notebook_query`,
`source_get_content`.

- **Notebook'u bul:** kullanıcı adını verdiyse onu kullan; vermediyse `notebook_list` ile
  listele ve makale konusuyla eşleşen başlığı seç. Birden fazla aday varsa kullanıcıya sor.
- **Her ana bulgu için** notebook'a `notebook_query` ile sor: "Bu bulguyu
  (ör. X grubunda Y daha yüksekti) destekleyen veya çelişen çalışmalar hangileri, ne
  bulmuşlar?" Dönen cevaplardan şunları çıkar: hangi çalışma ne bulmuş, bizim bulguyla
  uyum/çelişki yönü, varsa mekanizma notları. Bunlar §4 Tartışma'daki
  "literatürle karşılaştırma (destekleyen/çelişen)" paragraflarının iskeletini doldurur.
- **Kural:** NotebookLM cevabı **tartışma içeriği** sağlar, atıf sağlamaz. NotebookLM'in
  işaret ettiği her çalışma §5'teki `research` üzerinden (DOI/PMID ile) doğrulanır;
  doğrulanmadan `{{zref:KEY}}` basılmaz. NotebookLM'den gelen künye asla doğrudan atıfa
  dönüşmez.
- **Sessiz atlama:** MCP sunucu kurulu/bağlı değilse, oturum düşmüşse (`nlm login`
  gerekir) ya da yazılan bölüm Tartışma değilse bu adımı sessizce atla — akış bozulmaz.
- Bilinen kısıt: NotebookLM'in resmi API'si yok; sunucu tarayıcı oturumu üzerinden çalışır
  ve Google tarafı değişince geçici kırılabilir. Hata alırsan kullanıcıya `nlm login` /
  `nlm doctor` öner ve adımı atla.

### 4. Bölümü yaz
- Hedef derginin yapısına ve kelime limitine uy. Tipik bölüm mantığı:
  - **Giriş**: problem → boşluk → amaç. Literatür iddiaları burada yoğun → alıntı gerekir.
  - **Tartışma**: ana bulgu → literatürle karşılaştırma (destekleyen/çelişen) → mekanizma
    → kısıtlar → sonuç. Her "X ile uyumlu/aksine" cümlesi bir atıf ister. Karşılaştırma
    paragraflarında §3d'nin NotebookLM çıktısını kullan (hangi çalışma ne bulmuş,
    uyum/çelişki yönü).
  - **Özet**: derginin `abstract` kurallarına (kelime limiti, yapılandırılmış mı) uy.
- Kullanıcının halihazırda eklediği atıfları **koru, değiştirme**.

### 5. Yazarken alıntıları otomatik getir — takım üyesi `research`'ü tetikle
`research`, aynı plugin'de takım üyesi bir skill'dir. Bir paragrafı yazıp kanıt gerektiren bir
iddia içerdiğini ve kullanıcının o cümleye atıf vermediğini gördüğünde, **Skill aracıyla
`research` skill'ini çağır** (onay bekleme). O skill:
- önce kullanıcının verdiği referanslara, sonra yüklenen PDF'lere — bu arada kullanıcının sabit
  `pdflerim/` kütüphanesini (research skill'inin kendi klasöründeki PDF havuzu) **daima** tarar —,
  sonra Consensus/PubMed'e bakar,
- gerçek DOI/PMID'li, doğrulanabilir referans döndürür (uydurmaz),
- her öneri için kanıt düzeyi + kaynak + neden-destekliyor açıklaması verir.

**`research`'ün bulduğu/önerdiği makaleyi metinde fiilen kullan — sadece listeleme:**
- Kaynağın **bulgusunu cümleyi desteklemek/şekillendirmek için kullan.** Cümle sonuna kuru bir
  işaretçi iliştirip geçme; makalenin ne bulduğunu metne dokun — ör. "Su ve ark. benzer şekilde
  deliryum insidansında düşüş bildirdi {{zref:KEY}}" ya da "aksine, X çalışması fark saptamadı".
  Böylece research'ün getirdiği kanıt yazının argümanına katkı sağlar.
- **Atıfı bir işaretçi olarak koy — biçimini KENDİN verme.** Cümlenin desteklendiği tam yere
  kanonik `{{zref:ITEMKEY}}` işaretçisini yaz (aynı cümlede birden çok kaynak için gruplu
  `{{zref:KEY1;KEY2}}`). İşaretçi grameri tek yerde: `../zotero/references/zref-protocol.md`.
  Metin-içi atıf numarası/biçimi (Vancouver `[1]`, APA
  yazar-yıl vb.) ve kaynakça listesi **yalnızca `zotero` skill'inin yetkisindedir** — sen ham sayı
  veya `(Yazar, Yıl)` gömme, kaynakça listesi **tutma**. Bu yetki başka hiçbir skill'de değil.
  - Kaynak **Zotero kütüphanesindeyse**: `zotero_lib.py --search` ile item anahtarını bul,
    `{{zref:ANAHTAR}}` bas.
  - Kaynak Zotero'da **değilse**: `zotero` skill'inin `add-methods` akışıyla kütüphaneye
    eklet, anahtarı al, sonra işaretçi bas (kullanıcı eklemek istemiyorsa cümleyi işaretçisiz
    bırak ve kullanıcıya bildir).
- **Mükerrer** (aynı DOI/PMID) kontrolünü `zotero` render sırasında yapar; sen aynı kaynağa aynı
  işaretçiyi kullan.
- `research` "güvenilir kanıt yok" derse cümleyi **uydurma atıfla doldurma** — kullanıcıya bildir,
  cümleyi yumuşatmayı veya kaynak vermesini öner.
- Kanıt çelişkiliyse metinde belirsizliği yansıt (ör. "kanıtlar çelişkilidir") ve iki tarafı da işle.

### 6. Sun ve raporla
- Çıktıyı **künye bloğuyla başlat** (bkz. "Rapor künyesi").
- Yazılan bölümü göster (atıflar `{{zref:KEY}}` işaretçili haliyle). Ayrı bir kısımda **her eklenen
  alıntının** research çıktı formatını (Desteklenen cümle · Referans · Neden · Kanıt düzeyi ·
  Kaynak · Sayfa/DOI/PMID) listele ki kullanıcı denetleyebilsin.
- **Atıfları görünür `[1]`'e çevirmek ve kaynakçayı basmak `zotero`'nun işi.** Bölüm `.docx`'e
  işlenecekse: metni işaretçileriyle yaz, sonra `zotero` skill'inin `zotero_cite.py` refresh'ini
  çağır — metin-içi atıflar ve kaynakça listesi orada oluşur. Kaynakçayı **sen elle yazma**.
- Docx'e yazım global kurala tabi: **mevcut bir docx güncelleniyorsa eklenen/değişen metin kırmızı
  (RGB 255,0,0)**; sıfırdan yeni docx siyah. Önce yedek al. (Atıf/kaynakça kırmızısını `zotero_cite.py`
  zaten uygular.)

## Rapor künyesi (zorunlu)

Kullanıcıya sunulan çıktı/rapor, başlığın hemen altında şu künye bloğuyla başlar; o çalışmada
**fiilen** çağrılan subagent ve **fiilen** okunan reference'lar listelenir (kullanılmayan `—`):

```
Skill: writer
Subagent: <çağrılanlar: writer-s-danisman / journalstyle-s-authorguidelines / journalstyle-s-yayinstili>
References: <okunanlar: writer-s-danisman-r-bilgi.md>
NotebookLM: <sorgulanan notebook adı / —>
---
```

## Önemli kurallar
- Alıntı uydurma — bu skill'in tek kırmızı çizgisi. Gerçek olmayan hiçbir referans metne girmez.
  Doğrulamayı `research` yapar; sen onun çıktısına güven, kendi hafızandan DOI/PMID üretme.
- Kullanıcının yazım stilini ve dilini koru; jenerik ton dayatma.
- Yalnızca cümleyi **doğrudan** destekleyen atıfı koy; teğet ilgili makaleyi koyma.
- Bu skill YAZAR; salt biçimlendirme/format işi `journalstyle`'ın, **atıf/kaynakça işi
  `zotero`'nundur**. Sen `{{zref:KEY}}` işaretçisi basarsın; kaynakçayı asla elle tutmazsın.

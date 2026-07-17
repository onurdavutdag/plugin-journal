---
name: journalstyle
description: Bir .docx makalesini belirli bir akademik derginin (Elsevier, MDPI, IEEE, Springer, Türkçe ULAKBİM dergileri vb.) yazar kurallarına göre biçimlendirmek gerektiğinde kullan. Tetikleyiciler; "bu makaleyi [dergi adı] için formatla", "dergi şablonuna uydur", "submission için hazırla", "yazar kılavuzuna göre düzenle" gibi ifadeler. Birden fazla dergiye aynı makaleyi hazırlamak için de kullanılır (her dergi için ayrı profil ve ayrı çıktı üretir).
---

# Journal Style

Bu skill, tek bir kaynak `.docx` makaleden, hedef derginin kurallarına uyan bir `.docx` çıktı üretmek için bir **pipeline** çalıştırır. İki alt-agent'a delege eder ve profil önbelleği kullanarak tekrarlayan aramaları önler.

## Akış

0. **Workspace'i çöz (her şeyden önce).** Plugin artık her çalışmayı **kaynak `.docx`'in bulunduğu
   klasör** üzerinden yürütür. Kaynak `.docx` yolunu (ve dergi slug'ını biliyorsan) vererek şunu çağır:
   `PYTHONIOENCODING=utf-8 python "${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/journalstyle/scripts/workspace.py" "<kaynak.docx>" --slug <slug>`
   (`${CLAUDE_PLUGIN_ROOT}` plugin kökünü verir; global kurulumda cwd workspace olduğu için script'ler
   bu değişkenle çağrılır — göreli `scripts/...` yolu global'de kırılır.)
   Script, eksikse `yayinstili-pdf/`, `authorguidelines-pdf/`, `journal-profiles/`, `ciktilar/`
   klasörlerini ve bir `README.md` yer tutucuyu **otomatik oluşturur** (idempotent) ve stdout'a bir
   JSON basar. Bu JSON'daki **mutlak yolları** (`profiles_dir`, `yayinstili_slug_dir`,
   `authorguidelines_slug_dir`, `outputs_dir`) ve PDF listelerini (`yayinstili_pdfs`,
   `authorguidelines_pdfs`) akışın geri kalanında kullan. Slug'ı Adım 2'de öğrenirsen script'i
   `--slug` ile tekrar çağırıp alt klasörleri kurdur. **Artık plugin-içi `references/journal-profiles/`
   / `references/yayinstili-pdf/` yollarını KULLANMA** — hepsi workspace'e taşındı.

1. **Hedefi netleştir.** Kullanıcıdan hedef dergi adını (ve varsa makale türünü: research article, review, case report vb.) al. Birden fazla dergi verildiyse her biri için ayrı ayrı bu akışı çalıştır.

2. **Profili bul veya oluştur.**
   - Önce `<profiles_dir>/<dergi-slug>.json` dosyasına bak (Adım 0'dan gelen mutlak yol). Varsa ve
     6 aydan eskiyse kullanıcıya "önbellekteki profili mi kullanayım yoksa güncel kuralları tekrar
     arayayım mı" diye sor.
   - Yoksa, **journalstyle-s-authorguidelines** subagent'ını çağır. Agent'a şunları geçir: dergi adı
     + slug + (varsa) makale türü + **`authorguidelines_slug_dir` içindeki PDF yolları**
     (`authorguidelines_pdfs`, varsa) + `profiles_dir`. Agent **her durumda web araması yapar**;
     ayrıca PDF verildiyse onu da `Read` ile okur ve **iki bulguyu birleştirmeden** döndürür
     (`web_findings`, `pdf_findings` + kısa web-özeti). Bkz. `references/journalstyle-r-authorguidelines.md`.
   - **CHECKPOINT (kullanıcı onayı — zorunlu, atlanmaz):** Agent'ın döndürdüğü **web-sonuç özetini
     kullanıcıya göster**. Sonra sor: *PDF ile web'i birleştireyim mi, yoksa sadece web / sadece PDF
     / manuel düzeltme mi?* PDF yoksa çıktı web-only olur ama **web özetini yine göster** ve onay al.
   - Kullanıcının kararına göre final profili **sen** oluştur ve `<profiles_dir>/<dergi-slug>.json`
     altına kaydet (`guidelines_source` alanını karara göre `web` / `user-pdf` / `both-merged` yap).

2.5. **Yayın stilini analiz et.** Resmi profil hazır olunca **journalstyle-s-yayinstili**
   subagent'ını çağır: dergi adı + slug + resmi profil + **kaynak `.docx`'in konusu/anahtar
   kelimeleri** (başlık/abstract/keywords'ten çıkar) + Adım 0'dan gelen **`yayinstili_slug_dir`**
   ve **`profiles_dir`** mutlak yollarını ver. Agent stili **önce
   `<yayinstili_slug_dir>` altındaki kullanıcının yüklediği örnek PDF'lerden**
   çıkarır (birincil kaynak, `style_source: "user-pdf"`); bu klasör yok/boşsa dergiden web ile
   son 5 (yoksa son 10) yıl açık erişimli 3–6 örnek makaleye **yedek** olarak düşer
   (`style_source: "journal-auto"`). Sonucu
   `<profiles_dir>/<dergi-slug>.yayinstili.json` olarak üretir (fiili
   tablo/şekil sayısı ve numaralama, caption stili, referans sayısı, bölüm başlıkları, metin
   zaman/ses, atıf yoğunluğu, istatistik sunumu — bkz. `references/journalstyle-r-yayinstili.md`).
   Bu dosya varsa ve tazeyse yeniden çalıştırma; kullanıcıya sor. Bu adım **yalnızca bilgi toplar,
   metne dokunmaz** — resmi kural profilini (`<slug>.json`) ezmez, ayrı dosyaya yazar.
   **İpucu:** kullanıcı hedef dergiye ait PDF'leri workspace'teki `yayinstili-pdf/<slug>/` klasörüne
   (Adım 0'ın kurduğu `<yayinstili_slug_dir>`) ekleyerek stil kaynağını doğrudan kontrol edebilir. Kullanıcı belirli bir örnek makale verdiyse
   (dosya/URL/DOI, ör. "şu makalenin stiline bak"), onu `user_reference_article` olarak agent'a
   geçir; agent onu da birincil stil kaynağı alır.

3. **Kaynak dokümanı analiz et.** `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/journalstyle/scripts/extract_docx_structure.py` ile mevcut `.docx`'in yapısını (başlıklar, bölümler, referans stili, tablo/şekil sayısı, kelime sayısı) çıkar. Bunu profildeki gereksinimlerle karşılaştır; eksik bölüm (örn. "Highlights", "Data Availability Statement", "Declaration of Interest") varsa kullanıcıya bildir, otomatik boş şablon ekleyebileceğini söyle.

4. **Biçimlendirmeyi uygula.**
   - Sayfa düzeni, yazı tipi, satır aralığı, kenar boşlukları, başlık stilleri gibi mekanik kurallar için **journalstyle-s-docxformat** subagent'ını, profildeki `formatting` bloğu ile birlikte çağır. Bu agent `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/journalstyle/scripts/apply_profile.py` betiğini kullanır (python-docx tabanlı). **Çıktı `.docx`** Adım 0'daki `<outputs_dir>` (workspace `ciktilar/`) altına `<makale>_<slug>.docx` olarak yazılır; agent'a çıktı yolunu bu dizinden ver.
   - **Atıf/kaynakça bu skill'in işi DEĞİL.** Docx içindeki metin-içi atıfların ve kaynakça listesinin eklenmesi/çıkarılması/güncellenmesi ve stil dönüşümü (APA/Vancouver/IEEE/Chicago vb.) **yalnızca `zotero` skill'inin yetkisindedir.** Dergi profilindeki `citation_style` bilgisini `zotero`'ya aktar; docx atıf/kaynakça işini `zotero`'ya bırak. Bu skill kaynakçaya asla dokunmaz.

5. **Doğrula ve raporla.** Raporu **künye bloğuyla başlat** (bkz. "Rapor künyesi"). Uygulama sonrası, `${CLAUDE_PLUGIN_ROOT:-$(pwd)}/skills/journalstyle/scripts/extract_docx_structure.py`'yi tekrar çalıştırıp profil gereksinimleriyle kontrol et (kelime limiti, zorunlu bölümler). Referans/atıf **formatını doğrulama ve düzeltme işi `zotero`'nundur** — burada yalnızca "atıf stili dergiyle uyumlu mu, değilse zotero'ya yönlendir" notu düş. Kullanıcıya kısa bir "uyumluluk raporu" ver: neyin otomatik düzeltildiğini, neyin manuel kontrol gerektirdiğini (örn. şekil/tablo yerleşimi, telif izinleri, atıf/kaynakça için `zotero`) listele. Raporda ayrıca, kaynak makalenin fiili tablo/şekil/referans sayısı ve stilini dergideki tipik değerlerle (`<slug>.yayinstili.json`) **karşılaştır** (ör. "bu dergide medyan 3 tablo var, taslakta 7 tablo — sadeleştirme düşünülebilir"; "dergi şekil caption'ı görselin altında veriyor, taslakta üstte").

6. **Çoklu dergi senaryosu.** Aynı makale birden fazla dergi için hazırlanacaksa, kaynak dosyayı her seferinde temiz bir kopyadan başlatarak `<outputs_dir>/<makale-adı>_<dergi-slug>.docx` şeklinde ayrı çıktılar üret. Her dergi kendi `<slug>/` alt klasörünü (yayinstili-pdf, authorguidelines-pdf) ve profillerini aynı workspace içinde paylaşır. Ortak olmayan gereksinimleri (örn. kelime limiti farkı) raporda ayrıca belirt.

## Rapor künyesi (zorunlu)

Kullanıcıya sunulan her rapor, başlığın hemen altında şu künye bloğuyla başlar; o çalışmada
**fiilen** çağrılan subagent ve **fiilen** okunan reference'lar listelenir (kullanılmayan `—`):

```
Skill: journalstyle
Subagent: <çağrılanlar: journalstyle-s-authorguidelines / journalstyle-s-yayinstili / journalstyle-s-docxformat>
References: <okunanlar: journalstyle-r-authorguidelines.md / journalstyle-r-yayinstili.md>
---
```

## Önemli kurallar

- Asla emin olmadığın bir dergi kuralını uydurma. `journalstyle-s-authorguidelines` bir kuralı doğrulayamazsa, profildeki ilgili alanı `null` bırak ve kullanıcıyı uyar — sessizce varsayım yapma.
- Profil önbelleği artık **workspace'te** `<profiles_dir>` (`<workspace>/journal-profiles/`) altında saklanır — Adım 0'da `workspace.py` ile çözülür. Plugin-içi `references/journal-profiles/` **kullanılmaz** (yalnız `_example-mdpi.json` şablonu orada örnek olarak durur).
- Docx'e dokunmadan önce her zaman orijinal dosyanın bir yedeğini al (`<ad>_original_backup.docx`).

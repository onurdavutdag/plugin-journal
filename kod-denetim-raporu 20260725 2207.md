# Kod Denetim Raporu — plugin-journal

Skill: control-codebase
Tarih: 2026-07-25 22:07 (yerel)
References: stack-notlari.md · checklist-hatalar.md · checklist-guvenlik.md
---

## Özet

**Depo sağlıklı — 🔴 kritik bulgu yok.** Sızan sır yok, injection yüzeyi yok, kaynak `.docx`
sessizce ezilmiyor, yayıncı PDF'lerinin hiçbiri git'te izlenmiyor (telif kuralı tutuyor).
Bulgular iki kümede toplanıyor: (1) **1.6.0 değişikliğinin bıraktığı belge tutarsızlığı** — kök
`README.md` hâlâ "5 agents" diyor, `/journal` komutu ve CLAUDE.md §3 tetik tablosu öğretim
modunu tanımıyor; (2) **script kenar durumları** — 4 ajanın frontmatter'ı geçerli YAML değil,
Word biçimlendirmesi hyperlink run'larını atlıyor, PMID regex'i 6 haneden kısa PMID'leri
kaçırıyor, tek bozuk PDF tüm analizi düşürüyor.

## Kapsam ve istatistik

- **Stack:** Python 3 (9 script, 2137 satır) + Claude Code plugin varlıkları (Markdown + 2 JSON
  manifest). `pyproject.toml`/`requirements.txt` **yok** — bağımlılıklar (`python-docx`,
  `pypdf`/`pymupdf`) yalnız docstring'lerde anılıyor.
- **Kaynak dosya:** 9 `.py` + 2 `.json` manifest + ~50 `.md`. **Tam okunan:** 9 Python dosyasının
  **tamamı**, 2 manifest, 6 ajanın frontmatter'ı, `commands/journal.md` frontmatter'ı, kök
  `README.md`, `CLAUDE.md`, `skills/zotero/{SKILL,README}.md`.
- **Kapsam dışı (beyan):** diğer 4 `SKILL.md`'nin gövdesi ve ~30 `references/*.md` **tam
  okunmadı** — yalnız desen taraması (grep) yapıldı. İçerik doğruluğu (ör. STROBE madde
  listelerinin doğruluğu) denetlenmedi.
- **Statik analiz:** `pyflakes` ve `ruff` **kurulu değil** (`No module named pyflakes/ruff`).
  Yerine `python -m py_compile` çalıştırıldı: **9/9 dosya temiz**. Ayrıca özel doğrulayıcılar
  yazıldı: YAML frontmatter parse, JSON parse, karakter sınırları, referans dosya varlığı,
  `git check-ignore` PDF taraması.
- **Bulgu dağılımı:** 0🔴 · 9🟡 · 5🔵 · 4❓

**Güvenlik — kontrol edildi, temiz:** hardcoded API anahtarı/parola/JWT/özel anahtar yok · SQL
yalnız sabit sorgu, string birleştirme yok · `subprocess` çağrısı liste argümanlı, `shell=True`
yok · `eval`/`exec` yok · tüm ağ uçları HTTPS (yalnız Zotero yerel API'si `http://127.0.0.1` —
normal) · 10 yayıncı PDF'inin **10'u da** git tarafından yok sayılıyor.

---

## 🟡 Orta bulgular

### O1. 4 ajanın frontmatter'ı geçerli YAML değil (tırnaksız değer içinde `: `)
- **Konum:** `agents/journalstyle-s-authorguidelines.md:3` (sütun 450) ·
  `journalstyle-s-yayinstili.md:3` (359) · `journalstyle-s-docxformat.md:3` (296) ·
  `writer-s-danisman.md:3` (293)
- **Kanıt:** `description: Belirli bir akademik derginin … çağrılır. Tipik tetikleyiciler: yeni
  bir dergi için …` — tırnaksız düz skaler içinde `: ` var.
- **Sorun:** PyYAML dördünde de `mapping values are not allowed here` ile patlıyor. **Ajanlar şu
  an yükleniyor** (çalışma zamanı ajan listesinde altısı da görünüyor) — yani canlı arıza değil;
  Claude Code'un ayrıştırıcısı PyYAML'dan hoşgörülü. Ama dosyalar geçerli YAML olmadığı için her
  katı araç (doğrulayıcı, `plugin-validator`, CI, başka bir ayrıştırıcı) bunlarda kırılır.
  **Bu, 1.5.1'de `argument-hint` için düzeltilen hatanın tıpatıp aynısı** — ders ajan
  açıklamalarına uygulanmamış. Aynı repodaki `journal-s-notebooklm` (çift tırnak) ve
  `zotero-s-teacher` (tek tırnak) doğru yazılmış.
- **Öneri:** dördünü tek tırnağa al, içerideki apostrofları ikile (`zotero-s-teacher.md` deseni).

### O2. Kök `README.md` 1.6.0'dan sonra güncellenmedi
- **Konum:** `README.md:30` ve `README.md:44-50`
- **Kanıt:** `## Contents — 1 command + 5 skills + 5 agents`; ajan tablosunda 5 satır var,
  `zotero-s-teacher` yok.
- **Sorun:** Plugin 6 ajan taşıyor. `zotero` satırı da yalnız operasyonu anlatıyor, öğretim
  modunu anmıyor. Depoya ilk bakan (ve GitHub'da görünen) dosya yanlış envanter veriyor.
  `CLAUDE.md` bakım kuralı `CLAUDE.md`'yi zorunlu kılıyor ama kök `README.md`'yi kapsamıyor —
  kural boşluğu.
- **Öneri:** başlığı "6 agents" yap, ajan tablosuna satır ekle, `zotero` skill satırına öğretim
  modunu yaz; bakım kuralına kök `README.md`'yi de ekle.

### O3. `/journal` komutu ve CLAUDE.md §3 öğretim modunu tanımıyor
- **Konum:** `commands/journal.md:39` · `CLAUDE.md:129`
- **Kanıt:** `| Zotero library, add by DOI/PMID, write bibliography into Word, change citation
  style | skill journal:zotero | …`
- **Sorun:** `/journal Zotero'da ISBN ile kitap nasıl eklerim` yazıldığında komut bunu operasyon
  işi sanıp `.docx` + DOI/PMID isteyecek; kullanıcı ders istiyor. CLAUDE.md §3.5 "komuttaki niyet
  tablosu §3 ve §7'yi yansıtır ve onlar değişince güncellenir" diyor — §7'ye öğretmen satırı
  eklendi, §3 ve komut güncellenmedi.
- **Öneri:** her iki tabloya öğretim tetikleyicilerini ekle.

### O4. Biçimlendirme hyperlink içindeki run'ları atlıyor
- **Konum:** `skills/journalstyle/scripts/apply_profile.py:111`
- **Kanıt:** `for run in para.runs:` … `run.font.name = font_family`
- **Sorun:** python-docx'te `Paragraph.runs` yalnız **doğrudan çocuk** run'ları döndürür;
  `<w:hyperlink>` içindeki run'ları görmez. Somut senaryo: kaynakçasında DOI köprüleri olan bir
  makale MDPI için biçimlendirilir — bütün metin Times New Roman 10pt olur, **köprü metinleri
  eski fontta/boyutta kalır** ve gönderim öncesi göze çarpmaz. Aynı repodaki `zotero_cite.py:465`
  bu tuzağı açıkça çözmüş (`p._element.xpath(".//w:r")` + yorum: *"INCLUDING the runs inside a
  `<w:hyperlink>`, which `Paragraph.runs` … does not see"*) — bilgi var ama taşınmamış.
- **Öneri:** `docx_util.py`'ye ortak `iter_runs(paragraph)` ekle, `apply_profile.py` onu kullansın.

### O5. PMID regex'i 6 haneden kısa PMID'leri kaçırıyor
- **Konum:** `skills/zotero/scripts/zotero_lib.py:103`
- **Kanıt:** `_PMID_RE = re.compile(r"PMID:?\s*(\d{6,9})", re.IGNORECASE)`
- **Sorun:** PMID'ler 1'den başlar; 1950-70 arası klasik makalelerin PMID'leri 4-5 hanelidir
  (ör. `PMID: 13718`). Zotero'nun `extra` alanında böyle bir PMID varsa **sessizce `None`** döner
  → `vancouver_entry()` kaynakçaya `PMID:` satırı basmaz, `--search PMID` bulmaz.
  Omurga/nöroşirürji makalelerinde klasik kaynak atfı olağan.
- **Öneri:** `(\d{1,9})`.

### O6. Field modunda belgenin en üstüne boş paragraf ekleniyor
- **Konum:** `skills/zotero/scripts/zotero_cite.py:265-271`
- **Kanıt:** `p = doc.add_paragraph()` … `body.insert(0, p._p)` — `_add_field(..., "", red=False)`
  yani görünür sonuç metni yok.
- **Sorun:** Paragrafta yalnız alan tesisatı (`fldChar`/`instrText`) var, görünür metin yok →
  Word'de **başlığın üstünde boş bir satır** olarak render edilir. Field modu varsayılan olduğu
  için her `zotero_cite.py` çıktısı bu boş satırla geliyor; dergi şablonuna göre biçimlendirilmiş
  bir belgede ilk sayfa kayar.
- **Öneri:** PREF alanını ayrı paragraf yerine ilk mevcut paragrafın başına ekle.

### O7. Tek bozuk PDF tüm yayın-stili analizini düşürüyor
- **Konum:** `skills/journalstyle/scripts/extract_pdf_text.py:36-41`
- **Kanıt:** `try: import fitz; doc = fitz.open(path); return [...]` / `except ImportError: pass`
- **Sorun:** Yalnız `ImportError` yakalanıyor. `fitz` kuruluysa ama PDF şifreli/bozuksa
  `fitz.open()` `RuntimeError`/`FileDataError` fırlatır — yakalanmaz, `main()`'deki 5 PDF'lik
  döngü ilk bozuk dosyada traceback ile ölür, diğer 4 PDF hiç okunmaz. Aynı repodaki
  `search_pdfs.py:112` bunu doğru yapıyor: `except Exception as e:` → hatayı sonuca yazıp devam.
- **Öneri:** dosya başına `try/except Exception` sar, hatayı stderr'e yaz, sonraki PDF'e geç.

### O8. Kenar boşluğunda Türkçe ondalık virgülü çökertiyor
- **Konum:** `skills/journalstyle/scripts/apply_profile.py:45`
- **Kanıt:** `setattr(section, attr, Cm(float(value)))`
- **Sorun:** Profil JSON'unu `journalstyle-s-authorguidelines` ajanı üretiyor; Türkçe bir yazar
  kılavuzundan `"margins_cm": {"top": "2,5"}` yazması olağan. `float("2,5")` → `ValueError`,
  yakalanmıyor → traceback, çıktı `.docx` hiç oluşmuyor. Aynı dosyadaki `_spacing_setter:79` bu
  durumu **düşünmüş** (`float(key.replace(",", "."))`) — kenar boşluklarına uygulanmamış.
- **Öneri:** ortak `to_float(value)` yardımcısı; başarısızlıkta `warn()` + o alana dokunma.

### O9. `--collection` belgelenen "key" filtrelemesini yapmıyor
- **Konum:** `skills/zotero/scripts/zotero_lib.py:245-248`, yardım metni `:269`
- **Kanıt:** docstring `"""Filter by collection key or (case-insensitive) name."""`; gövde
  `any(wl == c.lower() for c in it["collections"])` — `it["collections"]` **yalnız derme
  adlarını** taşıyor (`:156`, `c.collectionName`).
- **Sorun:** Kullanıcı `--list-collections` çıktısındaki `key` alanını (ör. `4XQ7RJ8P`)
  `--collection`'a verirse **sessizce boş liste** döner; hata yok, "bu dermede kaynak yok" gibi
  görünür. `--items` çağrısı hatasız bittiği için yanlış sonuç sessizce yukarı akar.
- **Öneri:** kayda `collection_keys` ekleyip key eşleşmesini gerçekten destekle.

---

## 🔵 Düşük / kalite bulguları

- **D1. NCBI'ya yazarın kişisel e-postası gidiyor.** `skills/research/scripts/pubmed_eutils.py:43`
  — `_EMAIL = os.environ.get("NCBI_EMAIL") or "onurdavut.dag@outlook.com"`. Plugin'i kuran üçüncü
  bir kişi `NCBI_EMAIL` ayarlamazsa **kendi** sorgularını yazarın adresiyle imzalar; NCBI kötüye
  kullanımda yanlış kişiye ulaşır. (Adres zaten `plugin.json` author alanında public, yeni bir
  sızıntı değil.)
- **D2. Metin modu uydurma atıf basıyor, field modu basmıyor.** `zotero_cite.py:691` metin
  modunda tüm anahtarlar bilinmezse `cite = "[?]"` yazıp belgeye gömüyor; `refresh_fields:326`
  field modunda `continue` deyip işaretçiyi olduğu gibi bırakıyor. `unknown_keys` raporlandığı
  için sessiz değil, ama iki modun davranışı tutarsız ve `[?]` gönderilecek metne sızabilir.
- **D3. Vancouver numaralandırması tabloları en sona alıyor.** `zotero_cite.py:452-459`
  `_iter_paragraphs` önce tüm gövde paragraflarını, sonra tabloları geziyor. Belgenin ortasındaki
  bir tablo hücresindeki atıf, kendisinden sonra gelen gövde atıflarından **daha büyük** numara
  alır — Vancouver'ın "ilk görünme sırası" kuralına aykırı.
- **D4. `by_doi` NCBI nezaket gecikmesini atlıyor.** `pubmed_eutils.py:141` —
  `efetch(esearch(...))` iki isteği arka arkaya atıyor; `main()`'deki `--query` yolu
  `time.sleep(_GAP)` yaparken `--doi` yolu yapmıyor.
- **D5. Bileşen sınırını aşan iki çıplak yol.**
  `skills/research/references/research-r-pdf.md:53` zotero'nun referansını
  `references/zotero-r-storage-bridge.md` diye anıyor (research içinden çözülürse yok) ·
  `skills/peerreview/README.md:51` `../writer/references/…` kullanıyor — CLAUDE.md §2
  `../<other-skill>/` biçimini açıkça yasaklıyor. İkisi de düzyazı, çalışma zamanı çağrısı değil.

---

## ❓ Sorular (emin olunamayanlar)

- **S1. `${CLAUDE_PLUGIN_ROOT}` ajan/skill gövdesinde gerçekten genişliyor mu?** Spesifikasyon bu
  değişkeni hook ve MCP yapılandırmaları için belgeliyor; markdown gövdesinde genişletildiğine
  dair doğrulama bulunamadı. Genişlemiyorsa `Read` aracına literal `${CLAUDE_PLUGIN_ROOT}/...`
  gider ve **5 ajanın referans okuması sessizce başarısız olur**. Altı ajandan yalnız
  `zotero-s-teacher` `Glob` yedeği taşıyor. Bilinçli varsayım mı, yoksa yedek her ajana eklenmeli mi?
- **S2. `zotero_lib.py:229` — `SELECT key, value FROM settings WHERE setting = 'account'`.**
  Zotero `settings.value` alanını JSON olarak saklıyor; `str(v)` bir JSON dizesini tırnaklarıyla
  (`"12345"`) döndürebilir ve `item_uri()` bozuk URI üretir. Gerçek kütüphanede doğrulandı mı?
- **S3. `pubmed_eutils.py:141` — `f"{doi}[AID] OR {doi}[DOI]"`.** PubMed'in resmî alan etiketi
  listesinde `[DOI]` yok (`[AID]` var). Geçersiz etiket sorguyu bozmuyor mu, bilerek mi eklendi?
  (Ağ çağrısı yapılmadığı için doğrulanmadı.)
- **S4. `search_pdfs.py:134` — `break  # one hit per page`.** Üç terim aranıp sayfada üçü de geçse
  yalnız ilki raporlanıyor; çağıran diğer terimlerin de geçtiğini göremiyor. Kasıtlı mı?

---

## Uygulanan düzeltmeler

Kullanıcı onayı: **🟡 + 🔵 hepsi (O1-O9 + D1-D5)**. ❓ S1-S4 dokunulmadı — S1 netleşmeden
ajanlara toplu `Glob` yedeği eklenmez.

## Düzeltme sonucu — 14/14 uygulandı, sürüm 1.6.1

| # | Dosya(lar) | Ne yapıldı |
|---|---|---|
| O1 | 4 ajan `.md` | `description` tek tırnağa alındı, iç apostroflar ikilendi |
| O2 | `README.md` | "6 agents", `zotero-s-teacher` satırı, `zotero`'ya iki mod |
| O3 | `commands/journal.md`, `CLAUDE.md` §3 | Öğretim satırı eklendi; komutun "Limits" bölümünde doğrudan çağrılabilir ajan sayısı 1→2 |
| O4 | `docx_util.py`, `apply_profile.py` | Yeni `iter_runs()` (`.//w:r`) — köprü run'ları da biçimleniyor |
| O5 | `zotero_lib.py` | `_PMID_RE` `(\d{6,9})` → `(\d{1,9})\b` |
| O6 | `zotero_cite.py` | PREF alanı ayrı boş paragraf yerine ilk paragrafın içine (`<w:pPr>`'den sonra) |
| O7 | `extract_pdf_text.py` | Backend yokluğu ↔ dosya bozukluğu ayrıldı; bozuk PDF atlanıp devam ediliyor |
| O8 | `docx_util.py`, `apply_profile.py` | Yeni `to_float()` — `"2,5"` kabul; çevrilemezse uyarı + o alana dokunma |
| O9 | `zotero_lib.py` | Kayda `collection_keys` eklendi; `--collection` artık key ile de filtreliyor |
| D1 | `pubmed_eutils.py` | Sabit e-posta kaldırıldı; `NCBI_EMAIL` yoksa parametre gönderilmiyor + stderr uyarısı |
| D2 | `zotero_cite.py` | Metin modu da anahtar çözülmezse `[?]` basmıyor, işaretçiyi bırakıyor |
| D3 | `zotero_cite.py` | `_iter_paragraphs` `body.iter(w:p)` ile gerçek belge sırasında |
| D4 | `pubmed_eutils.py` | `by_doi` içine `time.sleep(_GAP)` |
| D5 | `research-r-pdf.md`, `peerreview/README.md` | İki çıplak yol `${CLAUDE_PLUGIN_ROOT:-$(pwd)}`'a çevrildi |

**Ek (kapsam içi, aynı sözleşme):** `zotero_cite.load_library()` bozuk stdout'ta traceback yerine
tek JSON hata nesnesi döndürüyor — docstring'in "exactly ONE JSON object per run" sözü artık her
yolda tutuyor.

**Kök neden kapatıldı:** `CLAUDE.md` bakım kuralı artık **dört yönlendirme yüzeyini** (CLAUDE.md ·
kök `README.md` · `commands/journal.md` · `plugin.json`) adıyla sayıyor — O2/O3'ün tekrar etmemesi için.

### Statik doğrulama

| Kontrol | Sonuç |
|---|---|
| 12 frontmatter bloğu katı PyYAML | **12/12 OK** (önce 4 hata) |
| `py_compile` 9 script | **9/9 OK** |
| `plugin.json` + `marketplace.json` parse | OK — v1.6.1, 6 ajan |
| 5 `SKILL.md` sürüm hizası | 1.6.1 |
| İzlenen PDF | yok (telif kuralı korunuyor) |

### Davranış doğrulaması (gerçek dosyalarla)

| Test | Sonuç |
|---|---|
| **O4** köprülü `.docx` → `apply_profile.py` | Köprü içindeki run **Times New Roman 12pt** oldu (`Paragraph.runs` 1 run görüyordu, `iter_runs` 2) |
| **O8** profilde `"top": "2,5"`, `"left": "3,0"` | `top=2.50 left=3.00 cm` — çökme yok |
| **O6** field modu çıktısı | PREF alanı başlık paragrafının **içinde**; üstte boş paragraf **yok** |
| **D3** ortada tablo, sonrasında gövde atfı | Tablo `[1]`, sonraki gövde `[2]` — gerçek belge sırası |
| **D2** çözülemeyen anahtar | Her iki modda `{{zref:ZZZZZZZZ}}` yerinde, `[?]` basılmadı, `unknown_keys` raporladı |
| **O7** bozuk PDF + sağlam PDF | Bozuk atlandı (uyarı), sağlam olan analiz edildi (27 sayfa, 4803 kelime) |
| **O5** `PMID: 13718` / `PMID: 1` / `PMID: 12345` | `13718` / `1` / `12345` — üçü de yakalandı (önce `None`) |
| **O9** `--collection EBW96XYW` (key) | **112 kayıt** (önce 0) |

**Kabul ölçütü karşılandı:** 5/5 statik kontrol, 8/8 davranış testi geçti; `zotero_cite.py` ve
`zotero_lib.py` çıktı sözleşmesini (tek JSON, `_zref.docx` varsayılanı) koruyor.

**Dokunulmayan:** ❓ S1-S4. Özellikle **S1** — `${CLAUDE_PLUGIN_ROOT}`'un ajan gövdesinde
genişleyip genişlemediği netleşmeden ajanlara toplu `Glob` yedeği eklenmedi.

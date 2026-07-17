# Citation format — SAHİBİ: zotero

Docx içindeki metin-içi atıf ve kaynakça biçiminin **tek yetkili tanımı burasıdır.**
Diğer skiller (research/writer/journalstyle) atıf/kaynakça biçimlemez; künye/kanıt üretip
bu skile devreder. `zotero_cite.py` bu kuralları uygular.

Varsayılan stil **Vancouver** (numaralı, çoğu biyomedikal dergi). Kullanıcı/dergi başka stil
isterse `references/styles.md` çözümleme sırasıyla geç.

## Vancouver — kaynakça listesi biçimi

`Authors. Title. Journal Abbreviation. Year;Volume(Issue):Pages. doi:DOI. PMID: PMID.`

Kurallar:
- Yazarlar *Soyad Baş harfler*, virgülle. **6'dan fazla yazar** varsa ilk altısı + `et al.`
- Dergi adı kısaltılır (NLM/Index Medicus stili).
- **DOI** varsa ekle; **PMID** varsa ekle.

**Örnek (dergi makalesi, DOI + PMID):**

```
1. Su X, Meng ZT, Wu XH, Cui F, Li HL, Wang DX, et al. Dexmedetomidine for prevention of
   delirium in elderly patients after non-cardiac surgery: a randomised, double-blind,
   placebo-controlled trial. Lancet. 2016;388(10054):1893-1902.
   doi:10.1016/S0140-6736(16)30580-3. PMID: 27542303.
```

## Diğer stiller (istenirse)

- **AMA**: Vancouver'a çok yakın; metin-içi üst-simge numara.
- **APA (7.)**: yazar–tarih, ör. `Su, X., Meng, Z. T., ... (2016). Title. *Lancet*, 388(10054),
  1893–1902. https://doi.org/10.1016/S0140-6736(16)30580-3` — `zotero_cite.py --style author-date`.
- Dergiye özel numaralı/yazar-yıl stil için `references/styles.md` (yerel CSL → Style Repository).
- Makale zaten bir stil kullanıyorsa onu takip et; kullanıcının mevcut referansları stili ele
  veriyorsa varsayılanı dayatma.

## De-duplikasyon

Kaynakçaya eklemeden önce zaten var olup olmadığını kontrol et:
- **Aynı DOI veya aynı PMID = aynı makale** — asla iki kez ekleme.
- Yakın-mükerrerlere dikkat: preprint vs yayımlanmış sürüm, early-access vs sayfalı final. Final
  yayımlanmış sürümü tercih et, ikisini birden listeleme.
- Kullanıcının o cümleye kendi eklediği atıfı önerme; mevcut atıfı olduğu gibi bırak.

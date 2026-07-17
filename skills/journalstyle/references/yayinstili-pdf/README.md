# yayinstili-pdf — Yerel yayın stili örnek makaleleri (ESKİ / örnek konum)

> **ÖNEMLİ — konum değişti.** Yayın stili örnek PDF'leri artık plugin'in içinde değil, her
> **çalışmanın kendi workspace'inde** (kaynak `.docx`'in klasörü) `yayinstili-pdf/<slug>/` altında
> tutulur. `journalstyle-s-yayinstili` agent'ı bu klasörü skill'ten `yayinstili_slug_dir` mutlak
> yoluyla alır. Workspace `skills/journalstyle/scripts/workspace.py` ile çözülür ve klasör yoksa
> otomatik oluşturulur. Bu plugin-içi klasör yalnızca **eski/örnek** olarak durur; yeni işlerde
> workspace'i kullan.

`journalstyle-s-yayinstili` agent'ı, bir derginin **fiili yayın geleneklerini** (tablo/şekil
sayısı ve numaralama, caption konumu, referans sayısı, bölüm başlıkları, cümle uzunluğu, atıf
biçimi, istatistik sunumu) bu PDF'lerden çıkarır. **Birincil stil kaynağıdır**; web araması
yalnızca eşleşen yerel PDF yoksa yedek olarak çalışır.

## Kullanım (workspace'te)

Hedef dergi için örnek makaleleri workspace içinde **derginin slug'ı adında bir alt klasöre** koy:

```
yayinstili-pdf/
  <slug>/
    makale1.pdf
    makale2.pdf
```

- `<slug>`, `journal-profiles/*.json` dosyalarındaki slug ile **aynıdır**
  (ör. The Spine Journal → `thespinejournal`).
- 3–6 yakın-tarihli, konu-benzeri makale ideal; 1–2 de olur (güvenilmez metrikler `null` kalır).
- PDF'ler gerçek metin katmanı içermeli (taranmış-görsel PDF'lerde metin çıkarımı zayıf olur).

Örnek: `yayinstili-pdf/thespinejournal/` — 5 The Spine Journal makalesi.

## Telif

Agent bu PDF'lerden **hiçbir cümle/caption/abstract metnini verbatim kopyalamaz**; yalnızca
sayısal metrik ve kural biçiminde yapısal örüntü çıkarır. PDF'ler yalnız yerelde stil analizi
için tutulur.

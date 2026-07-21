# journal

Akademik/tıbbi makale hazırlığı için Claude Code eklentisi (marketplace: `onur-plugins`).
Bir makaleyi **yaz → kaynak bul → kaynakça bas → dergiye formatla → hakem gözünden eleştir**
hattında yürütür. İçerik Türkçedir.

## Kurulum

```
/plugin marketplace add onurdavutdag/journal-plugin
/plugin install journal@onur-plugins
```

## İçerik — 5 skill + 4 agent

| Skill | Görev |
|---|---|
| `writer` | Makale bölümü (Giriş/Tartışma/Özet/Sonuç) hedef dergi stiline göre yazar; kanıt gerektiren iddialar için otomatik `research` çağırır. |
| `research` | Bilimsel/klinik iddialar için gerçek, doğrulanabilir kaynak (DOI/PMID) bulur — asla uydurmaz. |
| `journalstyle` | Bir `.docx` makalesini hedef derginin yazar kurallarına göre biçimlendirir (profil çıkarma → biçim uygulama → atıf formatı). |
| `zotero` | Kullanıcının gerçek Zotero kütüphanesine bağlanır; DOI/PMID ile kaynak ekler, Word'e atıf/kaynakça basar. |
| `peerreview` | Gönderim öncesi makaleyi hakem gözüyle değerlendirir (metodoloji, istatistik, raporlama standartları). |

| Agent (subagent) | Görev |
|---|---|
| `journalstyle-s-authorguidelines` | Dergi "Author Guidelines" kurallarını web + workspace PDF'inden çıkarır. |
| `journalstyle-s-yayinstili` | Dergide yayınlanmış gerçek makaleleri inceleyip fiili yazım geleneklerini çıkarır. |
| `journalstyle-s-docxformat` | Mekanik `.docx` biçimlendirmeyi (yazı tipi, punto, kenar boşluğu) uygular. |
| `writer-s-danisman` | Bölüm yazılmadan önce IMRaD-temelli yazım rehberliği ve eleştiri verir. |

Tam mimari referansı, tetikleyici tablosu ve workspace modeli için: **[`CLAUDE.md`](CLAUDE.md)**
(canlı doküman — her değişiklikte güncellenir).

<!-- Oluşturma: 20260725 2140 -->
# Kütüphane organizasyonu — dermeler, etiketler, mükerrer kayıtlar, notlar ve ekler

> İşaretler: ⚔️ kaynaklar ayrışıyor · ⚠️ videoda net değildi, kesin konuşma · 🔴 veri kaybı riski · ⭐ ders notları dışı

## Derme (Collection)

Derme = klasör. Kaynaklar konu, tez ya da makale bazlı gruplanır.

- **Kitaplığım** her eserin ana kaydını tutar; dermeler o kayda giden birer kısayoldur.
- Bir eser **birden fazla dermede** bulunabilir — sürükle-bırak ile eklenir, kopya oluşmaz.
- ⚠️ **Alt derme:** derme adına sağ tıklanıp *Yeni Alt Derme* seçilir. Menü adının sürümlere göre değişebileceğini unutma.
- Öneri: her makale/tez için ayrı bir derme açılır, o çalışmanın kaynakları oraya toplanır. Hem düzen sağlar hem 300 MB kotayı yönetilebilir kılar.

**🔴 Silmede iki ayrı seçenek var, karıştırılmaz:**

| Sağ tık seçeneği | Ne yapar |
|---|---|
| **Eseri dermeden sil** | Yalnız o klasörden çıkarır; eser **Kitaplığım**'da kalır |
| **Eseri çöp sepetine gönder** | Eseri kütüphaneden alır, çöp sepetine atar |

Çöp sepeti bir güvenlik ağıdır — yanlışlıkla silinen eser oradan geri alınabilir. 🔴 Çöp sepetini boşaltmak geri alınamaz; öncesinde yedek (`zotero-r-eklenti-senkron.md`).

## Etiketler (Tags)

Kaynaklara anahtar kelime atanır; sol alttaki **etiket seçici**den tıklanarak kütüphane anında filtrelenir. Dermeden farkı: derme klasördür (hiyerarşik), etiket çapraz kesittir (bir eser istediği kadar etiket alır).

## Mükerrer kayıtlar — 🔴 silme değil, birleştir

Aynı eser yanlışlıkla iki kez eklendiğinde:

1. Sol paneldeki **Yenilenmiş Eserler** (Duplicate Items) sekmesine gidilir.
2. Zotero aynı olduğunu düşündüğü kayıtları eşleştirip gösterir.
3. Kayıtlar seçilir, sağ panelde çıkan **Eserleri Birleştir** (Merge Items) butonuna basılır.
4. Kitaplıkta tek kayıt kalır.

⚠️ Hangi kaydın **ana kayıt (master item)** olacağının seçilip seçilmediği kaynaklarda anlatılmıyor — bu ayrıntıda kesin konuşma.

**Neden silmek değil birleştirmek:** aynı isimli iki ayrı kayıt olduğunda Zotero bunları farklı eser sanır ve ikinci atıflarda — normalde yalnız soyadı + kısa eser adı gelmesi gerekirken — ayırt etmek için parantez içinde ek bilgi basmaya başlar. Ayrıntı ve "hayalet kayıt" sorunu → `zotero-r-tuzaklar.md`.

🔴 Birleştirme geri alınamaz. Büyük bir temizlik öncesi **Dosya → Kitaplığı dışarı aktar** ile RDF yedeği alınır.

## Notlar ve ekler

- Bir künye seçilip sağ panelden **Not** eklenir: okuma notu, alıntı, "bu kaynağı şu bölümde kullan" gibi hatırlatmalar.
- Künyeye **ek (attachment)** iliştirilebilir: PDF, Word dosyası, web anlık görüntüsü (snapshot).
- Ekler **ataş işaretinden** görülür.
- 🔴 Ek silmek kotayı rahatlatır ama dosya gider — silmeden önce dosyanın başka bir yerde durduğu doğrulanır (`zotero-r-eklenti-senkron.md`).

## Dosyalanmış / dosyalanmamış eserler

Sol panelde **Dosyalanmamış Eserler** (hiçbir dermeye atanmamış kayıtlar) ve **Çöp Sepeti** ayrı görünür. Connector'le hızlı kaydedilen eserler burada birikmeye eğilimlidir; ara ara ilgili dermeye taşınır.

## Grup kitaplıkları

Sol altta, kişisel kütüphanenin altında görünür. Ortak proje ekipleri ve hazır künye havuzları (DİA, Şamile) buradan gelir → `zotero-r-ilahiyat.md`.

## Kütüphaneyi paylaşma / taşıma

*Dosya → Kitaplığı dışarı aktar* → **Zotero RDF** → dosya bir arkadaşa gönderilir (WhatsApp, flash bellek). Karşı taraf dosyaya çift tıklar, "içeri aktar" onayını verir; eserler yeni bir dermeye yüklenir. Aynı akış yedekleme akışıdır.

## Sık hatalar

- "Eseri dermeden sil" ile "çöp sepetine gönder"i karıştırmak.
- Mükerrer kaydı silip yeniden eklemek (atıf bozulur).
- Her şeyi tek dermeye yığıp sonra bulamamak.
- Connector'le kaydedip dermeye taşımayı unutmak → Dosyalanmamış Eserler şişer.

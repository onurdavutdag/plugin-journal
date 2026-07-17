# pdflerim — kişisel PDF kütüphanesi

Kendi makale PDF'lerini **buraya** bırak.

`research` skill'i, yazım sırasında (writer bir iddia için kaynak istediğinde)
bu klasörü **her zaman** otomatik tarar:

```
python ../scripts/search_pdfs.py --dir . --terms "anahtar kelime" "kavram" ...
```

Eşleşen sayfalar Read aracıyla doğrulanır ve gerçek DOI/PMID'li atıf olarak önerilir. Uydurma
atıf asla — sadece bu PDF'lerde veya doğrulanan kaynaklarda gerçekten bulunan kanıt kullanılır.

- Klasör boşsa research sessizce genel workspace/PubMed aramasına geçer.
- PDF metin çıkarımı için `pip install pypdf` (yoksa research PDF'leri doğrudan Read ile okur).

Ayrıntı: `../references/research-r-pdf.md` (adım 0).

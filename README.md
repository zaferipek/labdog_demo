# Lab Dog - Profesyonel Ar-Ge Yönetimi (İskelet)

Bu proje, Ar-Ge süreçlerini Salesforce Lightning tarzında, oyunlaştırılmış bir arayüzle yönetmek için hazırlanmış **Lab Dog** isimli örnek bir iskelettir.

## Özellikler (Bu aşamada iskelet)

- **Modüler mimari**
  - `app.py`: Streamlit giriş noktası (sidebar + sayfa yönlendirme)
  - `database.py`: SQLAlchemy ile Proje · Test · Hammadde veri modeli ve 5 Ar-Ge grubu
  - `auth.py`: Basit kullanıcı/rol ve giriş sistemi (demo kullanıcılar)
  - `styles.py`: Salesforce benzeri minimalist, hafif “oyunsu” CSS
- **Veri yapısı**
  - Projeler, Testler ve Hammaddeler arasında ilişkili yapı
  - 5 ana Ar-Ge grubu: PUD, PU, Hot Melt, Mürekkep, Boya/Finish
- **Arayüz**
  - Kart bazlı dashboard
  - İlerleme çubukları ve dairesel (radial) gösterge
  - Global arama (sidebar + dialog): SQLite **FTS5** (`search_fts.py`), gerekirse LIKE yedek; aranabilir tablolarda ORM **commit** sonrası indeks bir sonraki aramada tam yenilenir (`mark_labdog_fts_stale`)

## Kurulum

1. Sanal ortam (önerilir)

```bash
python -m venv .venv
.venv\\Scripts\\activate
```

2. Bağımlılıkları yükle

```bash
pip install -r requirements.txt
```

3. Uygulamayı çalıştır (Streamlit)

```bash
streamlit run app.py
```

**Not:** `app.py` ile `labdog_app.py` aynı arama kabuğunu kullanır; yedek giriş noktası olarak `labdog_app.py` de çalıştırılabilir.

4. Tarayıcıda Streamlit adresini açın (terminalde yazar).

Demo kullanıcılar:

- admin / admin
- pud_lead / pud123


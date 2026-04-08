# Lab Dog — “Yeni …” formları (modal pattern)

## Karar (plan ile uyumlu)

| Seçenek | Not |
|--------|-----|
| **`@st.dialog`** | **Seçildi.** Liste düzenini bozmaz; overlay modal hissi; widget etkileşimleri dialog fragment’ında yeniden çalışır. |
| URL `?modal=new_project` | Yedek: tarayıcı geri/ileri ile tam uyum veya `st.dialog` ile sorun çıkarsa kullanılır. |

## Uygulama kuralları

1. **Tek pattern:** Yeni Proje, Yeni Görev, Yeni Hammadde aynı yaklaşımı kullanır (`st.dialog` + başlıkta “✚ Yeni …” tetikleyici).
2. **Kapatma:** Form içinde **İptal** (`st.rerun()`); dışarı tıklama / **X** / **ESC** için `on_dismiss="rerun"` ile ana script tekrar çalışır ve dialog yeniden çağrılmadığı için kapanır.
3. **Başarılı kayıt:** `st.rerun()` — liste güncellenir, dialog kapanır.
4. **Oturum:** Gereksiz `pj_show_form` benzeri toggle kullanılmaz; dialog açılışı yalnızca ilgili butonun tıklandığı script turunda `dialog_fn()` çağrısı ile yapılır.

## Dosyalar

- Projeler: `views/projeler.py` — `_new_project_dialog`
- Görevler: `views/gorevler.py` — `_new_task_dialog`
- Hammaddeler: `views/hammaddeler.py` — `_new_material_dialog`

## Phase 2

- Sorun çıkarsa veya çok sayfalı akış gerekirse URL-tabanlı modal parametreleri (`app.py` + `query_params`) değerlendirilir.

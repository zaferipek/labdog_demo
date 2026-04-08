"""Ayarlar — Açılış, Dil, Kullanıcılar, Toplu yükleme (üst sekmeler)."""
from __future__ import annotations

import streamlit as st

from ld_rerun import ld_rerun

from database import (
    get_ai_settings,
    get_all_projects,
    get_user_preferences,
    save_user_preferences,
    set_ai_settings,
)
import views.users as users_view
import views.toplu_yukleme as toplu_yukleme_view

_STARTUP_TARGETS: list[tuple[str, str]] = [
    ("dashboard", "Dashboard"),
    ("projeler", "Projeler"),
    ("gorevler", "Görevler"),
    ("hammaddeler", "Hammaddeler"),
    ("ar_ge_talepleri", "Ar-Ge Talepleri"),
    ("raporlar", "Raporlar"),
]

_DASH_SUB_OPTS: list[tuple[str, str]] = [
    ("cards", "Kart seçim ekranı (özet)"),
    ("yonetim", "Yönetim Bakışı"),
    ("performans", "Ar-Ge Performans Analizi"),
]


def _render_tab_startup(current_user) -> None:
    """Giriş sonrası hangi sayfa ve (Dashboard ise) alt görünüm."""
    prefs = get_user_preferences(current_user.id)
    st.markdown(
        "<p class='ld-settings-lead'>Oturum açtığınızda veya yalnızca "
        "<code>?token=</code> ile geldiğinizde açılacak sayfa. "
        "Tarayıcıda geçerli <code>page=</code> varken o önceliklidir.</p>",
        unsafe_allow_html=True,
    )

    keys = [k for k, _ in _STARTUP_TARGETS]
    labels = [lbl for _, lbl in _STARTUP_TARGETS]
    cur_target = prefs["startup"].get("target", "dashboard")
    if cur_target not in keys:
        cur_target = "dashboard"
    t_index = keys.index(cur_target)

    sel_label = st.selectbox(
        "Varsayılan sayfa",
        labels,
        index=t_index,
        key="ld_prefs_target_lbl",
    )
    sel_key = keys[labels.index(sel_label)]

    sub_keys = [k for k, _ in _DASH_SUB_OPTS]
    sub_lbls = [x for _, x in _DASH_SUB_OPTS]
    dash_sub = prefs["startup"].get("dash_sub", "cards")
    if dash_sub not in sub_keys:
        dash_sub = "cards"
    d_index = sub_keys.index(dash_sub)

    chosen_sub = prefs["startup"].get("dash_sub", "cards")
    if sel_key == "dashboard":
        picked_lbl = st.selectbox(
            "Dashboard görünümü",
            sub_lbls,
            index=d_index,
            key="ld_prefs_dash_sub_lbl",
            help="Yalnızca açılış sayfası Dashboard iken uygulanır.",
        )
        chosen_sub = sub_keys[sub_lbls.index(picked_lbl)]
    else:
        st.info(
            "Dashboard dışı bir sayfa seçtiğinizde, kayıtlı dashboard alt görünümü "
            "saklanır; tekrar Dashboard seçtiğinizde kullanılır."
        )

    chosen_pid: int | None = None
    if sel_key == "projeler":
        projects = get_all_projects()
        p_labels: list[str] = ["(Proje listesi — tek proje açma)"]
        id_for: dict[str, int | None] = {p_labels[0]: None}
        for p in projects:
            lab = f"{p['name']} ({p['code']})"
            p_labels.append(lab)
            id_for[lab] = int(p["id"])

        saved_pid = prefs["startup"].get("project_id")
        default_ix = 0
        if saved_pid is not None:
            try:
                sid = int(saved_pid)
                for i, lab in enumerate(p_labels):
                    if i == 0:
                        continue
                    if id_for.get(lab) == sid:
                        default_ix = i
                        break
            except (TypeError, ValueError):
                pass

        pick = st.selectbox(
            "Açılışta açılacak proje (isteğe bağlı)",
            p_labels,
            index=default_ix,
            key="ld_prefs_project_pick",
        )
        chosen_pid = id_for[pick]

    if st.button("Açılış tercihlerini kaydet", key="ld_save_startup_prefs", type="primary"):
        upd = {
            "startup": {
                "target": sel_key,
                "dash_sub": chosen_sub,
                "project_id": chosen_pid if sel_key == "projeler" else None,
            },
        }
        ok, msg = save_user_preferences(current_user.id, upd)
        if ok:
            st.success(msg)
            st.session_state.pop("ld_startup_applied", None)
        else:
            st.error(msg)


def _render_tab_ai(current_user) -> None:
    """API anahtarı + master prompt; yalnızca Admin."""
    if current_user.role.value != "Admin":
        st.warning(
            "⛔ Yapay zeka ayarları yalnızca **Admin** rolü tarafından görüntülenebilir ve kaydedilebilir."
        )
        return

    st.markdown(
        "<p class='ld-settings-lead'>Gelecekteki analiz ve yardımcı özellikler için model "
        "erişimi. <strong>Üretim ortamında</strong> API anahtarını tercihen "
        "<code>.streamlit/secrets.toml</code> içinde "
        "<code>OPENAI_API_KEY</code> veya <code>LABDOG_AI_API_KEY</code> olarak tanımlayın; "
        "veritabanı saklaması geliştirme / MVP içindir ve diskte düz metin olarak durur.</p>",
        unsafe_allow_html=True,
    )

    settings = get_ai_settings()
    src = settings["api_key_source"]

    if src == "secrets":
        st.success(
            "API anahtarı **Streamlit Secrets** üzerinden yükleniyor. "
            "Çalışma zamanında bu değer önceliklidir."
        )
        if settings.get("has_database_api_key"):
            st.caption(
                "Veritabanında da bir anahtar kayıtlı; şu an kullanılmıyor. "
                "Aşağıdan silebilir veya yedek olarak güncelleyebilirsiniz."
            )
    elif src == "database":
        st.info("API anahtarı veritabanında saklanıyor. Mümkünse Secrets’a geçin.")
    else:
        st.warning(
            "Yapılandırılmış bir API anahtarı algılanmadı. Secrets ekleyin veya "
            "aşağıdan veritabanına kaydedin."
        )

    st.caption(
        "Durum özeti: "
        f"anahtar kaynağı = **{src}**; "
        f"çalışma için anahtar {'yapılandırıldı' if settings.get('api_key') else 'eksik'}."
    )

    mp_key = "ld_ai_master_prompt"
    if mp_key not in st.session_state:
        st.session_state[mp_key] = settings["master_prompt"]

    st.text_area(
        "Master prompt (sistem talimatı)",
        key=mp_key,
        height=200,
        help="Model çağrılarına eklenecek genel talimat veya bağlam.",
    )

    st.markdown("**API anahtarı (veritabanı)**")
    pw = st.text_input(
        "API anahtarı",
        type="password",
        key="ld_ai_api_key_input",
        label_visibility="collapsed",
        placeholder=(
            "Yeni anahtarı yapıştırın (boş bırakırsanız mevcut DB anahtarı korunur)"
            if src == "database" and settings.get("api_key")
            else "API anahtarını yapıştırın"
        ),
    )

    clear_db_key = st.checkbox(
        "Veritabanında kayıtlı API anahtarını sil",
        key="ld_ai_clear_api_key",
        disabled=not settings.get("has_database_api_key"),
    )

    if st.button("AI ayarlarını kaydet", key="ld_ai_save", type="primary"):
        master = (st.session_state.get(mp_key) or "").strip()
        if clear_db_key:
            api_upd: str | None = ""
        elif pw.strip():
            api_upd = pw.strip()
        else:
            api_upd = None

        ok, msg = set_ai_settings(master, api_key_update=api_upd)
        if ok:
            st.success(msg)
            st.session_state.pop("ld_ai_api_key_input", None)
            st.session_state[mp_key] = get_ai_settings()["master_prompt"]
            st.session_state.pop("ld_ai_clear_api_key", None)
            ld_rerun()
        else:
            st.error(msg)


def _render_tab_language(_current_user) -> None:
    """Dil — şimdilik yalnızca TR; ayrı sekme ile net ayrım."""
    st.markdown(
        "<p class='ld-settings-lead'>Uygulama dilini seçin. "
        "Şu an yalnızca Türkçe arayüz tam desteklenmektedir.</p>",
        unsafe_allow_html=True,
    )
    st.selectbox(
        "Arayüz dili",
        ["Türkçe"],
        index=0,
        key="ld_prefs_lang",
        help="İleride buradan kayıt yapılacak.",
    )
    st.warning(
        "**English** arayüzü yakında eklenecek; şimdilik tüm menü ve formlar Türkçedir."
    )
    if st.button("Dil tercihini kaydet (TR)", key="ld_save_lang_prefs"):
        ok, msg = save_user_preferences(_current_user.id, {"ui": {"language": "tr"}})
        if ok:
            st.success(msg)
        else:
            st.error(msg)


def render(current_user) -> None:
    st.markdown(
        "<div class='ld-page-header'>"
        "<h1 class='ld-page-title'>Ayarlar</h1>"
        "<p class='ld-page-sub'>Sol menüdeki ⚙ simgesinden bu sayfaya dönebilirsiniz.</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    with st.expander("Tarayıcı Geri / İleri ve yükleme hakkında", expanded=False):
        st.markdown(
            "LabDog, Streamlit ile sunucu tarafında çizilir. Tarayıcıdaki "
            "Geri veya İleri düğmesi çoğu zaman tam sayfa yenilemesi yapar; "
            "klasik tek sayfa uygulamasındaki gibi anında önceki görünüme dönüş "
            "bu mimaride beklenmemelidir. Daha akıcı geçişler ileride ayrı bir ön yüz "
            "(örneğin SPA) ile değerlendirilebilir.\n\n"
            "Sayfa, proje, sekme ve arama hedefi gibi adres çubuğu parametreleri "
            "senkron tutulur; anlamlı geri adımları için küçük bir geçmiş düzeltmesi "
            "kullanılır."
        )

    tab_startup, tab_lang, tab_ai, tab_users, tab_import = st.tabs([
        "🚀  Açılış ekranı",
        "🌐  Dil",
        "🤖  Yapay zeka",
        "👥  Kullanıcı yönetimi",
        "📥  Toplu yükleme",
    ])

    with tab_startup:
        _render_tab_startup(current_user)

    with tab_lang:
        _render_tab_language(current_user)

    with tab_ai:
        _render_tab_ai(current_user)

    with tab_users:
        users_view.render(current_user)

    with tab_import:
        toplu_yukleme_view.render(current_user)

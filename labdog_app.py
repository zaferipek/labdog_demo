"""
LabDog — giriş noktası (sidebar arama + dialog sonuçları güncel).
``app.py`` kilitliyse:  streamlit run labdog_app.py
İsterseniz bu dosyanın içeriğini ``app.py`` ile birleştirin.
"""
from __future__ import annotations

import base64
import os
import traceback

import streamlit as st
import streamlit.components.v1 as components

from auth     import authenticate, create_session, get_session, destroy_session
from database import get_dashboard_stats, get_user_preferences, project_exists
from styles   import base_css, login_css, dashboard_css
import views
from views.search_bar import open_pending_search_dialog, render_sidebar_global_search

st.set_page_config(
    page_title="Lab Dog Ar-Ge Yönetim Sistemi",
    layout="wide",
    initial_sidebar_state="expanded",
)

_DIR  = os.path.dirname(os.path.abspath(__file__))
_LOGO = os.path.join(_DIR, "assets", "labdog_logo.png")

_MAIN_MENU_PAGES: list[str] = [
    "Dashboard",
    "Projeler",
    "Görevler",
    "Hammaddeler",
    "Ar-Ge Talepleri",
    "Raporlar",
]
_SETTINGS_PAGE = "Ayarlar"
_ALL_APP_PAGES = frozenset(_MAIN_MENU_PAGES + [_SETTINGS_PAGE])

_NAV_ICONS = ["⊞", "⬡", "☑", "⚗", "🧪", "📈"]
_NAV_EXPANDED  = [f"{i}  {n}" for i, n in zip(_NAV_ICONS, _MAIN_MENU_PAGES)]
_NAV_COLLAPSED = _NAV_ICONS

_PLACEHOLDER_META: dict[str, tuple[str, str]] = {
    "Görevler":    ("☑", "Aktif görevlerinizi ve atamalarınızı buradan takip edin."),
    "Hammaddeler": ("⚗", "Hammadde stoklarını ve onay durumlarını yönetin."),
    "Ar-Ge Talepleri": (
        "🧪",
        "Ar-Ge talep ve iş paketi takibi yakında bu sayfada olacak.",
    ),
    "Raporlar": ("📈", "Özet raporlar ve dışa aktarım yakında burada olacak."),
}


@st.cache_resource
def _logo_bytes() -> bytes:
    with open(_LOGO, "rb") as fh:
        return fh.read()


def _login_logo_html(width: int = 200) -> str:
    b64 = base64.standard_b64encode(_logo_bytes()).decode("ascii")
    return (
        '<div class="ld-login-logo-wrap">'
        f'<img src="data:image/png;base64,{b64}" width="{width}" '
        'style="display:block;border-radius:8px;max-width:100%;height:auto;" '
        'alt="Lab Dog" />'
        "</div>"
    )


def _inject_history_manager() -> None:
    components.html(
        """
        <script>
        (function () {
            function appWindow() {
                try {
                    if (window.top && window.top.history && window.top.document) {
                        return window.top;
                    }
                } catch (e) {}
                try {
                    if (window.parent && window.parent.history) {
                        return window.parent;
                    }
                } catch (e2) {}
                return window;
            }
            var w = appWindow();
            if (w._ldHistoryInstalled) return;
            w._ldHistoryInstalled = true;

            function detailFingerprint(sp) {
                return [
                    'p:'  + (sp.get('project_id') || ''),
                    'm:'  + (sp.get('material_id') || ''),
                    't:'  + (sp.get('task_id') || ''),
                    'tab:' + (sp.get('project_tab') || ''),
                    'f:'  + (sp.get('formulation_id') || ''),
                    'pr:' + (sp.get('product_id') || ''),
                    'n:'  + (sp.get('note_id') || ''),
                    'e:'  + (sp.get('experiment_id') || ''),
                ].join('|');
            }

            var qs = new URLSearchParams(w.location.search || '');
            var _lastPage   = qs.get('page');
            var _lastDetail = detailFingerprint(qs);

            function parseNav(url) {
                try {
                    var sp = new URL(String(url), w.location.origin).searchParams;
                    return {
                        page: sp.get('page'),
                        detail: detailFingerprint(sp)
                    };
                } catch (e) {
                    return { page: null, detail: '' };
                }
            }

            function syncLastFromUrl() {
                var n = parseNav(w.location.href);
                if (n.page) {
                    _lastPage = n.page;
                    _lastDetail = n.detail;
                }
            }

            w.addEventListener('popstate', function () {
                if (w.__ldPopBusy) return;
                w.__ldPopBusy = true;
                syncLastFromUrl();
                w.setTimeout(function () {
                    w.location.reload();
                }, 0);
            }, true);

            w.addEventListener('pageshow', function (ev) {
                if (ev.persisted) {
                    w.location.reload();
                }
            });

            var _origPush = w.history.pushState.bind(w.history);
            w.history.pushState = function (state, title, url) {
                _origPush(state, title, url);
                if (url) {
                    var n = parseNav(url);
                    if (n.page) {
                        _lastPage = n.page;
                        _lastDetail = n.detail;
                    }
                }
            };

            var _origReplace = w.history.replaceState.bind(w.history);
            w.history.replaceState = function (state, title, url) {
                if (url) {
                    try {
                        var n = parseNav(url);
                        var newPage = n.page;
                        var newDetail = n.detail;
                        if (newPage) {
                            if (_lastPage === null || _lastPage === undefined) {
                                _lastPage = newPage;
                                _lastDetail = newDetail;
                            } else if (newPage !== _lastPage || newDetail !== _lastDetail) {
                                w.history.pushState(state, title, url);
                                return;
                            }
                        }
                    } catch (_) {}
                }
                _origReplace(state, title, url);
            };
        })();
        </script>
        """,
        height=0,
    )


def _login_screen() -> None:
    st.markdown(f"<style>{base_css()}{login_css()}</style>", unsafe_allow_html=True)
    col_left, col_right = st.columns([42, 58])
    with col_left:
        st.markdown(_login_logo_html(200), unsafe_allow_html=True)
        st.markdown(
            "<p class='ld-tagline'>Projelerinizi yönetin, hammaddelerinizi takip edin.<br>"
            "Deney sonuçlarınızı kaydedin.</p>",
            unsafe_allow_html=True,
        )
    with col_right:
        if st.session_state.get("login_error"):
            st.markdown(
                "<div class='ld-error'>" + st.session_state["login_error"] + "</div>",
                unsafe_allow_html=True,
            )
        with st.form("login_form"):
            st.markdown(
                "<h2 class='ld-form-title'>Hoş Geldiniz</h2>"
                "<p class='ld-form-sub'>Devam etmek için oturum açın.</p>",
                unsafe_allow_html=True,
            )
            username  = st.text_input("Kullanıcı Adı", placeholder="Kullanıcı adınızı girin")
            password  = st.text_input("Şifre", type="password", placeholder="Şifrenizi girin")
            submitted = st.form_submit_button("Giriş Yap", use_container_width=True)
            if submitted:
                user = authenticate(username, password)
                if user:
                    token = create_session(user)
                    st.session_state["user"]          = user
                    st.session_state["session_token"] = token
                    st.session_state["login_error"]   = ""
                    st.query_params["token"] = token
                    st.session_state.pop("ld_startup_applied", None)
                    st.rerun()
                else:
                    st.session_state["login_error"] = "Kullanıcı adı veya şifre hatalı."
                    st.rerun()
        st.markdown(
            "<p class='ld-form-footer'>LabDog &copy; 2026</p>",
            unsafe_allow_html=True,
        )


def _toggle_sidebar() -> None:
    st.session_state["sidebar_collapsed"] = not st.session_state.get(
        "sidebar_collapsed", False
    )


@st.fragment
def _sidebar_fragment() -> None:
    user      = st.session_state["user"]
    collapsed = st.session_state.get("sidebar_collapsed", False)
    if "last_main_nav_index" not in st.session_state:
        st.session_state["last_main_nav_index"] = 0
    nav_index = min(
        st.session_state.get("nav_index", 0),
        len(_MAIN_MENU_PAGES) - 1,
    )
    initials  = "".join(w[0].upper() for w in (user.name or "U K").split()[:2])
    expertise = user.expertise_group or ""

    arrow = "›" if collapsed else "‹"
    st.button(arrow, key="sb_toggle", on_click=_toggle_sidebar,
              help="Menüyü daralt / genişlet")

    if collapsed:
        st.markdown(
            "<div class='ld-sb-top-gap' aria-hidden='true'></div>",
            unsafe_allow_html=True,
        )

    if not collapsed:
        st.image(_logo_bytes(), width=136, use_container_width=False)
        st.markdown(
            "<div class='ld-sl-brand-below'>"
            "<div class='ld-sl-appsub'>Ar-Ge Yönetim Sistemi</div>"
            "</div>",
            unsafe_allow_html=True,
        )

    render_sidebar_global_search(collapsed=collapsed)

    nav_options  = _NAV_COLLAPSED if collapsed else _NAV_EXPANDED
    page_display = st.radio(
        " ",
        nav_options,
        index=nav_index,
        label_visibility="hidden",
        key="sidebar_nav",
    )
    new_index = nav_options.index(page_display)
    if new_index != nav_index:
        st.session_state["nav_index"] = new_index
        st.session_state["last_main_nav_index"] = new_index
        st.query_params["page"] = _MAIN_MENU_PAGES[new_index]
        st.rerun(scope="app")

    if collapsed:
        st.markdown(
            "<div class='ld-sb-collapsed'"
            " style='display:none;height:0;overflow:hidden'></div>",
            unsafe_allow_html=True,
        )

    badge = f"<span class='ld-sl-badge'>{expertise}</span>" if expertise else ""

    def _run_logout() -> None:
        destroy_session(st.session_state.get("session_token", ""))
        st.query_params.clear()
        st.session_state.clear()
        st.rerun(scope="app")

    def _run_open_settings() -> None:
        st.session_state["last_main_nav_index"] = st.session_state.get("nav_index", 0)
        st.query_params["page"] = _SETTINGS_PAGE
        st.rerun(scope="app")

    if collapsed:
        st.markdown(
            f"<div class='ld-sl-profile ld-sl-profile-collapsed-only'>"
            f"<div class='ld-sl-avatar'>{initials}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        c_set, c_out = st.columns(2, gap="small")
        with c_set:
            if st.button("⚙", key="sb_open_settings_c", help="Ayarlar", width="stretch"):
                _run_open_settings()
        with c_out:
            if st.button("⏻", key="logout_btn_c", help="Çıkış yap", width="stretch"):
                _run_logout()
    else:
        c_prof, c_set, c_out = st.columns([4.2, 0.55, 0.55], gap="small")
        with c_prof:
            st.markdown(
                f"<div class='ld-sl-profile ld-sl-profile-row'>"
                f"<div class='ld-sl-avatar'>{initials}</div>"
                f"<div class='ld-sl-profile-text'>"
                f"<div class='ld-sl-uname'>{user.name}</div>"
                f"<div class='ld-sl-urole'>{user.role.value} {badge}</div>"
                f"</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
        with c_set:
            if st.button("⚙", key="sb_open_settings", help="Ayarlar", width="stretch"):
                _run_open_settings()
        with c_out:
            if st.button("⏻", key="logout_btn", help="Çıkış yap", width="stretch"):
                _run_logout()


def _apply_user_startup_preferences(user) -> None:
    prefs = get_user_preferences(user.id)
    startup = prefs.get("startup") or {}
    target = (startup.get("target") or "dashboard").lower().strip()

    def _clear_detail_params() -> None:
        for k in (
            "project_id",
            "project_tab",
            "formulation_id",
            "product_id",
            "note_id",
            "experiment_id",
            "material_id",
            "task_id",
        ):
            if k in st.query_params:
                del st.query_params[k]

    if target == "dashboard":
        st.session_state["nav_index"] = _MAIN_MENU_PAGES.index("Dashboard")
        st.query_params["page"] = "Dashboard"
        sub = startup.get("dash_sub") or "cards"
        if sub not in ("cards", "yonetim", "performans"):
            sub = "cards"
        st.session_state["dash_sub"] = sub
        _clear_detail_params()
        return

    if target == "projeler":
        st.session_state["nav_index"] = _MAIN_MENU_PAGES.index("Projeler")
        st.query_params["page"] = "Projeler"
        _clear_detail_params()
        pid = startup.get("project_id")
        if pid is not None:
            try:
                pid_i = int(pid)
                if project_exists(pid_i):
                    st.query_params["project_id"] = str(pid_i)
            except (TypeError, ValueError):
                pass
        return

    if target == "gorevler":
        st.session_state["nav_index"] = _MAIN_MENU_PAGES.index("Görevler")
        st.query_params["page"] = "Görevler"
        _clear_detail_params()
        return

    if target == "hammaddeler":
        st.session_state["nav_index"] = _MAIN_MENU_PAGES.index("Hammaddeler")
        st.query_params["page"] = "Hammaddeler"
        _clear_detail_params()
        return

    if target in ("ar_ge_talepleri", "arge", "arge_talepleri"):
        st.session_state["nav_index"] = _MAIN_MENU_PAGES.index("Ar-Ge Talepleri")
        st.query_params["page"] = "Ar-Ge Talepleri"
        _clear_detail_params()
        return

    if target in ("raporlar", "reports"):
        st.session_state["nav_index"] = _MAIN_MENU_PAGES.index("Raporlar")
        st.query_params["page"] = "Raporlar"
        _clear_detail_params()
        return

    if target == "ayarlar":
        if "last_main_nav_index" not in st.session_state:
            st.session_state["last_main_nav_index"] = 0
        st.session_state["nav_index"] = st.session_state["last_main_nav_index"]
        st.query_params["page"] = _SETTINGS_PAGE
        _clear_detail_params()
        return

    st.session_state["nav_index"] = _MAIN_MENU_PAGES.index("Dashboard")
    st.query_params["page"] = "Dashboard"
    st.session_state["dash_sub"] = "cards"
    _clear_detail_params()


def _maybe_bootstrap_startup_page() -> None:
    if st.session_state.get("ld_startup_applied"):
        return
    user = st.session_state.get("user")
    if not user:
        return
    qp = st.query_params.get("page")
    if qp and qp in _ALL_APP_PAGES:
        st.session_state["ld_startup_applied"] = True
        if qp in _MAIN_MENU_PAGES:
            st.session_state["nav_index"] = _MAIN_MENU_PAGES.index(qp)
            st.session_state["last_main_nav_index"] = st.session_state["nav_index"]
        return
    _apply_user_startup_preferences(user)
    st.session_state["ld_startup_applied"] = True


_SEARCH_QP_DETAIL_KEYS = (
    "project_id",
    "project_tab",
    "formulation_id",
    "product_id",
    "note_id",
    "experiment_id",
    "material_id",
    "task_id",
)


def _apply_search_navigation() -> None:
    if not st.session_state.pop("ld_run_search_nav", False):
        return
    spec = st.session_state.pop("ld_search_nav_spec", None)
    if not spec:
        return
    page = spec.get("page", "Dashboard")
    if page not in _MAIN_MENU_PAGES:
        return

    for k in _SEARCH_QP_DETAIL_KEYS:
        if k in st.query_params:
            del st.query_params[k]

    st.session_state["nav_index"] = _MAIN_MENU_PAGES.index(page)
    st.session_state["last_main_nav_index"] = st.session_state["nav_index"]
    st.query_params["page"] = page

    if page == "Projeler" and spec.get("project_id"):
        pid = str(spec["project_id"]).strip()
        st.query_params["project_id"] = pid
        ptab = (spec.get("project_tab") or "ozet").strip().lower()
        valid_tabs = ("ozet", "form", "deney", "gorev", "notlar")
        if ptab in valid_tabs:
            st.query_params["project_tab"] = ptab
        for opt in ("formulation_id", "product_id", "note_id", "experiment_id"):
            v = spec.get(opt)
            if v is not None and str(v).strip() != "":
                st.query_params[opt] = str(v).strip()
        try:
            pid_int = int(pid)
        except ValueError:
            pid_int = None
        if pid_int is not None:
            nav: dict = {
                "project_id": pid_int,
                "project_tab": ptab if ptab in valid_tabs else "ozet",
            }
            for opt in ("formulation_id", "product_id", "note_id", "experiment_id"):
                v = spec.get(opt)
                if v is None or str(v).strip() == "":
                    continue
                try:
                    nav[opt] = int(str(v).strip())
                except ValueError:
                    nav[opt] = str(v).strip()
            st.session_state["ld_pj_nav_focus"] = nav

    elif page == "Görevler":
        tid = spec.get("task_id")
        if tid is not None and str(tid).strip() != "":
            ts = str(tid).strip()
            st.query_params["task_id"] = ts
            try:
                st.session_state["ld_gorev_nav_focus"] = {"task_id": int(ts)}
            except ValueError:
                st.session_state["ld_gorev_nav_focus"] = {"task_id": ts}

    elif page == "Hammaddeler" and spec.get("material_id"):
        st.query_params["material_id"] = str(spec["material_id"]).strip()

    st.session_state.pop("ld_focus_material_id", None)


def _sync_page_from_url() -> None:
    if "last_main_nav_index" not in st.session_state:
        st.session_state["last_main_nav_index"] = 0

    url_page = st.query_params.get("page", "Dashboard")

    if url_page in _MAIN_MENU_PAGES:
        st.session_state["nav_index"] = _MAIN_MENU_PAGES.index(url_page)
        st.session_state["last_main_nav_index"] = st.session_state["nav_index"]
    elif url_page == _SETTINGS_PAGE:
        st.session_state["nav_index"] = min(
            max(0, int(st.session_state["last_main_nav_index"])),
            len(_MAIN_MENU_PAGES) - 1,
        )
    else:
        st.session_state["nav_index"] = max(
            0,
            min(
                st.session_state.get("nav_index", 0),
                len(_MAIN_MENU_PAGES) - 1,
            ),
        )
        st.session_state["last_main_nav_index"] = st.session_state["nav_index"]
        st.query_params["page"] = _MAIN_MENU_PAGES[st.session_state["nav_index"]]

    cur = st.query_params.get("page", "")
    if cur in _MAIN_MENU_PAGES:
        want = _MAIN_MENU_PAGES[st.session_state["nav_index"]]
        if cur != want:
            st.query_params["page"] = want


def _dashboard_screen() -> None:
    """
    URL sırası: arama gezintisi → (bir kez) açılış tercihi → ``_sync_page_from_url``.
    """
    st.markdown(f"<style>{base_css()}{dashboard_css()}</style>", unsafe_allow_html=True)
    _inject_history_manager()
    _apply_search_navigation()
    _maybe_bootstrap_startup_page()
    _sync_page_from_url()

    with st.sidebar:
        _sidebar_fragment()
    open_pending_search_dialog()

    _main_content_fragment()


@st.fragment
def _main_content_fragment() -> None:
    """Yalnızca sağ ana alan — çoğu etkileşimde sol sidebar yeniden çizilmez."""
    user  = st.session_state["user"]
    stats = get_dashboard_stats()
    page = st.query_params.get("page", "Dashboard")
    if page not in _ALL_APP_PAGES:
        page = "Dashboard"
    if page != "Projeler":
        for k in (
            "project_id",
            "project_tab",
            "formulation_id",
            "product_id",
            "note_id",
            "experiment_id",
        ):
            if k in st.query_params:
                del st.query_params[k]
    if page != "Görevler" and "task_id" in st.query_params:
        del st.query_params["task_id"]
    if page != "Hammaddeler" and "material_id" in st.query_params:
        del st.query_params["material_id"]

    try:
        if page == "Dashboard":
            views.dashboard(stats)
        elif page == "Projeler":
            pid = st.query_params.get("project_id")
            views.projeler(int(pid) if pid else None)
        elif page == "Görevler":
            views.gorevler(user)
        elif page == "Hammaddeler":
            mid_raw = st.query_params.get("material_id")
            mid_parsed: int | None = None
            if mid_raw is not None and str(mid_raw).strip() != "":
                try:
                    mid_parsed = int(str(mid_raw).strip())
                except ValueError:
                    mid_parsed = None
            views.hammaddeler(user, material_id=mid_parsed)
        elif page == _SETTINGS_PAGE:
            views.ayarlar(user)
        else:
            icon, subtitle = _PLACEHOLDER_META.get(page, ("📄", ""))
            views.placeholder(icon, page, subtitle)
    except Exception:
        st.error("⚠️ Sayfa yüklenirken bir hata oluştu. Lütfen sayfayı yenileyin.")
        with st.expander("Hata detayı (geliştirici için)"):
            st.code(traceback.format_exc(), language="python")


def main() -> None:
    if "user" not in st.session_state:
        token = st.query_params.get("token", "")
        if token:
            user = get_session(token)
            if user:
                st.session_state["user"]          = user
                st.session_state["session_token"] = token
    if "user" not in st.session_state:
        _login_screen()
    else:
        _dashboard_screen()


if __name__ == "__main__":
    main()

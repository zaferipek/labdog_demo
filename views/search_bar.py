"""Global arama — sidebar kompakt kutu + sonuçlar ``st.dialog`` içinde."""
from __future__ import annotations

from collections import defaultdict

import streamlit as st

from database import global_search as _global_search_like

try:
    from search_fts import global_search as global_search
except Exception:
    global_search = _global_search_like

_TYPE_TR: dict[str, str] = {
    "project":      "Projeler",
    "task":         "Görevler",
    "material":     "Hammaddeler",
    "formulation":  "Formülasyonlar",
    "product":      "Ürünler",
    "note":         "Proje notları",
    "experiment":   "Deneyler",
}

_TYPE_ORDER = [
    "project", "task", "material", "formulation", "product", "note", "experiment",
]


def render_sidebar_global_search(*, collapsed: bool) -> None:
    """
    Sidebar içinde, logo / alt başlık altında — menü (Dashboard…) üstünde.
    Daraltılmış sidebar'da gösterilmez.
    """
    if collapsed:
        return

    st.markdown("<div class='ld-sb-search-wrap'>", unsafe_allow_html=True)

    with st.form("ld_gs_sb_form", clear_on_submit=False):
        c_in, c_btn = st.columns([1, 0.22])
        with c_in:
            st.text_input(
                "Ara",
                key="ld_gs_q",
                label_visibility="collapsed",
                placeholder="Ara…",
            )
        with c_btn:
            # Material search ikonu — CSS ile span'leri gizlemek ikonu da siliyordu; native icon kullan.
            # Eski Streamlit'te ``icon`` yoksa TypeError → boşluk etiketi + stiller.
            _btn_kw = dict(
                key="ld_gs_submit",
                width="stretch",
                help="Ara (Enter)",
            )
            try:
                submitted = st.form_submit_button(
                    "\u200b",  # zero-width: yalnızca ikon görünsün
                    type="secondary",
                    icon=":material/search:",
                    **_btn_kw,
                )
            except TypeError:
                submitted = st.form_submit_button("⌕", **_btn_kw)

    if submitted:
        q = (st.session_state.get("ld_gs_q") or "").strip()
        if len(q) < 2:
            st.session_state["ld_gs_sb_warn"] = "En az 2 karakter girin."
            st.rerun(scope="app")
        st.session_state.pop("ld_gs_sb_warn", None)
        st.session_state["ld_gs_pending_dialog"] = q
        st.rerun(scope="app")

    if st.session_state.pop("ld_gs_sb_warn", None):
        st.caption("⚠ En az 2 karakter girin.")

    st.markdown("</div>", unsafe_allow_html=True)


@st.dialog("Arama sonuçları", width="large", on_dismiss="rerun")
def _search_results_dialog(query: str) -> None:
    st.markdown(f"**Sorgu:** `{query}`")
    hits = global_search(query)
    if not hits:
        st.info("Bu sorgu için kayıt bulunamadı.")
        return

    st.caption(f"{len(hits)} sonuç")
    nonce = st.session_state.get("ld_gs_nonce", 0)
    by_type: dict[str, list] = defaultdict(list)
    for h in hits:
        by_type[h["type"]].append(h)

    for typ in [t for t in _TYPE_ORDER if t in by_type]:
        items = by_type[typ]
        st.markdown(f"### {_TYPE_TR.get(typ, typ)} ({len(items)})")
        for i, h in enumerate(items):
            code = h.get("code") or "—"
            title = h.get("title") or ""
            snip = (h.get("snippet") or "").replace("\n", " ")
            label = f"{code} · {title}"
            if snip:
                tail = snip[:100] + ("…" if len(snip) > 100 else "")
                label = f"{label} — {tail}"
            if st.button(
                label,
                key=f"ld_gs_dlg_{nonce}_{typ}_{i}",
                width="stretch",
            ):
                st.session_state["ld_search_nav_spec"] = dict(h["url"])
                st.session_state["ld_run_search_nav"] = True
                st.rerun()


def open_pending_search_dialog() -> None:
    """Ana içerikte çağrılır; bekleyen arama varsa dialog açar."""
    q = st.session_state.pop("ld_gs_pending_dialog", None)
    if q is None:
        return
    q = str(q).strip()
    if len(q) < 2:
        return
    st.session_state["ld_gs_nonce"] = st.session_state.get("ld_gs_nonce", 0) + 1
    _search_results_dialog(q)

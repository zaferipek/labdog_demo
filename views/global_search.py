"""Eski üst çubuk arama (inline).

Canlı uygulama ``app.py`` artık ``views.search_bar`` (sidebar + dialog,
``search_fts`` ile FTS5, yoksa LIKE) kullanır. Bu modül yalnızca geriye
dönük referans içindir.
"""
from __future__ import annotations

from collections import defaultdict

import streamlit as st

from ld_rerun import ld_rerun

from database import global_search

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

_CSS = """
<style>
.ld-gs-bar {
  background:#fff;border:1px solid #E9EDF2;border-radius:var(--radius-panel);
  padding:12px 16px;margin-bottom:18px;box-shadow:0 1px 4px rgba(15,23,42,.05);
}
.ld-gs-title{font-size:12px;font-weight:600;color:var(--text-meta);
  text-transform:uppercase;letter-spacing:.04em;margin:0 0 8px 0;}
.ld-gs-hit{font-size:13px;text-align:left;}
</style>
"""


def render_global_search_bar() -> None:
    """Ana blok üstü: form + (isteğe bağlı) sonuç listesi."""
    st.markdown(_CSS, unsafe_allow_html=True)

    st.markdown("<div class='ld-gs-bar'>", unsafe_allow_html=True)
    st.markdown("<p class='ld-gs-title'>Global arama</p>", unsafe_allow_html=True)

    with st.form("ld_gs_form", clear_on_submit=False):
        c1, c2, c3 = st.columns([5, 1, 1])
        with c1:
            st.text_input(
                "Arama sorgusu",
                key="ld_gs_q",
                label_visibility="collapsed",
                placeholder="Proje, görev, hammadde, formülasyon, not, deney… (en az 2 karakter)",
            )
        with c2:
            go = st.form_submit_button("Ara", width="stretch")
        with c3:
            clear = st.form_submit_button("Temizle", width="stretch")

    if clear:
        st.session_state["ld_gs_q"] = ""
        st.session_state.pop("ld_gs_show_results", None)
        st.session_state.pop("ld_gs_results_q", None)
        ld_rerun()

    q = (st.session_state.get("ld_gs_q") or "").strip()

    if go:
        if len(q) < 2:
            st.warning("En az **2 karakter** girin.")
            st.session_state.pop("ld_gs_show_results", None)
            st.session_state.pop("ld_gs_results_q", None)
        else:
            st.session_state["ld_gs_show_results"] = True
            st.session_state["ld_gs_results_q"] = q
            st.session_state["ld_gs_nonce"] = st.session_state.get("ld_gs_nonce", 0) + 1

    show = st.session_state.get("ld_gs_show_results") and st.session_state.get("ld_gs_results_q")
    rq = (st.session_state.get("ld_gs_results_q") or "").strip()

    if show and rq and len(rq) >= 2:
        nonce = st.session_state.get("ld_gs_nonce", 0)
        hits = global_search(rq)
        if not hits:
            st.info(f"**{rq!r}** için sonuç bulunamadı.")
        else:
            st.caption(f"{len(hits)} sonuç · sorgu: {rq!r}")
            by_type: dict[str, list] = defaultdict(list)
            for h in hits:
                by_type[h["type"]].append(h)

            for typ in [t for t in _TYPE_ORDER if t in by_type]:
                items = by_type[typ]
                st.markdown(f"**{_TYPE_TR.get(typ, typ)}** ({len(items)})")
                for i, h in enumerate(items):
                    code = h.get("code") or "—"
                    title = h.get("title") or ""
                    snip = (h.get("snippet") or "").replace("\n", " ")
                    label = f"{code} · {title}"
                    if snip:
                        tail = snip[:90] + ("…" if len(snip) > 90 else "")
                        label = f"{label} — {tail}"
                    if st.button(
                        label,
                        key=f"ld_gs_pick_{nonce}_{typ}_{i}",
                        width="stretch",
                    ):
                        st.session_state["ld_search_nav_spec"] = dict(h["url"])
                        st.session_state["ld_run_search_nav"] = True
                        st.session_state.pop("ld_gs_show_results", None)
                        st.session_state.pop("ld_gs_results_q", None)
                        ld_rerun()
                st.markdown("")

    st.markdown("</div>", unsafe_allow_html=True)

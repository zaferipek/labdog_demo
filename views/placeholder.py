"""Generic placeholder page for modules not yet implemented."""
from __future__ import annotations

import streamlit as st


def render(icon: str, title: str, subtitle: str) -> None:
    st.markdown(
        f"<div class='ld-page-header'>"
        f"<h1 class='ld-page-title'>{title}</h1>"
        f"<p class='ld-page-sub'>{subtitle}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='ld-placeholder'>"
        f"<div class='ld-placeholder-icon'>{icon}</div>"
        f"<p class='ld-placeholder-text'>{title} Modülü</p>"
        f"<p class='ld-placeholder-sub'>Bu modül yakında kullanıma açılacak.</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

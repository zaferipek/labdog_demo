"""Streamlit yenileme: ana içerik ``@st.fragment`` içindeyken yalnızca sağ sütunu yeniler."""
from __future__ import annotations

import streamlit as st
from streamlit.errors import StreamlitAPIException


def ld_rerun() -> None:
    """
    Dashboard'da sayfa gövdesi fragment ile sarılıyken ``scope=\"fragment\"`` kullanır;
    aksi halde (giriş, dialog sonrası tam akış vb.) tam uygulama yenilenir.
    """
    try:
        st.rerun(scope="fragment")
    except StreamlitAPIException:
        st.rerun()

"""
app.py'ye sidebar arama + dialog entegrasyonu (opsiyonel).

Önerilen: ``streamlit run labdog_app.py`` veya ``labdog_app.py`` içeriğini ``app.py`` ile birleştirin.

Bu script yalnızca ``app.py`` açık/kilitli değilken çalıştırılmalıdır.
"""
from pathlib import Path

APP = Path(__file__).resolve().parent / "app.py"
text = APP.read_text(encoding="utf-8")
old_import = "from views.global_search import render_global_search_bar"
new_import = "from views.search_bar import open_pending_search_dialog, render_sidebar_global_search"
if old_import in text:
    text = text.replace(old_import, new_import, 1)

needle = (
    '        "</div>",\n'
    "        unsafe_allow_html=True,\n"
    "    )\n\n"
    "    nav_options  = _NAV_COLLAPSED if collapsed else _NAV_EXPANDED"
)
insert = (
    '        "</div>",\n'
    "        unsafe_allow_html=True,\n"
    "    )\n\n"
    "    render_sidebar_global_search(collapsed=collapsed)\n\n"
    "    nav_options  = _NAV_COLLAPSED if collapsed else _NAV_EXPANDED"
)
if needle in text:
    text = text.replace(needle, insert, 1)

needle2 = (
    "    with st.sidebar:\n"
    "        _sidebar_fragment()\n\n"
    "    # ── PAGE ROUTING ──────────────────────────────────────────"
)
repl2 = (
    "    with st.sidebar:\n"
    "        _sidebar_fragment()\n\n"
    "    open_pending_search_dialog()\n\n"
    "    # ── PAGE ROUTING ──────────────────────────────────────────"
)
if needle2 in text:
    text = text.replace(needle2, repl2, 1)

needle3 = (
    "    if page != \"Projeler\" and \"project_id\" in st.query_params:\n"
    "        del st.query_params[\"project_id\"]\n\n"
    "    render_global_search_bar()\n\n"
    "    try:"
)
repl3 = (
    "    if page != \"Projeler\" and \"project_id\" in st.query_params:\n"
    "        del st.query_params[\"project_id\"]\n\n"
    "    try:"
)
if needle3 in text:
    text = text.replace(needle3, repl3, 1)

APP.write_text(text, encoding="utf-8")
print("Patched app.py OK.")

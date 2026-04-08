"""Projeler sayfası — Salesforce Lightning stili liste ve detay görünümü."""
from __future__ import annotations

import json
from datetime import date as dt_date

import streamlit as st

from ld_rerun import ld_rerun

from database import (
    ExpertiseArea,
    FormulationStatus,
    IngredientRole,
    NoteType,
    ProductStatus,
    ProjectPriority,
    ProjectStatus,
    TaskPriority,
    TaskStatus,
    add_formulation,
    add_ingredient,
    add_product,
    add_project,
    add_project_note,
    add_task,
    calculate_nco_index,
    calculate_weight_fractions,
    delete_formulation,
    delete_product,
    delete_project,
    display_project_status,
    get_all_formulations,
    get_all_products,
    get_all_projects,
    get_all_tasks,
    get_all_users,
    get_formulation_ingredients,
    get_project_by_id,
    get_project_notes,
    remove_ingredient,
    update_formulation,
    update_formulation_status,
    update_product_status,
    update_project,
    update_project_status,
    update_task_status,
)
from styles import page_header_with_action, render_field_label

# ── Colour palettes ──────────────────────────────────────────

_STATUS_COLORS: dict[str, str] = {
    ProjectStatus.FIKIR.value: "#6B7280",
    ProjectStatus.LITERATURE.value: "#7C3AED",
    ProjectStatus.HAMMADDE_TEDARIGI.value: "#0369A1",
    ProjectStatus.LAB_TEST.value: "#0176D3",
    ProjectStatus.PILOT.value: "#E06C00",
    ProjectStatus.VALIDASYON.value: "#B45309",
    ProjectStatus.DONE.value: "#0A8044",
}

_PRIORITY_COLORS: dict[str, str] = {
    "Düşük": "#6B7280",
    "Orta":  "#0176D3",
    "Yüksek": "#E06C00",
    "Acil":  "#C23030",
}

_AREA_COLORS: dict[str, str] = {
    "Boya/Finish": "#E06C00",
    "Hot Melt":    "#7B2D8B",
    "Mürekkep":    "#0A7F7F",
    "PUD":         "#1A56DB",
    "PU":          "#0A8044",
}

_NOTE_COLORS: dict[str, str] = {
    "Durum Raporu": "#0176D3",
    "Karar":        "#0A8044",
    "Not":          "#6B7280",
    "Sorun":        "#C23030",
}

_STATUSES = [s.value for s in ProjectStatus]
_PRIORITIES = [p.value for p in ProjectPriority]
_AREAS = [a.value for a in ExpertiseArea]
_NOTE_TYPES = [n.value for n in NoteType]

# ── CSS ───────────────────────────────────────────────────────

_CSS = """
<style>
/* ── Stage path (tasarım token’ları — styles.base_css :root) ───────── */
.pj-path{display:flex;align-items:center;flex-wrap:wrap;gap:6px 0;
  background:#fff;border-radius:var(--radius-panel);
  padding:14px 18px;border:1px solid var(--border-light);
  box-shadow:0 1px 4px rgba(15,23,42,.06);margin-bottom:20px;}
.pj-path-step{padding:6px 14px;border-radius:var(--radius-badge);font-size:12px;font-weight:600;
  line-height:1.25;background:var(--border-light);color:var(--text-meta);
  border:1px solid var(--border);white-space:nowrap;}
.pj-path-step.completed{background:#D1FAE5;color:#065F46;border-color:#A7F3D0;}
.pj-path-step.active{background:var(--sf-blue);color:#fff;border-color:var(--sf-blue);
  box-shadow:0 2px 8px var(--sf-focus);}
.pj-path-conn{flex:1;height:2px;background:var(--border-light);min-width:8px;max-width:32px;}
.pj-path-conn.done{background:#10B981;}

/* ── Highlights panel ──────────────────────────────────── */
.pj-highlights{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));
  gap:14px;background:#fff;border-radius:10px;padding:20px 24px;
  border:1px solid #E9EDF2;box-shadow:0 1px 4px rgba(15,23,42,.05);margin-bottom:20px;}
.pj-hl-item{}
.pj-hl-label{font-size:10px;font-weight:600;color:#6B7280;text-transform:uppercase;
  letter-spacing:.06em;margin:0 0 4px 0;}
.pj-hl-value{font-size:14px;font-weight:600;color:#0F172A;margin:0;}

/* ── Badges ────────────────────────────────────────────── */
.pj-badge{display:inline-block;padding:2px 10px;border-radius:12px;font-size:11px;
  font-weight:600;white-space:nowrap;}

/* ── Table ─────────────────────────────────────────────── */
.pj-th{font-size:11px;font-weight:600;color:var(--text-meta);text-transform:uppercase;
  letter-spacing:.05em;padding:6px 0;margin:0;}
.pj-code{font-size:11px;color:#9CA3AF;font-weight:500;font-family:monospace;}
.pj-name{font-weight:600;color:var(--navy-sidebar);font-size:13px;line-height:1.3;}
.pj-date{font-size:12px;color:var(--text-meta);}

/* ── Timeline ──────────────────────────────────────────── */
.pj-tl-item{display:flex;gap:14px;padding:14px 0;border-bottom:1px solid #F1F3F6;}
.pj-tl-item:last-child{border-bottom:none;}
.pj-tl-avatar{width:32px;height:32px;border-radius:50%;
  background:linear-gradient(135deg,#1669D8,#032D60);display:flex;
  align-items:center;justify-content:center;font-size:11px;font-weight:700;
  color:#fff;flex-shrink:0;}
.pj-tl-content{flex:1;min-width:0;}
.pj-tl-header{display:flex;align-items:center;gap:8px;margin-bottom:4px;flex-wrap:wrap;}
.pj-tl-author{font-size:13px;font-weight:600;color:#0F172A;}
.pj-tl-date{font-size:11px;color:#9CA3AF;}
.pj-tl-text{font-size:13px;color:#374151;line-height:1.6;margin:0;}

/* ── New project form panel ────────────────────────────── */
.pj-form-panel{background:#F8FAFC;border:1.5px solid #E9EDF2;
  border-radius:10px;padding:20px 24px;margin-bottom:20px;}

/* ── Detail section ────────────────────────────────────── */
.pj-section{background:#fff;border-radius:var(--radius-panel);padding:20px 24px;
  border:1px solid #E9EDF2;box-shadow:0 1px 4px rgba(15,23,42,.05);margin-bottom:16px;}
.pj-section-title{font-size:15px;font-weight:700;color:var(--text-heading);margin:0 0 14px 0;}

/* ── Delete confirm ────────────────────────────────────── */
.pj-del-panel{background:#fff1f0;border:1.5px solid #C2303044;
  border-radius:var(--radius-panel);padding:16px 20px;margin:10px 0;}
[class*="st-key-pj_del_confirm"] button{
  background:#C23030 !important;color:#fff !important;border:none !important;}
[class*="st-key-pj_del_confirm"] button:hover{background:#9b1c1c !important;}

/* ── Proje adı = link görünümlü buton ───────────────────── */
[class*="st-key-pj_name_"] button{
  background:transparent !important;
  border:none !important;
  box-shadow:none !important;
  color:#0F172A !important;
  font-size:13px !important;
  font-weight:600 !important;
  text-align:left !important;
  justify-content:flex-start !important;
  width:100% !important;
  padding:0 !important;
  min-height:unset !important;
  height:auto !important;
  white-space:nowrap !important;
  overflow:hidden !important;
  text-overflow:ellipsis !important;}
[class*="st-key-pj_name_"] button:hover{
  color:#0176D3 !important;
  text-decoration:underline !important;}

/* ── Filter header buttons ──────────────────────────────── */
[class*="st-key-pj_fhdr_"] button{
  background:transparent !important;border:none !important;
  box-shadow:none !important;color:var(--text-meta) !important;
  font-size:10px !important;font-weight:600 !important;
  text-transform:uppercase !important;letter-spacing:.05em !important;
  padding:4px 2px !important;justify-content:flex-start !important;
  min-height:unset !important;height:auto !important;
  width:100% !important;border-radius:0 !important;}
[class*="st-key-pj_fhdr_"] button:hover{
  color:#0176D3 !important;background:transparent !important;}

/* ── Filter panel ───────────────────────────────────────── */
.ld-filter-panel{background:#fff;border:1px solid #E9EDF2;
  border-radius:var(--radius-panel);padding:14px 18px;
  margin:0 0 10px 0;box-shadow:0 4px 16px rgba(15,23,42,.08);}

/* ── Filter chip buttons ────────────────────────────────── */
[class*="st-key-pj_chip_"]:not([class*="st-key-pj_chip_clear"]) button{
  background:#EFF6FF !important;color:#0176D3 !important;
  border:1px solid #BFDBFE !important;border-radius:999px !important;
  padding:2px 12px !important;font-size:11px !important;
  font-weight:600 !important;min-height:26px !important;
  height:26px !important;white-space:nowrap !important;}
[class*="st-key-pj_chip_"]:not([class*="st-key-pj_chip_clear"]) button:hover{
  background:#DBEAFE !important;border-color:#0176D3 !important;}
[class*="st-key-pj_chip_clear"] button{
  background:transparent !important;color:var(--error) !important;
  border:1px solid #C2303044 !important;border-radius:999px !important;
  padding:2px 12px !important;font-size:11px !important;
  font-weight:600 !important;min-height:26px !important;height:26px !important;}
[class*="st-key-pj_chip_clear"] button:hover{
  background:#FFF1F0 !important;border-color:var(--error) !important;}

/* Proje detay — yatay sekme (st.radio) */
[class*="st-key-pj_tab_rad_"] div[data-baseweb="radio"]{
  display:flex !important;flex-direction:row !important;flex-wrap:wrap !important;
  gap:8px !important;align-items:center !important;}
[class*="st-key-pj_tab_rad_"] div[data-baseweb="radio"] label{
  margin:0 !important;padding:8px 14px !important;font-size:12.5px !important;}
</style>
"""


# ── HTML helpers ──────────────────────────────────────────────

def _badge(label: str, color: str) -> str:
    return (
        f"<span class='pj-badge' style='background:{color}18;color:{color};"
        f"border:1px solid {color}33;'>{label}</span>"
    )


def _stage_path_html(current_status: str) -> str:
    stages = _STATUSES
    cur = display_project_status(current_status)
    cur_idx = stages.index(cur) if cur in stages else 0
    parts: list[str] = []
    for i, s in enumerate(stages):
        if i > 0:
            cls = "done" if i <= cur_idx else ""
            parts.append(f"<div class='pj-path-conn {cls}'></div>")
        if i < cur_idx:
            parts.append(f"<div class='pj-path-step completed'>✓ {s}</div>")
        elif i == cur_idx:
            parts.append(f"<div class='pj-path-step active'>{s}</div>")
        else:
            parts.append(f"<div class='pj-path-step'>{s}</div>")
    return f"<div class='pj-path'>{''.join(parts)}</div>"


def _initials(name: str) -> str:
    return "".join(w[0].upper() for w in name.split()[:2]) if name else "?"


# ══════════════════════════════════════════════════════════════
# LIST VIEW — Filter system
# ══════════════════════════════════════════════════════════════

_LIST_COLS = [0.7, 2.6, 1.2, 1.1, 1.5, 0.9, 1.0]

_FILTER_META: dict[str, str] = {
    "name":   "Proje Adı",
    "status": "Durum",
    "area":   "Uzmanlık",
    "resp":   "Sorumlu",
    "prio":   "Öncelik",
    "date":   "Hedef Tarih",
}


def _init_filters() -> None:
    st.session_state.setdefault("pj_fil_name",          "")
    st.session_state.setdefault("pj_fil_status",        [])
    st.session_state.setdefault("pj_fil_area",          [])
    st.session_state.setdefault("pj_fil_resp",          [])
    st.session_state.setdefault("pj_fil_prio",          [])
    st.session_state.setdefault("pj_fil_date_mode",     "")
    st.session_state.setdefault("pj_active_filter_col", None)


def _has_active_filter(key: str) -> bool:
    if key == "name":   return bool(st.session_state.get("pj_fil_name",      "").strip())
    if key == "status": return bool(st.session_state.get("pj_fil_status",    []))
    if key == "area":   return bool(st.session_state.get("pj_fil_area",      []))
    if key == "resp":   return bool(st.session_state.get("pj_fil_resp",      []))
    if key == "prio":   return bool(st.session_state.get("pj_fil_prio",      []))
    if key == "date":   return bool(st.session_state.get("pj_fil_date_mode", ""))
    return False


def _has_any_filter() -> bool:
    return any(_has_active_filter(k) for k in _FILTER_META)


def _clear_filter(key: str) -> None:
    if key == "name":   st.session_state["pj_fil_name"]      = ""
    if key == "status": st.session_state["pj_fil_status"]    = []
    if key == "area":   st.session_state["pj_fil_area"]      = []
    if key == "resp":   st.session_state["pj_fil_resp"]      = []
    if key == "prio":   st.session_state["pj_fil_prio"]      = []
    if key == "date":   st.session_state["pj_fil_date_mode"] = ""


def _clear_all_filters() -> None:
    for k in _FILTER_META:
        _clear_filter(k)
    st.session_state["pj_active_filter_col"] = None


def _apply_filters(projects: list) -> list:
    name_q    = st.session_state.get("pj_fil_name",      "").strip().lower()
    statuses  = st.session_state.get("pj_fil_status",    [])
    areas     = st.session_state.get("pj_fil_area",      [])
    resps     = st.session_state.get("pj_fil_resp",      [])
    prios     = st.session_state.get("pj_fil_prio",      [])
    date_mode = st.session_state.get("pj_fil_date_mode", "")
    date_1    = st.session_state.get("pj_fil_date_1")
    date_2    = st.session_state.get("pj_fil_date_2")

    out = projects
    if name_q:
        out = [p for p in out if name_q in p["name"].lower()]
    if statuses:
        out = [
            p for p in out
            if display_project_status(p.get("status")) in statuses
        ]
    if areas:
        out = [p for p in out if p["expertise_area"] in areas]
    if resps:
        out = [p for p in out if p["rd_specialist"] in resps]
    if prios:
        out = [p for p in out if p["priority"] in prios]
    if date_mode and date_1:
        filtered_by_date: list = []
        for p in out:
            raw = p.get("target_date")
            if raw is None:
                continue
            try:
                pd = dt_date.fromisoformat(str(raw).split(" ")[0])
            except Exception:
                continue
            if date_mode == "Önce" and pd < date_1:
                filtered_by_date.append(p)
            elif date_mode == "Sonra" and pd > date_1:
                filtered_by_date.append(p)
            elif date_mode == "Arasında" and date_2 and date_1 <= pd <= date_2:
                filtered_by_date.append(p)
        out = filtered_by_date
    return out


def _render_chips() -> None:
    """Active filter chips + clear-all button."""
    chips: list[tuple[str, str]] = []
    name = st.session_state.get("pj_fil_name", "")
    if name.strip():
        chips.append(("name", f"Ad: {name.strip()[:18]}"))
    if st.session_state.get("pj_fil_status"):
        chips.append(("status", "Durum: " + ", ".join(st.session_state["pj_fil_status"])))
    if st.session_state.get("pj_fil_area"):
        chips.append(("area", "Uzmanlık: " + ", ".join(st.session_state["pj_fil_area"])))
    if st.session_state.get("pj_fil_resp"):
        chips.append(("resp", "Sorumlu: " + ", ".join(st.session_state["pj_fil_resp"])))
    if st.session_state.get("pj_fil_prio"):
        chips.append(("prio", "Öncelik: " + ", ".join(st.session_state["pj_fil_prio"])))
    date_mode = st.session_state.get("pj_fil_date_mode", "")
    date_1    = st.session_state.get("pj_fil_date_1")
    date_2    = st.session_state.get("pj_fil_date_2")
    if date_mode and date_1:
        if date_mode == "Arasında" and date_2:
            chips.append(("date", f"Tarih: {date_1} – {date_2}"))
        else:
            chips.append(("date", f"Tarih: {date_mode} {date_1}"))

    if not chips:
        return

    n = len(chips)
    cols = st.columns([2.0] * n + [1.8, 4.0])
    for i, (key, label) in enumerate(chips):
        with cols[i]:
            if st.button(f"✕  {label}", key=f"pj_chip_{key}"):
                _clear_filter(key)
                ld_rerun()
    with cols[n]:
        if st.button("Filtreleri Temizle", key="pj_chip_clear_all"):
            _clear_all_filters()
            ld_rerun()


def _render_filter_panel(col_key: str, all_projects: list) -> None:
    """Per-column filter input panel."""
    st.markdown("<div class='ld-filter-panel'>", unsafe_allow_html=True)
    if col_key == "name":
        st.text_input(
            "Proje adına göre ara",
            placeholder="Proje adı yazın...",
            key="pj_fil_name",
            label_visibility="collapsed",
        )
    elif col_key == "status":
        st.multiselect(
            "Durum", options=_STATUSES,
            key="pj_fil_status",
            label_visibility="collapsed",
            placeholder="Durum seçin...",
        )
    elif col_key == "area":
        st.multiselect(
            "Uzmanlık", options=_AREAS,
            key="pj_fil_area",
            label_visibility="collapsed",
            placeholder="Uzmanlık alanı seçin...",
        )
    elif col_key == "resp":
        unique_resp = sorted({p["rd_specialist"] for p in all_projects if p.get("rd_specialist")})
        st.multiselect(
            "Sorumlu", options=unique_resp,
            key="pj_fil_resp",
            label_visibility="collapsed",
            placeholder="Sorumlu seçin...",
        )
    elif col_key == "prio":
        st.multiselect(
            "Öncelik", options=_PRIORITIES,
            key="pj_fil_prio",
            label_visibility="collapsed",
            placeholder="Öncelik seçin...",
        )
    elif col_key == "date":
        d1, d2, d3 = st.columns([1.2, 1.5, 1.5])
        with d1:
            st.selectbox(
                "Tarih modu",
                options=["", "Önce", "Sonra", "Arasında"],
                format_func=lambda x: "Tarih Filtresi..." if x == "" else x,
                key="pj_fil_date_mode",
                label_visibility="collapsed",
            )
        date_mode = st.session_state.get("pj_fil_date_mode", "")
        if date_mode:
            with d2:
                st.date_input("Tarih", key="pj_fil_date_1", label_visibility="collapsed")
            if date_mode == "Arasında":
                with d3:
                    st.date_input("Bitiş", key="pj_fil_date_2", label_visibility="collapsed")

    c_btn, _ = st.columns([1.8, 5])
    with c_btn:
        if st.button(f"Bu filtreyi temizle", key=f"pj_fil_clear_{col_key}"):
            _clear_filter(col_key)
            st.session_state["pj_active_filter_col"] = None
            ld_rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def _list_header(all_projects: list) -> None:
    """Clickable column headers with per-column filter toggle."""
    active_col = st.session_state.get("pj_active_filter_col")
    h = st.columns(_LIST_COLS)
    h[0].markdown("<p class='ld-th'>Kod</p>", unsafe_allow_html=True)

    filterable = [
        (1, "Proje Adı",   "name"),
        (2, "Durum",       "status"),
        (3, "Uzmanlık",    "area"),
        (4, "Sorumlu",     "resp"),
        (5, "Öncelik",     "prio"),
        (6, "Hedef Tarih", "date"),
    ]
    for col_idx, label, fkey in filterable:
        has_f   = _has_active_filter(fkey)
        is_open = active_col == fkey
        arrow   = "▲" if is_open else "▼"
        dot     = " ●" if has_f else ""
        if h[col_idx].button(
            f"{label} {arrow}{dot}",
            key=f"pj_fhdr_{fkey}",
            help=f"{label} filtresi {'(aktif)' if has_f else ''}",
        ):
            st.session_state["pj_active_filter_col"] = None if is_open else fkey
            ld_rerun()

    st.markdown(
        "<hr style='margin:0 0 4px 0;border:none;border-top:2px solid #e5e7eb;'>",
        unsafe_allow_html=True,
    )
    if active_col:
        _render_filter_panel(active_col, all_projects)




def _list_row(p: dict) -> None:
    st.markdown("<div class='pj-row-hover'>", unsafe_allow_html=True)
    cols = st.columns(_LIST_COLS)
    cols[0].markdown(f"<span class='pj-code'>{p['code']}</span>", unsafe_allow_html=True)
    if cols[1].button(
        p["name"],
        key=f"pj_name_{p['id']}",
        help=f"Projeyi aç: {p['name']}",
        type="secondary",
    ):
        st.query_params["project_id"] = str(p["id"])
        ld_rerun()
    st_disp = display_project_status(p.get("status"))
    cols[2].markdown(
        _badge(st_disp, _STATUS_COLORS.get(st_disp, "#6B7280")),
        unsafe_allow_html=True,
    )
    cols[3].markdown(
        _badge(p["expertise_area"], _AREA_COLORS.get(p["expertise_area"], "#888")),
        unsafe_allow_html=True,
    )
    cols[4].markdown(
        f"<span style='font-size:13px;color:var(--text-body);'>{p['rd_specialist']}</span>",
        unsafe_allow_html=True,
    )
    cols[5].markdown(
        _badge(p["priority"], _PRIORITY_COLORS.get(p["priority"], "#6B7280")),
        unsafe_allow_html=True,
    )
    target = str(p["target_date"]) if p.get("target_date") else "—"
    cols[6].markdown(f"<span class='pj-date'>{target}</span>", unsafe_allow_html=True)

    st.markdown(
        "<hr style='margin:2px 0;border:none;border-top:1px solid var(--border-light);'>"
        "</div>",
        unsafe_allow_html=True,
    )


@st.dialog("Yeni Proje Oluştur", width="large", on_dismiss="rerun")
def _new_project_dialog() -> None:
    """
    Modal içinde yeni proje formu — liste düzeni bozulmaz.
    Pattern: docs/ux_modal_pattern.md
    """
    users = get_all_users()
    active_names = [u["name"] for u in users if u.get("is_active", True)]

    render_field_label(
        "Uzmanlık alanı",
        required=True,
        hint="Seçime göre özel parametreler görünür.",
        variant="dark",
    )
    sel_area = st.selectbox(
        "Uzmanlık alanı",
        _AREAS,
        key="pj_new_area",
        label_visibility="collapsed",
        help="Uzmanlık alanı seçimine göre özel parametreler görünür.",
    )

    with st.form("pj_add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            render_field_label("Proje adı", required=True, variant="dark")
            f_name = st.text_input(
                "Proje adı",
                placeholder="Ör: Su Bazlı PUD Geliştirme",
                label_visibility="collapsed",
                key="pj_new_name",
            )
            render_field_label("Sorumlu", required=True, variant="dark")
            if active_names:
                f_resp = st.selectbox(
                    "Sorumlu",
                    active_names,
                    label_visibility="collapsed",
                    key="pj_new_resp",
                )
            else:
                f_resp = st.text_input(
                    "Sorumlu",
                    label_visibility="collapsed",
                    key="pj_new_resp_txt",
                )
            render_field_label("Öncelik", variant="dark")
            f_prio = st.selectbox(
                "Öncelik",
                _PRIORITIES,
                index=1,
                label_visibility="collapsed",
                key="pj_new_prio",
            )
        with c2:
            render_field_label("Başlangıç tarihi", required=True, variant="dark")
            f_start = st.date_input(
                "Başlangıç tarihi",
                value=dt_date.today(),
                label_visibility="collapsed",
                key="pj_new_start",
            )
            render_field_label("Hedef tarih", variant="dark")
            f_target = st.date_input(
                "Hedef tarih",
                value=None,
                label_visibility="collapsed",
                key="pj_new_target",
            )
            render_field_label("Müşteri / talep eden", variant="dark")
            f_cust = st.text_input(
                "Müşteri / talep eden",
                placeholder="İsteğe bağlı",
                label_visibility="collapsed",
                key="pj_new_cust",
            )

        render_field_label("Açıklama", variant="dark")
        f_desc = st.text_area(
            "Açıklama",
            placeholder="Projenin amacı ve hedefleri...",
            label_visibility="collapsed",
            key="pj_new_desc",
        )

        extra = {}
        if sel_area in ("PUD", "PU"):
            st.markdown("##### PUD / PU Parametreleri")
            ec1, ec2, ec3 = st.columns(3)
            with ec1:
                render_field_label("NCO hedef indeksi", variant="dark")
                extra["nco_target"] = st.number_input(
                    "NCO hedef indeksi",
                    value=1.05,
                    step=0.01,
                    format="%.2f",
                    label_visibility="collapsed",
                    key="pj_new_nco",
                )
            with ec2:
                render_field_label("Hedef parçacık boyutu (nm)", variant="dark")
                extra["particle_size_nm"] = st.number_input(
                    "Parçacık nm",
                    value=0,
                    step=10,
                    label_visibility="collapsed",
                    key="pj_new_ps_nm",
                )
            with ec3:
                render_field_label("İyonik içerik tipi", variant="dark")
                extra["ionic_type"] = st.selectbox(
                    "İyonik tip",
                    ["Anyonik", "Katyonik", "Non-iyonik"],
                    label_visibility="collapsed",
                    key="pj_new_ionic",
                )
        elif sel_area == "Hot Melt":
            st.markdown("##### Hot Melt Parametreleri")
            ec1, ec2, ec3 = st.columns(3)
            with ec1:
                render_field_label("Hedef yumuşama noktası (°C)", variant="dark")
                extra["softening_point_c"] = st.number_input(
                    "Yumuşama °C",
                    value=0,
                    step=5,
                    label_visibility="collapsed",
                    key="pj_new_sp",
                )
            with ec2:
                render_field_label("Hedef viskozite (cP)", variant="dark")
                extra["viscosity_target"] = st.number_input(
                    "Viskozite cP",
                    value=0,
                    step=100,
                    label_visibility="collapsed",
                    key="pj_new_visc",
                )
            with ec3:
                render_field_label("Açık süre (sn)", variant="dark")
                extra["open_time_sec"] = st.number_input(
                    "Açık süre sn",
                    value=0,
                    step=5,
                    label_visibility="collapsed",
                    key="pj_new_open",
                )
        elif sel_area in ("Boya/Finish", "Mürekkep"):
            st.markdown("##### Boya / Mürekkep Parametreleri")
            ec1, ec2, ec3 = st.columns(3)
            with ec1:
                render_field_label("Hedef parlaklık (GU)", variant="dark")
                extra["gloss_target_gu"] = st.number_input(
                    "Parlaklık GU",
                    value=0,
                    step=5,
                    label_visibility="collapsed",
                    key="pj_new_gloss",
                )
            with ec2:
                render_field_label("Film kalınlığı (µm)", variant="dark")
                extra["film_thickness_um"] = st.number_input(
                    "Film µm",
                    value=0,
                    step=5,
                    label_visibility="collapsed",
                    key="pj_new_film",
                )
            with ec3:
                render_field_label("Çözücü tipi", variant="dark")
                extra["solvent_type"] = st.selectbox(
                    "Çözücü",
                    ["Su Bazlı", "Solvent Bazlı", "UV Kürleme", "Hibrit"],
                    label_visibility="collapsed",
                    key="pj_new_solvent",
                )

        b_save, b_cancel = st.columns(2)
        submitted = b_save.form_submit_button("Projeyi Kaydet", width="stretch")
        cancelled = b_cancel.form_submit_button("İptal", width="stretch")

        if cancelled:
            ld_rerun()

        if submitted:
            if not f_name.strip():
                st.error("Proje adı zorunludur.")
            elif not active_names:
                st.error("Sorumlu seçilecek aktif kullanıcı bulunamadı.")
            else:
                ok, msg = add_project(
                    name=f_name,
                    expertise_area=sel_area,
                    rd_specialist=f_resp,
                    start_date=f_start,
                    target_date=f_target,
                    priority=f_prio,
                    customer=f_cust,
                    description=f_desc,
                    extra_params=json.dumps(extra, ensure_ascii=False) if extra else "",
                )
                if ok:
                    st.success(f"✅ {msg}")
                    ld_rerun()
                else:
                    st.error(f"❌ {msg}")


def _render_list() -> None:
    _init_filters()
    for k in ("project_tab", "formulation_id", "product_id", "note_id", "experiment_id"):
        if k in st.query_params:
            del st.query_params[k]

    if page_header_with_action(
        "Projeler",
        "Tüm Ar-Ge projelerinizi buradan yönetin.",
        "✚ Yeni Proje",
        "pj_open_new_project_dialog",
    ):
        _new_project_dialog()

    all_projects = get_all_projects()
    total        = len(all_projects)

    # Active filter chips
    _render_chips()

    # Apply filters
    projects = _apply_filters(all_projects)
    filtered = len(projects)

    if all_projects:
        _list_header(all_projects)
        if projects:
            for p in projects:
                _list_row(p)
            # Counter
            if filtered < total:
                counter = f"<strong>{filtered}</strong> proje filtrelendi / {total} toplam"
            else:
                counter = f"{total} proje"
            st.markdown(
                f"<p style='font-size:12px;color:var(--text-meta);margin:8px 0 0 0;'>"
                f"{counter}</p>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<div class='ld-placeholder'>"
                "<div class='ld-placeholder-icon'>🔍</div>"
                "<p class='ld-placeholder-text'>Filtre Sonucu Boş</p>"
                "<p class='ld-placeholder-sub'>Aktif filtrelere uyan proje bulunamadı. "
                "Filtreleri değiştirin veya temizleyin.</p>"
                "</div>",
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            "<div class='ld-placeholder'>"
            "<div class='ld-placeholder-icon'>📁</div>"
            "<p class='ld-placeholder-text'>Proje Bulunamadı</p>"
            "<p class='ld-placeholder-sub'>Henüz proje oluşturulmadı.</p>"
            "</div>",
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════
# DETAIL VIEW
# ══════════════════════════════════════════════════════════════

_PJ_TAB_KEYS: tuple[str, ...] = ("ozet", "form", "deney", "gorev", "notlar")


def _pj_tab_labels(project: dict) -> list[str]:
    return [
        "📋 Özet",
        f"🧪 Formülasyonlar ({project['formulation_count']})",
        f"🔬 Deneyler ({project['experiment_count']})",
        f"☑ Görevler ({project['task_count']})",
        f"📝 Durum Raporları ({project['note_count']})",
    ]


def _clear_project_query_params() -> None:
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


def _render_detail(project_id: int) -> None:
    project = get_project_by_id(project_id)
    if not project:
        st.error("Proje bulunamadı.")
        if st.button("← Projelere Dön"):
            _clear_project_query_params()
            ld_rerun()
        return

    # Back button
    if st.button("← Projelere Dön", key="pj_back"):
        _clear_project_query_params()
        ld_rerun()

    # Title
    st.markdown(
        f"<div style='margin-bottom:8px;'>"
        f"<span class='pj-code' style='font-size:12px;'>{project['code']}</span>"
        f"</div>"
        f"<h1 class='ld-page-title' style='margin-bottom:16px !important;'>"
        f"{project['name']}</h1>",
        unsafe_allow_html=True,
    )

    # Stage Path
    st.markdown(_stage_path_html(project["status"]), unsafe_allow_html=True)

    # Status change controls
    status_display = display_project_status(project.get("status"))
    status_idx = _STATUSES.index(status_display) if status_display in _STATUSES else 0
    sc1, sc2, _ = st.columns([2.5, 1.2, 5])
    with sc1:
        new_status = st.selectbox(
            "Durum", _STATUSES,
            index=status_idx,
            key=f"pj_status_sel_{project_id}",
            label_visibility="collapsed",
        )
    with sc2:
        if st.button("Durumu Güncelle", key=f"pj_status_btn_{project_id}"):
            if new_status != status_display:
                ok, msg = update_project_status(project_id, new_status)
                if ok:
                    st.success(f"✅ {msg}")
                    ld_rerun()
                else:
                    st.error(f"❌ {msg}")

    # Highlights Panel
    hl_items = [
        ("Uzmanlık Alanı", _badge(project["expertise_area"], _AREA_COLORS.get(project["expertise_area"], "#888"))),
        ("Sorumlu", f"<span style='font-size:14px;font-weight:600;color:#0F172A;'>{project['rd_specialist']}</span>"),
        ("Öncelik", _badge(project["priority"], _PRIORITY_COLORS.get(project["priority"], "#6B7280"))),
        ("Başlangıç", f"<span style='font-size:14px;color:#0F172A;'>{project['start_date']}</span>"),
        ("Hedef Tarih", f"<span style='font-size:14px;color:#0F172A;'>{project['target_date'] or '—'}</span>"),
        ("Müşteri", f"<span style='font-size:14px;color:#0F172A;'>{project['customer'] or '—'}</span>"),
    ]
    hl_html = "".join(
        f"<div class='pj-hl-item'><p class='pj-hl-label'>{lbl}</p>"
        f"<div class='pj-hl-value'>{val}</div></div>"
        for lbl, val in hl_items
    )
    st.markdown(f"<div class='pj-highlights'>{hl_html}</div>", unsafe_allow_html=True)

    # Sekmeler (URL / arama odağı ile uyumlu — st.radio yatay)
    labels = _pj_tab_labels(project)
    sk = f"pj_tab_rad_{project_id}"

    pending = st.session_state.pop("ld_pj_nav_focus", None)
    if isinstance(pending, dict) and int(pending.get("project_id", -1)) == project_id:
        ptab = (pending.get("project_tab") or "ozet").strip().lower()
        if ptab in _PJ_TAB_KEYS:
            st.session_state[sk] = labels[_PJ_TAB_KEYS.index(ptab)]
        if pending.get("formulation_id") is not None:
            try:
                st.session_state[f"frm_expand_{project_id}"] = int(pending["formulation_id"])
            except (TypeError, ValueError):
                pass
        if pending.get("note_id") is not None:
            try:
                st.session_state[f"pj_note_hi_{project_id}"] = int(pending["note_id"])
            except (TypeError, ValueError):
                pass
        if pending.get("product_id") is not None:
            try:
                st.session_state[f"pj_prod_hi_{project_id}"] = int(pending["product_id"])
            except (TypeError, ValueError):
                pass
        if pending.get("experiment_id") is not None:
            try:
                st.session_state[f"pj_exp_hi_{project_id}"] = int(pending["experiment_id"])
            except (TypeError, ValueError):
                pass

    if sk not in st.session_state:
        ptab = (st.query_params.get("project_tab") or "ozet").strip().lower()
        if ptab in _PJ_TAB_KEYS:
            st.session_state[sk] = labels[_PJ_TAB_KEYS.index(ptab)]
        else:
            st.session_state[sk] = labels[0]

    if st.session_state[sk] not in labels:
        st.session_state[sk] = labels[0]

    try:
        st.radio(
            " ",
            labels,
            key=sk,
            horizontal=True,
            label_visibility="collapsed",
        )
    except TypeError:
        st.radio(" ", labels, key=sk, label_visibility="collapsed")

    sel = st.session_state[sk]
    idx = labels.index(sel)

    if idx == 0:
        _tab_summary(project)
    elif idx == 1:
        _tab_formulations(project_id, project)
    elif idx == 2:
        _tab_placeholder(
            "Deneyler", "🔬",
            "Deney kayıtları ve test sonuçları bu sekmede yer alacak.",
        )
        ehi = st.session_state.pop(f"pj_exp_hi_{project_id}", None)
        if ehi is not None:
            st.caption(f"🔗 Arama hedefi: deney #{ehi}")
    elif idx == 3:
        _tab_gorevler(project_id, project)
    else:
        _tab_notes(project_id, project)


def _tab_summary(project: dict) -> None:
    """Özet tab content: description + extra params + actions."""
    # Description
    st.markdown("<div class='pj-section'>", unsafe_allow_html=True)
    st.markdown("<p class='pj-section-title'>Proje Açıklaması</p>", unsafe_allow_html=True)
    desc = project.get("description") or "Henüz açıklama eklenmemiş."
    st.markdown(
        f"<p style='font-size:14px;color:#374151;line-height:1.7;margin:0;'>{desc}</p>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Extra params
    if project.get("extra_params"):
        try:
            params = json.loads(project["extra_params"])
            if params:
                st.markdown("<div class='pj-section'>", unsafe_allow_html=True)
                st.markdown(
                    "<p class='pj-section-title'>Uzmanlık Alanı Parametreleri</p>",
                    unsafe_allow_html=True,
                )
                _PARAM_LABELS = {
                    "nco_target": "NCO Hedef İndeksi",
                    "particle_size_nm": "Hedef Parçacık Boyutu (nm)",
                    "ionic_type": "İyonik İçerik Tipi",
                    "softening_point_c": "Yumuşama Noktası (°C)",
                    "viscosity_target": "Hedef Viskozite (cP)",
                    "open_time_sec": "Açık Süre (sn)",
                    "gloss_target_gu": "Hedef Parlaklık (GU)",
                    "film_thickness_um": "Film Kalınlığı (µm)",
                    "solvent_type": "Çözücü Tipi",
                }
                grid_html = "<div class='pj-highlights'>"
                for key, val in params.items():
                    label = _PARAM_LABELS.get(key, key)
                    grid_html += (
                        f"<div class='pj-hl-item'>"
                        f"<p class='pj-hl-label'>{label}</p>"
                        f"<p class='pj-hl-value'>{val}</p>"
                        f"</div>"
                    )
                grid_html += "</div>"
                st.markdown(grid_html, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
        except (json.JSONDecodeError, TypeError):
            pass

    # Quick stats
    st.markdown("<div class='pj-section'>", unsafe_allow_html=True)
    st.markdown("<p class='pj-section-title'>Proje Özeti</p>", unsafe_allow_html=True)
    stats_html = (
        f"<div class='pj-highlights'>"
        f"<div class='pj-hl-item'><p class='pj-hl-label'>Formülasyonlar</p>"
        f"<p class='pj-hl-value'>{project['formulation_count']}</p></div>"
        f"<div class='pj-hl-item'><p class='pj-hl-label'>Deneyler</p>"
        f"<p class='pj-hl-value'>{project['experiment_count']}</p></div>"
        f"<div class='pj-hl-item'><p class='pj-hl-label'>Görevler</p>"
        f"<p class='pj-hl-value'>{project['task_count']}</p></div>"
        f"<div class='pj-hl-item'><p class='pj-hl-label'>Ürünler</p>"
        f"<p class='pj-hl-value'>{project['product_count']}</p></div>"
        f"</div>"
    )
    st.markdown(stats_html, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Edit & Delete actions
    st.markdown("---")
    st.session_state.setdefault("pj_show_edit", False)
    st.session_state.setdefault("pj_show_delete", False)

    ac1, ac2, _ = st.columns([1.2, 1.2, 5])
    with ac1:
        edit_lbl = "✕ Düzenlemeyi Kapat" if st.session_state["pj_show_edit"] else "✏️ Projeyi Düzenle"
        if st.button(edit_lbl, key="pj_edit_toggle", width="stretch"):
            st.session_state["pj_show_edit"] = not st.session_state["pj_show_edit"]
            st.session_state["pj_show_delete"] = False
            ld_rerun()
    with ac2:
        del_lbl = "✕ İptal" if st.session_state["pj_show_delete"] else "🗑️ Projeyi Sil"
        if st.button(del_lbl, key="pj_del_toggle", width="stretch"):
            st.session_state["pj_show_delete"] = not st.session_state["pj_show_delete"]
            st.session_state["pj_show_edit"] = False
            ld_rerun()

    if st.session_state["pj_show_edit"]:
        _edit_project_form(project)

    if st.session_state["pj_show_delete"]:
        _delete_project_confirm(project)


def _edit_project_form(project: dict) -> None:
    users = get_all_users()
    active_names = [u["name"] for u in users if u.get("is_active", True)]
    cur_resp_idx = active_names.index(project["rd_specialist"]) if project["rd_specialist"] in active_names else 0
    cur_prio_idx = _PRIORITIES.index(project["priority"]) if project["priority"] in _PRIORITIES else 1

    st.markdown("<div class='pj-form-panel'>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='font-size:14px;font-weight:700;color:#1A56DB;margin:0 0 14px 0;'>"
        f"✏️ Projeyi Düzenle — {project['code']}</p>",
        unsafe_allow_html=True,
    )

    with st.form(f"pj_edit_{project['id']}", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            f_name = st.text_input("Proje Adı", value=project["name"])
            f_resp = st.selectbox("Sorumlu", active_names, index=cur_resp_idx)
            f_prio = st.selectbox("Öncelik", _PRIORITIES, index=cur_prio_idx)
        with c2:
            f_target = st.date_input("Hedef Tarih", value=project["target_date"])
            f_cust = st.text_input("Müşteri", value=project["customer"])
        f_desc = st.text_area("Açıklama", value=project["description"])

        sc, cc, _ = st.columns([1.5, 1, 4])
        submitted = sc.form_submit_button("💾 Güncelle", width="stretch")
        cancelled = cc.form_submit_button("İptal", width="stretch")

        if submitted:
            if not f_name.strip():
                st.error("Proje adı boş bırakılamaz.")
            else:
                ok, msg = update_project(
                    project_id=project["id"],
                    name=f_name, rd_specialist=f_resp,
                    priority=f_prio, customer=f_cust,
                    description=f_desc, target_date=f_target,
                )
                if ok:
                    st.success(f"✅ {msg}")
                    st.session_state["pj_show_edit"] = False
                    ld_rerun()
                else:
                    st.error(f"❌ {msg}")
        if cancelled:
            st.session_state["pj_show_edit"] = False
            ld_rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def _delete_project_confirm(project: dict) -> None:
    st.markdown("<div class='pj-del-panel'>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='font-size:14px;font-weight:600;color:#C23030;margin:0 0 10px 0;'>"
        f"⚠️ Bu işlem geri alınamaz!</p>"
        f"<p style='font-size:13px;color:#374151;margin:0 0 14px 0;'>"
        f"<strong>{project['name']}</strong> ({project['code']}) projesini ve "
        f"tüm ilişkili verileri (deneyler, formülasyonlar, notlar) "
        f"kalıcı olarak silmek istediğinize emin misiniz?</p>",
        unsafe_allow_html=True,
    )
    yc, nc, _ = st.columns([1.4, 1, 5])
    with yc:
        if st.button("🗑️ Evet, Sil", key="pj_del_confirm", width="stretch"):
            ok, msg = delete_project(project["id"])
            if ok:
                st.success(f"✅ {msg}")
                st.session_state["pj_show_delete"] = False
                _clear_project_query_params()
                ld_rerun()
            else:
                st.error(f"❌ {msg}")
    with nc:
        if st.button("İptal", key="pj_del_cancel", width="stretch"):
            st.session_state["pj_show_delete"] = False
            ld_rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def _tab_notes(project_id: int, project: dict) -> None:
    """Durum Raporları tab — timeline with add-note form."""
    note_hi = st.session_state.pop(f"pj_note_hi_{project_id}", None)
    st.session_state.setdefault("pj_show_note_form", False)

    nc1, _ = st.columns([1.4, 5])
    with nc1:
        note_lbl = "✕ Formu Kapat" if st.session_state["pj_show_note_form"] else "✚ Yeni Not Ekle"
        if st.button(note_lbl, key="pj_note_toggle", width="stretch"):
            st.session_state["pj_show_note_form"] = not st.session_state["pj_show_note_form"]
            ld_rerun()

    if st.session_state["pj_show_note_form"]:
        with st.form("pj_add_note", clear_on_submit=True):
            nc1, nc2 = st.columns([2, 1])
            with nc1:
                n_content = st.text_area("Not İçeriği *", placeholder="Durum güncellemesi, karar veya not yazın...")
            with nc2:
                n_type = st.selectbox("Not Tipi", _NOTE_TYPES)
                n_author = st.text_input(
                    "Yazar",
                    value=st.session_state.get("user", type("", (), {"name": ""})()).name
                    if hasattr(st.session_state.get("user"), "name") else "",
                    disabled=True,
                )
            if st.form_submit_button("Notu Kaydet", width="stretch"):
                if not n_content.strip():
                    st.error("Not içeriği boş bırakılamaz.")
                else:
                    author_name = n_author or "Bilinmeyen"
                    ok, msg = add_project_note(project_id, author_name, n_type, n_content)
                    if ok:
                        st.success(f"✅ {msg}")
                        st.session_state["pj_show_note_form"] = False
                        ld_rerun()
                    else:
                        st.error(f"❌ {msg}")

    notes = get_project_notes(project_id)
    if notes:
        st.markdown("<div class='pj-section'>", unsafe_allow_html=True)
        st.markdown("<p class='pj-section-title'>Aktivite Geçmişi</p>", unsafe_allow_html=True)
        for n in notes:
            initials = _initials(n["author"])
            type_color = _NOTE_COLORS.get(n["note_type"], "#6B7280")
            created = str(n["created_at"])[:16] if n["created_at"] else ""
            try:
                hl = note_hi is not None and int(n["id"]) == int(note_hi)
            except (TypeError, ValueError):
                hl = False
            ring = (
                "box-shadow:0 0 0 2px #0176D3;border-radius:10px;padding:10px 8px;"
                "margin-bottom:8px;background:rgba(1,118,211,0.04);"
                if hl
                else ""
            )
            st.markdown(
                f"<div class='pj-tl-item' style='{ring}'>"
                f"<div class='pj-tl-avatar'>{initials}</div>"
                f"<div class='pj-tl-content'>"
                f"<div class='pj-tl-header'>"
                f"<span class='pj-tl-author'>{n['author']}</span>"
                f"{_badge(n['note_type'], type_color)}"
                f"<span class='pj-tl-date'>{created}</span>"
                f"</div>"
                f"<p class='pj-tl-text'>{n['content']}</p>"
                f"</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown(
            "<div class='ld-placeholder' style='padding:40px;'>"
            "<div class='ld-placeholder-icon'>📝</div>"
            "<p class='ld-placeholder-text'>Henüz Not Yok</p>"
            "<p class='ld-placeholder-sub'>Bu projeye ilk durum raporunu ekleyin.</p>"
            "</div>",
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════
# FORMÜLASYONLAR SEKMESİ
# ══════════════════════════════════════════════════════════════

_FRM_STATUSES   = [s.value for s in FormulationStatus]
_ING_ROLES      = [r.value for r in IngredientRole]

_FRM_STATUS_COLORS: dict[str, str] = {
    "Taslak":    "#6B7280",
    "Test":      "#0176D3",
    "Onaylandı": "#0A8044",
    "Arşiv":     "#9CA3AF",
}

_ING_ROLE_COLORS: dict[str, str] = {
    "İzosiyonat":    "#C23030",
    "Poliol":        "#1A56DB",
    "Zincir Uzatıcı": "#E06C00",
    "Katalizör":     "#7B2D8B",
    "Solvent":       "#0A7F7F",
    "Diğer":         "#6B7280",
}

# Column layout: code | name+ver | status | nco_idx | ing_count | expand | edit | del
_FRM_COLS = [0.7, 2.8, 1.1, 1.0, 0.8, 0.6, 0.5, 0.5]
# Ingredient cols: # | material | role | amount | wt% | eq_w | nco% | OH# | del
_ING_COLS = [0.3, 2.2, 1.2, 0.9, 0.7, 0.9, 0.8, 0.8, 0.5]


def _frm_header() -> None:
    h = st.columns(_FRM_COLS)
    for col, lbl in zip(h, ["Kod", "Formülasyon", "Durum", "NCO İndeks", "Bileşen", "", "", ""]):
        col.markdown(f"<p class='pj-th'>{lbl}</p>", unsafe_allow_html=True)
    st.markdown(
        "<hr style='margin:0 0 4px 0;border:none;border-top:2px solid #e5e7eb;'>",
        unsafe_allow_html=True,
    )


def _frm_row(f: dict, project_id: int) -> None:
    expand_id = st.session_state.get(f"frm_expand_{project_id}")
    edit_id   = st.session_state.get(f"frm_edit_{project_id}")
    delete_id = st.session_state.get(f"frm_delete_{project_id}")
    expanded  = expand_id == f["id"]
    editing   = edit_id   == f["id"]
    deleting  = delete_id == f["id"]

    cols = st.columns(_FRM_COLS)
    cols[0].markdown(f"<span class='pj-code'>{f['code']}</span>", unsafe_allow_html=True)
    cols[1].markdown(
        f"<div class='pj-name'>{f['name']}</div>"
        f"<div style='font-size:11px;color:#9CA3AF;'>v{f['version']}</div>",
        unsafe_allow_html=True,
    )
    sc = _FRM_STATUS_COLORS.get(f["status"], "#888")
    cols[2].markdown(_badge(f["status"], sc), unsafe_allow_html=True)

    nco_txt = f"{f['nco_index']:.3f}" if f["nco_index"] is not None else "—"
    cols[3].markdown(
        f"<span style='font-size:13px;font-weight:600;color:#0A1120;'>{nco_txt}</span>",
        unsafe_allow_html=True,
    )
    cols[4].markdown(
        f"<span style='font-size:12px;color:#6B7280;'>{f['ingredient_count']}</span>",
        unsafe_allow_html=True,
    )

    # Expand / collapse ingredients
    if cols[5].button(
        "▲" if expanded else "▼",
        key=f"frm_exp_btn_{f['id']}",
        help="Bileşenleri gizle" if expanded else "Bileşenleri göster",
    ):
        st.session_state[f"frm_expand_{project_id}"] = None if expanded else f["id"]
        st.session_state.pop(f"frm_edit_{project_id}", None)
        st.session_state.pop(f"frm_delete_{project_id}", None)
        ld_rerun()

    if cols[6].button(
        "✕" if editing else "✏️",
        key=f"frm_edit_btn_{f['id']}",
        help="Formu kapat" if editing else "Düzenle",
    ):
        if editing:
            st.session_state.pop(f"frm_edit_{project_id}", None)
        else:
            st.session_state[f"frm_edit_{project_id}"] = f["id"]
            st.session_state[f"frm_expand_{project_id}"] = None
            st.session_state.pop(f"frm_delete_{project_id}", None)
        ld_rerun()

    if cols[7].button(
        "✕" if deleting else "🗑️",
        key=f"frm_del_btn_{f['id']}",
        help="İptal" if deleting else "Sil",
    ):
        if deleting:
            st.session_state.pop(f"frm_delete_{project_id}", None)
        else:
            st.session_state[f"frm_delete_{project_id}"] = f["id"]
            st.session_state.pop(f"frm_edit_{project_id}", None)
            st.session_state[f"frm_expand_{project_id}"] = None
        ld_rerun()

    st.markdown(
        "<hr style='margin:2px 0;border:none;border-top:1px solid #f3f4f6;'>",
        unsafe_allow_html=True,
    )

    # ── Expanded: ingredient table ─────────────────────────────
    if expanded:
        _frm_ingredients_panel(f, project_id)

    # ── Edit form ──────────────────────────────────────────────
    if editing:
        _frm_edit_form(f, project_id)

    # ── Delete confirm ─────────────────────────────────────────
    if deleting:
        _frm_delete_confirm(f, project_id)


def _frm_ingredients_panel(f: dict, project_id: int) -> None:
    """Expanded bileşen tablosu + NCO/OH hesap + yeni bileşen ekleme + ürüne dönüştürme."""
    formulation_id = f["id"]
    ings = get_formulation_ingredients(formulation_id)
    enriched = calculate_weight_fractions(ings)
    nco = calculate_nco_index(ings)

    st.markdown(
        "<div style='background:#F8FAFC;border:1px solid #E9EDF2;border-radius:10px;"
        "padding:16px 20px;margin:4px 0 12px 0;'>",
        unsafe_allow_html=True,
    )

    # NCO index banner
    nco_color = "#0A8044" if nco and 0.9 <= nco <= 1.15 else "#E06C00" if nco else "#6B7280"
    nco_label = f"{nco:.3f}" if nco else "Hesaplanamadı"
    st.markdown(
        f"<div style='display:flex;gap:24px;margin-bottom:12px;'>"
        f"<span style='font-size:13px;color:#6B7280;'>NCO İndeksi: "
        f"<strong style='color:{nco_color};font-size:16px;'>{nco_label}</strong></span>"
        f"<span style='font-size:13px;color:#6B7280;'>Toplam: "
        f"<strong style='color:#0A1120;'>"
        f"{sum(float(i.get('amount_grams',0)) for i in ings):.1f} g</strong></span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    if enriched:
        # Table header
        h = st.columns(_ING_COLS)
        for col, lbl in zip(h, ["#", "Hammadde", "Rol", "Miktar (g)", "Ağırlık%", "EW", "NCO%", "OH#", ""]):
            col.markdown(f"<p class='pj-th'>{lbl}</p>", unsafe_allow_html=True)
        st.markdown(
            "<hr style='margin:0 0 4px 0;border:none;border-top:1px solid #e5e7eb;'>",
            unsafe_allow_html=True,
        )
        del_ing_id = st.session_state.get(f"frm_del_ing_{formulation_id}")
        for i, ing in enumerate(enriched, start=1):
            ic = st.columns(_ING_COLS)
            ic[0].markdown(f"<span style='font-size:12px;color:#9CA3AF;'>{i}</span>", unsafe_allow_html=True)
            ic[1].markdown(
                f"<span style='font-size:12px;font-weight:600;color:#0A1120;'>{ing['material_name']}</span>"
                f"<br><span style='font-size:10px;color:#9CA3AF;font-family:monospace;'>{ing['material_code']}</span>",
                unsafe_allow_html=True,
            )
            rc = _ING_ROLE_COLORS.get(ing["role"], "#888")
            ic[2].markdown(_badge(ing["role"][:8], rc), unsafe_allow_html=True)
            ic[3].markdown(f"<span style='font-size:12px;'>{ing['amount_grams']:.1f}</span>", unsafe_allow_html=True)
            ic[4].markdown(f"<span style='font-size:12px;color:#6B7280;'>{ing['weight_fraction']:.1f}%</span>", unsafe_allow_html=True)
            ic[5].markdown(f"<span style='font-size:11px;color:#6B7280;'>{ing['equivalent_weight'] or '—'}</span>", unsafe_allow_html=True)
            ic[6].markdown(f"<span style='font-size:11px;color:#6B7280;'>{ing['nco_content'] or '—'}</span>", unsafe_allow_html=True)
            ic[7].markdown(f"<span style='font-size:11px;color:#6B7280;'>{ing['oh_number'] or '—'}</span>", unsafe_allow_html=True)
            if ic[8].button("🗑️", key=f"del_ing_{ing['id']}", help="Bileşeni kaldır"):
                ok, msg = remove_ingredient(ing["id"])
                if ok:
                    ld_rerun()
                else:
                    st.error(msg)
            st.markdown(
                "<hr style='margin:1px 0;border:none;border-top:1px solid #f3f4f6;'>",
                unsafe_allow_html=True,
            )
    else:
        st.info("Henüz bileşen eklenmemiş.")

    # ── Add ingredient form ────────────────────────────────────
    key_add = f"frm_add_ing_{formulation_id}"
    st.session_state.setdefault(key_add, False)
    if st.button(
        "✕  Formu Kapat" if st.session_state[key_add] else "✚  Bileşen Ekle",
        key=f"toggle_add_ing_{formulation_id}",
    ):
        st.session_state[key_add] = not st.session_state[key_add]
        ld_rerun()

    if st.session_state[key_add]:
        # Hammadde listesini dinamik al (önbelleksiz basit çekme)
        from database import SessionLocal, RawMaterial  # noqa: PLC0415
        _sess = SessionLocal()
        try:
            _mats = _sess.query(RawMaterial).order_by(RawMaterial.name).all()
            mat_options = {f"{m.name} ({m.code or 'HM-?'})": m for m in _mats}
        finally:
            _sess.close()

        if not mat_options:
            st.warning("Henüz hammadde kaydı yok. Önce Hammaddeler sayfasına gidin.")
        else:
            with st.form(f"add_ing_form_{formulation_id}", clear_on_submit=True):
                c1, c2, c3 = st.columns(3)
                with c1:
                    mat_label = st.selectbox("Hammadde *", list(mat_options.keys()))
                with c2:
                    ing_role  = st.selectbox("Rol *", _ING_ROLES)
                with c3:
                    ing_amt   = st.number_input("Miktar (g) *", min_value=0.01, value=100.0, step=1.0)
                c4, c5, c6 = st.columns(3)
                with c4:
                    ing_ew  = st.number_input("Eş. Ağırlık (opsiyonel)", min_value=0.0, value=0.0, step=0.1)
                with c5:
                    ing_nco = st.number_input("NCO% (opsiyonel)", min_value=0.0, value=0.0, step=0.1)
                with c6:
                    ing_oh  = st.number_input("OH# (opsiyonel)", min_value=0.0, value=0.0, step=0.1)

                if st.form_submit_button("Bileşeni Kaydet", width="stretch"):
                    sel_mat = mat_options[mat_label]
                    ok, msg = add_ingredient(
                        formulation_id=formulation_id,
                        material_id=sel_mat.id,
                        role=ing_role,
                        amount_grams=ing_amt,
                        equivalent_weight=ing_ew if ing_ew > 0 else None,
                        nco_content=ing_nco if ing_nco > 0 else None,
                        oh_number=ing_oh if ing_oh > 0 else None,
                    )
                    if ok:
                        st.success(f"✅ {msg}")
                        st.session_state[key_add] = False
                        ld_rerun()
                    else:
                        st.error(f"❌ {msg}")

    # ── Ürüne Dönüştür (yalnızca Onaylandı formülasyonlar) ────
    if f["status"] == "Onaylandı":
        st.markdown(
            "<hr style='margin:14px 0 10px 0;border:none;border-top:1px solid #E9EDF2;'>",
            unsafe_allow_html=True,
        )
        key_prd = f"frm_to_prd_{formulation_id}"
        st.session_state.setdefault(key_prd, False)
        prd_lbl = "✕  Formu Kapat" if st.session_state[key_prd] else "📦  Ürüne Dönüştür"
        if st.button(prd_lbl, key=f"btn_to_prd_{formulation_id}"):
            st.session_state[key_prd] = not st.session_state[key_prd]
            ld_rerun()

        if st.session_state[key_prd]:
            st.markdown(
                "<div style='background:#f0fff4;border:1.5px solid #0A804433;"
                "border-radius:10px;padding:16px 20px;margin-top:10px;'>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<p style='font-size:13px;font-weight:700;color:#0A8044;margin:0 0 12px 0;'>"
                f"📦  {f['name']} → Yeni Ürün Oluştur</p>",
                unsafe_allow_html=True,
            )
            with st.form(f"prd_create_{formulation_id}", clear_on_submit=True):
                _PROD_STATUSES = [s.value for s in ProductStatus]
                _AREAS_LOCAL   = [a.value for a in ExpertiseArea]
                pc1, pc2 = st.columns(2)
                with pc1:
                    prd_name = st.text_input(
                        "Ürün Adı *",
                        placeholder="Örn: AquaCoat WB-200",
                    )
                with pc2:
                    prd_type = st.selectbox("Ürün Tipi *", _AREAS_LOCAL)
                    prd_status = st.selectbox("Başlangıç Durumu", _PROD_STATUSES)
                prd_notes = st.text_area("Notlar", height=60)
                if st.form_submit_button("Ürünü Kaydet", width="stretch"):
                    if not prd_name.strip():
                        st.error("Ürün adı zorunludur.")
                    else:
                        # project_id is captured from outer scope via closure
                        ok, msg = add_product(
                            project_id=project_id,
                            name=prd_name.strip(),
                            product_type=prd_type,
                            formulation_id=formulation_id,
                            status=prd_status,
                            notes=prd_notes.strip(),
                        )
                        if ok:
                            st.success(f"✅ {msg}")
                            st.session_state[key_prd] = False
                            ld_rerun()
                        else:
                            st.error(f"❌ {msg}")
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def _frm_edit_form(f: dict, project_id: int) -> None:
    st.markdown(
        "<div style='background:#f0f7ff;border:1.5px solid #1A56DB33;"
        "border-radius:10px;padding:18px 20px;margin:6px 0 14px 0;'>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='font-size:14px;font-weight:700;color:#1A56DB;margin:0 0 14px 0;'>"
        f"✏️  Formülasyonu Düzenle — {f['name']}</p>",
        unsafe_allow_html=True,
    )
    cur_status = f["status"] if f["status"] in _FRM_STATUSES else _FRM_STATUSES[0]
    with st.form(f"frm_edit_{f['id']}", clear_on_submit=False):
        f_name = st.text_input("Formülasyon Adı *", value=f["name"])
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            f_status = st.selectbox("Durum", _FRM_STATUSES, index=_FRM_STATUSES.index(cur_status))
        with c2:
            f_nco = st.number_input("NCO İndeks (hesaplanan, opsiyonel)", value=float(f["nco_index"] or 0), step=0.01)
        with c3:
            f_solid = st.number_input("% Katı Madde", value=float(f["solid_content"] or 0), step=0.1)
        with c4:
            f_visc = st.number_input("Hedef Viskozite (cP)", value=float(f["viscosity_target"] or 0), step=1.0)
        f_notes = st.text_area("Notlar", value=f["notes"], height=70)

        s_col, c_col, _ = st.columns([1.5, 1, 4])
        submitted = s_col.form_submit_button("💾  Güncelle", width="stretch")
        cancelled = c_col.form_submit_button("İptal",        width="stretch")

        if submitted:
            if not f_name.strip():
                st.error("Formülasyon adı boş olamaz.")
            else:
                ok, msg = update_formulation(
                    formulation_id=f["id"],
                    name=f_name.strip(),
                    status=f_status,
                    notes=f_notes.strip(),
                    nco_index=f_nco if f_nco > 0 else None,
                    solid_content=f_solid if f_solid > 0 else None,
                    viscosity_target=f_visc if f_visc > 0 else None,
                )
                if ok:
                    st.success(f"✅ {msg}")
                    st.session_state.pop(f"frm_edit_{project_id}", None)
                    ld_rerun()
                else:
                    st.error(f"❌ {msg}")

        if cancelled:
            st.session_state.pop(f"frm_edit_{project_id}", None)
            ld_rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def _frm_delete_confirm(f: dict, project_id: int) -> None:
    st.markdown(
        "<div style='background:#fff1f0;border:1.5px solid #C2303044;"
        "border-radius:10px;padding:16px 20px;margin:6px 0 14px 0;'>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='font-size:14px;font-weight:600;color:#C23030;margin:0 0 8px 0;'>"
        f"⚠️ Bu işlem geri alınamaz!</p>"
        f"<p style='font-size:13px;color:#374151;margin:0 0 12px 0;'>"
        f"<strong>{f['name']}</strong> ({f['code']}) formülasyonunu ve tüm "
        f"bileşenlerini silmek istediğinize emin misiniz?</p>",
        unsafe_allow_html=True,
    )
    yes_col, no_col, _ = st.columns([1.4, 1, 5])
    with yes_col:
        if st.button("🗑️  Evet, Sil", key=f"frm_del_confirm_{f['id']}", width="stretch"):
            ok, msg = delete_formulation(f["id"])
            if ok:
                st.success(f"✅ {msg}")
                st.session_state.pop(f"frm_delete_{project_id}", None)
                ld_rerun()
            else:
                st.error(f"❌ {msg}")
    with no_col:
        if st.button("İptal", key=f"frm_del_cancel_{f['id']}", width="stretch"):
            st.session_state.pop(f"frm_delete_{project_id}", None)
            ld_rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def _tab_formulations(project_id: int, project: dict) -> None:
    """Formülasyonlar sekmesi — liste + bileşen tablosu + NCO/OH."""
    prod_hi = st.session_state.pop(f"pj_prod_hi_{project_id}", None)
    # Default state keys
    st.session_state.setdefault(f"frm_show_add_{project_id}", False)
    st.session_state.setdefault(f"frm_expand_{project_id}", None)

    # Header row: title + add button
    _, btn_col = st.columns([5, 1.4])
    with btn_col:
        add_open = st.session_state[f"frm_show_add_{project_id}"]
        lbl = "✕  Formu Kapat" if add_open else "✚  Yeni Formülasyon"
        if st.button(lbl, key=f"frm_toggle_{project_id}", width="stretch"):
            st.session_state[f"frm_show_add_{project_id}"] = not add_open
            st.session_state.pop(f"frm_edit_{project_id}", None)
            st.session_state.pop(f"frm_delete_{project_id}", None)
            ld_rerun()

    # Add form
    if st.session_state[f"frm_show_add_{project_id}"]:
        st.markdown(
            "<div style='background:#F8FAFC;border:1.5px solid #E9EDF2;"
            "border-radius:10px;padding:18px 20px;margin-bottom:16px;'>",
            unsafe_allow_html=True,
        )
        st.markdown("#### Yeni Formülasyon")
        with st.form(f"frm_add_{project_id}", clear_on_submit=True):
            f_name = st.text_input("Formülasyon Adı *", placeholder="Örn: AquaCoat v1")
            c1, c2 = st.columns(2)
            with c1:
                f_status = st.selectbox("Başlangıç Durumu", _FRM_STATUSES)
            with c2:
                f_notes = st.text_input("Notlar (opsiyonel)")
            if st.form_submit_button("Formülasyonu Oluştur", width="stretch"):
                if not f_name.strip():
                    st.error("Formülasyon adı zorunludur.")
                else:
                    ok, msg = add_formulation(
                        project_id=project_id,
                        name=f_name.strip(),
                        status=f_status,
                        notes=f_notes.strip(),
                    )
                    if ok:
                        st.success(f"✅ {msg}")
                        st.session_state[f"frm_show_add_{project_id}"] = False
                        ld_rerun()
                    else:
                        st.error(f"❌ {msg}")
        st.markdown("</div>", unsafe_allow_html=True)

    # Formulation list
    formulations = get_all_formulations(project_id)
    if not formulations:
        st.info("Henüz formülasyon yok. '✚ Yeni Formülasyon' ile başlayın.")
        return

    _frm_header()
    for f in formulations:
        _frm_row(f, project_id)

    # ── Proje Ürünleri bölümü ───────────────────────────────
    _products_section(project_id, highlight_product_id=prod_hi)


# ══════════════════════════════════════════════════════════════
# ÜRÜNLER BÖLÜMÜ (Formülasyonlar sekmesi alt kısmı)
# ══════════════════════════════════════════════════════════════

_PRD_STATUSES = [s.value for s in ProductStatus]

_PRD_STATUS_COLORS: dict[str, str] = {
    "Geliştirme":  "#0176D3",
    "Pilot Üretim": "#E06C00",
    "Seri Üretim":  "#0A8044",
    "Durduruldu":   "#C23030",
}


def _products_section(
    project_id: int,
    *,
    highlight_product_id: int | None = None,
) -> None:
    """Alt bölüm: onaylanan formülasyonlardan oluşturulan ürünler."""
    products = get_all_products(project_id)
    if not products:
        return

    st.markdown(
        "<hr style='margin:24px 0 16px 0;border:none;border-top:2px solid #E9EDF2;'>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='font-size:15px;font-weight:700;color:#0F172A;margin:0 0 12px 0;'>"
        f"📦  Ürünler ({len(products)})</p>",
        unsafe_allow_html=True,
    )

    _PRD_COLS = [0.7, 2.6, 1.4, 1.1, 1.4, 0.9, 0.55]
    h = st.columns(_PRD_COLS)
    for lbl, col in zip(
        ["Kod", "Ürün Adı", "Kaynak Formülasyon", "Tip", "Durum", "Oluşturulma", ""],
        h,
    ):
        col.markdown(
            f"<p style='font-size:11px;font-weight:600;color:#6B7280;margin:0;"
            f"text-transform:uppercase;'>{lbl}</p>",
            unsafe_allow_html=True,
        )
    st.markdown(
        "<hr style='margin:4px 0;border:none;border-top:1.5px solid #e5e7eb;'>",
        unsafe_allow_html=True,
    )

    for p in products:
        try:
            hl = (
                highlight_product_id is not None
                and int(p["id"]) == int(highlight_product_id)
            )
        except (TypeError, ValueError):
            hl = False
        if hl:
            st.markdown(
                "<div style='margin:8px 0 4px 0;padding:8px 10px;"
                "background:rgba(1,118,211,0.08);border-left:4px solid #0176D3;"
                "border-radius:6px;'>"
                "<span style='font-size:11px;font-weight:600;color:#0176D3;'>"
                "Arama sonucu — bu ürün</span></div>",
                unsafe_allow_html=True,
            )
        cols = st.columns(_PRD_COLS)
        cols[0].markdown(
            f"<span style='font-size:11px;font-family:monospace;color:#6B7280;"
            f"background:#F3F4F6;padding:2px 6px;border-radius:4px;'>{p['code']}</span>",
            unsafe_allow_html=True,
        )
        cols[1].markdown(
            f"<span style='font-size:13px;font-weight:600;color:#0F172A;'>{p['name']}</span>",
            unsafe_allow_html=True,
        )
        cols[2].markdown(
            f"<span style='font-size:12px;color:#374151;'>{p['formulation_code']} — {p['formulation_name']}</span>",
            unsafe_allow_html=True,
        )
        cols[3].markdown(
            _badge(p["product_type"], "#6B7280"),
            unsafe_allow_html=True,
        )
        status_color = _PRD_STATUS_COLORS.get(p["status"], "#6B7280")
        cols[4].markdown(_badge(p["status"], status_color), unsafe_allow_html=True)
        created = str(p["created_at"])[:10] if p.get("created_at") else "—"
        cols[5].markdown(
            f"<span style='font-size:12px;color:#6B7280;'>{created}</span>",
            unsafe_allow_html=True,
        )

        del_key = f"prd_del_{p['id']}"
        st.session_state.setdefault(del_key, False)
        if not st.session_state[del_key]:
            if cols[6].button("🗑️", key=f"prd_del_btn_{p['id']}", help="Sil"):
                st.session_state[del_key] = True
                ld_rerun()
        else:
            if cols[6].button("✓", key=f"prd_del_ok_{p['id']}", help="Silmeyi onayla"):
                ok, msg = delete_product(p["id"])
                if ok:
                    st.success(f"✅ {msg}")
                    st.session_state[del_key] = False
                    ld_rerun()
                else:
                    st.error(f"❌ {msg}")

        st.markdown(
            "<hr style='margin:2px 0;border:none;border-top:1px solid #f3f4f6;'>",
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════════════════════
# GÖREVLER SEKMESİ (proje bazlı)
# ══════════════════════════════════════════════════════════════

_TASK_STATUSES   = [s.value for s in TaskStatus]
_TASK_PRIORITIES = [p.value for p in TaskPriority]

_TASK_STATUS_COLORS: dict[str, str] = {
    "Beklemede":    "#6B7280",
    "Devam Ediyor": "#0176D3",
    "Tamamlandı":   "#0A8044",
    "İptal":        "#C23030",
}
_TASK_PRIORITY_COLORS: dict[str, str] = {
    "Düşük":  "#6B7280",
    "Orta":   "#0176D3",
    "Yüksek": "#E06C00",
    "Acil":   "#C23030",
}

_TASK_COLS = [0.7, 2.6, 1.5, 1.0, 1.1, 0.7]


def _tab_gorevler(project_id: int, project: dict) -> None:
    """Proje bazlı Görevler sekmesi."""
    key_add = f"task_show_add_{project_id}"
    st.session_state.setdefault(key_add, False)

    _, btn_col = st.columns([5, 1.4])
    with btn_col:
        lbl = "✕  Formu Kapat" if st.session_state[key_add] else "✚  Yeni Görev"
        if st.button(lbl, key=f"task_toggle_{project_id}", width="stretch"):
            st.session_state[key_add] = not st.session_state[key_add]
            ld_rerun()

    # Add task form
    if st.session_state[key_add]:
        st.markdown(
            "<div style='background:#F8FAFC;border:1.5px solid #E9EDF2;"
            "border-radius:10px;padding:18px 20px;margin-bottom:16px;'>",
            unsafe_allow_html=True,
        )
        st.markdown("#### Bu Projeye Görev Ekle")
        with st.form(f"task_add_{project_id}", clear_on_submit=True):
            f_title    = st.text_input("Görev Başlığı *")
            f_desc     = st.text_area("Açıklama", height=60)
            c1, c2, c3 = st.columns(3)
            with c1:
                f_assignee = st.text_input("Atanan Kişi")
            with c2:
                f_pri = st.selectbox("Öncelik", _TASK_PRIORITIES, index=1)
            with c3:
                f_due = st.date_input("Son Tarih", value=None)
            if st.form_submit_button("Görevi Kaydet", width="stretch"):
                if not f_title.strip():
                    st.error("Görev başlığı zorunludur.")
                else:
                    ok, msg = add_task(
                        title=f_title.strip(),
                        description=f_desc.strip(),
                        project_id=project_id,
                        assignee=f_assignee.strip(),
                        priority=f_pri,
                        due_date=f_due,
                    )
                    if ok:
                        st.success(f"✅ {msg}")
                        st.session_state[key_add] = False
                        ld_rerun()
                    else:
                        st.error(f"❌ {msg}")
        st.markdown("</div>", unsafe_allow_html=True)

    # Task list
    tasks = get_all_tasks(project_id=project_id)
    if not tasks:
        st.info("Bu projeye henüz görev atanmamış.")
        return

    # Table header
    h = st.columns(_TASK_COLS)
    for col, lbl in zip(h, ["Kod", "Görev", "Atanan", "Öncelik", "Durum", "Son Tarih"]):
        col.markdown(f"<p class='pj-th'>{lbl}</p>", unsafe_allow_html=True)
    st.markdown(
        "<hr style='margin:0 0 4px 0;border:none;border-top:2px solid #e5e7eb;'>",
        unsafe_allow_html=True,
    )

    for t in tasks:
        tc = st.columns(_TASK_COLS)
        tc[0].markdown(f"<span class='pj-code'>{t['code']}</span>", unsafe_allow_html=True)
        tc[1].markdown(
            f"<span style='font-size:13px;font-weight:600;color:#0A1120;'>{t['title']}</span>",
            unsafe_allow_html=True,
        )
        tc[2].markdown(
            f"<span style='font-size:12px;color:#374151;'>{t['assignee'] or '—'}</span>",
            unsafe_allow_html=True,
        )
        pc = _TASK_PRIORITY_COLORS.get(t["priority"], "#888")
        tc[3].markdown(_badge(t["priority"], pc), unsafe_allow_html=True)
        sc  = _TASK_STATUS_COLORS.get(t["status"], "#888")
        s_idx = _TASK_STATUSES.index(t["status"]) if t["status"] in _TASK_STATUSES else 0
        next_s = _TASK_STATUSES[(s_idx + 1) % len(_TASK_STATUSES)]
        tc[4].markdown(_badge(t["status"], sc), unsafe_allow_html=True)
        if tc[4].button("▶", key=f"ts_cycle_{t['id']}", help=f"→ {next_s}"):
            update_task_status(t["id"], next_s)
            ld_rerun()
        due_str = t["due_date"].strftime("%d.%m.%Y") if t["due_date"] else "—"
        tc[5].markdown(f"<span class='pj-date'>{due_str}</span>", unsafe_allow_html=True)
        st.markdown(
            "<hr style='margin:2px 0;border:none;border-top:1px solid #f3f4f6;'>",
            unsafe_allow_html=True,
        )


def _tab_placeholder(title: str, icon: str, desc: str) -> None:
    st.markdown(
        f"<div class='ld-placeholder' style='padding:40px;'>"
        f"<div class='ld-placeholder-icon'>{icon}</div>"
        f"<p class='ld-placeholder-text'>{title}</p>"
        f"<p class='ld-placeholder-sub'>{desc}</p>"
        f"</div>",
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════
# MAIN RENDER
# ══════════════════════════════════════════════════════════════

def render(project_id: int | None = None) -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
    if project_id:
        _render_detail(project_id)
    else:
        _render_list()

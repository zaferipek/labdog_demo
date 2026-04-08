"""Görevler sayfası — Salesforce Lightning stili görev yönetimi."""
from __future__ import annotations

from datetime import date as dt_date

import streamlit as st

from ld_rerun import ld_rerun

from styles import render_field_label

from database import (
    TaskPriority,
    TaskStatus,
    add_task,
    delete_task,
    get_all_projects,
    get_all_tasks,
    update_task,
    update_task_status,
)

# ── Renk paleti ────────────────────────────────────────────────
_STATUS_COLORS: dict[str, str] = {
    "Beklemede":    "#6B7280",
    "Devam Ediyor": "#0176D3",
    "Tamamlandı":   "#0A8044",
    "İptal":        "#C23030",
}

_PRIORITY_COLORS: dict[str, str] = {
    "Düşük":  "#6B7280",
    "Orta":   "#0176D3",
    "Yüksek": "#E06C00",
    "Acil":   "#C23030",
}

_STATUSES   = [s.value for s in TaskStatus]
_PRIORITIES = [p.value for p in TaskPriority]

# ── CSS ────────────────────────────────────────────────────────
_CSS = """
<style>
/* Page title */
.gv-title{font-size:22px;font-weight:700;color:#0A1120;margin:0 0 4px 0;}
.gv-sub  {font-size:13px;color:#6B7280;margin:0 0 18px 0;}

/* Stat cards */
.gv-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:22px;}
.gv-stat{background:#fff;border-radius:10px;padding:16px 20px;
  border:1px solid #E9EDF2;box-shadow:0 1px 4px rgba(15,23,42,.05);}
.gv-stat-num{font-size:28px;font-weight:800;color:#0A1120;margin:0 0 2px 0;}
.gv-stat-lbl{font-size:11px;color:#6B7280;font-weight:600;text-transform:uppercase;
  letter-spacing:.05em;margin:0;}

/* Table header */
.gv-th{font-size:11px;font-weight:600;color:#6B7280;text-transform:uppercase;
  letter-spacing:.05em;padding:6px 0;margin:0;}

/* Cell styles */
.gv-code {font-size:11px;color:#9CA3AF;font-weight:500;font-family:monospace;}
.gv-name {font-weight:600;color:#0A1120;font-size:13px;line-height:1.3;}
.gv-desc {font-size:11px;color:#9CA3AF;margin-top:2px;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:260px;}
.gv-date {font-size:12px;color:#6B7280;}
.gv-overdue{color:#C23030 !important;font-weight:600;}

/* Badge */
.gv-badge{display:inline-block;padding:2px 9px;border-radius:12px;font-size:11px;
  font-weight:600;white-space:nowrap;}

/* Add form panel */
.gv-form-panel{background:#F8FAFC;border:1.5px solid #E9EDF2;
  border-radius:10px;padding:20px 24px;margin-bottom:20px;}

/* Edit panel */
.gv-edit-panel{background:#f0f7ff;border:1.5px solid #1A56DB33;
  border-radius:10px;padding:18px 20px;margin:6px 0 14px 0;}

/* Delete panel */
.gv-del-panel{background:#fff1f0;border:1.5px solid #C2303044;
  border-radius:10px;padding:16px 20px;margin:6px 0 14px 0;}

/* Quick status button */
[class*="st-key-gv_status_"] button{
  font-size:11px !important;padding:2px 8px !important;}

/* Red delete buttons */
[class*="st-key-gv_del_btn_"] button{
  background:#fff1f0 !important;color:#C23030 !important;
  border:1px solid #C2303066 !important;}
[class*="st-key-gv_del_btn_"] button:hover{
  background:#C23030 !important;color:#fff !important;}
[class*="st-key-gv_del_confirm_"] button{
  background:#C23030 !important;color:#fff !important;border:none !important;}
</style>
"""

# Column widths: code | title+desc | project | assignee | priority | due | status | edit | del
_COLS = [0.7, 2.6, 1.5, 1.3, 0.9, 1.0, 1.1, 0.55, 0.55]


# ── HTML helpers ───────────────────────────────────────────────

def _badge(label: str, color: str) -> str:
    return (
        f"<span class='gv-badge' style='background:{color}14;color:{color};"
        f"border:1px solid {color}33;'>{label}</span>"
    )


def _due_date_html(due: dt_date | None) -> str:
    if due is None:
        return "<span class='gv-date'>—</span>"
    today = dt_date.today()
    cls   = "gv-date gv-overdue" if due < today else "gv-date"
    return f"<span class='{cls}'>{due.strftime('%d.%m.%Y')}</span>"


# ── Stat cards ─────────────────────────────────────────────────

def _stat_cards(tasks: list[dict]) -> None:
    total    = len(tasks)
    bekleyen = sum(1 for t in tasks if t["status"] == "Beklemede")
    devam    = sum(1 for t in tasks if t["status"] == "Devam Ediyor")
    tamam    = sum(1 for t in tasks if t["status"] == "Tamamlandı")

    st.markdown(
        f"<div class='gv-stats'>"
        f"<div class='gv-stat'><p class='gv-stat-num'>{total}</p>"
        f"<p class='gv-stat-lbl'>Toplam Görev</p></div>"
        f"<div class='gv-stat'><p class='gv-stat-num' style='color:#6B7280'>{bekleyen}</p>"
        f"<p class='gv-stat-lbl'>Beklemede</p></div>"
        f"<div class='gv-stat'><p class='gv-stat-num' style='color:#0176D3'>{devam}</p>"
        f"<p class='gv-stat-lbl'>Devam Ediyor</p></div>"
        f"<div class='gv-stat'><p class='gv-stat-num' style='color:#0A8044'>{tamam}</p>"
        f"<p class='gv-stat-lbl'>Tamamlandı</p></div>"
        f"</div>",
        unsafe_allow_html=True,
    )


# ── Table ──────────────────────────────────────────────────────

def _table_header() -> None:
    h      = st.columns(_COLS)
    labels = ["Kod", "Görev", "Proje", "Atanan", "Öncelik", "Son Tarih", "Durum", "", ""]
    for col, lbl in zip(h, labels):
        col.markdown(f"<p class='gv-th'>{lbl}</p>", unsafe_allow_html=True)
    st.markdown(
        "<hr style='margin:0 0 4px 0;border:none;border-top:2px solid #e5e7eb;'>",
        unsafe_allow_html=True,
    )


def _table_row(
    t: dict,
    edit_id: int | None,
    delete_id: int | None,
    *,
    highlight_id: int | None = None,
) -> None:
    cols     = st.columns(_COLS)
    editing  = edit_id   == t["id"]
    deleting = delete_id == t["id"]

    if highlight_id is not None and t["id"] == highlight_id:
        st.markdown(
            "<div style='margin:6px 0 2px 0;padding:8px 10px;"
            "background:rgba(1,118,211,0.09);border-left:4px solid #0176D3;"
            "border-radius:6px;'>"
            "<span style='font-size:11px;font-weight:600;color:#0176D3;'>"
            "Arama sonucu — bu görev</span></div>",
            unsafe_allow_html=True,
        )

    # ── Static cells ──────────────────────────────────────────
    cols[0].markdown(f"<span class='gv-code'>{t['code']}</span>", unsafe_allow_html=True)
    desc_html = (
        f"<div class='gv-desc'>{t['description'][:80]}</div>"
        if t.get("description") else ""
    )
    cols[1].markdown(
        f"<div class='gv-name'>{t['title']}</div>{desc_html}",
        unsafe_allow_html=True,
    )
    cols[2].markdown(
        f"<span style='font-size:12px;color:#374151;'>{t['project_name'] or '—'}</span>",
        unsafe_allow_html=True,
    )
    cols[3].markdown(
        f"<span style='font-size:12px;color:#374151;'>{t['assignee'] or '—'}</span>",
        unsafe_allow_html=True,
    )
    cols[4].markdown(
        _badge(t["priority"], _PRIORITY_COLORS.get(t["priority"], "#888")),
        unsafe_allow_html=True,
    )
    cols[5].markdown(_due_date_html(t["due_date"]), unsafe_allow_html=True)

    # Quick status badge + cycle button
    sc    = _STATUS_COLORS.get(t["status"], "#888")
    s_idx = _STATUSES.index(t["status"]) if t["status"] in _STATUSES else 0
    next_status = _STATUSES[(s_idx + 1) % len(_STATUSES)]
    cols[6].markdown(_badge(t["status"], sc), unsafe_allow_html=True)
    if cols[6].button(
        "▶",
        key=f"gv_status_{t['id']}",
        help=f"→ {next_status}",
    ):
        ok, msg = update_task_status(t["id"], next_status)
        if ok:
            ld_rerun()
        else:
            st.error(msg)

    # ── Edit toggle ───────────────────────────────────────────
    if cols[7].button(
        "✕" if editing else "✏️",
        key=f"gv_edit_btn_{t['id']}",
        help="Formu kapat" if editing else "Düzenle",
    ):
        if editing:
            st.session_state.pop("gv_edit_id", None)
        else:
            st.session_state["gv_edit_id"] = t["id"]
            st.session_state.pop("gv_delete_id", None)
        ld_rerun()

    # ── Delete button ─────────────────────────────────────────
    if cols[8].button(
        "✕" if deleting else "🗑️",
        key=f"gv_del_btn_{t['id']}",
        help="İptal" if deleting else "Sil",
    ):
        if deleting:
            st.session_state.pop("gv_delete_id", None)
        else:
            st.session_state["gv_delete_id"] = t["id"]
            st.session_state.pop("gv_edit_id", None)
        ld_rerun()

    st.markdown(
        "<hr style='margin:2px 0;border:none;border-top:1px solid #f3f4f6;'>",
        unsafe_allow_html=True,
    )


# ── Inline edit form ───────────────────────────────────────────

def _edit_form(target: dict, projects: list[dict]) -> None:
    st.markdown("<div class='gv-edit-panel'>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='font-size:14px;font-weight:700;color:#1A56DB;margin:0 0 14px 0;'>"
        f"✏️  Görevi Düzenle — {target['title']}</p>",
        unsafe_allow_html=True,
    )

    cur_pri = target["priority"] if target["priority"] in _PRIORITIES else _PRIORITIES[1]
    # project list for display (code is immutable)
    proj_names = ["— Proje Yok —"] + [p["name"] for p in projects]
    cur_proj_name = target.get("project_name") or "— Proje Yok —"
    if cur_proj_name not in proj_names:
        cur_proj_name = "— Proje Yok —"

    with st.form(f"gv_edit_{target['id']}", clear_on_submit=False):
        f_title = st.text_input("Görev Başlığı *", value=target["title"])
        f_desc  = st.text_area(
            "Açıklama", value=target.get("description", ""), height=80,
        )
        c1, c2, c3 = st.columns(3)
        with c1:
            f_pri = st.selectbox(
                "Öncelik", _PRIORITIES,
                index=_PRIORITIES.index(cur_pri),
                key=f"gv_edit_pri_{target['id']}",
            )
        with c2:
            f_due = st.date_input(
                "Son Tarih",
                value=target["due_date"] or dt_date.today(),
                key=f"gv_edit_due_{target['id']}",
            )
        with c3:
            f_assignee = st.text_input("Atanan Kişi", value=target.get("assignee", ""))

        st.markdown(
            f"<p style='font-size:11px;color:#9ca3af;margin:4px 0 0 0;'>"
            f"Kod: <code>{target['code']}</code> — değiştirilemez.</p>",
            unsafe_allow_html=True,
        )

        s_col, c_col, _ = st.columns([1.5, 1, 4])
        submitted = s_col.form_submit_button("💾  Güncelle", width="stretch")
        cancelled = c_col.form_submit_button("İptal",        width="stretch")

        if submitted:
            if not f_title.strip():
                st.error("Görev başlığı boş bırakılamaz.")
            else:
                ok, msg = update_task(
                    task_id=target["id"],
                    title=f_title.strip(),
                    description=f_desc.strip(),
                    assignee=f_assignee.strip(),
                    priority=f_pri,
                    due_date=f_due,
                )
                if ok:
                    st.success(f"✅ {msg}")
                    st.session_state.pop("gv_edit_id", None)
                    ld_rerun()
                else:
                    st.error(f"❌ {msg}")

        if cancelled:
            st.session_state.pop("gv_edit_id", None)
            ld_rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ── Inline delete confirmation ─────────────────────────────────

def _delete_confirm(target: dict) -> None:
    st.markdown("<div class='gv-del-panel'>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='font-size:14px;font-weight:600;color:#C23030;margin:0 0 8px 0;'>"
        f"⚠️ Bu işlem geri alınamaz!</p>"
        f"<p style='font-size:13px;color:#374151;margin:0 0 12px 0;'>"
        f"<strong>{target['title']}</strong> ({target['code']}) görevini kalıcı olarak "
        f"silmek istediğinize emin misiniz?</p>",
        unsafe_allow_html=True,
    )
    yes_col, no_col, _ = st.columns([1.4, 1, 5])
    with yes_col:
        if st.button(
            "🗑️  Evet, Sil",
            key=f"gv_del_confirm_{target['id']}",
            width="stretch",
        ):
            ok, msg = delete_task(target["id"])
            if ok:
                st.success(f"✅ {msg}")
                st.session_state.pop("gv_delete_id", None)
                ld_rerun()
            else:
                st.error(f"❌ {msg}")
    with no_col:
        if st.button(
            "İptal",
            key=f"gv_del_cancel_{target['id']}",
            width="stretch",
        ):
            st.session_state.pop("gv_delete_id", None)
            ld_rerun()
    st.markdown("</div>", unsafe_allow_html=True)


@st.dialog("Yeni Görev Ekle", width="large", on_dismiss="rerun")
def _new_task_dialog() -> None:
    """Modal yeni görev — pattern: docs/ux_modal_pattern.md"""
    projects = get_all_projects()
    proj_map = {p["name"]: p["id"] for p in projects}

    with st.form("gv_add_task_form", clear_on_submit=True):
        render_field_label("Görev Başlığı", required=True, variant="dark")
        f_title = st.text_input(
            "Görev Başlığı",
            placeholder="Görev başlığını girin",
            label_visibility="collapsed",
            key="gv_new_title",
        )
        render_field_label("Açıklama", variant="dark")
        f_desc = st.text_area(
            "Açıklama",
            placeholder="Kısa açıklama (isteğe bağlı)",
            height=80,
            label_visibility="collapsed",
            key="gv_new_desc",
        )
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            proj_options = ["— Proje Yok —"] + list(proj_map.keys())
            render_field_label("Proje", variant="dark")
            f_proj_name = st.selectbox(
                "Proje",
                proj_options,
                label_visibility="collapsed",
                key="gv_new_proj",
            )
        with c2:
            render_field_label("Durum", variant="dark")
            f_status = st.selectbox(
                "Durum",
                _STATUSES,
                label_visibility="collapsed",
                key="gv_new_status",
            )
        with c3:
            render_field_label("Öncelik", variant="dark")
            f_pri = st.selectbox(
                "Öncelik",
                _PRIORITIES,
                index=1,
                label_visibility="collapsed",
                key="gv_new_pri",
            )
        with c4:
            render_field_label("Son Tarih", variant="dark")
            f_due = st.date_input(
                "Son Tarih",
                value=None,
                label_visibility="collapsed",
                key="gv_new_due",
            )

        render_field_label("Atanan Kişi", variant="dark")
        f_assignee = st.text_input(
            "Atanan Kişi",
            placeholder="Örn: Ahmet Yılmaz",
            label_visibility="collapsed",
            key="gv_new_assignee",
        )

        b_save, b_cancel = st.columns(2)
        submitted = b_save.form_submit_button("Görevi Kaydet", width="stretch")
        cancelled = b_cancel.form_submit_button("İptal", width="stretch")

        if cancelled:
            ld_rerun()

        if submitted:
            if not f_title.strip():
                st.error("Görev başlığı zorunludur.")
            else:
                pid = proj_map.get(f_proj_name) if f_proj_name != "— Proje Yok —" else None
                ok, msg = add_task(
                    title=f_title.strip(),
                    description=f_desc.strip(),
                    project_id=pid,
                    assignee=f_assignee.strip(),
                    status=f_status,
                    priority=f_pri,
                    due_date=f_due,
                )
                if ok:
                    st.success(f"✅ {msg}")
                    ld_rerun()
                else:
                    st.error(f"❌ {msg}")


# ── Ana render fonksiyonu ──────────────────────────────────────

def render(current_user=None) -> None:  # noqa: ARG001  (reserved for role checks)
    st.markdown(_CSS, unsafe_allow_html=True)

    # ── Başlık ────────────────────────────────────────────────
    st.markdown(
        "<p class='gv-title'>☑ Görevler</p>"
        "<p class='gv-sub'>Tüm Ar-Ge görevlerini takip edin, durumlarını güncelleyin.</p>",
        unsafe_allow_html=True,
    )

    # ── Filtre + Yeni Görev butonu ────────────────────────────
    filter_col, _, btn_col = st.columns([3, 3, 1.4])
    with filter_col:
        status_filter = st.selectbox(
            "Durum Filtresi",
            ["Tümü"] + _STATUSES,
            key="gv_status_filter",
            label_visibility="collapsed",
        )
    with btn_col:
        if st.button("✚  Yeni Görev", key="gv_open_new_task_dialog", width="stretch"):
            st.session_state.pop("gv_edit_id",   None)
            st.session_state.pop("gv_delete_id", None)
            _new_task_dialog()

    # ── Görev listesi ─────────────────────────────────────────
    projects = get_all_projects()
    all_tasks = get_all_tasks()

    highlight_id: int | None = None
    gf = st.session_state.pop("ld_gorev_nav_focus", None)
    if isinstance(gf, dict) and gf.get("task_id") is not None:
        try:
            highlight_id = int(gf["task_id"])
        except (TypeError, ValueError):
            highlight_id = None
    if highlight_id is None:
        tr = st.query_params.get("task_id")
        if tr is not None and str(tr).strip() != "":
            try:
                highlight_id = int(str(tr).strip())
            except ValueError:
                highlight_id = None

    # Apply filter
    tasks = (
        all_tasks
        if status_filter == "Tümü"
        else [t for t in all_tasks if t["status"] == status_filter]
    )

    # Stat cards (always based on full list)
    _stat_cards(all_tasks)

    if not tasks:
        st.info(
            "Henüz görev yok." if status_filter == "Tümü"
            else f"'{status_filter}' durumunda görev bulunamadı."
        )
        return

    _table_header()

    edit_id   = st.session_state.get("gv_edit_id")
    delete_id = st.session_state.get("gv_delete_id")

    # Guard against stale IDs after delete
    valid_ids = {t["id"] for t in tasks}
    if edit_id   not in valid_ids: edit_id   = st.session_state.pop("gv_edit_id",   None)
    if delete_id not in valid_ids: delete_id = st.session_state.pop("gv_delete_id", None)

    edit_target   = next((t for t in tasks if t["id"] == edit_id),   None)
    delete_target = next((t for t in tasks if t["id"] == delete_id), None)

    for t in tasks:
        _table_row(t, edit_id, delete_id, highlight_id=highlight_id)
        if edit_target   and t["id"] == edit_id:
            _edit_form(edit_target, projects)
        if delete_target and t["id"] == delete_id:
            _delete_confirm(delete_target)

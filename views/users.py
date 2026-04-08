"""Kullanıcı Yönetimi sayfası — Salesforce Lightning stili."""
from __future__ import annotations

import streamlit as st

from ld_rerun import ld_rerun

from database import (
    ExpertiseArea,
    UserRole,
    add_user,
    delete_user,
    get_all_users,
    update_user,
)
from styles import page_header_with_action, render_field_label

# ── Renk paleti ────────────────────────────────────────────────
_ROLE_COLORS: dict[str, str] = {
    "Admin":            "#C23030",
    "Yönetici":         "#E06C00",
    "Ar-Ge Mühendisi":  "#1A56DB",
    "Ar-Ge Uzmanı":     "#0F75BD",
    "Tekniker":         "#0A7F7F",
    "Kalite Kontrol":   "#0A8044",
    "Satın Alma":       "#7B2D8B",
    "Gözlemci":         "#888888",
}

_AREA_COLORS: dict[str, str] = {
    "Boya/Finish": "#E06C00",
    "Hot Melt":    "#7B2D8B",
    "Mürekkep":    "#0A7F7F",
    "PUD":         "#1A56DB",
    "PU":          "#0A8044",
}

_AVATAR_BG: list[str] = [
    "#1A56DB", "#0A8044", "#7B2D8B", "#0A7F7F",
    "#E06C00", "#C23030", "#0F75BD", "#5C4033",
]

_ROLES = [r.value for r in UserRole]
_AREAS = [a.value for a in ExpertiseArea]

# ── HTML helpers ───────────────────────────────────────────────

def _avatar(name: str, idx: int) -> str:
    initials = "".join(w[0].upper() for w in name.split()[:2])
    bg = _AVATAR_BG[idx % len(_AVATAR_BG)]
    return (
        f"<div style='width:34px;height:34px;border-radius:50%;background:{bg};"
        f"display:flex;align-items:center;justify-content:center;"
        f"font-size:12px;font-weight:700;color:#fff;'>{initials}</div>"
    )


def _badge(label: str, color: str) -> str:
    return (
        f"<span style='background:{color}18;color:{color};border:1px solid {color}44;"
        f"border-radius:12px;padding:2px 9px;font-size:11px;font-weight:600;"
        f"white-space:nowrap;'>{label}</span>"
    )


def _status_dot(active: bool) -> str:
    color, label = ("#0A8044", "Aktif") if active else ("#C23030", "Pasif")
    return (
        f"<span style='display:inline-flex;align-items:center;gap:5px;"
        f"font-size:12px;color:{color};font-weight:600;'>"
        f"<span style='width:8px;height:8px;border-radius:50%;"
        f"background:{color};display:inline-block;'></span>{label}</span>"
    )


# ── CSS ────────────────────────────────────────────────────────
_CSS = """
<style>
.um-title{font-size:26px;font-weight:700;color:var(--text-heading);margin:0 0 4px 0;}
.um-sub{font-size:14px;color:var(--text-meta);margin:0 0 18px 0;}
.um-th{font-size:11px;font-weight:600;color:var(--text-meta);text-transform:uppercase;
  letter-spacing:.05em;padding:6px 0;margin:0;}
.um-row-name{font-weight:600;color:var(--navy-sidebar);font-size:13px;line-height:1.3;}
.um-row-username{font-size:11px;color:#9ca3af;margin-top:1px;}
/* Inline edit panel — blue tint */
.um-edit-panel{background:#f0f7ff;border:1.5px solid #1A56DB33;
  border-radius:var(--radius-panel);padding:18px 20px;margin:6px 0 14px 0;}
/* Inline delete confirm panel — red tint */
.um-del-panel{background:#fff1f0;border:1.5px solid #C2303044;
  border-radius:var(--radius-panel);padding:16px 20px;margin:6px 0 14px 0;}
/* Red delete buttons */
[class*="st-key-del_btn"] button{
  background:#fff1f0 !important;color:#C23030 !important;
  border:1px solid #C2303066 !important;}
[class*="st-key-del_btn"] button:hover{
  background:#C23030 !important;color:#fff !important;}
/* Confirm delete button — bright red */
[class*="st-key-del_confirm"] button{
  background:#C23030 !important;color:#fff !important;
  border:none !important;}
[class*="st-key-del_confirm"] button:hover{
  background:#9b1c1c !important;}
</style>
"""

# Column proportions: avatar | name | role | expertise | status | edit | delete
_COLS = [0.5, 2.5, 1.9, 1.9, 1.3, 0.6, 0.6]


# ── Table helpers ──────────────────────────────────────────────

def _table_header() -> None:
    h = st.columns(_COLS)
    for col, lbl in zip(h, ["", "Kullanıcı", "Rol", "Uzmanlık", "Durum", "", ""]):
        col.markdown(f"<p class='ld-th'>{lbl}</p>", unsafe_allow_html=True)
    st.markdown(
        "<hr style='margin:0 0 4px 0;border:none;border-top:2px solid #e5e7eb;'>",
        unsafe_allow_html=True,
    )


def _table_row(u: dict, idx: int, edit_id: int | None, delete_id: int | None) -> None:
    cols      = st.columns(_COLS)
    is_admin  = u["role"] == "Admin"
    editing   = edit_id   == u["id"]
    deleting  = delete_id == u["id"]

    # ── Static cells ──────────────────────────────────────────
    cols[0].markdown(_avatar(u["name"], idx), unsafe_allow_html=True)
    cols[1].markdown(
        f"<div class='um-row-name'>{u['name']}</div>"
        f"<div class='um-row-username'>@{u['username']}</div>",
        unsafe_allow_html=True,
    )
    cols[2].markdown(
        _badge(u["role"], _ROLE_COLORS.get(u["role"], "#888")),
        unsafe_allow_html=True,
    )
    cols[3].markdown(
        _badge(u["expertise_group"], _AREA_COLORS.get(u["expertise_group"], "#888")),
        unsafe_allow_html=True,
    )
    cols[4].markdown(_status_dot(u.get("is_active", True)), unsafe_allow_html=True)

    # ── Edit toggle ───────────────────────────────────────────
    if cols[5].button(
        "✕" if editing else "✏️",
        key=f"edit_btn_{u['id']}",
        help="Formu kapat" if editing else "Düzenle",
    ):
        if editing:
            st.session_state.pop("um_edit_id", None)
        else:
            st.session_state["um_edit_id"] = u["id"]
            st.session_state.pop("um_delete_id", None)   # close delete confirm
            st.session_state["um_show_form"] = False
        ld_rerun()

    # ── Delete button (hidden for Admin) ──────────────────────
    if not is_admin:
        if cols[6].button(
            "✕" if deleting else "🗑️",
            key=f"del_btn_{u['id']}",
            help="İptal" if deleting else "Sil",
        ):
            if deleting:
                st.session_state.pop("um_delete_id", None)
            else:
                st.session_state["um_delete_id"] = u["id"]
                st.session_state.pop("um_edit_id", None)   # close edit form
                st.session_state["um_show_form"] = False
            ld_rerun()

    st.markdown(
        "<hr style='margin:2px 0;border:none;border-top:1px solid #f3f4f6;'>",
        unsafe_allow_html=True,
    )


# ── Inline edit form ───────────────────────────────────────────

def _edit_form(target: dict) -> None:
    st.markdown("<div class='ld-edit-panel'>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='font-size:14px;font-weight:700;color:#1A56DB;margin:0 0 14px 0;'>"
        f"✏️  Kullanıcıyı Düzenle — {target['name']}</p>",
        unsafe_allow_html=True,
    )

    cur_role = target["role"] if target["role"] in _ROLES else _ROLES[0]
    cur_area = target["expertise_group"] if target["expertise_group"] in _AREAS else _AREAS[0]

    with st.form(f"um_edit_{target['id']}", clear_on_submit=False):
        render_field_label("Kullanıcı kodu", hint="salt okunur")
        st.text_input(
            "Kullanıcı kodu",
            value=target["code"],
            disabled=True,
            key=f"um_ro_code_{target['id']}",
            label_visibility="collapsed",
            help="Sistem tarafından atanan benzersiz kod; değiştirilemez.",
        )

        c1, c2 = st.columns(2)
        with c1:
            render_field_label("Ad Soyad", required=True)
            f_name = st.text_input(
                "Ad Soyad",
                value=target["name"],
                label_visibility="collapsed",
                key=f"um_edit_name_{target['id']}",
            )
            render_field_label("Kullanıcı adı", required=True)
            f_username = st.text_input(
                "Kullanıcı adı",
                value=target["username"],
                label_visibility="collapsed",
                help="Giriş için kullanılan benzersiz kullanıcı adı.",
                key=f"um_edit_user_{target['id']}",
            )
            f_active = st.checkbox("Aktif kullanıcı", value=bool(target.get("is_active", True)))
        with c2:
            render_field_label("Rol", required=True)
            f_role = st.selectbox(
                "Rol",
                _ROLES,
                index=_ROLES.index(cur_role),
                label_visibility="collapsed",
                key=f"um_edit_role_{target['id']}",
            )
            render_field_label("Uzmanlık grubu", required=True)
            f_area = st.selectbox(
                "Uzmanlık grubu",
                _AREAS,
                index=_AREAS.index(cur_area),
                key=f"edit_area_{target['id']}",   # unique key prevents stale value
                label_visibility="collapsed",
            )

        s_col, c_col, _ = st.columns([1.5, 1, 4])
        submitted = s_col.form_submit_button("💾  Güncelle", width="stretch")
        cancelled = c_col.form_submit_button("İptal",        width="stretch")

        if submitted:
            if not f_name.strip():
                st.error("Ad Soyad boş bırakılamaz.")
            elif not (f_username or "").strip():
                st.error("Kullanıcı adı boş bırakılamaz.")
            else:
                ok, msg = update_user(
                    user_id=target["id"],
                    name=f_name.strip(),
                    username=f_username.strip(),
                    role=f_role,
                    expertise_group=f_area,
                    is_active=f_active,
                )
                if ok:
                    st.success(f"✅ {msg}")
                    st.session_state.pop("um_edit_id", None)
                    ld_rerun()
                else:
                    st.error(f"❌ {msg}")

        if cancelled:
            st.session_state.pop("um_edit_id", None)
            ld_rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ── Inline delete confirmation ─────────────────────────────────

def _delete_confirm(target: dict) -> None:
    st.markdown("<div class='ld-del-panel'>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='font-size:14px;font-weight:600;color:#C23030;margin:0 0 10px 0;'>"
        f"⚠️ Bu işlem geri alınamaz!</p>"
        f"<p style='font-size:13px;color:#374151;margin:0 0 14px 0;'>"
        f"<strong>{target['name']}</strong> (@{target['username']}) adlı kullanıcıyı "
        f"kalıcı olarak silmek istediğinize emin misiniz?</p>",
        unsafe_allow_html=True,
    )

    yes_col, no_col, _ = st.columns([1.4, 1, 5])
    with yes_col:
        if st.button(
            "🗑️  Evet, Sil",
            key=f"del_confirm_{target['id']}",
            width="stretch",
        ):
            ok, msg = delete_user(target["id"])
            if ok:
                st.success(f"✅ {msg}")
                st.session_state.pop("um_delete_id", None)
                ld_rerun()
            else:
                st.error(f"❌ {msg}")
    with no_col:
        if st.button("İptal", key=f"del_cancel_{target['id']}", width="stretch"):
            st.session_state.pop("um_delete_id", None)
            ld_rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ── Ana render fonksiyonu ──────────────────────────────────────

def render(current_user) -> None:
    st.markdown(_CSS, unsafe_allow_html=True)

    if current_user.role.value != "Admin":
        st.warning("⛔ Bu sayfaya yalnızca Admin rolündeki kullanıcılar erişebilir.")
        return

    # ── Başlık + Yeni Kullanıcı aksiyonu ─────────────────────
    st.session_state.setdefault("um_show_form", False)

    lbl = "✕  Formu Kapat" if st.session_state["um_show_form"] else "✚  Yeni Kullanıcı"
    if page_header_with_action(
        "👥 Kullanıcı Yönetimi",
        "Sisteme kayıtlı kullanıcıları görüntüle, ekle, düzenle ve sil.",
        lbl,
        "um_toggle_form",
    ):
        st.session_state["um_show_form"] = not st.session_state["um_show_form"]
        st.session_state.pop("um_edit_id",   None)
        st.session_state.pop("um_delete_id", None)
        ld_rerun()

    # ── Yeni kullanıcı ekleme formu ───────────────────────────
    if st.session_state["um_show_form"]:
        with st.container(border=True):
            st.markdown("#### Yeni Kullanıcı Ekle")
            with st.form("um_add_user_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    render_field_label("Ad Soyad", required=True)
                    f_name = st.text_input(
                        "Ad Soyad",
                        placeholder="Örn: Fatma Kaya",
                        label_visibility="collapsed",
                        key="um_add_name",
                    )
                    render_field_label("Kullanıcı adı", required=True)
                    f_user = st.text_input(
                        "Kullanıcı adı",
                        placeholder="Örn: fatma.kaya",
                        label_visibility="collapsed",
                        key="um_add_username",
                    )
                    render_field_label("Şifre", required=True)
                    f_pass = st.text_input(
                        "Şifre",
                        type="password",
                        placeholder="En az 4 karakter",
                        label_visibility="collapsed",
                        key="um_add_pass",
                    )
                with c2:
                    render_field_label("Rol", required=True)
                    f_role = st.selectbox(
                        "Rol",
                        _ROLES,
                        label_visibility="collapsed",
                        key="um_add_role",
                    )
                    render_field_label("Uzmanlık grubu", required=True)
                    f_area = st.selectbox(
                        "Uzmanlık grubu",
                        _AREAS,
                        label_visibility="collapsed",
                        key="um_add_area",
                    )

                if st.form_submit_button("Kullanıcıyı Kaydet", width="stretch"):
                    if not all([f_name.strip(), f_user.strip(), f_pass.strip()]):
                        st.error("Ad Soyad, Kullanıcı Adı ve Şifre zorunludur.")
                    elif len(f_pass) < 4:
                        st.error("Şifre en az 4 karakter olmalıdır.")
                    else:
                        ok, msg = add_user(
                            name=f_name.strip(),
                            username=f_user.strip(),
                            password=f_pass,
                            role=f_role,
                            expertise_group=f_area,
                        )
                        if ok:
                            st.success(f"✅ {msg}")
                            st.session_state["um_show_form"] = False
                            ld_rerun()
                        else:
                            st.error(f"❌ {msg}")

    # ── Kullanıcı tablosu ─────────────────────────────────────
    users = get_all_users()
    if not users:
        st.info("Henüz kayıtlı kullanıcı yok.")
        return

    st.markdown("<br>", unsafe_allow_html=True)
    _table_header()

    edit_id   = st.session_state.get("um_edit_id")
    delete_id = st.session_state.get("um_delete_id")

    # Verify IDs still exist in current user list (guard against stale state)
    valid_ids  = {u["id"] for u in users}
    if edit_id   not in valid_ids: edit_id   = st.session_state.pop("um_edit_id",   None)
    if delete_id not in valid_ids: delete_id = st.session_state.pop("um_delete_id", None)

    edit_target   = next((u for u in users if u["id"] == edit_id),   None)
    delete_target = next((u for u in users if u["id"] == delete_id), None)

    for i, u in enumerate(users):
        _table_row(u, i, edit_id, delete_id)
        if edit_target   and u["id"] == edit_id:
            _edit_form(edit_target)
        if delete_target and u["id"] == delete_id:
            _delete_confirm(delete_target)

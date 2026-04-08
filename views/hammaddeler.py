"""Hammaddeler sayfası — Salesforce Lightning stili malzeme yönetimi."""
from __future__ import annotations

import html
from datetime import date as dt_date

import streamlit as st

from ld_rerun import ld_rerun

from styles import render_field_label

from database import (
    MaterialApprovalStatus,
    add_material,
    add_material_equivalent,
    assign_material_msds_path,
    assign_material_tds_path,
    delete_material,
    get_all_materials,
    get_material_by_id,
    remove_material_equivalent,
    update_material,
    update_material_stock,
)
from material_files import read_material_pdf, save_material_pdf

# ── Sabitler ───────────────────────────────────────────────────
_APPROVAL_STATUSES = [s.value for s in MaterialApprovalStatus]
_UNITS = ["kg", "g", "L", "mL", "adet"]

_APPROVAL_COLORS: dict[str, str] = {
    "Onaylı":  "#0A8044",
    "Onaysız": "#C23030",
    "Testte":  "#0176D3",
    "Yolda":   "#E06C00",
}

# Tema beyaz metin verdiğinde de okunur olsun (inline > harici CSS; class strip olsa da çalışır)
_HM_INL = {
    "title": "font-size:22px;font-weight:700;color:#0A1120;margin:0 0 4px 0;",
    "sub": "font-size:13px;color:#6B7280;margin:0 0 18px 0;",
    "th": "font-size:11px;font-weight:600;color:#6B7280;text-transform:uppercase;"
    "letter-spacing:0.05em;padding:6px 0;margin:0;",
    "stat_num": "font-size:28px;font-weight:800;color:#0A1120;margin:0 0 2px 0;",
    "stat_lbl": "font-size:11px;font-weight:600;color:#6B7280;text-transform:uppercase;"
    "letter-spacing:0.05em;margin:0;",
    "detail_lbl": "font-size:10px;font-weight:600;color:#6B7280;text-transform:uppercase;"
    "letter-spacing:0.05em;margin:0 0 3px 0;",
    "detail_val": "font-size:13px;font-weight:600;color:#0A1120;margin:0;",
    "md_h": "margin:0 0 10px 0;font-size:15px;font-weight:600;color:#0F172A;",
}

# ── CSS ────────────────────────────────────────────────────────
_CSS = """
<style>
.hm-title{font-size:22px;font-weight:700;color:#0A1120;margin:0 0 4px 0;}
.hm-sub  {font-size:13px;color:#6B7280;margin:0 0 18px 0;}

/* Stat cards */
.hm-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:22px;}
.hm-stat{background:#fff;border-radius:10px;padding:16px 20px;
  border:1px solid #E9EDF2;box-shadow:0 1px 4px rgba(15,23,42,.05);}
.hm-stat-num{font-size:28px;font-weight:800;color:#0A1120;margin:0 0 2px 0;}
.hm-stat-lbl{font-size:11px;color:#6B7280;font-weight:600;text-transform:uppercase;
  letter-spacing:.05em;margin:0;}

/* Table */
.hm-th{font-size:11px;font-weight:600;color:#6B7280;text-transform:uppercase;
  letter-spacing:.05em;padding:6px 0;margin:0;}
.hm-code{font-size:11px;color:#9CA3AF;font-weight:500;font-family:monospace;}
.hm-name{font-weight:600;color:#0A1120;font-size:13px;}
.hm-sub-text{font-size:11px;color:#9CA3AF;margin-top:1px;}
.hm-num{font-size:12px;color:#374151;}

/* Badge */
.hm-badge{display:inline-block;padding:2px 9px;border-radius:12px;font-size:11px;
  font-weight:600;white-space:nowrap;}

/* Low stock warning */
.hm-low-stock{color:#C23030 !important;font-weight:600;}

/* Expanded detail panel */
.hm-detail-panel{background:#F8FAFC;border:1px solid #E9EDF2;border-radius:10px;
  padding:16px 20px;margin:4px 0 14px 0;}
.hm-detail-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));
  gap:12px;margin-bottom:14px;}
.hm-detail-label{font-size:10px;font-weight:600;color:#6B7280;text-transform:uppercase;
  letter-spacing:.05em;margin:0 0 3px 0;}
.hm-detail-value{font-size:13px;font-weight:600;color:#0A1120;margin:0;}

/* Edit panel */
.hm-edit-panel{background:#f0f7ff;border:1.5px solid #1A56DB33;
  border-radius:10px;padding:18px 20px;margin:6px 0 14px 0;}

/* Delete panel */
.hm-del-panel{background:#fff1f0;border:1.5px solid #C2303044;
  border-radius:10px;padding:16px 20px;margin:6px 0 14px 0;}

/* Delete buttons */
[class*="st-key-hm_del_btn_"] button{
  background:#fff1f0 !important;color:#C23030 !important;
  border:1px solid #C2303066 !important;}
[class*="st-key-hm_del_btn_"] button:hover{
  background:#C23030 !important;color:#fff !important;}
[class*="st-key-hm_del_confirm_"] button{
  background:#C23030 !important;color:#fff !important;border:none !important;}

/* Liste: kod / isim → detay sayfası (link görünümlü) */
[class*="st-key-hm_code_"] button,
[class*="st-key-hm_name_"] button{
  background:transparent !important;border:none !important;box-shadow:none !important;
  color:#0A1120 !important;font-size:13px !important;font-weight:600 !important;
  text-align:left !important;justify-content:flex-start !important;width:100% !important;
  padding:0 !important;min-height:unset !important;height:auto !important;
  white-space:nowrap !important;overflow:hidden !important;text-overflow:ellipsis !important;}
[class*="st-key-hm_code_"] button{color:#9CA3AF !important;font-size:11px !important;
  font-family:monospace !important;font-weight:500 !important;}
[class*="st-key-hm_code_"] button:hover,
[class*="st-key-hm_name_"] button:hover{color:#0176D3 !important;text-decoration:underline !important;}
</style>
"""

# Col widths: code | name+supplier | function | approval | stock | chem | edit | del
_COLS = [0.7, 2.4, 1.4, 1.0, 1.1, 0.8, 0.55, 0.55]


# ── HTML helpers ───────────────────────────────────────────────

def _badge(label: str, color: str) -> str:
    return (
        f"<span class='hm-badge' style='background:{color}14;color:{color};"
        f"border:1px solid {color}33;'>{label}</span>"
    )


def _stock_html(qty: float, unit: str) -> str:
    cls = "hm-low-stock" if qty <= 0 else "hm-num"
    label = "Stok Yok" if qty <= 0 else f"{qty:g} {unit}"
    return f"<span class='{cls}'>{label}</span>"


# ── Stat cards ─────────────────────────────────────────────────

def _stat_cards(materials: list[dict]) -> None:
    total   = len(materials)
    onayli  = sum(1 for m in materials if m["approval_status"] == "Onaylı")
    testte  = sum(1 for m in materials if m["approval_status"] == "Testte")
    stoksuz = sum(1 for m in materials if m["stock_quantity"] <= 0)

    sn = _HM_INL["stat_num"]
    sl = _HM_INL["stat_lbl"]
    st.markdown(
        f"<div class='hm-stats'>"
        f"<div class='hm-stat'><p class='hm-stat-num' style='{sn}'>{total}</p>"
        f"<p class='hm-stat-lbl' style='{sl}'>Toplam Hammadde</p></div>"
        f"<div class='hm-stat'><p class='hm-stat-num' style='{sn};color:#0A8044 !important'>{onayli}</p>"
        f"<p class='hm-stat-lbl' style='{sl}'>Onaylı</p></div>"
        f"<div class='hm-stat'><p class='hm-stat-num' style='{sn};color:#0176D3 !important'>{testte}</p>"
        f"<p class='hm-stat-lbl' style='{sl}'>Testte</p></div>"
        f"<div class='hm-stat'><p class='hm-stat-num' style='{sn};color:#C23030 !important'>{stoksuz}</p>"
        f"<p class='hm-stat-lbl' style='{sl}'>Stok Yok</p></div>"
        f"</div>",
        unsafe_allow_html=True,
    )


# ── Table ──────────────────────────────────────────────────────

def _table_header() -> None:
    h = st.columns(_COLS)
    ths = _HM_INL["th"]
    for col, lbl in zip(h, ["Kod", "Hammadde / Tedarikçi", "Fonksiyon", "Onay", "Stok", "Kimya", "", ""]):
        col.markdown(f"<p class='hm-th' style='{ths}'>{lbl}</p>", unsafe_allow_html=True)
    st.markdown(
        "<hr style='margin:0 0 4px 0;border:none;border-top:2px solid #e5e7eb;'>",
        unsafe_allow_html=True,
    )


def _go_material(
    mid: int,
    *,
    edit: bool = False,
    delete_: bool = False,
) -> None:
    st.query_params["material_id"] = str(mid)
    st.session_state.pop("hm_expand_id", None)
    if edit:
        st.session_state["hm_edit_id"] = mid
        st.session_state.pop("hm_delete_id", None)
    elif delete_:
        st.session_state["hm_delete_id"] = mid
        st.session_state.pop("hm_edit_id", None)
    else:
        st.session_state.pop("hm_edit_id", None)
        st.session_state.pop("hm_delete_id", None)
    ld_rerun()


def _table_row(m: dict, edit_id: int | None, delete_id: int | None) -> None:
    cols     = st.columns(_COLS)
    editing  = edit_id   == m["id"]
    deleting = delete_id == m["id"]

    if cols[0].button(
        m["code"],
        key=f"hm_code_{m['id']}",
        help="Kaydı aç",
        type="secondary",
    ):
        _go_material(m["id"])

    c1 = cols[1]
    brand = f" — {m['brand']}" if m["brand"] else ""
    if c1.button(
        m["name"],
        key=f"hm_name_{m['id']}",
        help="Kaydı aç",
        type="secondary",
    ):
        _go_material(m["id"])
    sn = (m.get("stock_name") or "").strip()
    stock_sub = ""
    if sn:
        stock_sub = (
            f"<div class='hm-sub-text' style='font-size:10px;color:#6B7280;margin-top:2px;'>"
            f"Stok adı: {html.escape(sn)}</div>"
        )
    c1.markdown(
        f"<div class='hm-sub-text' style='font-size:11px;color:#9CA3AF;'>{m['supplier']}{brand}</div>{stock_sub}",
        unsafe_allow_html=True,
    )
    cols[2].markdown(
        f"<span style='font-size:12px;color:#374151;'>{m['function'][:24]}</span>",
        unsafe_allow_html=True,
    )
    ac = _APPROVAL_COLORS.get(m["approval_status"], "#888")
    cols[3].markdown(_badge(m["approval_status"], ac), unsafe_allow_html=True)
    cols[4].markdown(_stock_html(m["stock_quantity"], m["unit"]), unsafe_allow_html=True)

    # Chemistry summary pill
    chem_parts = []
    if m["equivalent_weight"]: chem_parts.append(f"EW:{m['equivalent_weight']:.0f}")
    if m["nco_content"]:       chem_parts.append(f"NCO:{m['nco_content']:.1f}%")
    if m["oh_number"]:         chem_parts.append(f"OH:{m['oh_number']:.0f}")
    chem_txt = " · ".join(chem_parts) if chem_parts else "—"
    cols[5].markdown(
        f"<span style='font-size:11px;color:#6B7280;'>{chem_txt}</span>",
        unsafe_allow_html=True,
    )

    # ── Edit ──────────────────────────────────────────────────
    if cols[6].button("✕" if editing else "✏️", key=f"hm_edit_{m['id']}", help="Formu kapat" if editing else "Düzenle"):
        if editing:
            st.session_state.pop("hm_edit_id", None)
            ld_rerun()
        else:
            _go_material(m["id"], edit=True)

    # ── Delete ────────────────────────────────────────────────
    if cols[7].button("✕" if deleting else "🗑️", key=f"hm_del_btn_{m['id']}", help="İptal" if deleting else "Sil"):
        if deleting:
            st.session_state.pop("hm_delete_id", None)
            ld_rerun()
        else:
            _go_material(m["id"], delete_=True)

    st.markdown(
        "<hr style='margin:2px 0;border:none;border-top:1px solid #f3f4f6;'>",
        unsafe_allow_html=True,
    )


# ── Tam sayfa detay (URL material_id) ───────────────────────────


def _material_full_page(_current_user, m: dict) -> None:
    top1, top2 = st.columns([1.1, 5])
    with top1:
        if st.button("← Listeye dön", key="hm_back_list", width="stretch"):
            if "material_id" in st.query_params:
                del st.query_params["material_id"]
            st.session_state.pop("hm_expand_id", None)
            st.session_state.pop("hm_edit_id", None)
            st.session_state.pop("hm_delete_id", None)
            ld_rerun()
    brand = f" — {m['brand']}" if m.get("brand") else ""
    sn_head = (m.get("stock_name") or "").strip()
    stock_line = ""
    if sn_head:
        stock_line = (
            f"<p class='hm-sub' style='margin:-6px 0 14px 0;font-size:12px;color:#6B7280;'>"
            f"Stok adı: {html.escape(sn_head)}</p>"
        )
    with top2:
        st.markdown(
            f"<p class='hm-title' style='{_HM_INL['title']};margin-bottom:2px;'>{m['code']}</p>"
            f"<p class='hm-sub' style='{_HM_INL['sub']};margin-bottom:16px;'>"
            f"<span style='font-weight:700;color:#0A1120;'>{m['name']}</span>"
            f" · {m['supplier']}{brand}</p>"
            f"{stock_line}",
            unsafe_allow_html=True,
        )

    _detail_panel(m)
    _edit_form(m)

    st.markdown("---")
    if st.session_state.get("hm_delete_id") != m["id"]:
        if st.button("🗑️ Bu hammaddeyi sil…", key="hm_detail_open_delete"):
            st.session_state["hm_delete_id"] = m["id"]
            ld_rerun()

    if st.session_state.get("hm_delete_id") == m["id"]:
        _delete_confirm(m)


# ── Expanded detail panel ──────────────────────────────────────

def _detail_panel(m: dict) -> None:
    full = get_material_by_id(m["id"]) or m
    st.markdown("<div class='hm-detail-panel'>", unsafe_allow_html=True)

    # Chemical properties grid
    sn_raw = (full.get("stock_name") or "").strip()
    sn_disp = html.escape(sn_raw) if sn_raw else "—"
    props = [
        ("Stok adı (firma içi)", sn_disp, ""),
        ("Eş. Ağırlık (EW)",   full.get("equivalent_weight"), "g/mol"),
        ("% NCO",              full.get("nco_content"),        "%"),
        ("OH Numarası",        full.get("oh_number"),          "mg KOH/g"),
        ("% Katı Madde",       full.get("solid_content"),      "%"),
        ("CAS Numarası",       full.get("cas_number") or "—", ""),
        ("Varış Tarihi",       full.get("arrival_date").strftime("%d.%m.%Y")
                               if full.get("arrival_date") else "—", ""),
    ]
    dl, dv = _HM_INL["detail_lbl"], _HM_INL["detail_val"]
    grid_html = "<div class='hm-detail-grid'>"
    for lbl, val, unit in props:
        display = f"{val} {unit}".strip() if val is not None and val != "—" else "—"
        esc_disp = html.escape(str(display))
        grid_html += (
            f"<div><p class='hm-detail-label' style='{dl}'>{html.escape(lbl)}</p>"
            f"<p class='hm-detail-value' style='{dv}'>{esc_disp}</p></div>"
        )
    grid_html += "</div>"
    st.markdown(grid_html, unsafe_allow_html=True)

    if full.get("notes"):
        st.markdown(
            f"<p style='font-size:13px;color:#374151;margin:0 0 12px 0;'>"
            f"📝 {full['notes']}</p>",
            unsafe_allow_html=True,
        )

    # ── MSDS / TDS (yerel PDF + harici URL) ───────────────────
    st.markdown(
        "<p style='font-size:12px;font-weight:600;color:#6B7280;margin:14px 0 4px 0;'>"
        "MSDS / TDS</p>"
        "<p style='font-size:11px;color:#9CA3AF;margin:0 0 10px 0;'>"
        "Yerel PDF (en fazla 25 MB). Harici bağlantıları düzenleme formundan girebilirsiniz. "
        "Büyük dosyalar OneDrive senkronunda ek yük oluşturabilir.</p>",
        unsafe_allow_html=True,
    )
    mid = int(full["id"])
    msds_p = (full.get("msds_file_path") or "").strip()
    tds_p = (full.get("tds_file_path") or "").strip()
    msds_url = (full.get("safety_data_sheet_url") or "").strip()
    tds_url = (full.get("tds_url") or "").strip()

    dc1, dc2 = st.columns(2)
    with dc1:
        st.markdown(
            f"<p style='{_HM_INL['md_h']}'><strong>MSDS</strong></p>",
            unsafe_allow_html=True,
        )
        b_msds = read_material_pdf(msds_p or None, mid)
        if b_msds:
            st.download_button(
                "📄 MSDS indir (PDF)",
                data=b_msds,
                file_name=f"{full['code']}_MSDS.pdf",
                mime="application/pdf",
                key=f"hm_dl_msds_{mid}",
                width="stretch",
            )
        with st.form(f"hm_msds_ul_{mid}", clear_on_submit=True):
            u_msds = st.file_uploader(
                "PDF seçin",
                type=["pdf"],
                key=f"hm_f_msds_{mid}",
            )
            if st.form_submit_button("Yerel MSDS yükle", width="stretch"):
                if u_msds is None:
                    st.warning("Önce bir PDF seçin.")
                else:
                    ok, msg, rel = save_material_pdf(
                        mid, "msds", u_msds.getvalue(), u_msds.name,
                    )
                    if ok and rel:
                        ok2, msg2 = assign_material_msds_path(mid, rel)
                        if ok2:
                            st.success(msg2)
                            ld_rerun()
                        else:
                            st.error(msg2)
                    else:
                        st.error(msg)
        if msds_p:
            if st.button("MSDS dosyasını kaldır", key=f"hm_clr_msds_{mid}", width="stretch"):
                ok_clr, msg_clr = assign_material_msds_path(mid, None)
                if ok_clr:
                    ld_rerun()
                else:
                    st.error(msg_clr)
        if msds_url.lower().startswith(("http://", "https://")):
            st.link_button("Harici MSDS bağlantısı ↗", msds_url)
        elif msds_url:
            st.caption(f"Harici MSDS (metin): {msds_url}")

    with dc2:
        st.markdown(
            f"<p style='{_HM_INL['md_h']}'><strong>TDS</strong></p>",
            unsafe_allow_html=True,
        )
        b_tds = read_material_pdf(tds_p or None, mid)
        if b_tds:
            st.download_button(
                "📄 TDS indir (PDF)",
                data=b_tds,
                file_name=f"{full['code']}_TDS.pdf",
                mime="application/pdf",
                key=f"hm_dl_tds_{mid}",
                width="stretch",
            )
        with st.form(f"hm_tds_ul_{mid}", clear_on_submit=True):
            u_tds = st.file_uploader(
                "PDF seçin",
                type=["pdf"],
                key=f"hm_f_tds_{mid}",
            )
            if st.form_submit_button("Yerel TDS yükle", width="stretch"):
                if u_tds is None:
                    st.warning("Önce bir PDF seçin.")
                else:
                    ok, msg, rel = save_material_pdf(
                        mid, "tds", u_tds.getvalue(), u_tds.name,
                    )
                    if ok and rel:
                        ok2, msg2 = assign_material_tds_path(mid, rel)
                        if ok2:
                            st.success(msg2)
                            ld_rerun()
                        else:
                            st.error(msg2)
                    else:
                        st.error(msg)
        if tds_p:
            if st.button("TDS dosyasını kaldır", key=f"hm_clr_tds_{mid}", width="stretch"):
                ok_clr, msg_clr = assign_material_tds_path(mid, None)
                if ok_clr:
                    ld_rerun()
                else:
                    st.error(msg_clr)
        if tds_url.lower().startswith(("http://", "https://")):
            st.link_button("Harici TDS bağlantısı ↗", tds_url)
        elif tds_url:
            st.caption(f"Harici TDS (metin): {tds_url}")

    # ── Quick stock update ─────────────────────────────────────
    st.markdown(
        "<p style='font-size:12px;font-weight:600;color:#6B7280;margin:8px 0 6px 0;'>"
        "STOK GÜNCELLE</p>",
        unsafe_allow_html=True,
    )
    with st.form(f"hm_stock_{m['id']}", clear_on_submit=False):
        sc1, sc2, sc3 = st.columns([2, 1, 2])
        with sc1:
            new_qty = st.number_input(
                "Miktar", min_value=0.0,
                value=float(m["stock_quantity"]), step=0.5,
                key=f"hm_qty_{m['id']}",
            )
        with sc2:
            new_unit = st.selectbox(
                "Birim", _UNITS,
                index=_UNITS.index(m["unit"]) if m["unit"] in _UNITS else 0,
                key=f"hm_unit_{m['id']}",
            )
        with sc3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("Stoku Kaydet", width="stretch"):
                ok, msg = update_material_stock(m["id"], new_qty, new_unit)
                if ok:
                    st.success(f"✅ {msg}")
                    ld_rerun()
                else:
                    st.error(f"❌ {msg}")

    # ── Equivalents (muadiller) ────────────────────────────────
    st.markdown(
        "<p style='font-size:12px;font-weight:600;color:#6B7280;margin:14px 0 6px 0;'>"
        "MUADİL HAMMADDELER</p>",
        unsafe_allow_html=True,
    )
    equivs = full.get("equivalents", [])
    if equivs:
        for eq in equivs:
            ec1, ec2 = st.columns([5, 1])
            ec1.markdown(
                f"<span style='font-size:13px;font-weight:600;color:#0A1120;'>"
                f"{eq['eq_material_name']}</span> "
                f"<span style='font-size:11px;color:#9CA3AF;font-family:monospace;'>"
                f"{eq['eq_material_code']}</span>"
                + (f" — <span style='font-size:11px;color:#6B7280;'>{eq['notes']}</span>" if eq["notes"] else ""),
                unsafe_allow_html=True,
            )
            if ec2.button("🗑️", key=f"hm_rem_eq_{eq['id']}", help="Muadil ilişkisini kaldır"):
                ok, msg = remove_material_equivalent(eq["id"])
                if ok:
                    ld_rerun()
                else:
                    st.error(msg)
    else:
        st.markdown(
            "<p style='font-size:12px;color:#9CA3AF;margin:0 0 8px 0;'>"
            "Henüz muadil tanımlanmamış.</p>",
            unsafe_allow_html=True,
        )

    # Add equivalent form
    all_mats = get_all_materials()
    other_mats = [x for x in all_mats if x["id"] != m["id"]]
    if other_mats:
        with st.form(f"hm_add_eq_{m['id']}", clear_on_submit=True):
            mat_opts = {f"{x['name']} ({x['code']})": x["id"] for x in other_mats}
            ec1, ec2, ec3 = st.columns([3, 2, 1])
            with ec1:
                sel_label = st.selectbox("Muadil Hammadde", list(mat_opts.keys()), key=f"hm_eq_sel_{m['id']}")
            with ec2:
                eq_note = st.text_input("Not (opsiyonel)", key=f"hm_eq_note_{m['id']}")
            with ec3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("Ekle"):
                    ok, msg = add_material_equivalent(m["id"], mat_opts[sel_label], eq_note)
                    if ok:
                        st.success(f"✅ {msg}")
                        ld_rerun()
                    else:
                        st.error(f"❌ {msg}")

    st.markdown("</div>", unsafe_allow_html=True)


# ── Edit form ──────────────────────────────────────────────────

def _edit_form(m: dict) -> None:
    st.markdown("<div class='hm-edit-panel'>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='font-size:14px;font-weight:700;color:#1A56DB;margin:0 0 14px 0;'>"
        f"✏️  Hammaddeyi Düzenle — {m['name']}</p>",
        unsafe_allow_html=True,
    )
    cur_status = m["approval_status"] if m["approval_status"] in _APPROVAL_STATUSES else _APPROVAL_STATUSES[0]

    with st.form(f"hm_edit_form_{m['id']}", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            f_name     = st.text_input("Hammadde Adı *", value=m["name"])
            f_stock_name = st.text_input(
                "Stok adı (opsiyonel)",
                value=m.get("stock_name") or "",
                help="Firma içi kısa ad veya envanter kodu",
            )
            f_supplier = st.text_input("Tedarikçi *",    value=m["supplier"])
            f_function = st.text_input("Fonksiyon *",    value=m["function"])
            f_brand    = st.text_input("Marka",          value=m["brand"])
        with c2:
            f_cas      = st.text_input("CAS Numarası",   value=m["cas_number"])
            f_status   = st.selectbox(
                "Onay Durumu", _APPROVAL_STATUSES,
                index=_APPROVAL_STATUSES.index(cur_status),
            )
            f_arrival  = st.date_input(
                "Varış Tarihi",
                value=m["arrival_date"] or dt_date.today(),
                key=f"hm_edit_arr_{m['id']}",
            )

        st.markdown(
            f"<p style='{_HM_INL['md_h']};margin:12px 0 8px 0;'><strong>Kimyasal Özellikler</strong></p>",
            unsafe_allow_html=True,
        )
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            f_ew      = st.number_input(
                "Eş. Ağırlık (g/mol)",
                value=float(m["equivalent_weight"] or 0), min_value=0.0, step=0.1,
            )
        with d2:
            f_nco     = st.number_input(
                "% NCO",
                value=float(m["nco_content"] or 0), min_value=0.0, max_value=100.0, step=0.01,
            )
        with d3:
            f_oh      = st.number_input(
                "OH Numarası",
                value=float(m["oh_number"] or 0), min_value=0.0, step=0.1,
            )
        with d4:
            f_solid   = st.number_input(
                "% Katı Madde",
                value=float(m["solid_content"] or 0), min_value=0.0, max_value=100.0, step=0.1,
            )
        url_c1, url_c2 = st.columns(2)
        with url_c1:
            f_msds_url = st.text_input(
                "MSDS harici URL (opsiyonel)",
                value=m.get("safety_data_sheet_url") or "",
                help="https://… ile harici güvenlik bilgi formu bağlantısı",
            )
        with url_c2:
            f_tds_url = st.text_input(
                "TDS harici URL (opsiyonel)",
                value=m.get("tds_url") or "",
                help="https://… ile harici teknik veri sayfası",
            )
        f_notes = st.text_area("Notlar", value=m["notes"], height=60)

        s_col, c_col, _ = st.columns([1.5, 1, 4])
        submitted = s_col.form_submit_button("💾  Güncelle", width="stretch")
        cancelled = c_col.form_submit_button("İptal",        width="stretch")

        if submitted:
            if not all([f_name.strip(), f_supplier.strip(), f_function.strip()]):
                st.error("Ad, Tedarikçi ve Fonksiyon alanları zorunludur.")
            else:
                ok, msg = update_material(
                    material_id=m["id"],
                    name=f_name.strip(),
                    supplier=f_supplier.strip(),
                    function=f_function.strip(),
                    stock_name=f_stock_name.strip(),
                    brand=f_brand.strip(),
                    cas_number=f_cas.strip(),
                    approval_status=f_status,
                    arrival_date=f_arrival,
                    equivalent_weight=f_ew  if f_ew  > 0 else None,
                    nco_content=f_nco if f_nco > 0 else None,
                    oh_number=f_oh   if f_oh  > 0 else None,
                    solid_content=f_solid if f_solid > 0 else None,
                    notes=f_notes.strip(),
                    safety_data_sheet_url=f_msds_url.strip(),
                    tds_url=f_tds_url.strip(),
                )
                if ok:
                    st.success(f"✅ {msg}")
                    st.session_state.pop("hm_edit_id", None)
                    ld_rerun()
                else:
                    st.error(f"❌ {msg}")

        if cancelled:
            st.session_state.pop("hm_edit_id", None)
            ld_rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ── Delete confirm ─────────────────────────────────────────────

def _delete_confirm(m: dict) -> None:
    st.markdown("<div class='hm-del-panel'>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='font-size:14px;font-weight:600;color:#C23030;margin:0 0 8px 0;'>"
        f"⚠️ Bu işlem geri alınamaz!</p>"
        f"<p style='font-size:13px;color:#374151;margin:0 0 12px 0;'>"
        f"<strong>{m['name']}</strong> ({m['code']}) hammaddesini kalıcı olarak silmek "
        f"istediğinize emin misiniz? Formülasyonlarda kullanılıyorsa silinemez.</p>",
        unsafe_allow_html=True,
    )
    yes_col, no_col, _ = st.columns([1.4, 1, 5])
    with yes_col:
        if st.button("🗑️  Evet, Sil", key=f"hm_del_confirm_{m['id']}", width="stretch"):
            ok, msg = delete_material(m["id"])
            if ok:
                st.success(f"✅ {msg}")
                st.session_state.pop("hm_delete_id", None)
                if "material_id" in st.query_params:
                    del st.query_params["material_id"]
                ld_rerun()
            else:
                st.error(f"❌ {msg}")
    with no_col:
        if st.button("İptal", key=f"hm_del_cancel_{m['id']}", width="stretch"):
            st.session_state.pop("hm_delete_id", None)
            ld_rerun()
    st.markdown("</div>", unsafe_allow_html=True)


@st.dialog("Yeni Hammadde Ekle", width="large", on_dismiss="rerun")
def _new_material_dialog() -> None:
    """Modal yeni hammadde — pattern: docs/ux_modal_pattern.md"""
    with st.form("hm_add_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            render_field_label("Hammadde Adı", required=True, variant="dark")
            f_name = st.text_input(
                "Hammadde Adı",
                placeholder="Örn: Lupranat M20S",
                label_visibility="collapsed",
                key="hm_new_name",
            )
            render_field_label("Stok adı", hint="Opsiyonel — firma içi kod", variant="dark")
            f_stock_name = st.text_input(
                "Stok adı",
                placeholder="Örn: LP-M20S-01",
                label_visibility="collapsed",
                key="hm_new_stock_name",
            )
            render_field_label("Tedarikçi", required=True, variant="dark")
            f_supplier = st.text_input(
                "Tedarikçi",
                placeholder="Örn: BASF",
                label_visibility="collapsed",
                key="hm_new_supplier",
            )
            render_field_label("Fonksiyon", required=True, variant="dark")
            f_function = st.text_input(
                "Fonksiyon",
                placeholder="Örn: İzosiyonat",
                label_visibility="collapsed",
                key="hm_new_function",
            )
            render_field_label("Marka", variant="dark")
            f_brand = st.text_input(
                "Marka",
                placeholder="Opsiyonel",
                label_visibility="collapsed",
                key="hm_new_brand",
            )
        with c2:
            render_field_label("CAS Numarası", variant="dark")
            f_cas = st.text_input(
                "CAS Numarası",
                placeholder="Opsiyonel",
                label_visibility="collapsed",
                key="hm_new_cas",
            )
            render_field_label("Onay Durumu", variant="dark")
            f_status = st.selectbox(
                "Onay Durumu",
                _APPROVAL_STATUSES,
                label_visibility="collapsed",
                key="hm_new_status",
            )
            render_field_label("Başlangıç Stok", variant="dark")
            f_stock = st.number_input(
                "Başlangıç Stok",
                min_value=0.0,
                value=0.0,
                step=1.0,
                label_visibility="collapsed",
                key="hm_new_stock",
            )
            render_field_label("Birim", variant="dark")
            f_unit = st.selectbox(
                "Birim",
                _UNITS,
                label_visibility="collapsed",
                key="hm_new_unit",
            )

        render_field_label(
            "Kimyasal Özellikler",
            hint="Opsiyonel — formülasyon hesaplamaları için",
            variant="dark",
        )
        d1, d2, d3, d4 = st.columns(4)
        with d1:
            render_field_label("Eş. Ağırlık (g/mol)", variant="dark")
            f_ew = st.number_input(
                "Eş. Ağırlık (g/mol)",
                min_value=0.0,
                value=0.0,
                step=0.1,
                label_visibility="collapsed",
                key="hm_new_ew",
            )
        with d2:
            render_field_label("% NCO", variant="dark")
            f_nco = st.number_input(
                "% NCO",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=0.01,
                label_visibility="collapsed",
                key="hm_new_nco",
            )
        with d3:
            render_field_label("OH Numarası", variant="dark")
            f_oh = st.number_input(
                "OH Numarası",
                min_value=0.0,
                value=0.0,
                step=0.1,
                label_visibility="collapsed",
                key="hm_new_oh",
            )
        with d4:
            render_field_label("% Katı Madde", variant="dark")
            f_solid = st.number_input(
                "% Katı Madde",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=0.1,
                label_visibility="collapsed",
                key="hm_new_solid",
            )

        render_field_label("Notlar", variant="dark")
        f_notes = st.text_area(
            "Notlar",
            placeholder="Opsiyonel",
            height=60,
            label_visibility="collapsed",
            key="hm_new_notes",
        )

        b_save, b_cancel = st.columns(2)
        submitted = b_save.form_submit_button("Hammaddeyi Kaydet", width="stretch")
        cancelled = b_cancel.form_submit_button("İptal", width="stretch")

        if cancelled:
            ld_rerun()

        if submitted:
            if not all([f_name.strip(), f_supplier.strip(), f_function.strip()]):
                st.error("Ad, Tedarikçi ve Fonksiyon alanları zorunludur.")
            else:
                ok, msg = add_material(
                    name=f_name.strip(),
                    supplier=f_supplier.strip(),
                    function=f_function.strip(),
                    stock_name=f_stock_name.strip(),
                    brand=f_brand.strip(),
                    cas_number=f_cas.strip(),
                    stock_quantity=f_stock,
                    unit=f_unit,
                    approval_status=f_status,
                    equivalent_weight=f_ew    if f_ew    > 0 else None,
                    nco_content=f_nco   if f_nco   > 0 else None,
                    oh_number=f_oh    if f_oh    > 0 else None,
                    solid_content=f_solid if f_solid > 0 else None,
                    notes=f_notes.strip(),
                )
                if ok:
                    st.success(f"✅ {msg}")
                    ld_rerun()
                else:
                    st.error(f"❌ {msg}")


# ── Ana render fonksiyonu ──────────────────────────────────────

def render(current_user=None, material_id: int | None = None) -> None:  # noqa: ARG001
    st.markdown(_CSS, unsafe_allow_html=True)

    # Eski oturum anahtarı → URL (bir kez)
    _legacy = st.session_state.pop("ld_focus_material_id", None)
    if _legacy is not None:
        st.query_params["material_id"] = str(int(_legacy))
        ld_rerun()

    if material_id is not None:
        full = get_material_by_id(material_id)
        if not full:
            st.error("Hammadde bulunamadı veya silinmiş.")
            if "material_id" in st.query_params:
                del st.query_params["material_id"]
            ld_rerun()
            return
        _material_full_page(current_user, full)
        return

    st.markdown(
        f"<p class='hm-title' style='{_HM_INL['title']}'>⚗ Hammaddeler</p>"
        f"<p class='hm-sub' style='{_HM_INL['sub']}'>Hammadde envanterini yönetin, onay durumlarını ve "
        "kimyasal özellikleri takip edin.</p>",
        unsafe_allow_html=True,
    )

    # ── Filtre + Yeni Hammadde ─────────────────────────────────
    filter_col, _, btn_col = st.columns([3, 3, 1.6])
    with filter_col:
        status_filter = st.selectbox(
            "Onay Durumu Filtresi",
            ["Tümü"] + _APPROVAL_STATUSES,
            key="hm_status_filter",
            label_visibility="collapsed",
        )
    with btn_col:
        if st.button("✚  Yeni Hammadde", key="hm_open_new_material_dialog", width="stretch"):
            st.session_state.pop("hm_edit_id",   None)
            st.session_state.pop("hm_delete_id", None)
            st.session_state.pop("hm_expand_id", None)
            if "material_id" in st.query_params:
                del st.query_params["material_id"]
            _new_material_dialog()

    # ── Hammadde listesi ───────────────────────────────────────
    all_mats = get_all_materials()
    materials = (
        all_mats if status_filter == "Tümü"
        else [m for m in all_mats if m["approval_status"] == status_filter]
    )

    _stat_cards(all_mats)

    if not materials:
        st.info(
            "Henüz hammadde kaydı yok." if status_filter == "Tümü"
            else f"'{status_filter}' onay durumunda hammadde yok."
        )
        return

    _table_header()

    edit_id   = st.session_state.get("hm_edit_id")
    delete_id = st.session_state.get("hm_delete_id")

    # Stale ID guard
    valid_ids = {m["id"] for m in materials}
    if edit_id   not in valid_ids:
        edit_id = st.session_state.pop("hm_edit_id", None)
    if delete_id not in valid_ids:
        delete_id = st.session_state.pop("hm_delete_id", None)

    for m in materials:
        _table_row(m, edit_id, delete_id)

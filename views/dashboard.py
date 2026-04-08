"""Dashboard page — Yönetim Bakışı & Ar-Ge Performans Analizi."""
from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

from database import ProjectStatus, display_project_status
from ld_rerun import ld_rerun


_TR_MONTHS = ["Oca", "Şub", "Mar", "Nis", "May", "Haz",
               "Tem", "Ağu", "Eyl", "Eki", "Kas", "Ara"]


def _fmt_date(raw: str) -> str:
    """'2026-03-16 19:35:07' → '16 Mar 2026'"""
    try:
        dt = datetime.fromisoformat(str(raw).split(".")[0])
        return f"{dt.day} {_TR_MONTHS[dt.month - 1]} {dt.year}"
    except Exception:
        return str(raw)


def _st(p: dict) -> str:
    return display_project_status(p.get("status"))


def render(stats: list) -> None:
    all_projects = [p for s in stats for p in s["projects"]]
    total  = len(all_projects)
    done   = sum(1 for p in all_projects if _st(p) == ProjectStatus.DONE.value)
    lab    = sum(1 for p in all_projects if _st(p) == ProjectStatus.LAB_TEST.value)
    lit    = sum(1 for p in all_projects if _st(p) == ProjectStatus.LITERATURE.value)
    ham    = sum(1 for p in all_projects if _st(p) == ProjectStatus.HAMMADDE_TEDARIGI.value)
    pilot  = sum(1 for p in all_projects if _st(p) == ProjectStatus.PILOT.value)
    val    = sum(1 for p in all_projects if _st(p) == ProjectStatus.VALIDASYON.value)
    fikir  = sum(1 for p in all_projects if _st(p) == ProjectStatus.FIKIR.value)
    recent = sorted(all_projects, key=lambda p: p["createdAt"], reverse=True)[:5]

    sub = st.session_state.get("dash_sub", "cards")

    if sub == "cards":
        st.markdown(
            "<div class='ld-page-header'>"
            "<h1 class='ld-page-title'>Dashboardlar</h1>"
            "<p class='ld-page-sub'>Analiz etmek istediğiniz veri görünümünü seçin.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2, gap="large")
        with c1:
            with st.container(border=True):
                st.markdown(
                    "<div class='ld-card-icon'>⊞</div>"
                    "<h3 class='ld-card-title'>Yönetim Bakışı</h3>"
                    "<p class='ld-card-desc'>Genel proje durumları, uzmanlık alanlarına göre"
                    " dağılım ve son aktiviteler.</p>",
                    unsafe_allow_html=True,
                )
                if st.button("Yönetim Bakışını Aç →", key="open_yonetim", width="stretch"):
                    st.session_state["dash_sub"] = "yonetim"
                    ld_rerun()
        with c2:
            with st.container(border=True):
                st.markdown(
                    "<div class='ld-card-icon purple'>📊</div>"
                    "<h3 class='ld-card-title'>Ar-Ge Performans Analizi</h3>"
                    "<p class='ld-card-desc'>Deney başarı oranları, test yoğunluğu ve"
                    " laboratuvar verimlilik metrikleri.</p>",
                    unsafe_allow_html=True,
                )
                if st.button("Performans Analizini Aç →", key="open_perf", width="stretch"):
                    st.session_state["dash_sub"] = "performans"
                    ld_rerun()

    elif sub == "yonetim":
        if st.button("← Dashboardlara Dön", key="back_y"):
            st.session_state["dash_sub"] = "cards"
            ld_rerun()
        st.markdown(
            "<div class='ld-page-header'>"
            "<h1 class='ld-page-title'>Yönetim Bakışı</h1>"
            "<p class='ld-page-sub'>Genel proje durumları ve son aktiviteler.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div class='ld-metric-grid'>"
            f"<div class='ld-metric'><p class='ld-metric-label'>Toplam Proje</p>"
            f"<p class='ld-metric-value'>{total}</p></div>"
            f"<div class='ld-metric'><p class='ld-metric-label'>Tamamlanan</p>"
            f"<p class='ld-metric-value ld-metric-accent'>{done}</p></div>"
            f"<div class='ld-metric'><p class='ld-metric-label'>Fikir</p>"
            f"<p class='ld-metric-value'>{fikir}</p></div>"
            f"<div class='ld-metric'><p class='ld-metric-label'>Literatür</p>"
            f"<p class='ld-metric-value'>{lit}</p></div>"
            f"<div class='ld-metric'><p class='ld-metric-label'>Hammadde</p>"
            f"<p class='ld-metric-value'>{ham}</p></div>"
            f"<div class='ld-metric'><p class='ld-metric-label'>Lab Test</p>"
            f"<p class='ld-metric-value'>{lab}</p></div>"
            f"<div class='ld-metric'><p class='ld-metric-label'>Pilot</p>"
            f"<p class='ld-metric-value'>{pilot}</p></div>"
            f"<div class='ld-metric'><p class='ld-metric-label'>Validasyon</p>"
            f"<p class='ld-metric-value'>{val}</p></div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div class='ld-section'><p class='ld-section-title'>Son Aktiviteler</p>",
            unsafe_allow_html=True,
        )
        if recent:
            items = "".join(
                f"<div class='ld-activity-item'>"
                f"<div class='ld-activity-dot'></div>"
                f"<div><p class='ld-activity-name'>{p['name']}</p>"
                f"<p class='ld-activity-meta'>{p['rdSpecialist']} &bull; {_fmt_date(p['createdAt'])}</p>"
                f"<span class='ld-status-pill'>{_st(p)}</span></div>"
                f"</div>"
                for p in recent
            )
            st.markdown(items + "</div>", unsafe_allow_html=True)
        else:
            st.info("Henüz aktivite yok.")
            st.markdown("</div>", unsafe_allow_html=True)

    elif sub == "performans":
        if st.button("← Dashboardlara Dön", key="back_p"):
            st.session_state["dash_sub"] = "cards"
            ld_rerun()
        st.markdown(
            "<div class='ld-page-header'>"
            "<h1 class='ld-page-title'>Ar-Ge Performans Analizi</h1>"
            "<p class='ld-page-sub'>Uzmanlık alanına göre proje dağılımı.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        chart_df = pd.DataFrame({
            "Uzmanlık Alanı": [s["expertiseArea"] for s in stats],
            "Proje Sayısı":   [s["count"]         for s in stats],
        })
        st.markdown(
            "<div class='ld-section'><p class='ld-section-title'>Proje Dağılımı</p>",
            unsafe_allow_html=True,
        )
        # color: Streamlit — liste uzunluğu yalnızca renklendirilecek *sütun* sayısıyla eşleşir (burada 1).
        st.bar_chart(
            chart_df.set_index("Uzmanlık Alanı"),
            color="#0176D3",
            width="stretch",
        )
        st.markdown("</div>", unsafe_allow_html=True)

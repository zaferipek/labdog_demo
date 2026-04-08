"""Toplu Yükleme modülü — Excel/CSV ile Projeler, Kullanıcılar ve Hammaddeler için toplu veri aktarımı."""
from __future__ import annotations

import streamlit as st

from ld_rerun import ld_rerun

from database import (
    bulk_import_materials,
    bulk_import_projects,
    bulk_import_users,
    generate_import_template,
    generate_materials_template,
    generate_users_template,
)

_CSS = """
<style>
.ty-section{background:#fff;border-radius:var(--radius-card);padding:24px 28px;
  border:1px solid #E9EDF2;box-shadow:0 1px 4px rgba(15,23,42,.05);margin-bottom:20px;}
.ty-section-title{font-size:15px;font-weight:700;color:var(--text-heading);margin:0 0 6px 0;}
.ty-section-sub{font-size:13px;color:var(--text-meta);margin:0 0 20px 0;line-height:1.6;}
/* Step indicator */
.ty-step{display:flex;align-items:center;gap:8px;margin-bottom:8px;}
.ty-step-num{width:22px;height:22px;border-radius:50%;background:#0176D3;color:#fff;
  font-size:11px;font-weight:700;display:inline-flex;align-items:center;
  justify-content:center;flex-shrink:0;}
.ty-step-text{font-size:13px;font-weight:600;color:var(--text-body);}
.ty-cols-badge{display:inline-block;padding:2px 9px;border-radius:10px;font-size:11px;
  font-weight:600;background:#EFF6FF;color:#0176D3;border:1px solid #BFDBFE;
  margin:2px 3px;}
.ty-info-box{background:#F0F7FF;border:1px solid #BFDBFE;border-radius:8px;
  padding:12px 16px;margin-bottom:18px;}
.ty-info-box p{font-size:12px;color:#1E40AF;margin:0;line-height:1.6;}
.ty-result-ok{background:#ECFDF5;border:1px solid #6EE7B7;border-radius:8px;
  padding:12px 16px;margin-top:12px;}
.ty-result-ok p{font-size:13px;color:#065F46;font-weight:600;margin:0;}
.ty-result-warn{background:#FFF7ED;border:1px solid #FED7AA;border-radius:8px;
  padding:12px 16px;margin-top:12px;}
.ty-result-warn p{font-size:13px;color:#92400E;font-weight:600;margin:0;}
</style>
"""

_MIME_XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


def _import_panel(
    *,
    section_title: str,
    section_color: str,
    section_icon: str,
    description: str,
    required_cols: list[str],
    optional_cols: list[str],
    template_fn,
    template_filename: str,
    import_fn,
    result_unit: str,
    key_prefix: str,
) -> None:
    """
    Reusable import panel: info + template download + file upload + import button + results.
    """
    st.markdown(f"<div class='ty-section'>", unsafe_allow_html=True)

    # Header
    st.markdown(
        f"<p class='ty-section-title'>{section_icon} {section_title}</p>"
        f"<p class='ty-section-sub'>{description}</p>",
        unsafe_allow_html=True,
    )

    # Column info
    required_badges = "".join(
        f"<span class='ty-cols-badge' style='background:#FEF2F2;color:#C23030;"
        f"border-color:#FECACA;'>{c}</span>"
        for c in required_cols
    )
    optional_badges = "".join(
        f"<span class='ty-cols-badge'>{c}</span>" for c in optional_cols
    )
    st.markdown(
        f"<div class='ty-info-box'>"
        f"<p><strong>Zorunlu sütunlar:</strong> {required_badges}</p>"
        f"<p style='margin-top:6px;'><strong>İsteğe bağlı sütunlar:</strong> {optional_badges}</p>"
        f"<p style='margin-top:6px;color:#4B5563;'>Sütun adları <strong>tam olarak</strong> şablondaki gibi olmalıdır. "
        f"Şablonun 2. sayfasında geçerli değer listesi bulunur.</p>"
        f"</div>",
        unsafe_allow_html=True,
    )

    col_tmpl, col_upload = st.columns([1.3, 2.7])

    with col_tmpl:
        st.markdown(
            "<div class='ty-step'>"
            "<span class='ty-step-num'>1</span>"
            "<span class='ty-step-text'>Şablonu İndir</span>"
            "</div>",
            unsafe_allow_html=True,
        )
        try:
            tmpl_bytes = template_fn()
            st.download_button(
                label="📄 Şablonu İndir (.xlsx)",
                data=tmpl_bytes,
                file_name=template_filename,
                mime=_MIME_XLSX,
                key=f"{key_prefix}_tmpl",
                width="stretch",
            )
        except Exception as exc:
            st.error(f"Şablon oluşturulamadı: {exc}")

    with col_upload:
        st.markdown(
            "<div class='ty-step'>"
            "<span class='ty-step-num'>2</span>"
            "<span class='ty-step-text'>Doldurulmuş Dosyayı Yükle</span>"
            "</div>",
            unsafe_allow_html=True,
        )
        uploaded = st.file_uploader(
            "Dosya seç",
            type=["xlsx", "xls", "csv"],
            key=f"{key_prefix}_file",
            label_visibility="collapsed",
            help="xlsx, xls veya csv formatı desteklenir.",
        )

    if uploaded is not None:
        st.markdown(
            f"<p style='font-size:12px;color:#6B7280;margin:10px 0 6px 0;'>"
            f"Seçilen dosya: <strong>{uploaded.name}</strong></p>",
            unsafe_allow_html=True,
        )
        if st.button(
            f"🚀 İçe Aktar",
            key=f"{key_prefix}_run",
            type="primary",
        ):
            with st.spinner("Veriler işleniyor…"):
                file_data = uploaded.read()
                success, errors = import_fn(file_data)

            if success > 0:
                st.markdown(
                    f"<div class='ty-result-ok'>"
                    f"<p>✅ {success} {result_unit} başarıyla eklendi.</p>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                ld_rerun()
            else:
                st.markdown(
                    "<div class='ty-result-warn'>"
                    "<p>⚠️ Hiçbir kayıt eklenemedi. Hataları inceleyin.</p>"
                    "</div>",
                    unsafe_allow_html=True,
                )

            if errors:
                with st.expander(f"⚠️ {len(errors)} satır hatası — tıklayın", expanded=success == 0):
                    for e in errors:
                        st.markdown(
                            f"<p style='font-size:12px;color:#C23030;margin:3px 0;'>• {e}</p>",
                            unsafe_allow_html=True,
                        )

    st.markdown("</div>", unsafe_allow_html=True)


def render(current_user) -> None:
    st.markdown(_CSS, unsafe_allow_html=True)

    st.markdown(
        "<div class='ld-page-header'>"
        "<h1 class='ld-page-title'>Toplu Yükleme</h1>"
        "<p class='ld-page-sub'>"
        "Excel şablonlarını indirin, doldurun ve sisteme toplu olarak veri aktarın. "
        "Bu işlem nadir kullanılır — tek tek kayıt için ilgili modüllerin kendi formlarını kullanın."
        "</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    tab_prj, tab_usr, tab_mat = st.tabs([
        "⬡  Projeler",
        "👥  Kullanıcılar",
        "⚗  Hammaddeler",
    ])

    with tab_prj:
        _import_panel(
            section_title="Toplu Proje Aktarımı",
            section_color="#0176D3",
            section_icon="⬡",
            description=(
                "Birden fazla projeyi aynı anda sisteme aktarmak için bu aracı kullanın. "
                "Mevcut projeler tekrar eklenmez; "
                "aynı isimli proje olsa bile sistem yeni bir kayıt oluşturur."
            ),
            required_cols=["Proje Adı", "Uzmanlık Alanı", "Sorumlu", "Başlangıç Tarihi"],
            optional_cols=["Hedef Tarih", "Durum", "Öncelik", "Müşteri", "Açıklama"],
            template_fn=generate_import_template,
            template_filename="proje_toplu_yukleme_sablonu.xlsx",
            import_fn=bulk_import_projects,
            result_unit="proje",
            key_prefix="ty_prj",
        )
        st.markdown(
            "<div class='ty-info-box'>"
            "<p><strong>Uzmanlık Alanı geçerli değerleri:</strong> "
            "Boya/Finish, Hot Melt, Mürekkep, PUD, PU</p>"
            "<p style='margin-top:4px;'><strong>Durum geçerli değerleri:</strong> "
            "Fikir, Literatür Taraması, Hammadde tedariği, Lab Test, Pilot, Validasyon, Tamamlandı</p>"
            "<p style='margin-top:2px;font-size:12px;color:#6B7280;'>Eski şablonda "
            "\"Laboratuvar Testleri\" de kabul edilir (Lab Test olarak kaydedilir).</p>"
            "<p style='margin-top:4px;'><strong>Öncelik geçerli değerleri:</strong> "
            "Düşük, Orta, Yüksek, Acil</p>"
            "</div>",
            unsafe_allow_html=True,
        )

    with tab_usr:
        if current_user.role.value != "Admin":
            st.warning("⛔ Kullanıcı toplu yüklemesi yalnızca Admin rolü için geçerlidir.")
        else:
            _import_panel(
                section_title="Toplu Kullanıcı Aktarımı",
                section_color="#0A8044",
                section_icon="👥",
                description=(
                    "Yeni kullanıcıları Excel ile sisteme toplu olarak ekleyin. "
                    "Var olan kullanıcı adına sahip satırlar atlanır ve hata listesinde gösterilir."
                ),
                required_cols=["Kullanıcı Adı", "Ad Soyad", "Şifre", "Rol", "Uzmanlık Grubu"],
                optional_cols=[],
                template_fn=generate_users_template,
                template_filename="kullanici_toplu_yukleme_sablonu.xlsx",
                import_fn=bulk_import_users,
                result_unit="kullanıcı",
                key_prefix="ty_usr",
            )
            st.markdown(
                "<div class='ty-info-box'>"
                "<p><strong>Rol geçerli değerleri:</strong> "
                "Admin, Yönetici, Ar-Ge Mühendisi, Ar-Ge Uzmanı, Tekniker, Kalite Kontrol, Satın Alma, Gözlemci</p>"
                "<p style='margin-top:4px;'><strong>Uzmanlık Grubu geçerli değerleri:</strong> "
                "Boya/Finish, Hot Melt, Mürekkep, PUD, PU</p>"
                "</div>",
                unsafe_allow_html=True,
            )

    with tab_mat:
        _import_panel(
            section_title="Toplu Hammadde Aktarımı",
            section_color="#7B2D8B",
            section_icon="⚗",
            description=(
                "Hammadde kataloğunuzu Excel ile sisteme toplu olarak aktarın. "
                "NCO içeriği ve OH sayısı gibi kimyasal parametreleri de dahil edebilirsiniz — "
                "bu değerler formülasyon hesaplamalarında otomatik kullanılacaktır."
            ),
            required_cols=["Hammadde Adı", "Tedarikçi", "Fonksiyon"],
            optional_cols=[
                "Stok Adı",
                "Marka", "CAS No", "Stok Miktarı", "Birim",
                "Onay Durumu", "Eşdeğer Ağırlık", "NCO İçeriği (%)",
                "OH Sayısı", "Katı Madde (%)", "Notlar",
            ],
            template_fn=generate_materials_template,
            template_filename="hammadde_toplu_yukleme_sablonu.xlsx",
            import_fn=bulk_import_materials,
            result_unit="hammadde",
            key_prefix="ty_mat",
        )
        st.markdown(
            "<div class='ty-info-box'>"
            "<p><strong>Onay Durumu geçerli değerleri:</strong> "
            "Onaylı, Onaysız, Testte, Yolda</p>"
            "<p style='margin-top:4px;'><strong>Birim örnek değerleri:</strong> "
            "kg, g, L, mL, adet</p>"
            "</div>",
            unsafe_allow_html=True,
        )

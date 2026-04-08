from typing import Literal

def base_css() -> str:
    """
    Shared CSS: Streamlit chrome removal, typography, CSS vars.
    Also includes dashboard-specific styles.
    """
    return """
    /* ─── STREAMLIT CHROME REMOVAL ───────────────────────── */

    header[data-testid="stHeader"],
    div[data-testid="stToolbar"],
    div[data-testid="stDecoration"],
    div[data-testid="stStatusWidget"],
    #MainMenu,
    footer {
        display: none !important;
        height: 0 !important;
        overflow: hidden !important;
    }

    /* ─── TYPOGRAPHY & VARS ───────────────────────────────── */

    :root {
        --sf-blue:       #0176D3;
        --sf-blue-hover: #014486;
        --sf-focus:      rgba(1, 118, 211, 0.22);
        --text-main:     #181818;
        --text-soft:     #514F4D;
        --border:        #DDDBDA;
        --navy:          #0A1628;

        /* ── Design System Tokens ──────────────────────── */
        --error:         #C23030;
        --navy-sidebar:  #0A1120;
        --text-meta:     #6B7280;
        --text-body:     #374151;
        --text-heading:  #0F172A;
        --border-light:  #F1F3F6;
        --radius-card:   12px;
        --radius-panel:  10px;
        --radius-badge:  12px;

        /* Form etiketleri — açık / koyu yüzey (dialog vs ana içerik) */
        --field-label-on-light: var(--text-heading);
        --field-label-on-dark:  #F3F4F6;
        --field-hint-on-light:    var(--text-meta);
        --field-hint-on-dark:     #A8B0BC;
    }

    html, body, * {
        font-family: "Salesforce Sans", "Helvetica Neue", Arial, sans-serif;
        box-sizing: border-box;
    }
    """


def dashboard_css() -> str:
    """CSS injected ONLY by dashboard_screen()."""
    return """
    /* ─── STREAMLIT CHROME ─────────────────────────────────── */

    header[data-testid="stHeader"],
    div[data-testid="stToolbar"],
    div[data-testid="stDecoration"],
    div[data-testid="stStatusWidget"],
    #MainMenu, footer {
        display: none !important;
        height: 0 !important;
    }

    /* ═══════════════════════════════════════════════════════════
       SIDEBAR  —  clean single-source layout
       Expanded: 260 px  |  Collapsed: 80 px
       Toggle button: position absolute inside sidebar (moves with it)
       ═══════════════════════════════════════════════════════════ */

    /* 1 ── Outer section: widths + anti-hide */
    section[data-testid="stSidebar"] {
        position:    relative   !important;
        background:  var(--navy-sidebar) !important;
        overflow:    hidden     !important;
        transition:  min-width 0.3s ease, max-width 0.3s ease !important;
        transform:   none       !important;
        visibility:  visible    !important;
        margin-left: 0          !important;
        display:     block      !important;
        opacity:     1          !important;
    }

    /* Anti-hide for every Streamlit version's collapse mechanism */
    section[data-testid="stSidebar"][aria-expanded="false"],
    section[data-testid="stSidebar"][data-collapsed="true"] {
        transform:  none    !important;
        visibility: visible !important;
        display:    block   !important;
        opacity:    1       !important;
    }

    /* Expanded width */
    section[data-testid="stSidebar"]:not(:has(.ld-sb-collapsed)) {
        min-width: 260px !important;
        max-width: 260px !important;
    }

    /* Collapsed width */
    section[data-testid="stSidebar"]:has(.ld-sb-collapsed) {
        min-width: 80px !important;
        max-width: 80px !important;
    }

    /* 2 ── Inner wrapper: tam yükseklik, dış kaydırma yok (yalnız menü kayar) */
    section[data-testid="stSidebar"] > div:first-child {
        background:     var(--navy-sidebar) !important;
        padding:        0          !important;
        display:        flex       !important;
        flex-direction: column     !important;
        min-height:     100vh      !important;
        max-height:     100vh      !important;
        overflow-x:     hidden     !important;
        overflow-y:     hidden     !important;
    }

    /* İç sarmalayıcı + kök dikey blok: tam yükseklik flex sütunu */
    section[data-testid="stSidebar"] > div:first-child > div:nth-child(1) {
        flex:           1 1 auto   !important;
        min-height:     0          !important;
        overflow:       hidden     !important;
        display:        flex       !important;
        flex-direction: column     !important;
    }

    section[data-testid="stSidebar"] > div:first-child > div:nth-child(1)[data-testid="stVerticalBlock"],
    section[data-testid="stSidebar"] > div:first-child > div:nth-child(1) > [data-testid="stVerticalBlock"] {
        display:        flex       !important;
        flex-direction: column     !important;
        flex:           1 1 auto   !important;
        min-height:     0          !important;
        overflow:       hidden     !important;
    }

    /* @st.fragment bazı sürümlerde ek sarmalayıcı — aynı flex zinciri */
    section[data-testid="stSidebar"] > div:first-child [data-testid="stFragment"] {
        flex:           1 1 auto   !important;
        min-height:     0          !important;
        overflow:       hidden     !important;
        display:        flex       !important;
        flex-direction: column     !important;
        width:          100%       !important;
    }

    section[data-testid="stSidebar"] > div:first-child [data-testid="stFragment"] > [data-testid="stVerticalBlock"] {
        display:        flex       !important;
        flex-direction: column     !important;
        flex:           1 1 auto   !important;
        min-height:     0          !important;
        overflow:       hidden     !important;
    }

    /* Üst sabit: toggle, boşluk, logo, başlık, arama — küçülmesin */
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {
        flex-shrink:    0          !important;
    }

    /* Orta: yalnız ana menü (radyo) kaydırılabilir */
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:has(.stRadio) {
        flex:           1 1 auto   !important;
        min-height:     0          !important;
        max-height:     none       !important;
        overflow-y:     auto       !important;
        overflow-x:     hidden     !important;
        flex-shrink:    1          !important;
        padding-right:  2px        !important;
    }

    /* Eski boşluk: flex itme yerine gizli; footer margin-top:auto ile yapışır */
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:has(.ld-nav-spacer),
    section[data-testid="stSidebar"] > div > div:has(.ld-nav-spacer) {
        display:        none       !important;
        flex:           0 0 0      !important;
        height:         0          !important;
        margin:         0          !important;
        padding:        0          !important;
    }

    /* Alt sabit: profil satırı en alta */
    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:has(.ld-sl-profile-collapsed-only) {
        margin-top:     auto       !important;
        flex-shrink:    0          !important;
    }

    section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div:has([data-testid="stHorizontalBlock"] .ld-sl-profile-row) {
        margin-top:     auto       !important;
        flex-shrink:    0          !important;
    }

    /* 3 ── Hide Streamlit's own resize handle & ALL native collapse controls
            Covers every known data-testid across Streamlit versions:
              • collapsedControl          – floating button when sidebar is hidden
              • stSidebarCollapsedControl – newer alias
              • stSidebarHeader           – header wrapper that holds the collapse btn
              • baseButton-headerNoPadding    – old collapse btn (pre-1.33)
              • stBaseButton-headerNoPadding  – new collapse btn (1.33 +, 1.55+)
    */
    [data-testid="stSidebarResizeHandle"],
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarHeader"],
    button[data-testid="baseButton-headerNoPadding"],
    button[data-testid="stBaseButton-headerNoPadding"] {
        display:        none         !important;
        pointer-events: none         !important;
    }

    /* 4 ── Main area slides smoothly when sidebar width changes */
    section[data-testid="stMain"] {
        transition: margin-left 0.3s ease !important;
    }

    /* ───────────────────────────────────────────────────────────
       TOGGLE BUTTON  (key=sb_toggle)
       Absolutely positioned inside the sidebar — moves with it.
       ─────────────────────────────────────────────────────────── */

    section[data-testid="stSidebar"] .st-key-sb_toggle {
        position: absolute !important;
        top:      18px     !important;
        right:    10px     !important;
        z-index:  100      !important;
        width:    auto     !important;
        padding:  0        !important;
        margin:   0        !important;
    }

    /* Centered in collapsed mode */
    section[data-testid="stSidebar"]:has(.ld-sb-collapsed) .st-key-sb_toggle {
        right: auto                    !important;
        left:  50%                     !important;
        transform: translateX(-50%)    !important;
    }

    /* The <button> itself */
    section[data-testid="stSidebar"] .st-key-sb_toggle button {
        width:         28px                             !important;
        height:        28px                             !important;
        min-height:    unset                            !important;
        background:    rgba(26, 79, 138, 0.85)          !important;
        color:         #ffffff                          !important;
        border:        1px solid rgba(255,255,255,0.18) !important;
        border-radius: 50%                              !important;
        font-size:     17px                             !important;
        font-weight:   700                              !important;
        font-family:   'Segoe UI', Arial, sans-serif    !important;
        padding:       0 0 1px 0                        !important;
        display:       flex                             !important;
        align-items:   center                           !important;
        justify-content: center                         !important;
        cursor:        pointer                          !important;
        transition:    background 0.15s, transform 0.15s !important;
        line-height:   1                                !important;
        user-select:   none                             !important;
        box-shadow:    0 2px 8px rgba(0,0,0,0.35)       !important;
    }

    section[data-testid="stSidebar"] .st-key-sb_toggle button:hover {
        background: #1B5EBE    !important;
        transform:  scale(1.1) !important;
    }

    /* Dar sidebar: toggle position:absolute akışta yer kaplamaz — boşluk + nav aşağı */
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"]:has(.ld-sb-top-gap) {
        margin-bottom: 0 !important;
    }
    section[data-testid="stSidebar"] .ld-sb-top-gap {
        display:        block        !important;
        height:         56px         !important;
        min-height:     56px         !important;
        flex-shrink:    0            !important;
        width:          100%         !important;
        margin:         0            !important;
        padding:        0            !important;
        pointer-events: none         !important;
        box-sizing:     border-box   !important;
    }

    /* ───────────────────────────────────────────────────────────
       SIDEBAR LOGO (geniş mod: PNG + marka; dar modda render yok)
       ─────────────────────────────────────────────────────────── */

    section[data-testid="stSidebar"] [data-testid="stImage"] {
        display:         flex                    !important;
        justify-content: center                  !important;
        padding:       18px 12px 6px            !important;
        margin-bottom: 0                        !important;
    }
    section[data-testid="stSidebar"] [data-testid="stImage"] img {
        max-width:     136px                    !important;
        width:         auto                     !important;
        height:        auto                     !important;
        object-fit:    contain                  !important;
    }

    .ld-sl-brand-below {
        text-align:    center;
        padding:       0 12px 12px;
        margin:        0;
        border-bottom: 1px solid rgba(255,255,255,0.07);
    }

    .ld-sl-appname {
        font-size:   15px;
        font-weight: 700;
        color:       #E8EDF2;
        line-height: 1.25;
    }

    .ld-sl-appsub {
        font-size:      10px;
        font-weight:    600;
        color:          #8FA6BC;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        margin-top:     0;
        line-height:    1.35;
    }

    /* Sidebar — kompakt arama (logo altı, nav üstü; input + sağ büyüteç)
       Not: Streamlit sütunları data-testid="stColumn" (eski "column" da yedek) */
    section[data-testid="stSidebar"] .ld-sb-search-wrap {
        padding:       0 10px 12px 10px;
        margin:        0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.07);
    }
    section[data-testid="stSidebar"] .ld-sb-search-wrap [data-testid="stHorizontalBlock"] {
        gap:           0 !important;
        align-items:   stretch !important;
    }
    /* Arama gönder: sabit genişlik kare — ⚙ / ⏻ ile aynı 36px yükseklik ailesi */
    section[data-testid="stSidebar"] .ld-sb-search-wrap [data-testid="stColumn"]:last-child,
    section[data-testid="stSidebar"] .ld-sb-search-wrap [data-testid="column"]:last-child {
        display:         flex !important;
        align-items:     stretch !important;
        align-self:      stretch !important;
        flex:            0 0 40px !important;
        min-width:       40px !important;
        max-width:       40px !important;
        width:           40px !important;
    }
    section[data-testid="stSidebar"] .ld-sb-search-wrap [data-testid="stColumn"]:last-child > div,
    section[data-testid="stSidebar"] .ld-sb-search-wrap [data-testid="column"]:last-child > div {
        flex:            1 1 auto !important;
        display:         flex !important;
        align-items:     center !important;
        justify-content: center !important;
        width:           100% !important;
        min-width:       0 !important;
        min-height:      0 !important;
        overflow:        hidden !important;
    }
    section[data-testid="stSidebar"] .ld-sb-search-wrap [data-testid="stForm"] {
        margin-bottom: 0 !important;
    }
    section[data-testid="stSidebar"] .ld-sb-search-wrap .stTextInput > div {
        margin-bottom: 0 !important;
    }
    section[data-testid="stSidebar"] .ld-sb-search-wrap .stTextInput input {
        background:    rgba(255, 255, 255, 0.08) !important;
        border:        1px solid rgba(255, 255, 255, 0.12) !important;
        border-right:  none !important;
        border-radius: 10px 0 0 10px !important;
        color:         #E8EDF2 !important;
        min-height:    36px !important;
        font-size:     13px !important;
        padding-left:  10px !important;
        padding-right: 8px !important;
    }
    section[data-testid="stSidebar"] .ld-sb-search-wrap .stTextInput input::placeholder {
        color: rgba(232, 238, 247, 0.42) !important;
    }
    /* Arama gönder — ikon ``views/search_bar.py`` içinde ``icon=:material/search:`` (monokrom).
       Eski hata: span/p display:none + ::after, BaseButton iç katmanının altında kalıyordu / ikon siliniyordu. */
    section[data-testid="stSidebar"] .ld-sb-search-wrap .st-key-ld_gs_submit [data-testid="stBaseButton-secondaryFormSubmit"],
    section[data-testid="stSidebar"] .ld-sb-search-wrap .st-key-ld_gs_submit [data-testid="stBaseButton-tertiaryFormSubmit"],
    section[data-testid="stSidebar"] .ld-sb-search-wrap .st-key-ld_gs_submit [data-testid="stBaseButton-primaryFormSubmit"] {
        border-radius:    0 10px 10px 0 !important;
        min-height:       36px !important;
        height:           36px !important;
        width:            100% !important;
        padding:          0 6px !important;
        margin:           0 !important;
        margin-top:       0 !important;
        background:       rgba(255, 255, 255, 0.08) !important;
        border:           1px solid rgba(255, 255, 255, 0.12) !important;
        border-left:      none !important;
        color:            #E8EDF2 !important;
        box-shadow:       none !important;
    }
    section[data-testid="stSidebar"] .ld-sb-search-wrap .st-key-ld_gs_submit button,
    section[data-testid="stSidebar"] .ld-sb-search-wrap [data-testid="stFormSubmitButton"] button {
        border-radius:    0 10px 10px 0 !important;
        min-height:       36px !important;
        height:           36px !important;
        max-height:       36px !important;
        width:            100% !important;
        max-width:        100% !important;
        padding:          0 6px !important;
        margin:           0 !important;
        margin-top:       0 !important;
        box-sizing:       border-box !important;
        display:          flex !important;
        align-items:      center !important;
        justify-content:  center !important;
        gap:              4px !important;
        border:           1px solid rgba(255, 255, 255, 0.12) !important;
        border-left:      none !important;
        color:            #E8EDF2 !important;
        font-size:        15px !important;
        line-height:      1 !important;
        font-weight:      500 !important;
        box-shadow:       none !important;
        letter-spacing:   0 !important;
        overflow:         visible !important;
        background:       rgba(255, 255, 255, 0.08) !important;
        -webkit-appearance: none !important;
        appearance:       none !important;
    }
    section[data-testid="stSidebar"] .ld-sb-search-wrap .st-key-ld_gs_submit button svg,
    section[data-testid="stSidebar"] .ld-sb-search-wrap [data-testid="stFormSubmitButton"] button svg {
        fill:   currentColor !important;
        color:  #E8EDF2 !important;
        width:  22px !important;
        height: 22px !important;
        flex-shrink: 0 !important;
    }
    section[data-testid="stSidebar"] .ld-sb-search-wrap .st-key-ld_gs_submit button p,
    section[data-testid="stSidebar"] .ld-sb-search-wrap [data-testid="stFormSubmitButton"] button p {
        margin:      0 !important;
        padding:     0 !important;
        color:       inherit !important;
        line-height: 1.2 !important;
    }
    section[data-testid="stSidebar"] .ld-sb-search-wrap .st-key-ld_gs_submit button:hover,
    section[data-testid="stSidebar"] .ld-sb-search-wrap [data-testid="stFormSubmitButton"] button:hover,
    section[data-testid="stSidebar"] .ld-sb-search-wrap .st-key-ld_gs_submit [data-testid="stBaseButton-secondaryFormSubmit"]:hover {
        background: rgba(255, 255, 255, 0.14) !important;
        color:      #FFFFFF !important;
        border:     1px solid rgba(255, 255, 255, 0.18) !important;
        border-left: none !important;
    }
    section[data-testid="stSidebar"] .ld-sb-search-wrap .st-key-ld_gs_submit button:active,
    section[data-testid="stSidebar"] .ld-sb-search-wrap [data-testid="stFormSubmitButton"] button:active {
        background: rgba(255, 255, 255, 0.1) !important;
    }
    /* Material ikon + ZWSP: iç flex satırı ikonu sola iter — kutuda tam ortala */
    section[data-testid="stSidebar"] .ld-sb-search-wrap .st-key-ld_gs_submit button,
    section[data-testid="stSidebar"] .ld-sb-search-wrap .st-key-ld_gs_submit [data-testid="stBaseButton-secondaryFormSubmit"],
    section[data-testid="stSidebar"] .ld-sb-search-wrap .st-key-ld_gs_submit [data-testid="stBaseButton-tertiaryFormSubmit"],
    section[data-testid="stSidebar"] .ld-sb-search-wrap .st-key-ld_gs_submit [data-testid="stBaseButton-primaryFormSubmit"] {
        padding-left:    0 !important;
        padding-right:   0 !important;
        gap:             0 !important;
        justify-content: center !important;
    }
    section[data-testid="stSidebar"] .ld-sb-search-wrap .st-key-ld_gs_submit button > div,
    section[data-testid="stSidebar"] .ld-sb-search-wrap .st-key-ld_gs_submit [data-testid="stBaseButton-secondaryFormSubmit"] > div:first-of-type {
        width:           100% !important;
        max-width:       100% !important;
        display:         flex !important;
        align-items:     center !important;
        justify-content: center !important;
        gap:             0 !important;
    }
    section[data-testid="stSidebar"] .ld-sb-search-wrap .st-key-ld_gs_submit [data-testid="stHorizontalBlock"] {
        width:           100% !important;
        justify-content: center !important;
        align-items:     center !important;
        gap:             0 !important;
    }
    /* Yalnızca metin sütunu (svg yok) yer kaplamasın */
    section[data-testid="stSidebar"] .ld-sb-search-wrap .st-key-ld_gs_submit [data-testid="stMarkdownContainer"]:not(:has(svg)) {
        flex:       0 0 0 !important;
        width:      0 !important;
        min-width:  0 !important;
        margin:     0 !important;
        padding:    0 !important;
        overflow:   hidden !important;
        opacity:    0 !important;
    }
    section[data-testid="stSidebar"] .ld-sb-search-wrap .st-key-ld_gs_submit button svg {
        display:     block !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    section[data-testid="stSidebar"] .ld-sb-search-wrap [data-testid="stVerticalBlock"] > div {
        margin-bottom: 0 !important;
    }
    section[data-testid="stSidebar"] .ld-sb-search-wrap .stCaption {
        color: rgba(255, 200, 120, 0.95) !important;
        font-size: 11px !important;
        margin-top: 4px !important;
    }

    /* ───────────────────────────────────────────────────────────
       NAVIGATION (radio)
       ─────────────────────────────────────────────────────────── */

    section[data-testid="stSidebar"] .stRadio > label,
    section[data-testid="stSidebar"] .stRadio [data-testid="stWidgetLabel"] {
        display:  none   !important;
        height:   0      !important;
        overflow: hidden !important;
        margin:   0      !important;
        padding:  0      !important;
    }

    section[data-testid="stSidebar"] .stRadio > div {
        flex-direction: column !important;
        gap:            1px    !important;
        padding:        10px 0 !important;
    }

    section[data-testid="stSidebar"] .stRadio label {
        display:     flex      !important;
        align-items: center    !important;
        padding:     10px 20px !important;
        border-radius: 8px     !important;
        margin:      1px 10px  !important;
        font-size:   13.5px    !important;
        font-weight: 400       !important;
        color:       #7A8FA3   !important;
        cursor:      pointer   !important;
        transition:  background 0.15s, color 0.15s !important;
        width:       calc(100% - 20px) !important;
        white-space: nowrap    !important;
    }

    section[data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(255,255,255,0.06) !important;
        color:      #C9D5E2               !important;
    }

    section[data-testid="stSidebar"] .stRadio label:has(input:checked) {
        background:  #1A4F8A !important;
        color:       #ffffff !important;
        font-weight: 600     !important;
    }

    section[data-testid="stSidebar"] .stRadio label > div:first-child {
        display: none !important;
    }

    /* Collapsed: icon only, centred */
    section[data-testid="stSidebar"]:has(.ld-sb-collapsed) .stRadio label {
        justify-content: center !important;
        padding:         10px 0 !important;
        margin:          2px 4px !important;
        font-size:       20px    !important;
        overflow:        hidden  !important;
        white-space:     nowrap  !important;
        width:           64px    !important;
        min-width:       64px    !important;
    }

    /* ───────────────────────────────────────────────────────────
       PROFILE CARD
       ─────────────────────────────────────────────────────────── */

    .ld-sl-profile {
        display:     flex;
        align-items: center;
        gap:         10px;
        padding:     0;
        border-top:  none;
        background:  transparent;
    }

    .ld-sl-profile-row {
        display:         flex;
        align-items:     center;
        gap:             10px;
        padding:         12px 0 10px 2px;
        margin-top:      4px;
        border-top:      1px solid rgba(255,255,255,0.07);
        background:      rgba(255,255,255,0.03);
        border-radius:   0 0 8px 8px;
        min-width:       0;
    }

    .ld-sl-profile-text {
        flex:       1;
        min-width:  0;
    }

    .ld-sl-profile-collapsed-only {
        display:         flex;
        justify-content: center;
        padding:         10px 0 6px;
        margin-top:      4px;
        border-top:      1px solid rgba(255,255,255,0.07);
    }

    .ld-sl-avatar {
        width:          36px;
        height:         36px;
        border-radius:  50%;
        background:     linear-gradient(135deg, #1669D8, #032D60);
        display:        flex;
        align-items:    center;
        justify-content: center;
        font-size:      12px;
        font-weight:    700;
        color:          #fff;
        flex-shrink:    0;
        letter-spacing: 0.02em;
    }

    .ld-sl-uname {
        font-size:     12.5px;
        font-weight:   600;
        color:         #E8EDF2;
        line-height:   1.25;
        white-space:   nowrap;
        overflow:      hidden;
        text-overflow: ellipsis;
        max-width:     140px;
    }

    .ld-sl-urole {
        font-size:   10.5px;
        color:       #4E6074;
        display:     flex;
        align-items: center;
        gap:         4px;
        margin-top:  1px;
    }

    .ld-sl-badge {
        background:     #0176D3;
        color:          #fff;
        font-size:      9px;
        font-weight:    700;
        padding:        1px 5px;
        border-radius:  4px;
        letter-spacing: 0.04em;
    }

    /* Collapsed: sadece avatar + altında ikonlar */
    section[data-testid="stSidebar"]:has(.ld-sb-collapsed) .ld-sl-uname,
    section[data-testid="stSidebar"]:has(.ld-sb-collapsed) .ld-sl-urole {
        display: none !important;
    }

    /* ───────────────────────────────────────────────────────────
       Ayarlar (⚙) + Çıkış (⏻) — kompakt ikon düğmeleri
       ─────────────────────────────────────────────────────────── */

    section[data-testid="stSidebar"] .st-key-sb_open_settings button,
    section[data-testid="stSidebar"] .st-key-logout_btn button,
    section[data-testid="stSidebar"] .st-key-sb_open_settings_c button,
    section[data-testid="stSidebar"] .st-key-logout_btn_c button {
        width:            36px           !important;
        height:           36px           !important;
        min-height:       36px           !important;
        padding:          0              !important;
        border-radius:    10px           !important;
        display:          flex           !important;
        align-items:      center         !important;
        justify-content:  center         !important;
        font-size:        17px           !important;
        line-height:      1              !important;
        background:       rgba(255,255,255,0.08) !important;
        border:           1px solid rgba(255,255,255,0.12) !important;
        color:            #E8EDF2        !important;
        margin-top:       14px           !important;
    }
    section[data-testid="stSidebar"]:has(.ld-sb-collapsed) .st-key-sb_open_settings_c button,
    section[data-testid="stSidebar"]:has(.ld-sb-collapsed) .st-key-logout_btn_c button {
        margin-top:       6px            !important;
    }
    section[data-testid="stSidebar"] .st-key-logout_btn button,
    section[data-testid="stSidebar"] .st-key-logout_btn_c button {
        color:            #F4B4B4        !important;
        border-color:     rgba(240,100,100,0.35) !important;
        background:       rgba(240,80,80,0.12) !important;
    }
    section[data-testid="stSidebar"] .st-key-sb_open_settings button:hover,
    section[data-testid="stSidebar"] .st-key-sb_open_settings_c button:hover {
        background:       rgba(255,255,255,0.16) !important;
    }
    section[data-testid="stSidebar"] .st-key-logout_btn button:hover,
    section[data-testid="stSidebar"] .st-key-logout_btn_c button:hover {
        background:       rgba(240,80,80,0.22) !important;
    }

    /* ─── MAIN CONTENT AREA ────────────────────────────────── */

    section[data-testid="stMain"],
    .main {
        background: #F4F6F9 !important;
    }

    .main .block-container,
    [data-testid="stMainBlockContainer"] {
        background: #F4F6F9 !important;
        max-width:  1140px  !important;
        padding:    36px 40px 48px !important;
    }

    /*
     * Hammaddeler (ve benzeri): ``st.markdown`` ile gömülü ``<style>`` bazı Streamlit
     * sürümlerinde uygulanmayabiliyor → .hm-* renkleri yok, tema beyaz metin kalıyor.
     * Aynı kuralları ana alanda !important ile sabitle.
     */
    section[data-testid="stMain"] .hm-title,
    section[data-testid="stMain"] p.hm-title {
        font-size:   22px              !important;
        font-weight: 700              !important;
        color:       #0A1120          !important;
        margin:      0 0 4px 0       !important;
    }
    section[data-testid="stMain"] .hm-sub,
    section[data-testid="stMain"] p.hm-sub {
        font-size: 13px               !important;
        color:     #6B7280            !important;
        margin:    0 0 18px 0        !important;
    }
    section[data-testid="stMain"] .hm-stat-num {
        font-size:   28px            !important;
        font-weight: 800             !important;
        color:       #0A1120         !important;
        margin:      0 0 2px 0       !important;
    }
    section[data-testid="stMain"] .hm-stat-lbl {
        font-size:      11px         !important;
        color:          #6B7280    !important;
        font-weight:    600         !important;
        text-transform: uppercase   !important;
        letter-spacing: .05em      !important;
        margin:         0           !important;
    }
    section[data-testid="stMain"] .hm-th {
        font-size:      11px         !important;
        font-weight:    600         !important;
        color:          #6B7280    !important;
        text-transform: uppercase   !important;
        letter-spacing: .05em      !important;
        padding:        6px 0      !important;
        margin:         0           !important;
    }
    section[data-testid="stMain"] .hm-code {
        font-size:   11px            !important;
        color:       #9CA3AF        !important;
        font-weight: 500            !important;
        font-family: monospace      !important;
    }
    section[data-testid="stMain"] .hm-name {
        font-weight: 600            !important;
        color:       #0A1120       !important;
        font-size:   13px          !important;
    }
    section[data-testid="stMain"] .hm-sub-text {
        font-size: 11px             !important;
        color:     #9CA3AF         !important;
        margin-top: 1px            !important;
    }
    section[data-testid="stMain"] .hm-num {
        font-size: 12px             !important;
        color:     #374151        !important;
    }
    section[data-testid="stMain"] .hm-detail-label {
        font-size:      10px        !important;
        font-weight:    600        !important;
        color:          #6B7280   !important;
        text-transform: uppercase  !important;
        letter-spacing: .05em     !important;
        margin:         0 0 3px 0  !important;
    }
    section[data-testid="stMain"] .hm-detail-value {
        font-size:   13px          !important;
        font-weight: 600           !important;
        color:       #0A1120      !important;
        margin:      0             !important;
    }
    /* Streamlit markdown kalın başlıklar (ör. **MSDS**, **TDS**) */
    section[data-testid="stMain"] [data-testid="stMarkdownContainer"] strong {
        color:       var(--text-heading) !important;
        font-weight: 600                !important;
    }

    /*
     * Koyu tema / Streamlit 1.3x+: ana alanda widget etiketleri ve saf markdown
     * bazen beyaz (#fff) kalıyor — açık gri zeminde görünmez oluyor.
     * section + [data-testid="stMain"] (iframe / sürüm farkı).
     */
    [data-testid="stMain"] [data-testid="stWidgetLabel"] p,
    [data-testid="stMain"] [data-testid="stWidgetLabel"] label,
    section[data-testid="stMain"] [data-testid="stWidgetLabel"] p,
    section[data-testid="stMain"] [data-testid="stWidgetLabel"] span,
    [data-testid="stMain"] .stTextInput [data-testid="stWidgetLabel"] p,
    [data-testid="stMain"] .stNumberInput [data-testid="stWidgetLabel"] p,
    [data-testid="stMain"] .stSelectbox [data-testid="stWidgetLabel"] p,
    [data-testid="stMain"] .stDateInput [data-testid="stWidgetLabel"] p,
    [data-testid="stMain"] .stFileUploader [data-testid="stWidgetLabel"] p {
        color: #0F172A !important;
    }
    [data-testid="stMain"] label,
    section[data-testid="stMain"] label {
        color: #0F172A !important;
    }
    /* Base Web form etiketleri (selectbox / file uploader) */
    [data-testid="stMain"] [data-baseweb="form-control"] label,
    section[data-testid="stMain"] [data-baseweb="form-control"] label {
        color: #0F172A !important;
    }

    /* ─── st.tabs — global kontrast (#F4F6F9 üzerinde okunaklı) ─ */

    [data-testid="stTabs"] [data-baseweb="tab-list"],
    .stTabs [data-baseweb="tab-list"] {
        background:    transparent !important;
        border-bottom: 2px solid #CBD5E1 !important;
        gap:           6px !important;
        padding:       0 2px 0 0 !important;
    }

    /* Seçili olmayan sekme — açık gri arka planda net görünür */
    [data-testid="stTabs"] button[data-baseweb="tab"],
    .stTabs button[data-baseweb="tab"] {
        color:            var(--text-body) !important;
        background-color: #E2E8F0 !important;
        border:           1px solid #94A3B8 !important;
        border-radius:    8px 8px 0 0 !important;
        font-weight:      500 !important;
        font-size:        14px !important;
        margin-bottom:    -2px !important;
        padding:          10px 16px !important;
        transition:       background-color 0.15s ease, color 0.15s ease,
                          border-color 0.15s ease !important;
    }

    [data-testid="stTabs"] button[data-baseweb="tab"]:hover,
    .stTabs button[data-baseweb="tab"]:hover {
        background-color: #CBD5E1 !important;
        color:            var(--text-heading) !important;
        border-color:     #64748B !important;
    }

    /* Seçili sekme — beyaz panel + mavi vurgu (≈4.5:1 hedefi) */
    [data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"],
    .stTabs button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #FFFFFF !important;
        color:            var(--sf-blue) !important;
        font-weight:      600 !important;
        border-color:     #CBD5E1 !important;
        border-bottom-color: #FFFFFF !important;
        box-shadow:       0 1px 0 #FFFFFF !important;
    }

    /* role="tab" yedek (bazı sürümler) */
    [data-testid="stTabs"] [role="tab"]:not([aria-selected="true"]) {
        color: var(--text-body) !important;
    }
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        color:       var(--sf-blue) !important;
        font-weight: 600 !important;
    }

    /* ─── PAGE HEADER ──────────────────────────────────────── */

    .ld-page-header { margin-bottom: 28px; }

    .ld-page-title {
        font-size:   26px                    !important;
        font-weight: 700                     !important;
        color:       var(--text-heading)     !important;
        margin:      0 0 6px 0               !important;
        line-height: 1.2                     !important;
    }

    .ld-page-sub {
        font-size: 14px                  !important;
        color:     var(--text-meta)      !important;
        margin:    0                     !important;
    }

    .ld-settings-lead {
        font-size:   13px;
        color:       var(--text-meta);
        line-height: 1.55;
        margin:      0 0 20px 0;
        max-width:   44rem;
    }
    .ld-settings-lead code {
        font-size:     11px;
        padding:       1px 6px;
        border-radius: 4px;
        background:    rgba(1, 118, 211, 0.08);
        color:         var(--text-body);
    }

    /* ─── FORM FIELD LABELS (üst etiket + zorunlu *) ──────── */

    p.ld-field-label {
        font-size:   13px                        !important;
        font-weight: 600                        !important;
        color:       var(--field-label-on-light) !important;
        margin:      0 0 6px 0                  !important;
        line-height: 1.3                        !important;
        text-align:  left                       !important;
    }
    p.ld-field-label.ld-field-label--dark {
        color:       var(--field-label-on-dark)  !important;
    }
    span.ld-req {
        color:       var(--error)         !important;
        font-weight: 700                  !important;
        margin-left: 2px                 !important;
    }
    span.ld-field-hint {
        font-weight: 400                     !important;
        color:       var(--field-hint-on-light) !important;
        font-size:   12px                    !important;
        margin-left: 8px                     !important;
    }
    p.ld-field-label.ld-field-label--dark span.ld-field-hint {
        color:       var(--field-hint-on-dark) !important;
    }

    /* ─── DASHBOARD CARDS ──────────────────────────────────── */

    .ld-card {
        background:    #ffffff;
        border-radius: var(--radius-card);
        padding:       28px;
        border:        1px solid #E9EDF2;
        box-shadow:    0 1px 6px rgba(15,23,42,0.06);
        height:        100%;
        transition:    box-shadow 0.2s, transform 0.15s;
    }

    .ld-card:hover {
        box-shadow: 0 6px 22px rgba(15,23,42,0.11);
        transform:  translateY(-2px);
    }

    .ld-card-icon {
        width:         46px;
        height:        46px;
        border-radius: 10px;
        background:    #EFF6FF;
        display:       flex;
        align-items:   center;
        justify-content: center;
        font-size:     22px;
        margin-bottom: 18px;
    }

    .ld-card-icon.purple { background: #F3F0FF; }

    .ld-card-title {
        font-size:   16px;
        font-weight: 700;
        color:       var(--text-heading);
        margin:      0 0 10px 0;
    }

    .ld-card-desc {
        font-size:   13px;
        color:       var(--text-meta);
        line-height: 1.6;
        margin:      0 0 22px 0;
    }

    .ld-card-link {
        font-size:   13px;
        font-weight: 600;
        color:       #0176D3;
        display:     inline-flex;
        align-items: center;
        gap:         4px;
    }

    /* ─── METRIC CARDS ─────────────────────────────────────── */

    .ld-metric-grid {
        display:               grid;
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
        gap:                   16px;
        margin-bottom:         28px;
    }

    .ld-metric {
        background:    #ffffff;
        border-radius: var(--radius-panel);
        padding:       18px 20px;
        border:        1px solid #E9EDF2;
        box-shadow:    0 1px 4px rgba(15,23,42,0.05);
    }

    .ld-metric-label {
        font-size:      11px;
        color:          var(--text-meta);
        font-weight:    600;
        margin:         0 0 8px 0;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .ld-metric-value {
        font-size:   30px;
        font-weight: 700;
        color:       var(--text-heading);
        margin:      0;
        line-height: 1;
    }

    .ld-metric-accent { color: #0176D3; }

    /* ─── GLOBAL TABLE HEADER ─────────────────────────── */

    .ld-th {
        font-size:      11px;
        font-weight:    600;
        color:          var(--text-meta);
        text-transform: uppercase;
        letter-spacing: .05em;
        padding:        6px 0;
        margin:         0;
    }

    /* ─── GLOBAL INLINE PANELS ─────────────────────────── */

    .ld-del-panel {
        background:    #fff1f0;
        border:        1.5px solid #C2303044;
        border-radius: var(--radius-panel);
        padding:       16px 20px;
        margin:        10px 0;
    }

    .ld-edit-panel {
        background:    #f0f7ff;
        border:        1.5px solid #1A56DB33;
        border-radius: var(--radius-panel);
        padding:       18px 20px;
        margin:        6px 0 14px 0;
    }

    /* ─── PROJECT LIST ROW HOVER ───────────────────────── */

    section[data-testid="stMain"] .pj-row-hover {
        transition: background 0.15s;
    }

    section[data-testid="stMain"] .pj-row-hover:hover {
        background: #F8FAFF !important;
    }

    /* ─── SECTION CARD ─────────────────────────────────────── */

    .ld-section {
        background:    #ffffff;
        border-radius: var(--radius-card);
        padding:       24px 28px;
        border:        1px solid #E9EDF2;
        box-shadow:    0 1px 6px rgba(15,23,42,0.05);
        margin-bottom: 20px;
    }

    .ld-section-title {
        font-size:   15px;
        font-weight: 700;
        color:       var(--text-heading);
        margin:      0 0 16px 0;
    }

    /* ─── PLACEHOLDER PAGES ────────────────────────────────── */

    .ld-placeholder {
        background:    #ffffff;
        border-radius: var(--radius-card);
        padding:       72px 40px;
        text-align:    center;
        border:        1px solid #E9EDF2;
        box-shadow:    0 1px 6px rgba(15,23,42,0.05);
    }

    .ld-placeholder-icon {
        font-size:     52px;
        margin-bottom: 16px;
        line-height:   1;
    }

    .ld-placeholder-text {
        font-size:   17px;
        font-weight: 700;
        color:       var(--text-body);
        margin:      0 0 8px 0;
    }

    .ld-placeholder-sub {
        font-size: 14px;
        color:     #9CA3AF;
        margin:    0;
    }

    /* ─── ACTIVITY FEED ────────────────────────────────────── */

    .ld-activity-item {
        display:     flex;
        align-items: flex-start;
        gap:         12px;
        padding:     10px 0;
        border-bottom: 1px solid var(--border-light);
    }

    .ld-activity-item:last-child { border-bottom: none; }

    .ld-activity-dot {
        width:         8px;
        height:        8px;
        border-radius: 50%;
        background:    #0176D3;
        margin-top:    5px;
        flex-shrink:   0;
    }

    .ld-activity-name {
        font-size:   13px;
        font-weight: 600;
        color:       var(--text-heading);
        margin:      0 0 2px 0;
    }

    .ld-activity-meta {
        font-size: 11px;
        color:     var(--text-meta);
        margin:    0;
    }

    .ld-status-pill {
        display:       inline-block;
        padding:       2px 8px;
        border-radius: 999px;
        font-size:     10px;
        font-weight:   600;
        background:    #EFF6FF;
        color:         #0176D3;
        margin-top:    4px;
    }
    """


def login_css() -> str:
    """
    CSS injected ONLY by login_screen().
    Uses st.columns([42, 58]) layout.
    """
    return """
    /* ─── FULL-PAGE OVERFLOW LOCK ─────────────────────────── */

    html, body {
        margin:   0 !important;
        padding:  0 !important;
        height:   100% !important;
        overflow: hidden !important;
    }

    .stApp {
        overflow: hidden !important;
        height:   100vh  !important;
    }

    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    section.main {
        overflow:   hidden  !important;
        padding:    0       !important;
        height:     100vh   !important;
        max-height: 100vh   !important;
    }

    .main .block-container,
    [data-testid="stMainBlockContainer"] {
        padding:    0      !important;
        max-width:  100%   !important;
        height:     100vh  !important;
        overflow:   hidden !important;
    }

    [data-testid="stMainBlockContainer"] > div,
    [data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] {
        height:   100vh  !important;
        overflow: hidden !important;
        padding:  0      !important;
        margin:   0      !important;
    }

    /* ─── COLUMN WRAPPER ──────────────────────────────────── */

    [data-testid="stHorizontalBlock"] {
        gap:        0       !important;
        height:     100vh   !important;
        max-height: 100vh   !important;
        align-items: stretch !important;
        padding:    0       !important;
        margin:     0       !important;
        overflow:   hidden  !important;
    }

    [data-testid="stColumn"] {
        padding:  0       !important;
        overflow: hidden  !important;
    }

    [data-testid="stColumn"] > div,
    [data-testid="stColumn"] > [data-testid="stVerticalBlockBorderWrapper"],
    [data-testid="stColumn"] [data-testid="stVerticalBlockBorderWrapper"],
    [data-testid="stColumn"] [data-testid="stVerticalBlock"] {
        height:     100%   !important;
        min-height: 100vh  !important;
        overflow:   hidden !important;
        padding:    0      !important;
    }

    /* ─── LEFT COLUMN — dark navy ─────────────────────────── */

    [data-testid="stColumn"]:first-child {
        background: var(--navy) !important;
    }

    [data-testid="stColumn"]:first-child [data-testid="stVerticalBlock"] {
        display:         flex        !important;
        flex-direction:  column      !important;
        justify-content: center      !important;
        align-items:     center      !important;
        gap:             20px        !important;
        padding:         48px 40px   !important;
        min-height:      100vh       !important;
        height:          100vh       !important;
    }

    /* ─── RIGHT COLUMN — pure white ───────────────────────── */

    [data-testid="stColumn"]:nth-child(2) {
        background: #ffffff !important;
    }

    [data-testid="stColumn"]:nth-child(2) [data-testid="stVerticalBlock"] {
        display:         flex      !important;
        flex-direction:  column    !important;
        justify-content: center    !important;
        align-items:     center    !important;
        padding:         48px 60px !important;
        min-height:      100vh     !important;
        height:          100vh     !important;
    }

    [data-testid="stColumn"]:nth-child(2) [data-testid="stVerticalBlock"] > div {
        max-width: 360px !important;
        width:     100%  !important;
    }

    /* ─── LEFT PANEL — logo (HTML img; st.image tam ekran butonu yok) ─── */

    [data-testid="stColumn"]:first-child .ld-login-logo-wrap {
        background:    #ffffff;
        border-radius: 16px;
        padding:       12px 16px;
        margin:        0 auto;
        display:       inline-block;
        box-shadow:
            0 1px 2px rgba(15, 23, 42, 0.06),
            0 8px 28px rgba(15, 23, 42, 0.22),
            0 0 0 1px rgba(255, 255, 255, 0.14) inset;
        transition:    box-shadow 0.2s ease;
    }

    [data-testid="stColumn"]:first-child [data-testid="stElementContainer"]:has(.ld-login-logo-wrap),
    [data-testid="stColumn"]:first-child [data-testid="stMarkdownContainer"]:has(.ld-login-logo-wrap) {
        display:         flex                    !important;
        justify-content: center                  !important;
        width:           100%                    !important;
    }

    /* Tagline: blok ortada, iki satır */
    [data-testid="stColumn"]:first-child [data-testid="stElementContainer"]:has(.ld-tagline),
    [data-testid="stColumn"]:first-child [data-testid="stMarkdownContainer"]:has(.ld-tagline) {
        display:         flex                    !important;
        justify-content: center                  !important;
        width:           100%                    !important;
    }
    .ld-tagline {
        max-width:     min(480px, 96vw);
        width:         100%;
        margin:        0 auto;
        text-align:    center;
        font-size:     13px;
        line-height:   1.5;
        color:         #607088;
        hyphens:       none;
    }

    /* ─── FORM HEADINGS ───────────────────────────────────── */

    .ld-form-title {
        font-size:   24px;
        font-weight: 700;
        color:       var(--text-main);
        margin:      0 0 4px 0;
        line-height: 1.25;
    }

    .ld-form-sub {
        font-size: 13px;
        color:     var(--text-soft);
        margin:    0 0 20px 0;
    }

    .ld-error {
        display:       flex;
        align-items:   flex-start;
        gap:           8px;
        font-size:     12.5px;
        color:         var(--error);
        background:    #FFF4F3;
        border:        1px solid #F9BDBB;
        border-left:   4px solid var(--error);
        border-radius: 4px;
        padding:       9px 12px;
        margin-bottom: 14px;
        line-height:   1.4;
    }

    .ld-form-footer {
        text-align:     center;
        font-size:      11px;
        color:          #938E8A;
        margin-top:     20px;
        letter-spacing: 0.02em;
    }

    /* ─── STREAMLIT FORM WIDGET OVERRIDES ─────────────────── */

    [data-testid="stForm"] {
        border:     none        !important;
        background: transparent !important;
        padding:    0           !important;
    }

    .stTextInput label p,
    .stTextInput label {
        font-size:   13px    !important;
        font-weight: 600     !important;
        color:       #3E3E3C !important;
    }

    .stTextInput > div > div {
        border:        1px solid var(--border) !important;
        border-radius: 4px                     !important;
        background:    #ffffff                 !important;
        box-shadow:    none                    !important;
        transition:    border-color 0.15s, box-shadow 0.15s !important;
    }

    .stTextInput > div > div:focus-within {
        border-color: var(--sf-blue)  !important;
        box-shadow:   0 0 0 3px var(--sf-focus) !important;
        background:   #ffffff        !important;
    }

    .stTextInput input {
        font-size:  14px              !important;
        color:      var(--text-main)  !important;
        background: transparent       !important;
    }

    [data-testid="stFormSubmitButton"] > button,
    .stFormSubmitButton > button {
        width:          100%            !important;
        background:     var(--sf-blue)  !important;
        color:          #ffffff         !important;
        border:         none            !important;
        border-radius:  4px             !important;
        font-size:      14px            !important;
        font-weight:    600             !important;
        height:         40px            !important;
        letter-spacing: 0.025em         !important;
        transition:     background 0.15s ease !important;
        box-shadow:     none            !important;
        margin-top:     6px             !important;
        cursor:         pointer         !important;
    }

    [data-testid="stFormSubmitButton"] > button:hover,
    .stFormSubmitButton > button:hover {
        background: var(--sf-blue-hover) !important;
        border:     none                 !important;
        color:      #ffffff              !important;
    }

    [data-testid="stFormSubmitButton"] > button:active {
        background: #032D60 !important;
    }

    [data-testid="InputInstructions"] {
        display: none !important;
    }

    /* ─── MOBILE ──────────────────────────────────────────── */

    @media screen and (max-width: 768px) {
        [data-testid="stColumn"]:first-child {
            display: none !important;
        }

        [data-testid="stColumn"]:nth-child(2) [data-testid="stVerticalBlock"] {
            padding: 40px 24px !important;
        }

        [data-testid="stColumn"]:nth-child(2) [data-testid="stVerticalBlock"] > div {
            max-width: 100% !important;
        }
    }
    """


# ──────────────────────────────────────────────────────────────
# FORM LABEL HELPER  (üst etiket + kırmızı * — pilot formlar)
# ──────────────────────────────────────────────────────────────

def render_field_label(
    text: str,
    *,
    required: bool = False,
    hint: str | None = None,
    variant: Literal["light", "dark"] = "light",
) -> None:
    """
    Salesforce tarzı üst etiket; zorunlu alanlarda kırmızı *.
    Widget'ta label_visibility='collapsed' kullanın.

    ``variant``:
      - ``light`` — beyaz / açık gri panel (varsayılan).
      - ``dark`` — ``st.dialog`` ve koyu yüzey; kontrast için açık metin rengi.
    """
    import streamlit as st

    mod = " ld-field-label--dark" if variant == "dark" else ""
    req = "<span class='ld-req' aria-hidden='true'>*</span>" if required else ""
    hint_html = (
        f"<span class='ld-field-hint'>{hint}</span>" if hint else ""
    )
    st.markdown(
        f"<p class='ld-field-label{mod}'>{text}{req}{hint_html}</p>",
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────────────────────
# PAGE HEADER HELPERS  (slot pattern)
# ──────────────────────────────────────────────────────────────

def page_header(title: str, subtitle: str = "") -> None:
    """Render the standard page header block (no action button)."""
    import streamlit as st
    sub = f"<p class='ld-page-sub'>{subtitle}</p>" if subtitle else ""
    st.markdown(
        f"<div class='ld-page-header'>"
        f"<h1 class='ld-page-title'>{title}</h1>"
        f"{sub}"
        f"</div>",
        unsafe_allow_html=True,
    )


def page_header_with_action(
    title: str,
    subtitle: str,
    action_label: str,
    action_key: str,
) -> bool:
    """
    Render page header with right-aligned action button on the same visual row.
    Returns True if the action button was clicked.
    """
    import streamlit as st
    c_left, c_right = st.columns([5, 1.4])
    with c_left:
        sub = f"<p class='ld-page-sub'>{subtitle}</p>" if subtitle else ""
        st.markdown(
            f"<div class='ld-page-header'>"
            f"<h1 class='ld-page-title'>{title}</h1>"
            f"{sub}"
            f"</div>",
            unsafe_allow_html=True,
        )
    with c_right:
        st.markdown("<div style='padding-top:14px;'>", unsafe_allow_html=True)
        clicked = st.button(action_label, key=action_key, width="stretch")
        st.markdown("</div>", unsafe_allow_html=True)
    return clicked

def load_custom_css():
    import streamlit as st
    st.markdown("""
<style>
    /* ── Google Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400..700;1,400..700&family=Inter:wght@400;500;600;700&display=swap');

    /* ── Root Variables ── */
    :root {
        --bg-warm: #f5f5f0;
        --bg-card: #ffffff;
        --primary: #2e7d32;
        --primary-light: #4caf50;
        --primary-hover: #1b5e20;
        --accent-blue: #29b6f6;
        --text-dark: #1a1a1a;
        --text-muted: #6b7280;
        --text-light: #9ca3af;
        --border: #e5e7e0;
        --shadow-sm: 0 1px 3px rgba(0,0,0,0.06);
        --shadow-md: 0 4px 16px rgba(0,0,0,0.08);
        --shadow-lg: 0 8px 32px rgba(0,0,0,0.10);
        --radius-sm: 12px;
        --radius-md: 20px;
        --radius-lg: 28px;
        --radius-pill: 999px;
    }

    /* ── Global Background ── */
    .stApp, .main, [data-testid="stAppViewContainer"] {
        background-color: var(--bg-warm) !important;
    }
    .block-container {
        max-width: 720px !important;
        padding-top: 2rem !important;
        padding-bottom: 4rem !important;
    }

    /* ── Hide Streamlit chrome (keep sidebar toggle visible) ── */
    #MainMenu, footer, [data-testid="stToolbar"] { display: none !important; }
    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }

    /* ── Typography ── */
    h1, h2, h3 { font-family: 'Lora', Georgia, serif !important; color: var(--text-dark) !important; }
    p, label, li { font-family: 'Inter', -apple-system, sans-serif !important; }
    h1 { font-size: 2.4rem !important; letter-spacing: -0.02em !important; }

    /* ── Card-style containers ── */
    [data-testid="stVerticalBlock"] > div > div[data-testid="stExpander"] {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-md) !important;
        box-shadow: var(--shadow-sm);
    }

    /* ── File uploader area ── */
    [data-testid="stFileUploader"] section {
        border-radius: var(--radius-md) !important;
        border: 2px dashed var(--border) !important;
        background: var(--bg-card) !important;
        padding: 2rem 1.5rem !important;
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
    }
    [data-testid="stFileUploader"] section:hover {
        border-color: var(--primary-light) !important;
        box-shadow: var(--shadow-md) !important;
    }
    [data-testid="stFileUploader"] small {
        color: var(--text-muted) !important;
    }
    /* Fix: nút Browse bị hiện chữ đè */
    [data-testid="stFileUploader"] button {
        border-radius: var(--radius-pill) !important;
        background: var(--primary) !important;
        color: white !important;
        border: none !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
        min-height: 38px !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stFileUploader"] button:hover {
        background: var(--primary-hover) !important;
    }

    /* ── Text inputs ── */
    input[type="text"], input[type="password"],
    [data-testid="stTextInput"] input {
        border-radius: var(--radius-sm) !important;
        border: 1.5px solid var(--border) !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.95rem !important;
        color: var(--text-dark) !important;
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
        background: var(--bg-card) !important;
    }
    input[type="text"]::placeholder, input[type="password"]::placeholder {
        color: var(--text-muted) !important;
        opacity: 0.7 !important;
    }
    input[type="text"]:focus, input[type="password"]:focus,
    [data-testid="stTextInput"] input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(46,125,50,0.12) !important;
    }

    /* ── Primary button (Convert) ── */
    [data-testid="stBaseButton-primary"],
    button[kind="primary"] {
        background: var(--primary) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-pill) !important;
        padding: 0.85rem 2rem !important;
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        letter-spacing: 0.01em !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 14px rgba(46,125,50,0.25) !important;
    }
    [data-testid="stBaseButton-primary"]:hover,
    button[kind="primary"]:hover {
        background: var(--primary-hover) !important;
        box-shadow: 0 6px 20px rgba(46,125,50,0.35) !important;
        transform: translateY(-1px) !important;
    }

    /* ── Download button ── */
    [data-testid="stDownloadButton"] button {
        background: var(--bg-card) !important;
        color: var(--primary) !important;
        border: 2px solid var(--primary) !important;
        border-radius: var(--radius-pill) !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stDownloadButton"] button:hover {
        background: var(--primary) !important;
        color: white !important;
    }

    /* ── Radio buttons (mode selector) ── */
    [data-testid="stRadio"] > div {
        gap: 0.5rem !important;
    }
    [data-testid="stRadio"] label {
        background: var(--bg-card) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.6rem 1rem !important;
        transition: all 0.25s ease !important;
        cursor: pointer !important;
    }
    [data-testid="stRadio"] label:hover {
        border-color: var(--primary-light) !important;
        box-shadow: var(--shadow-sm) !important;
    }

    /* ── Alerts (success, warning, error) ── */
    [data-testid="stAlert"] {
        border-radius: var(--radius-sm) !important;
        border-left-width: 4px !important;
    }

    /* ── Text area (preview) ── */
    [data-testid="stTextArea"] textarea {
        border-radius: var(--radius-md) !important;
        border: 1.5px solid var(--border) !important;
        background: var(--bg-card) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.9rem !important;
        line-height: 1.7 !important;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: var(--bg-card) !important;
        border-right: 1px solid var(--border) !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {
        font-size: 1.2rem !important;
    }

    /* ── Spinner ── */
    [data-testid="stSpinner"] {
        color: var(--primary) !important;
    }

    /* ── Divider ── */
    hr {
        border-color: var(--border) !important;
        margin: 2rem 0 !important;
    }

    /* ── Smooth scrolling ── */
    html { scroll-behavior: smooth; }

    /* ── Custom hero badge ── */
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(46,125,50,0.08);
        color: var(--primary);
        border: 1px solid rgba(46,125,50,0.2);
        border-radius: var(--radius-pill);
        padding: 6px 16px;
        font-size: 0.82rem;
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        letter-spacing: 0.02em;
        margin-bottom: 1rem;
    }
    .hero-subtitle {
        color: var(--text-muted);
        font-family: 'Inter', sans-serif;
        font-size: 1.05rem;
        line-height: 1.65;
        max-width: 540px;
    }
    .format-chips {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 0.8rem;
    }
    .format-chip {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-pill);
        padding: 5px 14px;
        font-size: 0.78rem;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        color: var(--text-muted);
        transition: all 0.2s ease;
    }
    .format-chip:hover {
        border-color: var(--primary-light);
        color: var(--primary);
        background: rgba(46,125,50,0.04);
    }
    .section-label {
        font-family: 'Inter', sans-serif;
        font-size: 0.82rem;
        font-weight: 600;
        color: var(--text-muted);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.6rem;
    }
    .result-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        padding: 1.5rem;
        box-shadow: var(--shadow-sm);
        margin-top: 1rem;
    }
    .result-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 1rem;
        font-family: 'Inter', sans-serif;
    }
    .result-icon {
        width: 36px;
        height: 36px;
        background: rgba(46,125,50,0.1);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
    }
    .result-title {
        font-weight: 600;
        color: var(--text-dark);
        font-size: 0.95rem;
    }
    .result-meta {
        color: var(--text-light);
        font-size: 0.78rem;
    }
    
    /* ── Mobile Responsiveness ── */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        h1 {
            font-size: 1.8rem !important;
        }
        .hero-subtitle {
            font-size: 0.95rem;
        }
        .format-chips {
            gap: 6px;
        }
        .format-chip {
            padding: 4px 10px;
            font-size: 0.7rem;
        }
        .hero-badge {
            font-size: 0.75rem;
            padding: 4px 12px;
        }
    }
</style>
""", unsafe_allow_html=True)

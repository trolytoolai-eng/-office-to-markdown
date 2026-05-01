import streamlit as st
import os
import re
import tempfile
import subprocess
import json
from datetime import datetime

try:
    from markitdown import MarkItDown
except ImportError:
    st.error("Thư viện markitdown chưa được cài đặt.")
    st.stop()

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api.proxies import GenericProxyConfig, WebshareProxyConfig
except ImportError:
    YouTubeTranscriptApi = None
    GenericProxyConfig = None
    WebshareProxyConfig = None

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Office to Markdown",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="auto",
)

# ─────────────────────────────────────────────
# CUSTOM CSS — Eco-Modern Design System
# Inspired by "Don't Make Me Think" principles
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Google Fonts ── */
    @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=Inter:wght@400;500;600;700&display=swap');

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
    h1, h2, h3 { font-family: 'DM Serif Display', Georgia, serif !important; color: var(--text-dark) !important; }
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


# Load proxy config locally
proxy_config_file = "proxy_config.json"
try:
    if os.path.exists(proxy_config_file):
        with open(proxy_config_file, "r") as f:
            proxy_config = json.load(f)
    else:
        proxy_config = {}
except Exception:
    proxy_config = {}

# Variables initialized globally from config
proxy_mode = proxy_config.get("proxy_mode", "Không dùng (Local)")
ws_user = proxy_config.get("ws_user", "")
ws_pass = proxy_config.get("ws_pass", "")
custom_proxy_raw = proxy_config.get("custom_proxy_raw", "")
# ─────────────────────────────────────────────
# HERO SECTION
# ─────────────────────────────────────────────
st.markdown('<div class="hero-badge">✨ Powered by Microsoft MarkItDown</div>', unsafe_allow_html=True)
st.markdown("# Office to Markdown")
st.markdown(
    '<p class="hero-subtitle">'
    'Chuyển đổi tài liệu Office và video YouTube thành Markdown '
    'chỉ trong vài giây'
    '</p>',
    unsafe_allow_html=True
)

# Format chips
formats = ["PDF", "DOCX", "XLSX", "PPTX", "HTML", "CSV", "JSON", "XML", "EPUB", "ZIP", "YouTube"]
chips_html = '<div class="format-chips">' + ''.join(
    [f'<span class="format-chip">{f}</span>' for f in formats]
) + '</div>'
st.markdown(chips_html, unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────
# MODE SELECTOR — One thing at a time
# ─────────────────────────────────────────────
st.markdown('<p class="section-label">Chọn nguồn dữ liệu</p>', unsafe_allow_html=True)
mode = st.radio(
    "mode_selector",
    ["📁  Upload File", "🔗  YouTube URL"],
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("")  # spacer

# ─────────────────────────────────────────────
# INPUT AREA
# ─────────────────────────────────────────────
uploaded_file = None
youtube_url = ""

if mode == "📁  Upload File":
    uploaded_file = st.file_uploader(
        "Kéo thả hoặc chọn file cần chuyển đổi",
        help="DOCX, PDF, EPUB, XLSX, PPTX, HTML, CSV, JSON, XML, ZIP"
    )
else:
    youtube_url = st.text_input(
        "Dán link YouTube",
        placeholder="https://www.youtube.com/watch?v=...",
        label_visibility="visible"
    )
    
    with st.expander("⚙️ Cấu hình Proxy (Nếu bị YouTube chặn)"):
        st.caption("Sử dụng khi bị giới hạn IP truy cập Youtube.")
        
        # Determine index for radio button
        radio_options = ["Không dùng (Local)", "Webshare", "Custom URL"]
        try:
            default_index = radio_options.index(proxy_mode)
        except ValueError:
            default_index = 0
            
        new_proxy_mode = st.radio(
            "Loại Proxy:",
            radio_options,
            index=default_index,
            horizontal=True
        )

        new_ws_user = ws_user
        new_ws_pass = ws_pass
        new_custom_proxy_raw = custom_proxy_raw

        if new_proxy_mode == "Webshare":
            st.markdown(
                "[webshare.io](https://www.webshare.io/) → gói **Residential** "
                "→ [Proxy Settings](https://proxy2.webshare.io/proxy/settings)"
            )
            col1, col2 = st.columns(2)
            with col1:
                new_ws_user = st.text_input("Username", value=ws_user, placeholder="webshare_username")
            with col2:
                new_ws_pass = st.text_input("Password", value=ws_pass, type="password")
            if new_ws_user and new_ws_pass:
                st.success("✅ Proxy ready")
        elif new_proxy_mode == "Custom URL":
            new_custom_proxy_raw = st.text_input(
                "Proxy",
                value=custom_proxy_raw,
                placeholder="IP:PORT:USER:PASS",
                type="password"
            )
            if new_custom_proxy_raw:
                st.success("✅ Proxy ready")
                
        if st.button("💾 Lưu cấu hình (Dùng cho lần sau)"):
            try:
                with open(proxy_config_file, "w") as f:
                    json.dump({
                        "proxy_mode": new_proxy_mode,
                        "ws_user": new_ws_user,
                        "ws_pass": new_ws_pass,
                        "custom_proxy_raw": new_custom_proxy_raw
                    }, f)
                st.toast("✅ Đã lưu cấu hình proxy thành công!")
                
                # Update current session variables immediately
                proxy_mode = new_proxy_mode
                ws_user = new_ws_user
                ws_pass = new_ws_pass
                custom_proxy_raw = new_custom_proxy_raw
            except Exception as e:
                st.error(f"Không thể lưu cấu hình: {e}")

st.markdown("")  # spacer


# ─────────────────────────────────────────────
# UTILITY FUNCTIONS
# ─────────────────────────────────────────────
def sanitize_filename(name):
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = re.sub(r'\s+', '_', name.strip())
    return name[:80]

def make_output_filename(source_name, source_type="file"):
    date_str = datetime.now().strftime("%Y%m%d")
    clean_name = sanitize_filename(source_name)
    prefix = "YT" if source_type == "youtube" else "File"
    return f"{prefix}_{clean_name}_{date_str}.md"

def extract_video_id(url):
    for pattern in [
        r'(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'(?:embed/)([a-zA-Z0-9_-]{11})',
        r'(?:shorts/)([a-zA-Z0-9_-]{11})',
    ]:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def parse_proxy_input(raw):
    raw = raw.strip()
    if not raw:
        return ""
    if raw.startswith(("http://", "https://", "socks")):
        return raw
    parts = raw.split(":")
    if len(parts) == 4:
        host, port, user, password = parts
        return f"http://{user}:{password}@{host}:{port}"
    if "@" in raw:
        try:
            creds, server = raw.rsplit("@", 1)
            return f"http://{creds}@{server}"
        except ValueError:
            pass
    return f"http://{raw}"

def get_youtube_metadata(url):
    import requests as req
    title = ""
    description = ""
    try:
        oembed_url = f"https://www.youtube.com/oembed?url={url}&format=json"
        resp = req.get(oembed_url, timeout=10)
        if resp.status_code == 200:
            title = resp.json().get("title", "")
    except Exception:
        pass
    if not title:
        try:
            r = subprocess.run(
                ["python", "-m", "yt_dlp", "--dump-json", "--no-download", "--skip-download", url],
                capture_output=True, text=True, timeout=30, encoding='utf-8'
            )
            if r.returncode == 0 and r.stdout.strip():
                meta = json.loads(r.stdout)
                title = meta.get("title", "")
                description = meta.get("description", "")
        except Exception:
            pass
    return title, description

def create_ytt_api(p_mode, p_user, p_pass, p_custom):
    if p_mode == "Webshare" and p_user and p_pass and WebshareProxyConfig:
        import urllib.parse
        enc_user = urllib.parse.quote(p_user, safe='')
        enc_pass = urllib.parse.quote(p_pass, safe='')
        return YouTubeTranscriptApi(proxy_config=WebshareProxyConfig(
            proxy_username=enc_user, proxy_password=enc_pass,
        ))
    elif p_mode == "Custom URL" and p_custom and GenericProxyConfig:
        url = parse_proxy_input(p_custom)
        return YouTubeTranscriptApi(proxy_config=GenericProxyConfig(
            http_url=url, https_url=url,
        ))
    return YouTubeTranscriptApi()

def get_youtube_transcript(url, p_mode, p_user, p_pass, p_custom):
    video_id = extract_video_id(url)
    if not video_id:
        return None, None, "Không thể trích xuất Video ID."
    title, description = get_youtube_metadata(url)
    if not YouTubeTranscriptApi:
        return None, title, "youtube_transcript_api chưa được cài."
    try:
        transcript = create_ytt_api(p_mode, p_user, p_pass, p_custom).fetch(video_id)
        text = ' '.join([s.text for s in transcript.snippets])
    except Exception as e:
        msg = str(e)
        if any(k in msg for k in ["RequestBlocked", "IpBlocked", "429"]):
            return None, title, (
                f"🚫 IP bị YouTube chặn.\n\n"
                "Mở **sidebar ⚙️** → cấu hình Proxy để vượt qua."
            )
        return None, title, f"Lỗi: {msg}"

    parts = [f"# {title}" if title else "# YouTube Video", "", f"**URL:** {url}", ""]
    if description:
        parts += ["## Description", description, ""]
    parts += ["## Transcript", "", text]
    return '\n'.join(parts), title, None


# ─────────────────────────────────────────────
# CONVERT BUTTON & RESULTS
# ─────────────────────────────────────────────
if st.button("Convert to Markdown  →", type="primary", use_container_width=True):
    if mode == "📁  Upload File" and not uploaded_file:
        st.warning("Vui lòng chọn một file để chuyển đổi.")
    elif mode == "🔗  YouTube URL" and not youtube_url:
        st.warning("Vui lòng dán link YouTube.")
    else:
        with st.spinner("Đang chuyển đổi…"):
            try:
                result_content = ""
                output_filename = "output.md"

                if mode == "📁  Upload File" and uploaded_file:
                    md = MarkItDown()
                    suffix = os.path.splitext(uploaded_file.name)[1]
                    base_name = os.path.splitext(uploaded_file.name)[0]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        tmp.write(uploaded_file.getbuffer())
                        tmp_path = tmp.name
                    result = md.convert(tmp_path)
                    result_content = result.text_content
                    os.unlink(tmp_path)
                    output_filename = make_output_filename(base_name, "file")

                elif mode == "🔗  YouTube URL" and youtube_url:
                    content, video_title, error = get_youtube_transcript(
                        youtube_url, new_proxy_mode, new_ws_user, new_ws_pass, new_custom_proxy_raw
                    )
                    if error:
                        st.error(f"❌ {error}")
                        st.stop()
                    result_content = content
                    name = video_title or extract_video_id(youtube_url) or "video"
                    output_filename = make_output_filename(name, "youtube")

                # ── Results card ──
                st.markdown(
                    '<div class="result-card">'
                    '<div class="result-header">'
                    '<div class="result-icon">✅</div>'
                    '<div><div class="result-title">Chuyển đổi thành công!</div>'
                    f'<div class="result-meta">{output_filename}</div>'
                    '</div></div></div>',
                    unsafe_allow_html=True
                )

                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        label="⬇️  Tải file .md",
                        data=result_content,
                        file_name=output_filename,
                        mime="text/markdown",
                        use_container_width=True
                    )
                with col2:
                    if st.button("📋  Copy nội dung", use_container_width=True):
                        st.toast("Đã copy!")

                st.markdown('<p class="section-label" style="margin-top:1.5rem">Xem trước nội dung</p>', unsafe_allow_html=True)
                st.text_area(
                    "preview",
                    value=result_content,
                    height=400,
                    label_visibility="collapsed"
                )

            except Exception as e:
                st.error(f"❌ Đã xảy ra lỗi: {str(e)}")

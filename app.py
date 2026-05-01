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
    st.error("Thư viện markitdown chưa được cài đặt. Vui lòng kiểm tra lại.")
    st.stop()

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api.proxies import GenericProxyConfig
except ImportError:
    YouTubeTranscriptApi = None
    GenericProxyConfig = None

st.set_page_config(page_title="Office to Markdown", page_icon="📝")

# --- Sidebar: Proxy Settings ---
with st.sidebar:
    st.header("⚙️ Cài đặt Proxy")
    st.caption(
        "Khi deploy lên cloud (Streamlit Cloud, AWS...), YouTube sẽ chặn IP. "
        "Nhập proxy để vượt qua giới hạn này. Bỏ trống nếu dùng trên máy cá nhân."
    )
    proxy_url = st.text_input(
        "Proxy URL",
        placeholder="http://user:pass@proxy-host:port",
        help="Hỗ trợ HTTP/HTTPS/SOCKS proxy. Ví dụ: http://user:pass@p.webshare.io:80",
        type="password"
    )
    if proxy_url:
        st.success("✅ Proxy đã được cấu hình.")
    else:
        st.info("ℹ️ Không dùng proxy (phù hợp chạy local).")

st.markdown("<h1>Office to Markdown</h1>", unsafe_allow_html=True)
st.markdown("### 📄 Word, Excel, PDF ➡️ **Markdown (M↓)**")

# --- Chọn chế độ ---
mode = st.radio(
    "Chọn cách chuyển đổi:",
    ["📁 Upload File", "🔗 YouTube URL"],
    horizontal=True
)

uploaded_file = None
youtube_url = ""

if mode == "📁 Upload File":
    uploaded_file = st.file_uploader(
        "Upload a file to convert",
        help="Supported: DOCX, PDF, EPUB, XLSX, PPTX, HTML, CSV, JSON, XML, ZIP"
    )
else:
    youtube_url = st.text_input(
        "Enter a YouTube URL",
        placeholder="https://www.youtube.com/watch?v=...",
        help="Dán link YouTube vào đây để lấy transcript"
    )


def sanitize_filename(name):
    """Loại bỏ ký tự đặc biệt, giữ lại tên file sạch."""
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = re.sub(r'\s+', '_', name.strip())
    name = name[:80]  # Giới hạn độ dài
    return name


def make_output_filename(source_name, source_type="file"):
    """Tạo tên file output khoa học: [nguồn]_[tên gốc]_[ngày].md"""
    date_str = datetime.now().strftime("%Y%m%d")
    clean_name = sanitize_filename(source_name)
    if source_type == "youtube":
        return f"YT_{clean_name}_{date_str}.md"
    else:
        return f"File_{clean_name}_{date_str}.md"


def extract_video_id(url):
    """Trích xuất video ID từ URL YouTube."""
    patterns = [
        r'(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})',
        r'(?:embed/)([a-zA-Z0-9_-]{11})',
        r'(?:shorts/)([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def get_youtube_metadata(url):
    """Lấy metadata (title, description) bằng yt-dlp."""
    title = ""
    description = ""
    try:
        meta_cmd = [
            "python", "-m", "yt_dlp",
            "--dump-json", "--no-download",
            "--skip-download",
            url
        ]
        meta_result = subprocess.run(
            meta_cmd, capture_output=True, text=True, timeout=30, encoding='utf-8'
        )
        if meta_result.returncode == 0 and meta_result.stdout.strip():
            meta = json.loads(meta_result.stdout)
            title = meta.get("title", "")
            description = meta.get("description", "")
    except Exception:
        pass
    return title, description


def create_ytt_api(proxy_url_str):
    """Tạo YouTubeTranscriptApi instance, có hoặc không có proxy."""
    if proxy_url_str and GenericProxyConfig is not None:
        proxy_config = GenericProxyConfig(
            http_url=proxy_url_str,
            https_url=proxy_url_str,
        )
        return YouTubeTranscriptApi(proxy_config=proxy_config)
    else:
        return YouTubeTranscriptApi()


def get_youtube_transcript(url, proxy_url_str=""):
    """Lấy transcript YouTube bằng youtube_transcript_api + metadata bằng yt-dlp."""
    video_id = extract_video_id(url)
    if not video_id:
        return None, None, "Không thể trích xuất Video ID từ URL."

    # Lấy metadata
    title, description = get_youtube_metadata(url)

    # Lấy transcript bằng youtube_transcript_api
    if YouTubeTranscriptApi is None:
        return None, title, "Thư viện youtube_transcript_api chưa được cài đặt."

    try:
        ytt_api = create_ytt_api(proxy_url_str)
        transcript = ytt_api.fetch(video_id)
        transcript_text = ' '.join([snippet.text for snippet in transcript.snippets])
    except Exception as e:
        error_msg = str(e)
        if "RequestBlocked" in error_msg or "IpBlocked" in error_msg or "429" in error_msg:
            return None, title, (
                f"🚫 IP bị YouTube chặn: {error_msg}\n\n"
                "**Cách khắc phục:** Mở thanh bên trái ⚙️ Cài đặt Proxy → nhập proxy URL.\n"
                "Bạn có thể dùng dịch vụ proxy miễn phí/trả phí như Webshare, ProxyScrape..."
            )
        return None, title, f"Không lấy được transcript: {error_msg}"

    # Ghép thành Markdown
    md_parts = []
    md_parts.append(f"# {title}" if title else "# YouTube Video")
    md_parts.append("")
    md_parts.append(f"**URL:** {url}")
    md_parts.append("")
    if description:
        md_parts.append("## Description")
        md_parts.append(description)
        md_parts.append("")
    md_parts.append("## Transcript")
    md_parts.append("")
    md_parts.append(transcript_text)

    return '\n'.join(md_parts), title, None


if st.button("Convert to Markdown", type="primary", use_container_width=True):
    if mode == "📁 Upload File" and not uploaded_file:
        st.warning("⚠️ Vui lòng tải lên một file.")
    elif mode == "🔗 YouTube URL" and not youtube_url:
        st.warning("⚠️ Vui lòng nhập link YouTube.")
    else:
        with st.spinner("Đang chuyển đổi sang Markdown..."):
            try:
                result_content = ""
                output_filename = "output.md"

                if mode == "📁 Upload File" and uploaded_file:
                    md = MarkItDown()
                    suffix = os.path.splitext(uploaded_file.name)[1]
                    base_name = os.path.splitext(uploaded_file.name)[0]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                        tmp_file.write(uploaded_file.getbuffer())
                        tmp_path = tmp_file.name

                    result = md.convert(tmp_path)
                    result_content = result.text_content
                    os.unlink(tmp_path)
                    output_filename = make_output_filename(base_name, "file")

                elif mode == "🔗 YouTube URL" and youtube_url:
                    content, video_title, error = get_youtube_transcript(youtube_url, proxy_url)
                    if error:
                        st.error(f"❌ {error}")
                        st.stop()
                    result_content = content
                    name_source = video_title if video_title else extract_video_id(youtube_url) or "video"
                    output_filename = make_output_filename(name_source, "youtube")

                st.success("✅ Chuyển đổi thành công!")

                st.download_button(
                    label=f"⬇️ Tải file: {output_filename}",
                    data=result_content,
                    file_name=output_filename,
                    mime="text/markdown",
                    use_container_width=True
                )

                st.markdown("### Kết quả xem trước:")
                st.text_area("Output", value=result_content, height=400, label_visibility="collapsed")

            except Exception as e:
                st.error(f"❌ Đã xảy ra lỗi: {str(e)}")

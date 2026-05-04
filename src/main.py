import streamlit as st
import os
import sys
import tempfile

# Thêm thư mục gốc (ConvertToMD) vào sys.path để python nhận diện được package src
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from src.config.settings import load_config
from src.ui.styles import load_custom_css
from src.ui.components import render_hero, render_proxy_config, render_ai_config, render_results
from src.core.converter import convert_file, format_alt_text
from src.core.youtube import get_youtube_transcript
from src.utils.helpers import make_output_filename, extract_video_id

def main():
    st.set_page_config(
        page_title="Office to Markdown",
        page_icon="📝",
        layout="centered",
        initial_sidebar_state="auto",
    )
    
    load_custom_css()
    app_config = load_config()
    
    render_hero()
    
    st.markdown('<p class="section-label">Chọn nguồn dữ liệu</p>', unsafe_allow_html=True)
    mode = st.radio(
        "mode_selector",
        ["📁  Upload File", "🔗  YouTube URL"],
        horizontal=True,
        label_visibility="collapsed"
    )
    st.markdown("")
    
    uploaded_file = None
    youtube_url = ""
    proxy_settings = {}
    
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
        proxy_settings = render_proxy_config(app_config)
        
    ai_settings, enable_ai_images = render_ai_config(app_config)
    
    if st.button("Convert to Markdown  →", type="primary", use_container_width=True):
        if mode == "📁  Upload File" and not uploaded_file:
            st.warning("Vui lòng chọn một file để chuyển đổi.")
        elif mode == "🔗  YouTube URL" and not youtube_url:
            st.warning("Vui lòng dán link YouTube.")
        else:
            progress_bar = st.progress(0, text="Đang chuẩn bị…")
            try:
                result_content = ""
                output_filename = "output.md"

                if mode == "📁  Upload File" and uploaded_file:
                    suffix = os.path.splitext(uploaded_file.name)[1].lower()
                    base_name = os.path.splitext(uploaded_file.name)[0]
                    progress_bar.progress(5, text="Đang tải file lên…")

                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        tmp.write(uploaded_file.getbuffer())
                        tmp_path = tmp.name

                    progress_bar.progress(15, text="Đang khởi tạo…")
                    
                    try:
                        progress_bar.progress(25, text="Đang chuyển đổi nội dung…")
                        result_content = convert_file(
                            tmp_path, suffix, enable_ai_images, 
                            ai_settings["ai_provider"], ai_settings["ai_api_key"], ai_settings["ai_model"]
                        )
                    except Exception as e:
                        progress_bar.progress(50, text="Đang thử phương pháp dự phòng…")
                        st.warning(f"⚠️ Lỗi mô tả ảnh bằng AI: {str(e)}. Đang chuyển về chế độ convert thường (không có AI)...")
                        
                        from markitdown import MarkItDown
                        md = MarkItDown()
                        result = md.convert(tmp_path)
                        result_content = f"> ⚠️ **LƯU Ý TỪ HỆ THỐNG:** Quá trình gọi AI mô tả hình ảnh đã bị lỗi (Nguyên nhân: `{str(e)}`). Điều này thường xảy ra khi dùng API Free bị vượt quá giới hạn (Rate limit). File dưới đây được trích xuất bằng chế độ tiêu chuẩn (Không dùng AI).\n\n---\n\n{result.text_content}"
                    finally:
                        try:
                            os.unlink(tmp_path)
                        except:
                            pass

                    progress_bar.progress(80, text="Đang định dạng lại mô tả hình ảnh…")
                    result_content = format_alt_text(result_content)
                    progress_bar.progress(85, text="Đang hoàn tất…")
                    output_filename = make_output_filename(base_name, "file")

                elif mode == "🔗  YouTube URL" and youtube_url:
                    progress_bar.progress(20, text="Đang tải transcript từ YouTube…")
                    content, video_title, error = get_youtube_transcript(
                        youtube_url, 
                        proxy_settings.get("proxy_mode"), proxy_settings.get("ws_user"), 
                        proxy_settings.get("ws_pass"), proxy_settings.get("custom_proxy_raw")
                    )
                    if error:
                        progress_bar.empty()
                        st.error(f"❌ {error}")
                        st.stop()
                    result_content = content
                    name = video_title or extract_video_id(youtube_url) or "video"
                    output_filename = make_output_filename(name, "youtube")

                progress_bar.progress(100, text="✅ Hoàn tất!")
                render_results(result_content, output_filename)

            except Exception as e:
                progress_bar.empty()
                st.error(f"❌ Đã xảy ra lỗi: {str(e)}")

if __name__ == "__main__":
    main()

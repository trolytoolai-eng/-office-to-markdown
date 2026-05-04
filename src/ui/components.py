import streamlit as st
import os
from src.config.settings import save_config

def render_hero():
    # Adjust path assuming this runs from src/main.py or project root
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    logo_path = os.path.join(root_dir, "assets", "logo.png")
    
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
    elif os.path.exists(os.path.join(root_dir, "logo.png")): # fallback
        st.image(os.path.join(root_dir, "logo.png"), use_container_width=True)

    st.markdown("<h1 style='text-align: center;'>Office to Markdown</h1>", unsafe_allow_html=True)

    formats = ["PDF", "DOCX", "XLSX", "PPTX", "HTML", "CSV", "JSON", "XML", "EPUB", "ZIP", "YouTube"]
    chips_html = '<div class="format-chips">' + ''.join(
        [f'<span class="format-chip">{f}</span>' for f in formats]
    ) + '</div>'
    st.markdown(chips_html, unsafe_allow_html=True)
    st.markdown("---")

def render_proxy_config(app_config):
    with st.expander("⚙️ Cấu hình Proxy (Nếu bị YouTube chặn)"):
        st.caption("Sử dụng khi bị giới hạn IP truy cập Youtube.")
        
        radio_options = ["Không dùng (Local)", "Webshare", "Custom URL"]
        try:
            default_index = radio_options.index(app_config["proxy_mode"])
        except ValueError:
            default_index = 0
            
        new_proxy_mode = st.radio("Loại Proxy:", radio_options, index=default_index, horizontal=True)

        new_ws_user = app_config["ws_user"]
        new_ws_pass = app_config["ws_pass"]
        new_custom_proxy_raw = app_config["custom_proxy_raw"]

        if new_proxy_mode == "Webshare":
            st.markdown("[webshare.io](https://www.webshare.io/) → gói **Residential** → [Proxy Settings](https://proxy2.webshare.io/proxy/settings)")
            col1, col2 = st.columns(2)
            with col1:
                new_ws_user = st.text_input("Username", value=app_config["ws_user"], placeholder="webshare_username")
            with col2:
                new_ws_pass = st.text_input("Password", value=app_config["ws_pass"], type="password")
            if new_ws_user and new_ws_pass:
                st.success("✅ Proxy ready")
                if st.button("🔄 Kiểm tra kết nối Proxy"):
                    with st.spinner("Đang kiểm tra..."):
                        try:
                            import requests
                            user = new_ws_user.strip()
                            pwd = new_ws_pass.strip()
                            proxy_url = f"http://{user}:{pwd}@p.webshare.io:80"
                            res = requests.get("https://api.myip.com", proxies={"http": proxy_url, "https": proxy_url}, timeout=10)
                            if res.status_code == 200:
                                st.success(f"Kết nối thành công! IP của proxy: {res.json().get('ip')}")
                            else:
                                st.error(f"Proxy lỗi HTTP {res.status_code}: {res.text}")
                        except Exception as e:
                            st.error(f"Lỗi kết nối proxy: {str(e)}")
        elif new_proxy_mode == "Custom URL":
            new_custom_proxy_raw = st.text_input("Proxy", value=app_config["custom_proxy_raw"], placeholder="IP:PORT:USER:PASS", type="password")
            if new_custom_proxy_raw:
                st.success("✅ Proxy ready")
                
        if st.button("💾 Lưu cấu hình (Dùng cho lần sau)"):
            app_config["proxy_mode"] = new_proxy_mode
            app_config["ws_user"] = new_ws_user
            app_config["ws_pass"] = new_ws_pass
            app_config["custom_proxy_raw"] = new_custom_proxy_raw
            success, msg = save_config(app_config)
            if success:
                st.toast(msg)
            else:
                st.error(msg)
                
    return {"proxy_mode": new_proxy_mode, "ws_user": new_ws_user, "ws_pass": new_ws_pass, "custom_proxy_raw": new_custom_proxy_raw}

def render_ai_config(app_config):
    with st.expander("🤖 Cài đặt AI (Mô tả hình ảnh)"):
        st.caption("Cấu hình API key và model AI dùng để mô tả hình ảnh trong tài liệu.")
        
        provider_opts = ["Google Gemini", "OpenAI", "Anthropic Claude"]
        try:
            _prov_idx = provider_opts.index(app_config["ai_provider"])
        except ValueError:
            _prov_idx = 0
        new_ai_provider = st.selectbox("Provider", provider_opts, index=_prov_idx)
        new_ai_api_key = st.text_input("API Key", value=app_config["ai_api_key"], type="password", help="API key được lưu cục bộ trên máy tính của bạn.")
        
        if new_ai_provider == "Google Gemini":
            model_opts = ["gemini-2.0-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro", "gemini-3.1-flash-lite-preview", "gemini-3.1-pro-preview", "gemini-3-flash-preview"]
        elif new_ai_provider == "OpenAI":
            model_opts = ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-4.1", "gpt-4.1-nano", "o4-mini"]
        else:
            model_opts = ["claude-sonnet-4-20250514", "claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"]
        
        try:
            _mod_idx = model_opts.index(app_config["ai_model"])
        except ValueError:
            _mod_idx = 0
        new_ai_model = st.selectbox("Model", model_opts, index=_mod_idx)

        if st.button("💾 Lưu cấu hình AI"):
            app_config["ai_provider"] = new_ai_provider
            app_config["ai_api_key"] = new_ai_api_key
            app_config["ai_model"] = new_ai_model
            success, msg = save_config(app_config)
            if success:
                st.toast(msg)
            else:
                st.error(msg)
                
    st.markdown("")
    st.info("💡 **Lưu ý quan trọng:**\n"
            "- Khuyên dùng API Key từ các tài khoản đã thanh toán (nạp tối thiểu 5$) để được nâng hạn mức Token, tránh lỗi 429 (Rate Limit) khi xử lý tài liệu dài.\n"
            "- Đối với các file nặng (chứa hàng chục hình ảnh), phần mềm cần thêm thời gian để xử lý và tự động giãn cách các lượt gọi nhằm tránh spam hệ thống AI. Vui lòng kiên nhẫn!")
            
    enable_ai_images = st.checkbox("🖼️ Mô tả hình ảnh bằng AI (tốn thêm thời gian)", value=False, help="Bật tính năng này để AI tự động mô tả các hình ảnh trong tài liệu bằng tiếng Việt.")
    st.markdown("")
    
    return {"ai_provider": new_ai_provider, "ai_api_key": new_ai_api_key, "ai_model": new_ai_model}, enable_ai_images

def render_results(result_content, output_filename):
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
    
    tab1, tab2 = st.tabs(["🌐 Preview HTML", "📝 Raw Markdown"])
    with tab1:
        st.markdown(result_content, unsafe_allow_html=True)
    with tab2:
        st.text_area(
            "preview_raw",
            value=result_content,
            height=400,
            label_visibility="collapsed"
        )

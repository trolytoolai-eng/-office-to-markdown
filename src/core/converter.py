import re

def initialize_llm_client(provider, api_key, model):
    if not api_key:
        return None, None
    try:
        from openai import OpenAI
        if provider == "Google Gemini":
            return OpenAI(api_key=api_key, base_url="https://generativelanguage.googleapis.com/v1beta/openai/", timeout=15.0, max_retries=1), model
        elif provider == "OpenAI":
            return OpenAI(api_key=api_key, timeout=15.0, max_retries=1), model
        elif provider == "Anthropic Claude":
            return OpenAI(api_key=api_key, base_url="https://api.anthropic.com/v1/", timeout=15.0, max_retries=1), model
    except Exception:
        pass
    return None, None

def _describe_image_with_llm(llm_client, md_model, image_path):
    import base64
    import time
    try:
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Thử lại tối đa 4 lần nếu bị Rate Limit (429)
        for attempt in range(4):
            try:
                response = llm_client.chat.completions.create(
                    model=md_model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Hãy viết mô tả chi tiết bằng tiếng Việt cho hình ảnh này."},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{base64_image}",
                                        "detail": "auto"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=300
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                err_str = str(e)
                # Nếu lỗi 429 Rate limit, đợi 15 giây rồi thử lại (vì TPM limit tính theo phút)
                if "429" in err_str or "rate limit" in err_str.lower():
                    if attempt < 3:
                        time.sleep(15)
                        continue
                raise e
    except Exception as e:
        return f"📎 *[Lỗi gọi AI hoặc ảnh không hợp lệ: {str(e)}]*"

def _process_pdf_images(result_content, llm_client, md_model):
    import concurrent.futures
    import os
    matches = list(re.finditer(r'!\[([^\]]*)\]\(([^\)]+)\)', result_content))
    if not matches:
        return result_content
        
    replacements = {}
    unique_paths = list(set([m.group(2) for m in matches]))
    
    def process_image(img_path):
        if os.path.exists(img_path):
            return img_path, _describe_image_with_llm(llm_client, md_model, img_path)
        return img_path, "📎 *[Hình ảnh gốc không thể trích xuất]*"

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        results = executor.map(process_image, unique_paths)
        for path, desc in results:
            if "Lỗi gọi AI" in desc or "không thể trích xuất" in desc:
                replacements[path] = f"\n> {desc}\n"
            else:
                replacements[path] = f"\n> 🤖 **[AI MÔ TẢ HÌNH ẢNH]**\n> *{desc}*\n"
                
    def replacer(match):
        img_path = match.group(2)
        return replacements.get(img_path, match.group(0))
        
    return re.sub(r'!\[([^\]]*)\]\(([^\)]+)\)', replacer, result_content)

def convert_file(tmp_path, suffix, enable_ai_images, ai_provider, ai_api_key, ai_model):
    from markitdown import MarkItDown
    import tempfile
    import os
    
    result_content = ""
    llm_client = None
    md_model = None

    if enable_ai_images and ai_api_key:
        llm_client, md_model = initialize_llm_client(ai_provider, ai_api_key, ai_model)

    def get_md():
        if llm_client and md_model:
            return MarkItDown(llm_client=llm_client, llm_model=md_model)
        return MarkItDown()

    if suffix == ".pdf":
        import pymupdf4llm
        if llm_client and md_model:
            with tempfile.TemporaryDirectory() as tmp_img_dir:
                result_content = pymupdf4llm.to_markdown(tmp_path, write_images=True, image_path=tmp_img_dir)
                result_content = _process_pdf_images(result_content, llm_client, md_model)
        else:
            result_content = pymupdf4llm.to_markdown(tmp_path)
            
        # Clean up
        result_content = re.sub(r'\**==>\s*picture\s*\[[^\]]+\]\s*intentionally\s*omitted\s*<==\**(?:<br>|\n)*', '', result_content)
        result_content = re.sub(r'\**-----\s*Start of picture text\s*-----\**(.*?)\**-----\s*End of picture text\s*-----\**(?:<br>|\n)*', '', result_content, flags=re.DOTALL)
    else:
        _orig_pptx_desc = None
        _orig_img_desc = None
        if llm_client and md_model:
            import markitdown._markitdown as _md_module
            _orig_pptx_desc = getattr(_md_module.PptxConverter, '_get_llm_description', None)
            _orig_img_desc = getattr(_md_module.ImageConverter, '_get_llm_description', None)

            if _orig_pptx_desc:
                def _vi_pptx_desc(self_conv, llm_c, llm_m, image_blob, content_type, prompt=None):
                    vi_prompt = "Hãy viết mô tả chi tiết bằng tiếng Việt cho hình ảnh này, dưới 50 từ."
                    return _orig_pptx_desc(self_conv, llm_c, llm_m, image_blob, content_type, prompt=vi_prompt)
                _md_module.PptxConverter._get_llm_description = _vi_pptx_desc

            if _orig_img_desc:
                def _vi_img_desc(self_conv, local_path, extension, client, model, prompt=None):
                    vi_prompt = "Hãy viết mô tả chi tiết bằng tiếng Việt cho hình ảnh này."
                    return _orig_img_desc(self_conv, local_path, extension, client, model, prompt=vi_prompt)
                _md_module.ImageConverter._get_llm_description = _vi_img_desc

        md = get_md()
        result = md.convert(tmp_path)
        result_content = result.text_content

        if llm_client and md_model:
            import markitdown._markitdown as _md_module
            if _orig_pptx_desc:
                _md_module.PptxConverter._get_llm_description = _orig_pptx_desc
            if _orig_img_desc:
                _md_module.ImageConverter._get_llm_description = _orig_img_desc

    return result_content

def format_alt_text(result_content):
    def _format_alt_text(match):
        alt = match.group(1).strip()
        # Nếu alt trống hoặc tên mặc định (Shape, Picture) -> hiển thị mờ/nhạt
        if not alt or len(alt.split()) < 4 or "Shape" in alt or "Picture" in alt or "Image" in alt:
            return f"\n> 📎 *[Hình ảnh gốc không có mô tả: {alt}]*\n"
        
        # Nếu có chữ -> Khả năng cao là do AI sinh ra (vì prompt yêu cầu chi tiết)
        # Bọc trong một khối Blockquote rõ ràng để người dùng không phải đoán
        return f"\n> 🤖 **[AI MÔ TẢ HÌNH ẢNH]**\n> *{alt}*\n"
    
    return re.sub(r'!\[([^\]]*)\]\([^\)]+\)', _format_alt_text, result_content)

# Office to Markdown Converter

Ứng dụng web chuyển đổi file Office (Word, Excel, PDF, PowerPoint...) và YouTube URL sang Markdown.

## Tính năng
- 📁 Upload file: DOCX, PDF, XLSX, PPTX, HTML, CSV, JSON, XML, ZIP, EPUB
- 🔗 YouTube URL: Lấy transcript + metadata từ video YouTube
- 💾 Tải file output với tên khoa học: `[Nguồn]_[Tên]_[Ngày].md`

## Cài đặt local
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy
Ứng dụng được thiết kế để deploy trên Streamlit Community Cloud hoặc Hugging Face Spaces.

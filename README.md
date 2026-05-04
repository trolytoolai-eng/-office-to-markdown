# Office to Markdown Converter

![Giao diện Office to Markdown](screenshots/demo.png)

Một ứng dụng web hiện đại được xây dựng bằng Python & Streamlit giúp bạn chuyển đổi nhanh chóng các file tài liệu (Word, Excel, PDF, PowerPoint...) và bóc băng Video YouTube sang định dạng Markdown chuẩn xác.

---

## 🚀 Hướng dẫn Cài Đặt Dành Cho AI Agent (Dễ Nhất)

Nếu bạn đang sử dụng một AI Agent (như **Google Antigravity**, **Claude Code**, hay **Cursor**), bạn không cần phải thao tác thủ công. Chỉ cần copy đường link của Github này và đưa ra câu lệnh Prompt (yêu cầu) sau cho AI:

> *"Hãy clone kho lưu trữ này về máy của tôi, tạo một virtual environment (venv) nếu cần, cài đặt toàn bộ `requirements.txt` và sau đó chạy file `Start_App.bat` để bật phần mềm lên giúp tôi."*

AI Agent sẽ tự động xử lý toàn bộ quá trình tải về, thiết lập môi trường và bật phần mềm lên cho bạn chỉ trong 1 nốt nhạc!

---

## 🛠 Hướng dẫn Cài Đặt Thủ Công

Nếu bạn muốn tự tay cài đặt, hãy làm theo các bước cực kỳ đơn giản dưới đây:

### Bước 1: Tải mã nguồn về máy
Mở Terminal / Command Prompt và chạy:
```bash
git clone <ĐƯỜNG_DẪN_REPO_GIT_CỦA_BẠN_TẠI_ĐÂY>
cd ConvertToMD
```

### Bước 2: Khởi tạo Môi trường Ảo (Tùy chọn nhưng khuyên dùng)
Việc tạo môi trường ảo giúp ứng dụng chạy mượt mà, không bị xung đột với các thư viện khác trên máy của bạn.
```bash
# Tạo môi trường ảo (venv)
python -m venv venv

# Kích hoạt trên Windows:
venv\Scripts\activate

# Kích hoạt trên Mac/Linux:
source venv/bin/activate
```

### Bước 3: Cài đặt Thư Viện
Gõ lệnh sau để tải xuống tất cả thư viện cần thiết:
```bash
pip install -r requirements.txt
```

### Bước 4: Chạy Ứng dụng
- **Trên Windows (Siêu Nhanh):** Bạn chỉ cần **click đúp (double-click) vào file `Start_App.bat`**. Phần mềm sẽ tự động bật máy chủ và mở trình duyệt lên cho bạn ngay lập tức.
- **Trên MacOS/Linux (hoặc thủ công qua Terminal):**
  ```bash
  python -m streamlit run src/main.py
  ```
  Sau đó vào trình duyệt gõ: `http://localhost:8501`

---

## 🌟 Tính năng nổi bật
- **Đa dạng định dạng**: Hỗ trợ PDF, DOCX, XLSX, PPTX, HTML, CSV, JSON, XML, ZIP, EPUB.
- **Trích xuất Video YouTube**: Tự động lấy transcript và siêu dữ liệu (metadata) từ YouTube. Hỗ trợ cấu hình Proxy để vượt rào khi IP bị YouTube chặn.
- **AI Mô tả hình ảnh**: Tích hợp OpenAI, Google Gemini, Anthropic Claude để tự động mô tả hình ảnh trong file tài liệu thành văn bản tiếng Việt.
- **Phân tích PDF thông minh**: Nhận diện siêu chuẩn xác bảng biểu, danh sách nhờ `PyMuPDF4LLM`. Cơ chế dự phòng thông minh (fallback) tự động bằng `MarkItDown`.
- **Lưu trữ Cục bộ**: Tự động lưu cấu hình API, Proxy an toàn trực tiếp trên máy của bạn (không bao giờ sợ lộ lọt lên Git).

## 📁 Cấu trúc thư mục chuyên nghiệp
```text
ConvertToMD/
├── assets/                  # Tài nguyên tĩnh (Logo...)
├── screenshots/             # Hình ảnh demo UI
├── src/                     # Mã nguồn chính
│   ├── config/              # Quản lý file cấu hình
│   ├── core/                # Xử lý lõi (Logic Convert, Youtube)
│   ├── ui/                  # Các thành phần giao diện
│   ├── utils/               # Công cụ hỗ trợ
│   └── main.py              # File chạy chính của giao diện
├── Start_App.bat            # Tệp khởi chạy 1-click cho Windows
├── requirements.txt         # Danh sách thư viện Python
└── README.md                # Tài liệu hướng dẫn này
```

**Bảo Mật:** Các API Key và cấu hình quan trọng sẽ tự động sinh ra và lưu tại file `app_config.json`. File này đã được thêm vào danh sách `.gitignore` nên bạn hoàn toàn yên tâm commit code lên Github mà không lo rò rỉ API Key.

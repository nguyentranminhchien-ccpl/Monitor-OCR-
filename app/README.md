# 🫀 Monitor OCR & Auto-fill Desktop Web App

**Hệ thống Trích xuất Dữ liệu Monitor & Tự động Nhập liệu Huyết động EVT**  
**Tác giả:** BS. Nguyễn Trần Minh Chiến ([nguyentranminhchien.hpmu@gmail.com](mailto:nguyentranminhchien.hpmu@gmail.com))  
**Phục vụ:** Nghiên cứu Khoa học Can thiệp Mạch Não (EVT) & Hồi sức Cấp cứu.

---

## 🚀 Cách khởi động ứng dụng (Rất nhanh & Tiện lợi)

Bạn có thể mở ứng dụng bằng bất kỳ cách nào dưới đây:

- **Cách 1 (Nhanh nhất):** Nhấp đúp chuột vào file **`Chay_App_Monitor_AutoFill.bat`** trong thư mục plugin (hoặc shortcut trên Desktop).
- **Cách 2:** Chạy trực tiếp file `run.bat` ngay trong thư mục `app`.
- **Cách 3:** Chạy lệnh trong terminal:
  ```bash
  cd app
  pip install -r requirements.txt
  python start_app.py
  ```

> Ứng dụng sẽ tự động mở trên trình duyệt web mặc định của bạn tại địa chỉ: `http://localhost:5000`.

---

## ⚙️ Cài đặt lần đầu (Chỉ tốn 1 phút)

1. Mở ứng dụng $\rightarrow$ nhấp vào nút **`⚙️ Cài đặt`** ở góc trên bên phải.
2. Dán **Gemini API Key** của bạn vào ô:
   - Nếu chưa có API Key, nhấp vào link [Google AI Studio API Keys](https://aistudio.google.com/app/apikey) để tạo miễn phí.
3. Nhấn **`Lưu Cấu hình`**. Key sẽ được lưu an toàn trong file `config.json` cục bộ trên máy bạn, các lần sau không cần nhập lại.

---

## 📖 Hướng dẫn sử dụng chi tiết

### Bước 1: Chọn bệnh nhân & Quét AI
1. Trong dropdown **"Chọn Thư mục Bệnh nhân"**, chọn bệnh nhân bạn cần nhập liệu (ví dụ: `nguyễn bá phương`, `lê xuân toản`...).
2. Danh sách ảnh monitor sẽ tự động tải lên và hiển thị dải ảnh thu nhỏ phía dưới.
3. Nhấn nút xanh: **`⚡ BẮT ĐẦU QUÉT AI TOÀN BỘ ẢNH`**.
4. Hệ thống sẽ lần lượt gọi Gemini 2.0 Flash Vision để trích xuất đầy đủ bảng dấu hiệu sinh tồn từng phút.

### Bước 2: Chuẩn hóa mốc thời gian ($T_0 \rightarrow T_{end}$)
1. Chọn mốc **$T_0$** (khởi đầu can thiệp) và **$T_{end}$** (kết thúc can thiệp).
2. Chọn phương pháp xử lý khuyết thiếu (mặc định là `Forward-fill`).
3. Bảng dữ liệu chuẩn hóa 3 phút/lần sẽ tự động cập nhật ngay lập tức.
4. Bạn có thể nhấp chuột vào bất kỳ ô nào trên bảng để chỉnh sửa tay nếu muốn.

### Bước 3: Nhập liệu hoặc Xuất Excel
- **Cách 1 (1-Click Copy Script):** Nhấn nút **`📋 Sao chép Script Auto-fill`** $\rightarrow$ chuyển sang tab form bệnh án trên Chrome $\rightarrow$ mở Console (F12) $\rightarrow$ Paste (`Ctrl + V`) $\rightarrow$ Enter.
- **Cách 2 (Xuất Excel):** Nhấn nút **`📊 Xuất Excel (.xlsx)`** để tải bảng số liệu đã chuẩn hóa về máy phục vụ phân tích R / SPSS / Jamovi.

---
name: monitor-ocr-autofill
description: >-
  Nhận diện ảnh màn hình monitor bệnh viện (Philips IntelliVue, GE, Mindray...),
  trích xuất chuỗi dấu hiệu sinh tồn theo mốc thời gian, dừng lại hỏi người dùng chọn mốc T0,
  T kết thúc và phương pháp xử lý dữ liệu khuyết thiếu, sau đó mới tạo mã JavaScript auto-fill.
---

# Monitor OCR & Auto-fill Skill

## Mục đích
Skill này điều phối quy trình **2 giai đoạn** chuẩn mực:
1. **Giai đoạn 1 (OCR & Phỏng vấn xác nhận):** Đọc trích xuất toàn bộ dữ liệu $\rightarrow$ Xuất bảng tóm tắt thời gian thực $\rightarrow$ **DỪNG LẠI** hỏi người dùng xác nhận mốc giờ $T_0$ (khởi đầu), $T_{end}$ (kết thúc) và phương pháp xử lý khuyết thiếu.
2. **Giai đoạn 2 (Chuẩn hóa & Sinh mã Auto-fill):** Sau khi người dùng trả lời, chuẩn hóa chuỗi mốc phút (0, 3, 6, ...) $\rightarrow$ Tạo Probe script $\rightarrow$ Tạo mã JavaScript Console hoàn chỉnh.

---

## GIAI ĐOẠN 1 — OCR, TRÍCH XUẤT & HỎI XÁC NHẬN (BẮT BUỘC DỪNG LẠI)

### Bước 1: Nhận diện ảnh monitor
- Đọc **toàn bộ ảnh** được cung cấp.
- Ghép theo thứ tự thời gian tăng dần, loại bỏ timestamp trùng lặp.
- Tách NIBP dạng `SBP / DBP (MAP)` thành 3 cột riêng.
- Xuất bảng markdown tổng hợp theo thời gian thực:
  `DateTime | HR | SBP | DBP | MAP | Ghi chú`

### Bước 2: Phát hiện khuyết thiếu & DỪNG LẠI hỏi người dùng
Agent **BẮT BUỘC DỪNG LẠI** và đưa ra 2 câu hỏi, **TUYỆT ĐỐI KHÔNG TỰ Ý VIẾT SCRIPT AUTO-FILL Ở BƯỚC NÀY**:

1. **Câu hỏi mốc thời gian thủ thuật:**
   *"Dải dữ liệu trích xuất từ [HH:MM] đến [HH:MM]. Bạn muốn chọn mốc giờ nào làm $T_0$ (khởi đầu thủ thuật) và mốc giờ nào làm $T_{end}$ (kết thúc thủ thuật)?"*
2. **Câu hỏi xử lý khuyết thiếu (nếu có):**
   *"Phát hiện [N] mốc bị khuyết thiếu: [liệt kê]. Bạn muốn xử lý như thế nào?"*
   - `[1] Forward-fill`: Lấy giá trị mốc TRƯỚC đó.
   - `[2] Lấy trung bình`: Tính giá trị trung bình giữa mốc trước và mốc sau.
   - `[3] Skip`: Bỏ qua, để trống không nhập.

---

## GIAI ĐOẠN 2 — CHUẨN HÓA & TẠO MÃ AUTO-FILL (Sau khi user đã phản hồi)

### Bước 3: Chuẩn hóa chuỗi thời gian
- Mốc bắt đầu $T_0$ được gán là **0 phút**.
- Mỗi mốc kế tiếp tăng đều **3 phút/lần** cho đến $T_{end}$.
- Áp dụng phương pháp imputation người dùng đã chọn.
- Xuất bảng chuẩn hóa cuối cùng: `Mốc (phút) | DateTime | HR | SBP | DBP | MAP | Ghi chú`.

### Bước 4: Tạo mã JavaScript Auto-fill chuẩn
- Luôn cung cấp **Probe script** để người dùng kiểm tra số cột/input trên form.
- Tạo script Auto-fill hoàn chỉnh:
  - Bắt buộc dùng `nativeInputValueSetter`:
    `Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set`
  - Bỏ qua ô MAP (index 3) nếu form tự tính.
  - Đánh dấu `_imputed: true` và `console.warn()` cho các ô được xử lý khuyết thiếu.

---

## Quy tắc hành vi bắt buộc của Agent

1. **Khi nhận ảnh:** Trích xuất và lập bảng dữ liệu thời gian thực.
2. **Nguyên tắc DỪNG LẠI:** Khi hỏi $T_0$, $T_{end}$ và phương pháp khuyết thiếu, agent **PHẢI DỪNG LẠI** để người dùng trả lời. **KHÔNG ĐƯỢC sinh mã script trước khi người dùng xác nhận**.
3. **Khi nhận phản hồi:** Lập tức chuẩn hóa chuỗi và xuất mã JavaScript hoàn chỉnh.

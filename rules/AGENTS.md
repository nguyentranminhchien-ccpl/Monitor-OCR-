# RULE — Monitor OCR & Auto-fill Behavior

## Khi người dùng gửi ảnh màn hình monitor bệnh viện

Agent PHẢI thực hiện quy trình 2 giai đoạn theo đúng thứ tự, không được bỏ qua bước dừng chờ người dùng:

---

### GIAI ĐOẠN 1 — Nhận diện, Trích xuất & Hỏi xác nhận (BẮT BUỘC DỪNG LẠI)

1. **Nhận diện & trích xuất tự động:**
   - Đọc TẤT CẢ ảnh được gửi cùng lúc.
   - Ghép theo thứ tự thời gian (timestamp tăng dần), loại bỏ hàng trùng timestamp.
   - Tách NIBP dạng `SBP/DBP(MAP)` thành các giá trị riêng.
   - Xuất bảng Markdown tổng hợp đầy đủ theo mốc thời gian thực tế:
     `DateTime | HR | SBP | DBP | MAP | Ghi chú`

2. **Xác định mốc khuyết thiếu & Mốc bắt đầu/kết thúc:**
   - Liệt kê các mốc thời gian phát hiện được trên monitor từ ảnh đầu tiên đến ảnh cuối cùng.
   - Liệt kê rõ các mốc bị thiếu / rỗng / NOT READY (nếu có).

3. **BẮT BUỘC DỪNG LẠI VÀ HỎI NGƯỜI DÙNG — KHÔNG VIẾT SCRIPT AUTO-FILL Ở BƯỚC NÀY:**
   - **Câu hỏi 1 (Mốc T0 & Tend):** Hỏi người dùng muốn chọn mốc giờ nào làm $T_0$ (bắt đầu thủ thuật) và mốc giờ nào làm $T_{end}$ (kết thúc thủ thuật) trong dải thời gian vừa trích xuất.
   - **Câu hỏi 2 (Xử lý khuyết thiếu):** Nếu có mốc bị khuyết thiếu, hỏi người dùng chọn:
     - `[1] Forward-fill (lấy giá trị mốc trước đó)`
     - `[2] Lấy trung bình (trung bình mốc trước và sau)`
     - `[3] Skip (bỏ qua không nhập mốc đó)`
   - **TUYỆT ĐỐI KHÔNG TỰ Ý CHỌN PHƯƠNG PHÁP HOẶC TỰ Ý TẠO MÃ JAVASCRIPT KHI NGƯỜI DÙNG CHƯA TRẢ LỜI.**

---

### GIAI ĐOẠN 2 — Chuẩn hóa & Tạo mã Auto-fill (Chỉ thực hiện sau khi người dùng đã trả lời)

Sau khi nhận được phản hồi của người dùng về $T_0$, $T_{end}$ và phương pháp xử lý khuyết thiếu:
1. Chuẩn hóa chuỗi dữ liệu bắt đầu từ mốc 0 phút tại $T_0$, tăng 3 phút/lần cho đến $T_{end}$.
2. Áp dụng chính xác phương pháp khuyết thiếu mà người dùng đã chọn.
3. Xuất bảng dữ liệu chuẩn hóa cuối cùng:
   `Mốc (phút) | DateTime | HR | SBP | DBP | MAP | Ghi chú`
4. Cung cấp Probe script để kiểm tra cấu trúc DOM form nếu cần.
5. Cung cấp Mã JavaScript auto-fill hoàn chỉnh:
   - Dùng `nativeInputValueSetter` chuẩn: `Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set`.
   - Mốc phút bắt đầu từ 0, tăng 3 phút/lần.
   - Không ghi đè ô MAP nếu form tự tính (index 3 trong form dotquyevt).
   - Đánh dấu `_imputed: true` và `console.warn()` cho các mốc được impute.

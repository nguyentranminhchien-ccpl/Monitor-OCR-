# Monitor OCR & Auto-fill Plugin

Plugin tự động nhận diện ảnh chụp màn hình monitor theo dõi bệnh nhân trong phòng can thiệp mạch não / hồi sức (Philips IntelliVue, GE Carescape, Mindray...), trích xuất chuỗi huyết áp và nhịp tim theo mốc thời gian thực, xử lý dữ liệu khuyết thiếu, và tạo mã JavaScript Console để điền tự động vào biểu mẫu web nghiên cứu khoa học.

---

## 🌟 Tính năng nổi bật

- 📷 **OCR Monitor Đa hãng**: Nhận diện bảng *"Vital Signs 1 min"* hoặc *"Trends"* từ ảnh chụp màn hình monitor Philips, GE, Mindray.
- 🔗 **Ghép nối đa ảnh thông minh**: Tự động liên kết nhiều ảnh chụp liên tiếp theo thứ tự thời gian tăng dần, lọc bỏ các dòng trùng lặp.
- ⏱️ **Tùy biến mốc $T_0$ và $T_{end}$**: Cho phép người dùng chỉ định chính xác thời điểm bắt đầu can thiệp ($T_0 = 0$ phút) và kết thúc thủ thuật ($T_{end}$).
- 🩹 **Xử lý dữ liệu khuyết thiếu (Interactive Imputation)**: Tự động phát hiện các mốc thiếu đo hoặc tuột sensor, **dừng lại hỏi người dùng** lựa chọn giữa *Forward-fill*, *Nội suy tuyến tính*, hoặc *Skip* trước khi sinh mã.
- ⚡ **Auto-fill Native Setter**: Sử dụng `Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set` cùng sự kiện `Event('input')` và `Event('change')` giúp kích hoạt đầy đủ tính năng reactivity của React, Vue, Livewire, Alpine.js.
- 🛡️ **Bảo vệ ô MAP**: Tự động bỏ qua ô Huyết áp trung bình (MAP) nếu form web có công thức tự động tính toán từ SBP và DBP.
- 🔍 **Probe Script tích hợp**: Hỗ trợ script thăm dò cấu trúc DOM bảng trước khi chạy script chính thức.

---

## 📋 Vị trí áp dụng trong Form nhập liệu Bệnh án điện tử

Mã script được tối ưu cho hệ thống web bệnh án nghiên cứu can thiệp đột quỵ (ví dụ: `dotquyevt` hoặc các form nghiên cứu đa trung tâm tương đương):

- **Phân hệ:** Bệnh án nghiên cứu can thiệp lấy huyết khối đường động mạch (EVT).
- **Vị trí bước nhập liệu:** **Bước 5 — Diễn biến trong can thiệp / Theo dõi dấu hiệu sinh tồn trong thủ thuật**.
- **Địa chỉ URL mẫu:** `.../benh-an/{id}/buoc/5`
- **Cấu trúc bảng nhập liệu:** Bảng theo dõi diễn biến huyết áp - mạch theo mốc thời gian (0 phút, 3 phút, 6 phút, 9 phút...).

---

## 📖 Hướng dẫn sử dụng chi tiết từng bước

### Bước 1: Gửi ảnh cho Antigravity
Chụp ảnh màn hình monitor (cửa sổ xu hướng Vital Signs 1 phút) và gửi ảnh hoặc đường dẫn thư mục ảnh cho Antigravity với câu lệnh:
> *"Dùng plugin monitor-ocr-autofill nhận diện ảnh monitor tại thư mục [đường dẫn ảnh] và tạo script nhập liệu."*

### Bước 2: Duyệt bảng trích xuất & Chọn phương án
Agent sẽ đọc toàn bộ ảnh, audit lại từng dòng HR, SBP, DBP, MAP và **dừng lại** hiển thị bảng dữ liệu thời gian thực kèm 2 câu hỏi:
1. **Chọn mốc giờ:** Xác nhận thời điểm bắt đầu ($T_0$) và kết thúc ($T_{end}$).
2. **Chọn phương pháp khuyết thiếu (nếu có):**
   - `[1] Forward-fill`: Lấy giá trị của mốc đo liền trước.
   - `[2] Linear interpolation`: Lấy trung bình cộng giữa mốc trước và mốc sau.
   - `[3] Skip`: Bỏ qua, để trống mốc đó.

Sau khi bạn xác nhận, Agent sẽ tạo bảng chuẩn hóa mốc 3 phút/lần và đoạn mã JavaScript Console.

---

### Bước 3: Chuẩn bị trang web nhập liệu
1. Mở trình duyệt Chrome (hoặc Edge, Cốc Cốc, Brave).
2. Đăng nhập vào hệ thống web nghiên cứu và mở đúng bệnh án cần nhập.
3. Chuyển đến **Bước 5 (Diễn biến trong can thiệp)**.
4. Đảm bảo bảng theo dõi huyết áp đã hiển thị trên màn hình. *(Nếu form yêu cầu bấm nút "Thêm hàng" để sinh sẵn các dòng nhập liệu, hãy đảm bảo số dòng hiển thị đủ hoặc vượt số mốc cần điền).*

---

### Bước 4: Mở Developer Tools Console trên Trình duyệt
Có 3 cách để mở Console:
- **Cách 1 (Nhanh nhất):** Nhấn phím **`F12`** trên bàn phím.
- **Cách 2:** Nhấn tổ hợp phím **`Ctrl + Shift + I`** (trên máy tính Mac: `Cmd + Option + I`).
- **Cách 3:** Nhấp chuột phải vào bất kỳ khoảng trống nào trên trang web $\rightarrow$ chọn **Inspect (Kiểm tra)**.

Sau khi cửa sổ DevTools mở ra ở cạnh phải hoặc phía dưới màn hình, nhấp chuột vào tab **`Console`** (Bảng điều khiển).

---

### Bước 5: Mở khóa tính năng dán mã của trình duyệt (Bắt buộc với Chrome/Edge mới)

> [!IMPORTANT]
> Trên các phiên bản Google Chrome và Microsoft Edge hiện nay, trình duyệt có cơ chế bảo mật chống tấn công Self-XSS. Lần đầu tiên bạn dán mã vào Console, trình duyệt sẽ chặn lại và hiện cảnh báo:
>
> `Warning: Don't paste code into the DevTools Console that you don't understand...`
>
> **Cách xử lý rất đơn giản:**
> 1. Nhấp chuột vào dòng nhắc lệnh cuối cùng trong Console (ngay cạnh dấu `>`).
> 2. Gõ dòng chữ sau rồi nhấn **Enter**:
>    - Nếu trình duyệt tiếng Anh: gõ **`allow pasting`**
>    - Nếu trình duyệt tiếng Việt: gõ **`cho phép dán`**
> 3. Sau khi nhấn Enter, tính năng dán mã sẽ được kích hoạt vĩnh viễn trên trình duyệt của bạn.

---

### Bước 6: (Tùy chọn) Chạy Probe Script kiểm tra bảng
Trước khi điền dữ liệu thực tế, bạn có thể copy đoạn **Probe script** do Agent cung cấp, dán vào Console và nhấn **Enter**. 

Script này sẽ in ra cấu trúc các ô `inputs[i]` trong hàng đầu tiên để bảo đảm khớp hoàn toàn với cấu trúc:
- `inputs[0]`: Mốc (phút)
- `inputs[1]`: Huyết áp tâm thu (SBP)
- `inputs[2]`: Huyết áp tâm trương (DBP)
- `inputs[3]`: Huyết áp trung bình (MAP — tự tính, bỏ qua)
- `inputs[4]`: Tần số tim (HR)
- `selects[0]`: Phương pháp đo (`cuff` / `arterial`)

---

### Bước 7: Dán mã Auto-fill và Thực thi
1. Sao chép (Copy) toàn bộ đoạn mã JavaScript Console do Agent cung cấp.
2. Quay lại tab Console trên trình duyệt, dán (Paste / `Ctrl + V`) mã vào.
3. Nhấn **Enter**.
4. Script sẽ tự động chạy trong tích tắc và hiển thị hộp thoại thông báo:
   > `✅ Đã điền thành công X/Y mốc vào form!`
   > `⚠️ Có N mốc được xử lý khuyết thiếu (xem Console F12).`
5. Kiểm tra lại dữ liệu trên giao diện web và nhấn nút **Lưu / Lưu bước 5** để hoàn tất.

---

## 🛠️ Xử lý sự cố thường gặp (FAQ)

| Sự cố | Nguyên nhân | Cách khắc phục |
| :--- | :--- | :--- |
| **Không dán được code vào Console** | Chrome chặn tính năng paste bảo mật. | Gõ `allow pasting` (hoặc `cho phép dán`) vào Console rồi nhấn Enter trước khi dán. |
| **Không tìm thấy bảng (`table tbody tr`)** | Đang đứng sai trang hoặc form chưa tải xong DOM. | Chuyển đến đúng Bước 5 của bệnh án EVT, đợi bảng tải xong rồi dán lại code. |
| **Bảng web không tự tính ô MAP** | Biểu mẫu web không có hàm JavaScript tự tính MAP. | Bạn có thể yêu cầu Agent cập nhật script để ghi trực tiếp giá trị MAP vào `inputs[3]`. |
| **Sau khi submit web bị mất số** | Form dùng React/Vue không bắt được lệnh `.value = x` thông thường. | Script đã tích hợp sẵn `nativeInputValueSetter` và kích hoạt đồng thời `input` + `change` event để ép form cập nhật state. |
| **Bảng trên web ít hàng hơn số mốc** | Web chỉ hiển thị sẵn một số hàng mặc định. | Bấm nút **"Thêm mốc theo dõi"** hoặc **"Thêm dòng"** trên trang web cho đủ số lượng mốc rồi chạy script. |

---

## 👨‍💻 Tác giả & Bản quyền

- **Tác giả:** Nguyễn Trần Minh Chiến
- **Email:** [nguyentranminhchien.hpmu@gmail.com](mailto:nguyentranminhchien.hpmu@gmail.com)
- **Tổ chức / Dự án:** Đề án thạc sĩ Y học & Nghiên cứu Khoa học Can thiệp Lấy huyết khối Đột quỵ Não (EVT).
- **Giấy phép:** Nội bộ phục vụ nghiên cứu lâm sàng.

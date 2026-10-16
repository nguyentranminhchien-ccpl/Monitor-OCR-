#!/bin/bash
# ======================================================================
#   HỆ THỐNG TRÍCH XUẤT HUYẾT ĐỘNG MONITOR & TỰ ĐỘNG NHẬP LIỆU BỆNH ÁN EVT
#   Tác giả: BS. Nguyễn Trần Minh Chiến (nguyentranminhchien.hpmu@gmail.com)
#   Bản chạy 1-Click dành cho macOS (MacBook M1/M2/M3/M4 & Intel)
# ======================================================================

# Chuyển vào thư mục chứa script
cd "$(dirname "$0")"

echo "======================================================================"
echo "  HỆ THỐNG TRÍCH XUẤT HUYẾT ĐỘNG MONITOR & TỰ ĐỘNG NHẬP LIỆU BỆNH ÁN EVT"
echo "  Tác giả: BS. Nguyễn Trần Minh Chiến"
echo "  Hệ điều hành: macOS"
echo "======================================================================"
echo ""

# Tìm kiếm lệnh Python 3 trên macOS
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
fi

# Nếu chưa có Python trên máy Mac
if [ -z "$PYTHON_CMD" ]; then
    echo "======================================================================"
    echo "  [THÔNG BÁO] CHƯA PHÁT HIỆN PYTHON TRÊN MACBOOK CỦA BẠN!"
    echo "======================================================================"
    echo ""
    echo "Ứng dụng cần môi trường Python 3.10 trở lên để chạy máy chủ AI."
    echo ""
    echo "Bạn muốn cài đặt Python bằng cách nào?"
    echo "  [1] Tự động cài đặt nhanh qua Homebrew (nếu máy đã có brew)"
    echo "  [2] Mở trang tải gói cài đặt Python chính thức cho macOS trên Safari"
    echo "  [3] Thoát"
    echo ""
    read -p "Nhập lựa chọn của bạn [1, 2 hoặc 3]: " py_choice
    if [ "$py_choice" = "1" ]; then
        if command -v brew &> /dev/null; then
            echo "[*] Đang cài đặt Python qua Homebrew, vui lòng chờ..."
            brew install python
            PYTHON_CMD="python3"
        else
            echo "[!] Máy chưa có Homebrew. Đang mở trang web tải Python chính thức..."
            open "https://www.python.org/downloads/macos/"
            echo "Vui lòng tải bản macOS 64-bit universal2 installer và cài đặt."
            exit 0
        fi
    elif [ "$py_choice" = "2" ]; then
        echo "[*] Đang mở trang web tải Python chính thức..."
        open "https://www.python.org/downloads/macos/"
        echo "Vui lòng tải bản macOS 64-bit universal2 installer và cài đặt."
        exit 0
    else
        exit 1
    fi
fi

echo "[*] Môi trường: $($PYTHON_CMD --version)"
echo "[*] Đang kiểm tra và tự động cài thư viện phụ thuộc (flask, requests, pandas, openpyxl)..."

# Chuyển vào thư mục app
cd app

# Cài đặt requirements
$PYTHON_CMD -m pip install -r requirements.txt --quiet --disable-pip-version-check

echo ""
echo "[*] Đang khởi động máy chủ ứng dụng và mở giao diện trên trình duyệt..."
echo "    Địa chỉ: http://localhost:5000"
echo ""

# Khởi chạy ứng dụng
$PYTHON_CMD start_app.py

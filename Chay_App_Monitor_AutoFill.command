#!/bin/bash
# ======================================================================
#   HE THONG TRICH XUAT HUYET DONG MONITOR & TU DONG NHAP LIEU EVT
#   Tac gia: BS. Nguyen Tran Minh Chien (nguyentranminhchien.hpmu@gmail.com)
#   Chuyen nganh: Dot quy nao & Hoi suc Tich cuc
#   He dieu hanh: macOS (MacBook M1/M2/M3/M4 & Intel)
# ======================================================================

# Chuyen vao thu muc chua script
cd "$(dirname "$0")"

echo "======================================================================"
echo "  HE THONG TRICH XUAT HUYET DONG MONITOR & TU DONG NHAP LIEU EVT"
echo "  Tac gia: BS. Nguyen Tran Minh Chien"
echo "  Chuyen nganh: Dot quy nao & Hoi suc Tich cuc"
echo "  He dieu hanh: macOS"
echo "======================================================================"
echo ""

# 1. Kiem tra xem Python 3 co hoat dong thuc su khong (tranh Xcode stub cua Apple)
PYTHON_CMD=""

for candidate in python3 /opt/homebrew/bin/python3 /usr/local/bin/python3 /Library/Frameworks/Python.framework/Versions/Current/bin/python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then
        if "$candidate" -c "import sys" >/dev/null 2>&1; then
            PYTHON_CMD="$candidate"
            break
        fi
    fi
done

# 2. Neu chua co Python hoat dong tren Mac
if [ -z "$PYTHON_CMD" ]; then
    echo "======================================================================"
    echo "  [THONG BAO] CHUA PHAT HIEN PYTHON HOAT DONG TREN MACBOOK CUA BAN!"
    echo "======================================================================"
    echo ""
    echo "Ung dung can moi truong Python 3.10 tro len de chay may chu xu ly AI."
    echo ""
    echo "Ban muon cai dat Python bang cach nao?"
    echo "  [1] Mo trang tai goi cai dat Python chinh thuc cho macOS (.pkg)"
    echo "  [2] Tu dong cai dat qua Homebrew (neu may da co brew)"
    echo "  [3] Thoat"
    echo ""
    
    printf "Vui long nhap lua chon cua ban [1, 2 hoac 3] roi nhan Enter: "
    read -r py_choice
    
    case "$py_choice" in
        1)
            echo ""
            echo "[*] Dang mo trang web tai Python chinh thuc cho macOS tren Safari..."
            open "https://www.python.org/downloads/macos/"
            echo "Huong dan: Tai ban 'macOS 64-bit universal2 installer' (.pkg) va cai dat."
            exit 0
            ;;
        2)
            echo ""
            if command -v brew >/dev/null 2>&1; then
                echo "[*] Dang cai dat Python qua Homebrew, vui long cho..."
                brew install python
                PYTHON_CMD="python3"
            else
                echo "[!] May chua cai dat Homebrew."
                echo "Dang chuyen sang mo trang web tai Python chinh thuc tren Safari..."
                open "https://www.python.org/downloads/macos/"
                exit 0
            fi
            ;;
        *)
            echo ""
            echo "Da huy khoi dong."
            exit 1
            ;;
    esac
fi

echo "[*] Moi truong: $($PYTHON_CMD --version)"
echo "[*] Dang kiem tra va tu dong cai thu vien phu thuoc (flask, requests, pandas, openpyxl)..."

cd app
$PYTHON_CMD -m pip install -r requirements.txt --quiet --disable-pip-version-check

echo ""
echo "[*] Dang khoi dong may chu ung dung va mo giao dien tren trinh duyet..."
echo "    Dia chi: http://localhost:5000"
echo ""

$PYTHON_CMD start_app.py

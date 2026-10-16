@echo off
chcp 65001 > nul
title Monitor OCR & Auto-fill v2.0 - BS. Nguyễn Trần Minh Chiến
echo ======================================================================
echo   HỆ THỐNG TRÍCH XUẤT HUYẾT ĐỘNG MONITOR & TỰ ĐỘNG NHẬP LIỆU BỆNH ÁN EVT
echo   Tác giả: BS. Nguyễn Trần Minh Chiến (nguyentranminhchien.hpmu@gmail.com)
echo ======================================================================
echo.

:: Kiểm tra cài đặt Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo.
    echo ======================================================================
    echo   [THÔNG BÁO] CHƯA PHÁT HIỆN PYTHON TRÊN MÁY TÍNH CỦA BẠN!
    echo ======================================================================
    echo.
    echo Ứng dụng cần môi trường Python 3.10 trở lên để chạy máy chủ xử lý AI.
    echo.
    echo Bạn muốn cài đặt Python bằng cách nào?
    echo   [1] Tự động cài đặt nhanh qua Windows Package Manager (Khuyên dùng)
    echo   [2] Mở trang tải chính thức python.org trên trình duyệt
    echo   [3] Thoát
    echo.
    set /p py_choice="Nhập lựa chọn của bạn [1, 2 hoặc 3]: "
    if "%py_choice%"=="1" (
        echo.
        echo [*] Đang tải và cài đặt Python tự động, vui lòng chờ trong giây lát...
        winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
        if %errorlevel% equ 0 (
            echo.
            echo [OK] Đã cài đặt Python thành công!
            echo Vui lòng đóng cửa sổ này và nhấp đúp lại vào file để khởi động ứng dụng.
        ) else (
            echo.
            echo [!] Không thể cài tự động qua winget. Đang mở trang web python.org...
            start https://www.python.org/downloads/
            echo Vui lòng tải bản cài đặt, nhớ tick vào ô "Add Python to PATH" trước khi bấm Install.
        )
        pause
        exit /b 0
    )
    if "%py_choice%"=="2" (
        echo.
        echo [*] Đang mở trang web tải Python chính thức trên trình duyệt...
        start https://www.python.org/downloads/
        echo.
        echo LƯU Ý KHI CÀI ĐẶT:
        echo Nhớ tick chọn ô [Add Python to PATH] ở dưới cùng cửa sổ cài đặt trước khi bấm Install!
        pause
        exit /b 0
    )
    exit /b 1
)

cd /d "%~dp0app"

:: Tự động kiểm tra và cài đặt thư viện phụ thuộc nếu chưa có
echo [*] Đang kiểm tra thư viện phụ thuộc (flask, requests, pandas, openpyxl)...
python -m pip install -r requirements.txt --quiet --disable-pip-version-check

echo [*] Đang khởi động máy chủ ứng dụng và mở giao diện trên trình duyệt...
echo.
python start_app.py

echo.
echo Ứng dụng đã dừng.
pause

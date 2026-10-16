@echo off
chcp 65001 > nul
title Monitor OCR & Auto-fill - BS. Nguyễn Trần Minh Chiến
echo ========================================================
echo  KHỞI ĐỘNG HỆ THỐNG MONITOR OCR & AUTO-FILL
echo  Tác giả: BS. Nguyễn Trần Minh Chiến
echo ========================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [THONG BAO] Chua tim thay Python tren may tinh!
    echo [1] Cai dat tu dong qua winget
    echo [2] Mo trang web python.org
    echo [3] Thoat
    set /p py_c="Lua chon [1/2/3]: "
    if "%py_c%"=="1" winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
    if "%py_c%"=="2" start https://www.python.org/downloads/
    pause
    exit /b 0
)

cd /d "%~dp0"
python -m pip install -r requirements.txt --quiet --disable-pip-version-check
python start_app.py
pause

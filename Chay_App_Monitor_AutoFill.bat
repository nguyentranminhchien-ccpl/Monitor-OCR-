@echo off
setlocal
chcp 65001 >nul
title Monitor OCR ^& Auto-fill v2.0 - BS. Nguyen Tran Minh Chien

echo ======================================================================
echo   HE THONG TRICH XUAT HUYET DONG MONITOR ^& TU DONG NHAP LIEU EVT
echo   Tac gia: BS. Nguyen Tran Minh Chien (nguyentranminhchien.hpmu@gmail.com)
echo   Chuyen nganh: Dot quy nao ^& Hoi suc Tich cuc
echo ======================================================================
echo.

:: 1. Kiem tra xem Python co san sang va hoat dong khong
set "PY_CMD="

:: Kiem tra lenh python
python -c "import sys" >nul 2>nul
if %errorlevel% equ 0 (
    set "PY_CMD=python"
    goto :PYTHON_FOUND
)

:: Kiem tra lenh py (Python Launcher tren Windows)
py -3 -c "import sys" >nul 2>nul
if %errorlevel% equ 0 (
    set "PY_CMD=py -3"
    goto :PYTHON_FOUND
)

:: Kiem tra python3
python3 -c "import sys" >nul 2>nul
if %errorlevel% equ 0 (
    set "PY_CMD=python3"
    goto :PYTHON_FOUND
)

:: 2. Neu chua co Python, hien thong bao va MENU LUA CHON
:PYTHON_NOT_FOUND
echo ======================================================================
echo   [THONG BAO] CHUA PHAT HIEN PYTHON HOAT DONG TREN MAY TINH CUA BAN!
echo ======================================================================
echo.
echo Phan mem can moi truong Python 3.10 tro len de chay may chu xu ly AI.
echo.
echo Ban muon cai dat Python bang cach nao?
echo   [1] Tu dong cai dat nhanh qua Windows Package Manager (winget)
echo   [2] Mo trang web tai chinh thuc python.org tren trinh duyet
echo   [3] Thoat
echo.

choice /c 123 /n /m "Vui long bam phim 1, 2 hoac 3 tren ban phim: "
if errorlevel 3 goto :OPT_EXIT
if errorlevel 2 goto :OPT_BROWSER
if errorlevel 1 goto :OPT_WINGET
goto :OPT_EXIT

:OPT_WINGET
echo.
echo [*] Dang tai va cai dat Python 3.12 tu dong qua winget, vui long cho...
winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
if %errorlevel% equ 0 (
    echo.
    echo ======================================================================
    echo [OK] DA CAI DAT PYTHON THANH CONG!
    echo Vui long dong cua so nay va nhap dup lai vao file de bat dau su dung.
    echo ======================================================================
    pause
    exit /b 0
) else (
    echo.
    echo [!] Khong the cai dat tu dong qua winget.
    echo Dang chuyen sang mo trang web python.org...
    goto :OPT_BROWSER
)

:OPT_BROWSER
echo.
echo [*] Dang mo trang web tai Python chinh thuc tren trinh duyet...
start https://www.python.org/downloads/
echo.
echo ======================================================================
echo LUU Y RAT QUAN TRONG KHI CAI DAT:
echo Khi cua so cai dat Python hien len, hay TICK CHON vao o:
echo      [v] "Add python.exe to PATH"
echo o duoi cung cua so truoc khi bam "Install Now"!
echo ======================================================================
echo.
pause
exit /b 0

:OPT_EXIT
echo.
echo Da huy khoi dong.
exit /b 1

:PYTHON_FOUND
echo [*] Tim thay moi truong:
%PY_CMD% --version
echo.
echo [*] Dang kiem tra va tu dong cai thu vien phu thuoc (flask, requests, pandas, openpyxl)...
cd /d "%~dp0app"
%PY_CMD% -m pip install -r requirements.txt --quiet --disable-pip-version-check

echo.
echo [*] Dang khoi dong may chu ung dung va mo giao dien tren trinh duyet...
echo     Dia chi: http://localhost:5000
echo.
%PY_CMD% start_app.py

echo.
echo Ung dung da dung.
pause

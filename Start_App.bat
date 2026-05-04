@echo off
title Khoi dong Phan mem ConvertToMD
color 0A
echo ===================================================
echo   PHAN MEM DANG KHOI DONG... VUI LONG DOI 3 GIAY
echo ===================================================
echo.
echo Luu y: Cua so nay giup duy tri phan mem hoat dong.
echo Khi muon tat phan mem, hay tat cua so nay nhe!
echo.

:: Dam bao thu muc hien hanh la thu muc chua file .bat
cd /d "%~dp0"

:: Chay Streamlit an duoi nen bang Python module
start "" /B python -m streamlit run src/main.py --server.headless true >nul 2>&1

:: Doi 3 giay de Server kip khoi dong
timeout /t 3 /nobreak >nul

:: Mo Chrome o che do App
start chrome --app=http://localhost:8501

:: Giu cua so console mo
cmd /k

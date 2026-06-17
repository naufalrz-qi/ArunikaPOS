@echo off
echo ========================================================
echo           MEMULAI ARUNIKA POS & BACKGROUND WORKER
echo ========================================================
echo.

echo [1] Menjalankan Django-Q2 Worker (Latar Belakang)...
start "Arunika POS - Background Worker" cmd /k "venv\Scripts\activate && python manage.py qcluster"

echo [2] Menjalankan Django Web Server...
start "Arunika POS - Web Server" cmd /k "venv\Scripts\activate && python manage.py runserver"

echo.
echo Proses telah dimulai di dua jendela terpisah!
echo Anda bisa menutup jendela launcher ini.
exit

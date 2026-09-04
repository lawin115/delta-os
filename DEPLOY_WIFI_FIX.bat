@echo off
title Delta OS - Deploy Universal WiFi & Superchannel Fix
echo ========================================================
echo   Deploying Universal Wi-Fi & Superchannel 4.9G-6.1G Fix
echo ========================================================
echo.
echo Connecting to router at 192.168.88.1...
"C:\Users\delta\AppData\Local\Programs\Python\Python310\python.exe" deploy_and_verify_all.py
echo.
pause

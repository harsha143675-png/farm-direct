@echo off
echo ========================================================
echo        Starting FarmDirect Web Application
echo    Direct Farmer-to-Consumer Platform (0%% Mediators)
echo ========================================================
echo.
echo Server starting at http://127.0.0.1:5000 ...
echo Press Ctrl+C in this window to stop the server.
echo.
start http://127.0.0.1:5000
python app.py
pause

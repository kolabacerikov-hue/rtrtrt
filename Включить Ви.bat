@echo off
chcp 65001 >nul
title Запуск Джонни Сильверхенда

echo [1/2] Запускаю скрытый server Ollama на видеокарте...
start "" "%USERPROFILE%\AppData\Local\Programs\Ollama\ollama.exe" serve
timeout /t 5 >nul

echo [2/2] Включаю голосовую систему Джонни с Рабочего стола...
python "%USERPROFILE%\Desktop\fly.py"

pause

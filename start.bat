python -m venv .venv
.venv/Scripts/activate.bat
python -m pip install -r requirements.txt
cd C://"Program Files"/Google/Chrome/Application/
./chrome.exe --remote-debugging-port=9222
@echo off
echo Хром запустился
echo Зайдите в аккаунт, если вы этого еще не сделали.
echo Отредактируйте в файле config.json значения.
echo Нажмите Enter, чтобы продолжить или Ctrl+C, чтобы выйти.
set /p dummy=
echo Скрипт запускается!
pause
python main.py

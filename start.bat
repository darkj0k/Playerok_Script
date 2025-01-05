python -m venv .venv
.venv/Scripts/activate.bat
python -m pip install -r requirements.txt
cd C://"Program Files"/Google/Chrome/Application/
chrome.exe --remote-debugging-port=9222

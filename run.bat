@echo off
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate
    echo Installing requirements...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate
)
python main.py
pause

@echo off
call venv\Scripts\activate
pyrcc5 resources.qrc -o resources.py
pyinstaller --onefile --windowed --icon=icon.ico --name=GoogleForm main.py
pause
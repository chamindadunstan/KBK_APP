@echo off
echo ===============================
echo Building EXE for main.py
echo ===============================

REM Clean previous build
rmdir /s /q build
rmdir /s /q dist
del main.spec

REM Build EXE with waveform, views, and ttk included
pyinstaller --onefile --windowed --clean ^
--icon=assets/app.ico ^
--add-data "waveform.py;." ^
--add-data "views;views" ^
--add-data "assets/app.ico;assets" ^
--add-data "assets/kbk.ico;assets" ^
--hidden-import=tkinter.ttk ^
main.py

echo ===============================
echo Build complete!
echo Your EXE is in the /dist folder
echo ===============================
pause
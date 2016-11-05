@echo 1.Generate Spec File
@echo 2.Pack
set /p c=Choose:
if /i "%c%"=="1" goto firstrun
if /i "%c%"=="2" goto pack
echo No
ping -n 2 localhost>nul
:firstrun
cls
cd dist
pyi-makespec -F Game.py
goto end
:pack
cls
cd dist
rmdir /s /q build
rmdir /s /q dist
pyinstaller --clean -F --log-level DEBUG Game.spec
goto end
:end
pause

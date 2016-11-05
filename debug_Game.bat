@echo off
start pydoc.bat
cd dist
cls
call Game.py
cd ..
move /Y dist\*.log .\
pause

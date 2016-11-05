@echo off
cd dist
cls
pydoc -w Game
cd ..
move .\dist\Game.html .\
exit

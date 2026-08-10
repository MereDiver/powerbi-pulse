@echo off
setlocal
python "%~dp0..\launch.py" %*
if errorlevel 1 pause


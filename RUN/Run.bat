@echo off
SET EVENTLOGGER_DEBUG=False
start /B python\App\python.exe website\project\manage.py runserver 0.0.0.0:8000 --insecure
PING -n 20 127.0.0.1>nul
start http://127.0.0.1:8000
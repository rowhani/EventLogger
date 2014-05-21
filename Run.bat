@echo off
SET EVENTLOGGER_DEBUG=True
start /B python\App\python.exe website\project\manage.py runserver --insecure
PING -n 5 127.0.0.1>nul
start http://127.0.0.1:8000
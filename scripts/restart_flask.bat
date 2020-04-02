@echo off 
if "%1" == "h" goto begin 
mshta vbscript:createobject("wscript.shell").run("%~nx0 h",0)(window.close)&&exit 
:begin
C:
cd C:\smsplatform
call venv\Scripts\activate
tasklist|findstr -i "python.exe"
if ERRORLEVEL 1 (
  start /b python server.py 8080
  start /b python server.py 8081
  start /b python server.py 8082
  start /b python server.py 8083
) else (
  taskkill /F /IM python.exe /T
  start /b python server.py 8080
  start /b python server.py 8081
  start /b python server.py 8082
  start /b python server.py 8083
)


exit  
@echo off 
if "%1" == "h" goto begin 
mshta vbscript:createobject("wscript.shell").run("%~nx0 h",0)(window.close)&&exit 
:begin
D:
cd D:\smsplatform
call venv\Scripts\activate
tasklist|findstr -i "python.exe"
if ERRORLEVEL 1 (
  start /b python server.py 8088
  start /b python server.py 8081
  start /b python server.py 8082
  start /b python server.py 8083
  start /b python server.py 8084
  start /b python server.py 8085
  start /b python server.py 8086
  start /b python server.py 8087
) else (
  taskkill /F /IM python.exe /T
  start /b python server.py 8088
  start /b python server.py 8081
  start /b python server.py 8082
  start /b python server.py 8083
  start /b python server.py 8084
  start /b python server.py 8085
  start /b python server.py 8086
  start /b python server.py 8087
)


exit  
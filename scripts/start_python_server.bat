C:
cd C:\smsplatform
call venv\Scripts\activate

start /b python server.py 8080
start /b python server.py 8081
start /b python server.py 8082
start /b python server.py 8083

exit  
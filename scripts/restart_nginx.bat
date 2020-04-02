C:
cd C:\nginx-1.16.1
tasklist|findstr -i "nginx.exe"
if ERRORLEVEL 1 (
  start nginx.exe
) else (
  start nginx.exe -s reload
)
exit  
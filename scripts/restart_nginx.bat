D:
cd D:\nginx-1.29.2
tasklist|findstr -i "nginx.exe"
if ERRORLEVEL 1 (
  start nginx.exe
) else (
  start nginx.exe -s reload
)
exit  
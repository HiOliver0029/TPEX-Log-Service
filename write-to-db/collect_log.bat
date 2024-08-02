@echo off
setlocal

REM 取得主機名稱
for /f "tokens=2 delims==" %%i in ('"wmic computersystem get name /value"') do set "HOST_NAME=%%i"

REM 取得主機IP
for /f "tokens=2 delims==" %%i in ('"wmic nicconfig get ipaddress /value"') do set "HOST_IP=%%i"
set "HOST_IP=%HOST_IP:~2,-2%"

REM 設定系統代碼
set "SYSTEM_TYPE=EBTS.P"

REM 設定Log等級
set "LEVEL=INFO"

REM 取得當前時間
@REM for /f "tokens=1-3 delims=:" %%a in ('time /t') do set "TIME=%%a%%b%%c"
@REM for /f "tokens=1-3 delims=/" %%a in ('date /t') do set "DATE=%%a%%b%%c"
@REM set "LOG_TIME=%DATE%%TIME%"
set "LOG_TIME=%LOG_TIME%"
echo %LOG_TIME%

REM 設定Log來源程序
set "PROCESS_NAME=SampleProcess"

REM 設定Log內容
set "CONTENT=This is a sample log message"

REM 生成JSON格式
set "LOG_JSON={\"HOST_NAME\":\"%HOST_NAME%\",\"HOST_IP\":\"%HOST_IP%\",\"SYSTEM_TYPE\":\"%SYSTEM_TYPE%\",\"LEVEL\":\"%LEVEL%\",\"PROCESS_NAME\":\"%PROCESS_NAME%\",\"CONTENT\":\"%CONTENT%\",\"LOG_TIME\":\"%LOG_TIME%\"}"

REM 輸出JSON到檔案
echo %LOG_JSON% > log.json

REM 傳送至伺服器
curl -X POST -H "Content-Type: application/json" -d "%LOG_JSON%" http://localhost:5000/log

endlocal

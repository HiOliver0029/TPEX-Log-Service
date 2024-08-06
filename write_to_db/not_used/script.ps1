
# 取得主機名稱、IP、系統類型等資訊
$hostname = hostname
$ipaddress = (Invoke-WebRequest http://ipinfo.io/ip -UseBasicParsing).Content

# 讀取組態檔案來獲取 SYSTEM_TYPE
$config = Get-Content "config.cfg" | Select-String "type=" | ForEach-Object { $_ -replace "type=", "" }
$systemtype = $config.Trim()

$level = "INFO"
$processname = "SampleProcess"

# 設定檔案路徑及已讀取的行數記錄
$logFilePath = "test.log"
$offsetFile = "offset.txt"

# 檢查並創建 offset 文件
if (-not (Test-Path $offsetFile)) {
    0 > $offsetFile
}

# 讀取已讀取的行數
$offset = [int](Get-Content $offsetFile)

# 讀取新內容
$logEntries = Get-Content $logFilePath | Select-Object -Skip $offset
$newOffset = (Get-Content $logFilePath).Count

# 更新 offset
$newOffset > $offsetFile

# 處理每一行新的Log內容
foreach ($line in $logEntries) {
    # 取得目前時間並格式化成 ISO 8601 格式
    $logtime = Get-Date -Format s

    # 解析 CONTENT 中的 value 部分
    # $content = $line | ConvertFrom-Json | Select-Object -ExpandProperty value

    # 組合 JSON 字串
    $json = @{
        HOST_NAME = $hostname
        HOST_IP = $ipaddress
        SYSTEM_TYPE = $systemtype
        LEVEL = $level
        PROCESS_NAME = $processname
        CONTENT = $line
        LOG_TIME = $logtime
    } | ConvertTo-Json


    # 將 JSON 寫入檔案
    $json | Out-File -FilePath log.json -Append

    # 使用 Invoke-WebRequest 發送 POST 請求
    Invoke-WebRequest -Uri http://localhost:5000/log -Method POST -ContentType "application/json" -Body $json
}

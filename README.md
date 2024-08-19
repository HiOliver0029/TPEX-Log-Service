##  Log Service
這是一個可以新增跟查詢 log 的專案，其中新增 log 的功能在`processor_collector`資料夾，查詢 log 的功能及 UI 在`express-app`資料夾。

### 查詢 Log 的功能及 UI
#### 安裝依賴項
進入`express-app`資料夾，在terminal輸入`npm install`安裝所需套件。  
`npm start`啟動專案。  

#### 連結資料庫
進入`express-app`資料夾，新增一個`.env`檔，自行輸入以下資訊以連結至自己的資料庫。
```
DB_USER=username
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_DATABASE=yourdb
```
接著開啟terminal輸入`node app.js`開始使用查詢功能。（在此之前請安裝node及相關套件）  
#### 瀏覽
打開瀏覽器輸入`localhost:3000`可看到查詢 log 的網頁 UI。透過輸入關鍵字進行搜尋（可複合查詢），如下圖。若未輸入任何欄位就按下Search，則預設會返回所有logs. 點擊 `Dark Mode` 可以切換為夜間模式，搜尋結果可以透過`Download Search Result`按鈕下載為 .CSV 檔案。    

![前端介面](/images/express-appUI.png)

### 新增 Log 功能
首先進入`processor_collector`資料夾。

#### 檔案關連與概要
進入 `processor_collector` 資料夾並先開啟 `logger.py` 後，可執行 `collector.py` 跟 `monitor processor.py` 來處理 `config.cfg` 檔案中所寫的log檔案。  

`processor.py` 將會記錄目前已寫入到第幾行log(藉由創立並讀取 `offsets_{Date}.json` )，並將尚未處理過的原始log資料以及如何處理資料的正則表達式POST給 `collector.py`。  

接著由 `collector.py` 根據規則取出所需資料後 POST 給 `logger.py`，最後藉由 `logger.py` 檢查格式是否錯誤並POST到資料庫。  

成功後可以從 `express-app` 的資料夾中透過 `node app.js` 開啟前端查看資料庫中的資料。 

#### 開啟檔案指令與詳細說明
##### 與 DB 連接的 Logger Service
進入`processor_collector`資料夾下的`logger`資料夾。需額外創建 `db_config.txt`，在裡面輸入資訊後以連接至自己的資料庫。以下是 `db_config.txt` 的範例檔
```
[DEFAULT]  
user=username
password=yourpassword  
host=localhost  
database=yourdb  
```
透過`create_table.md`內的指令在自行指定的 MySQL Database 內建立資料庫及 table，並將此 table 命名為 `log_data`.
接著透過執行以下指令開啟server.
```python logger.py```

##### 轉換格式的 Collector
透過以下指令開啟 collector.
```python collector.py```
Collector 負責去接收客戶打過來的初始資料，並依照客戶端提供 Regex 格式切割傳近來的 Raw Data ， 成功切割後 post 給負責將 data 寫入 data base 的 microservice。

**身分驗證**
進行身分驗證的流程，是先由 collector 確認連進來的 processor IP 是否在白名單中，如果是在白名單中，則會發送經過 sha256 加密後的 key 發給 processor，有效期限設為24 hr。取得key之後會儲存成json檔，之後可透過讀取該json檔去POST資料給collector，但如果collector關掉，則下次要重新將資料POST給它，就需要再進行一次身分驗證。

**設定白名單**
為了驗證processor的身分，需要建立`whitelist.json`來允許特定IP才能獲取API key，json設定範例如下：
```
{
    "ips": [
        "172.17.9.178",
        "172.17.16.80",
        "172.17.16.81",
        "172.17.16.82",
        "172.17.16.83",
    ]
}
```

##### 客戶端的 Processor
這個檔案會即時監控並傳送客戶端各種程式的 processes 所產生的不同格式之 log 檔案。Processor 會去讀 config 中的相關設定檔，並將IP、host name等相關資料組成 JSON 格式資料，傳送給負責切割檔案的 collector.


<!-- **建立 API key 檔案**
我們需要事先建立 `api_key.json` 檔案，才能將資料 POST 給 collector，範例如下：
```
{
    "collector-api-key": "<1234567890abcdef>"
}
```
其中 <> 的部分請填入由 collector 允許的金鑰以取得權限。 -->

**建立 config 檔案**
我們也需要事先建立 `config.cfg` 檔案，config 檔案需依據 log 的格式進行修改，範例如下：
```
logs:
  - file_path: processor_collector\test_rtfServer.log
    system_type: EBTS
    fields:
      log_time: ^(\d{2}:\d{2}:\d{2})
      level: \s([A-Z]+)\|
      content: \#\s(.+)
    level_rule: {"NORMAL": "INFO"}
```
其中 file_path 是該 log 檔案的絕對路徑，system_type 是系統相關的資訊，fields 則是告訴 collector 如何切割 log 檔案的正則表達式規範。level_rule 則會將原本 log 檔案中特定格式轉換為可以存進資料庫的規則，比如在上面的例子中，原本 log 檔案透過正則表達式抓到的字串可能是'NORMAL'，此時透過此 rule 可以讓 collector 知道要將其轉換為 'INFO' 以符合規範。符合規範的 level 包含 {INFO, WARN, ERRO, DEBUG}.

### 錯誤代碼說明
請參考 `error_code.md` 檔案

### 壓力測試
首先透過 `pip install locust` 指令安裝 locust。
Locust 是一個開源的負載測試工具，可以用來測試系統在高負載情況下的性能。透過 `locustfile_collector.py` 跟 `locustfile_server.py` 二個檔案，可分別對collector跟logger的api進行壓力測試。在終端中分別運行以下命令來啟動: ```locust -f locustfile_collector.py --host=http://localhost:5050``` 
和 
```locust -f locustfile_server.py --host=http://localhost:5000```
然後打開瀏覽器並訪問 http://localhost:8089，會看到 Locust 的 Web 界面。在這裡你可以設置並啟動壓力測試。其中`locustfile_collector.py`是壓力測試的原始碼檔案名稱，`http://localhost:5050`使用目前測試 API 的 IP 跟 Port。

記得在測試前，先把collector和logger打開，並且logger要正確連接至資料庫後再開始測，IP白名單的部分要新增`127.0.0.1`。

在 Locust Web 界面中，你可以設置以下參數：
- Number of users to simulate（模擬的使用者數量）：這是你想要模擬的並發用戶數。
- Spawn rate（生成速率）：每秒生成多少個新的使用者。
點擊 "Start swarming" 按鈕開始測試。

#### Locust 測試報告和參數
平均響應時間（Average response time）：顯示所有請求的平均響應時間。  
每秒請求數（Requests per second, RPS）：顯示每秒處理的請求數量。  
失敗數（Failures）：顯示失敗的請求數量。  
百分位數（Percentiles）：顯示響應時間的百分位數（例如 50%，90%，95%，99%）。  

在Locust網站上有`Statistics`選項，會顯示當前正在測試的API跟相對應資料，如下圖所示。另有`Download Data`的選項，按下後可以看到`Download Report`，點擊後可以看見上述相關資訊的詳細報表，範例如 `https://drive.google.com/file/d/1g-wlys7SK9bj4C6vg3VgRmAiucKBfBXQ/view?usp=sharing`，包含測試結果的基本資訊及圖表。另外，在`Failures`選項中可以看到API失敗的原因，方便除錯。  
![Locust 介面](/images/Locust)
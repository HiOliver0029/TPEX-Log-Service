##  Log Service
這是一個可以新增跟查詢 log 的專案，其中新增 log 的功能在`processor_collector`資料夾，查詢 log 的功能及 UI 在`express-app`資料夾。

### 新增 log 功能
首先進入`processor_collector`資料夾。
#### MySQL Database
需額外創建 `db_config.txt`，在裡面輸入資訊後以連接至自己的資料庫。以下是 `db_config.txt` 的範例檔
```
[DEFAULT]  
user=username
password=yourpassword  
host=localhost  
database=yourdb  
```
透過`create_table.md`內的指令在自行指定的 MySQL Database 內建立資料庫及 table，並將此 table 命名為 `log_data`.

#### Server
執行
``python log_server.py``
來連結至資料庫

#### Client
執行
``python client.py``  
，每次執行此 python client 會產生 10 筆隨機 log 資料並儲存至 DB. 如下圖
![新增log資料](/images/Screenshot%202024-07-31%20114418.png)

#### C 
安裝環境
```
sudo dnf install libcurl-devel #安裝所需函式庫
```
執行
```
gcc -o client2 client2.c -lcurl  
./client2
```

#### Java  
安裝編譯器
```
dnf install java-1.8.0-openjdk-devel
```
執行
```
javac client3.java  
java client3  
```

### 查詢 log 的功能及 UI
### 系統建置
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
### 瀏覽
打開瀏覽器輸入`localhost:3000`可看到查詢 log 的網頁 UI。透過輸入關鍵字進行搜尋（可複合查詢），如下圖。若未輸入任何欄位就按下Search，則會返回所有logs. 點擊 `Dark Mode` 可以切換為夜間模式，搜尋結果可以透過`Download Search Result`按鈕下載為 .CSV 檔案。    

![前端介面](/images/Screenshot%202024-07-30%20171210.png)

### Data Preprocessor
#### 檔案關連與概要
進入 `processor_collector` 資料夾並先開啟 `log_server.py` 後，可執行 `collector.py` 跟 `monitor processor.py` 來處理 `config.cfg` 檔案中所寫的log檔案。  
`monitor processor.py` 將會記錄目前已寫入到第幾行log(藉由創立並讀取 `offsets.json` )，並將尚未處理過的原始log資料以及如何處理資料的正則表達式POST給 `collector.py`。  
接著由 `collector.py` 根據規則取出所需資料後 POST 給 `log_server.py`，最後藉由 `log_server.py` 檢查格式是否錯誤並POST到資料庫。  
成功後可以從 `express-app` 的資料夾中透過 `node app.js` 開啟前端查看資料庫中的資料。
#### 開啟檔案指令與詳細說明
##### 與 DB 連接的 Logger Service
需先建立`db_config.txt`檔案，輸入跟自己資料庫相關的資訊以建立連接，並需要事先在資料庫中建立相關 table (如上方說明)，以下是 `db_config.txt` 的範例檔。
```
[DEFAULT]  
user=username
password=yourpassword  
host=localhost  
database=yourdb  
```
接著透過執行以下指令開啟server.
```python log_server.py```

##### 轉換格式的 Collector
透過以下指令開啟 collector.
```python collector.py```
Collector 負責去接收客戶打過來的初始資料，並依照客戶端提供 Regex 格式切割傳近來的 Raw Data ， 成功切割後 post 給負責將 data 寫入 data base 的 microservice。

##### 客戶端的 Processor
這個檔案會即時監控並傳送客戶端各種程式的 processes 所產生的不同格式之 log 檔案。Processor 會去讀 config 中的相關設定檔，並將IP、host name等相關資料組成 JSON 格式資料，傳送給負責切割檔案的 collector.

config檔案需依據 log 的格式進行修改，範例如下：
```
logs:
  - file_path: processor_collector\test_rtfServer.log
    system_type: EBTS
    fields:
      log_time: ^(\d{2}:\d{2}:\d{2})
      level: \s([A-Z]+)\|
      content: \#\s(.+)
```
其中 file_path 是該 log 檔案的絕對路徑，system_type 是系統相關的資訊，fields 則是告訴 collector 如何切割 log 檔案的正則表達式規範。
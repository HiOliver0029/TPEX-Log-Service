##  Log Service
這是一個可以新增跟查詢 log 的專案，其中新增 log 的功能在`write-to-db`資料夾，查詢 log 的功能及 UI 在`express-app`資料夾。

### 新增 log 功能
首先進入`write-to-db`資料夾。
#### MySQL Database
需額外創建 db_config.txt，在裡面輸入資訊後以連接至自己的資料庫。以下是 db_config.txt 的範例檔
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
#### 相關檔案
進入`write-to-db`資料夾並開啟`log_server.py`後，可執行`script.py`來處理`rtfServer`的log檔案，將會記錄目前已寫入到第幾行log(透過offset.txt)，並將資料藉由`log_server.py` POST到資料庫。
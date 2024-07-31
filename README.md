##  Logger Service
這是一個模擬client發送請求到server，並可以在資料庫新增data的一套log程式

### client發送post請求
#### Database
需額外創建db_config.txt，在裡面輸入資訊後才能連接至自己的資料庫。以下是db_config.txt的範例檔
```
[DEFAULT]  
user=username
password=yourpassword  
host=localhost  
database=yourdb  
```
在自行指定的Database內建立table，並將此table命名為'log_data'.

#### Python
執行
``python client.py``  

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

### 查詢介面
### 建置
進入`express-app`資料夾，建立一個`.env`檔，自行輸入以下資訊以連結至自己的資料庫。
```
DB_USER=username
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_DATABASE=yourdb
```
接著開啟terminal輸入`node app.js`開始使用查詢功能。（在此之前請安裝node及指定套件）  
### 瀏覽
打開瀏覽器輸入`localhost:3000`可看到查詢log的網頁。透過輸入關鍵字進行搜尋，如下圖。若未輸入任何欄位就按下Search，則會返回所有logs.  
![前端介面](/images/Screenshot%202024-07-30%20171210.png)
搜尋結果可以透過Download按鈕下載為CSV檔案。

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

### 前端查詢介面
打開瀏覽器輸入`localhost:5000`可看到查詢log的輸入欄位。透過輸入關鍵字進行搜尋，如下圖。若未輸入任何欄位就按下Search，則會返回所有logs.  
![螢幕擷取畫面 2024-07-29 114615](https://github.com/user-attachments/assets/70c13560-8b23-429d-a2a7-717c0359784d)


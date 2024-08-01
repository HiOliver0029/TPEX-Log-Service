建立新DB跟table  
```sql
-- Create the log database
CREATE DATABASE logdb;

-- Switch to the log database
USE logdb;

-- Create the log table
CREATE TABLE log_data (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    HOST_NAME VARCHAR(16),
    HOST_IP VARCHAR(15),
    SYSTEM_TYPE VARCHAR(20),
    LEVEL VARCHAR(4),
    PROCESS_NAME VARCHAR(64),
    CONTENT VARCHAR(512),
    LOG_TIME DATETIME,
    TIMESTAMP TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
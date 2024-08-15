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

-- -- Create the api key table
-- CREATE TABLE api_key (
--     HOST_IP VARCHAR(15) PRIMARY KEY,
--     HASHED_KEY VARCHAR(64),  -- 假設 hashed_key 為 64 個字元的雜湊值
--     EXPIRATION_DATE DATETIME
-- );
```
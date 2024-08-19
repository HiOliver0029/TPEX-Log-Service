-- Create the log table
CREATE TABLE IF NOT EXISTS log_data (
    ID INT PRIMARY KEY AUTO_INCREMENT,
    HOST_NAME VARCHAR(32),
    HOST_IP VARCHAR(15),
    SYSTEM_TYPE VARCHAR(20),
    LEVEL VARCHAR(6),
    PROCESS_NAME VARCHAR(64),
    CONTENT VARCHAR(512),
    LOG_TIME DATETIME,
    TIMESTAMP TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
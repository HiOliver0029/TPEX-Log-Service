import os
import platform
import requests
import json
import socket
from datetime import datetime

# 功能：
# 取得主機資訊（System type, Host name, Host IP），並傳送給 Collector。
# 指定字串切割的規則，並告知 Collector。
# 監視指定的 log 檔案，將新的 log 資料依據指定的規則進行處理，組成 Format A 的資料，傳送至 Collector。

# 設定檔案路徑及已讀取的行數記錄
# log_file_path = 'rtfServer.log'
log_file_path = 'test.log'
offset_file = 'offset.txt'
config_file = 'config.cfg'

# 讀取組態檔案來獲取 SYSTEM_TYPE
def get_system_type(config_file):
    with open(config_file, 'r') as f:
        for line in f:
            if line.startswith('type='):
                return line.split('=')[1].strip()
    return "Unknown"

# 取得系統類型
system_type = get_system_type(config_file)

# 取得主機名稱
# hostname = os.uname().nodename
name = platform.uname()
hostname = name.node

# 取得主機IP
def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # 這裡使用 8.8.8.8 作為 DNS 伺服器，您也可以使用其他 DNS 伺服器
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception as e:
        ip = "Could not get the IP"
    finally:
        s.close()
    return ip
ipaddress = get_ip()

def get_process(file_path):
    # Split the path by "."
    parts = file_path.split(".")

    # Extract the process name (assuming the first part is the process name)
    if len(parts) > 0:
        process_name = parts[0]
    else:
        process_name = "unknown"  # Handle cases where there's no "." in the path
    return process_name
# log 檔案名稱(第一個.之前)
process_name = get_process(log_file_path)

# 傳送主機資訊給 Collector
host_info = {
    "SYSTEM_TYPE": system_type,
    "HOST_NAME": hostname,
    "HOST_IP": ipaddress,
    "PROCESS_NAME": process_name
}
print(host_info)
requests.post('http://localhost:5050/host_info', json=host_info)

# 設定切割規則並傳送給 Collector
split_rule = {
    "log_time_regex": r"(\d{2}:\d{2}:\d{2})",
    "level_regex": r"\s([A-Z]+)\|",
    "message_regex": r"#\s(.+)"
}
print(split_rule)
requests.post('http://localhost:5050/split_rule', json=split_rule)

# 讀取已讀取的行數
if not os.path.exists(offset_file):
    with open(offset_file, 'w') as f:
        f.write('0')

with open(offset_file, 'r') as f:
    offset = int(f.read().strip())

with open(log_file_path, 'r') as f:
    lines = f.readlines()
    new_content = lines[offset:]
    offset = len(lines)

# 更新 offset
with open(offset_file, 'w') as f:
    f.write(str(offset))

# 傳送新內容至 Collector
for line in new_content:
    log_data = {
        "raw_message": line.strip()
    }
    print("Raw data:", log_data)
    requests.post('http://localhost:5050/raw_log', json=log_data)
import os
import socket
import platform
import json
import requests
import yaml
import hashlib
import time
from datetime import datetime

# 配置檔案路徑
config_file = 'config.cfg'
offsets_file = 'hash_offsets.json'
api_key_file = 'api_key.json'

# 讀取配置檔案
def load_config(config_file):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    return config

config = load_config(config_file)

# 讀取API密鑰
def load_api_key(api_key_file):
    with open(api_key_file, 'r') as f:
        api_key = yaml.safe_load(f)
    return api_key

api_key = load_api_key(api_key_file)

# 保存偏移量
def save_offsets(offsets):
    with open(offsets_file, 'w') as f:
        json.dump(offsets, f, indent=4)

# 讀取偏移量
def load_offsets():
    if not os.path.exists(offsets_file):
        return {}
    with open(offsets_file, 'r') as f:
        return json.load(f)

offsets = load_offsets()

# 取得主機資訊
def get_host_info():
    name = platform.uname()
    host_name = name.node
    ip_address = socket.gethostbyname(socket.gethostname())
    return host_name, ip_address

host_name, ip_address = get_host_info()

# 計算文件哈希值
def calculate_hash(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

# 檢查文件是否發生變更
def check_files(log_configs):
    for log_config in log_configs:
        file_path = log_config['file_path']
        new_hash = calculate_hash(file_path)
        old_hash = offsets.get(file_path)

        if new_hash != old_hash:
            print(f"File {file_path} has changed.")
            offsets[file_path] = new_hash
            save_offsets(offsets)
            event_handler.process(file_path)  # 調用處理函數

# 檔案變更處理類
class LogHandler:
    def __init__(self, config):
        self.config = config

    def process(self, file_path):
        for log_config in self.config['logs']:
            if log_config['file_path'] == file_path:
                print("Now handling file:", file_path)
                self.handle_log(log_config)

    def handle_log(self, log_config):
        file_path = log_config['file_path']

        with open(file_path, 'r', encoding='big5', errors='ignore') as f:
            lines = f.readlines()

        # 處理新增加的 log 行
        for line in lines:
            fields = log_config['fields']
            regex = {
                "log_time_regex": fields['log_time'],
                "level_regex": fields['level'],
                "message_regex": fields['content']
            }
            # 組合 Format A 的資料
            log_data = {
                "HOST_NAME": host_name,
                "HOST_IP": ip_address,
                "SYSTEM_TYPE": log_config['system_type'],
                "PROCESS_NAME": os.path.basename(log_config['file_path']).split('.')[0],
                "REGEX": regex,
                "RAW_LOG": line.strip(),
                "TIMESTAMP": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            print("Raw data:", log_data)
            # 發送資料到 Collector
            self.send_to_collector(log_data)

    def send_to_collector(self, log_data):
        try:
            response = requests.post('http://localhost:5050/contentA', json=log_data, headers=api_key)
            if response.status_code == 201:
                print(f"Log sent successfully: {response.status_code}")
            elif response.status_code == 400:
                print(f"Log error (Data missing): {response.status_code}, {response.json().get('error')}")
            elif response.status_code == 401:
                print(f"API key error: {response.status_code}, {response.json().get('error')}")
            elif response.status_code == 402:
                print(f"Log error (Level issue): {response.status_code}, {response.json().get('error')}")
            else:
                print(f"Unexpected error: {response.status_code}, {response.json().get('error')}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending log data to collector: {e}")

# 主循環
if __name__ == "__main__":
    config = load_config(config_file)
    offsets = load_offsets()
    event_handler = LogHandler(config)

    try:
        while True:
            check_files(config['logs'])
            time.sleep(1)  # 每隔 1 秒檢查一次文件狀態
    except KeyboardInterrupt:
        print("Stopping the file watcher.")

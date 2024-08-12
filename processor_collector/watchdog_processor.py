import os
import socket
import platform
import subprocess
import json
import requests
import yaml
import re
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

curr_time = datetime.now().strftime('%Y%m%d')

# 配置檔案路徑
config_file = 'config.cfg'
offsets_file = f'offsets_{curr_time}.json'
api_key_file = 'api_key.json'

# 讀取配置檔案
def load_config(config_file):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    return config

config = load_config(config_file)

def load_api_key(api_key_file):
    with open(api_key_file, 'r') as f:
        api_key = yaml.safe_load(f)
    return api_key

api_key = load_api_key(api_key_file)

# 保存偏移量
def save_offsets(offsets):
    with open(offsets_file, 'w') as f:
        json.dump(offsets, f, indent=4) # 使用缩进确保每个日志文件的偏移量在单独的行上

# 讀取偏移量
def load_offsets():
    if not os.path.exists(offsets_file):
        return {}
    with open(offsets_file, 'r') as f:
        return json.load(f)

offsets = load_offsets() 
print("offsets: ", offsets)

# 取得主機資訊
# def get_host_info():
#     name = platform.uname()
#     host_name = name.node
#     ip_address = socket.gethostbyname(socket.gethostname())
#     return host_name, ip_address

# host_name, ip_address = get_host_info()
class HostInfo:
    @staticmethod
    def get_host_info():
        system_type = platform.system()  # 判斷系統類型
        if system_type == "Windows":
            # Windows 系統的處理方式
            name = platform.uname()
            host_name = name.node
            ip_address = socket.gethostbyname(socket.gethostname())
        elif system_type == "Linux":
            # Linux 系統的處理方式
            subprocess.run(['chmod', '+x', 'get_host_info.sh'])
            result = subprocess.run(['./get_host_info.sh'], capture_output=True, text=True)
            host_name = None
            host_ip = None
            for line in result.stdout.splitlines():
                if line.startswith("HOST_NAME="):
                    host_name = line.split('=', 1)[1].strip()
                elif line.startswith("HOST_IP="):
                    host_ip = line.split('=', 1)[1].strip()
            if not host_name or not host_ip:
                raise ValueError("HOST_NAME or HOST_IP not found in script output")
        else:
            raise ValueError(f"Unsupported system type: {system_type}")

        return host_name, ip_address if system_type == "Windows" else host_ip

host_name, ip_address = HostInfo.get_host_info()

# 檔案變更處理類
class LogHandler(FileSystemEventHandler):
    def __init__(self, config):
        self.config = config
        self.offsets = offsets
        #初始化,更新一遍所有log狀態
        for log_config in self.config['logs']:
            self.process(log_config['file_path'])

    def on_modified(self, event):
        if event.is_directory:
            return
        # print("New log data added.")
        self.process(event.src_path)

    def process(self, file_path):
        for log_config in self.config['logs']:
            if log_config['file_path'] == file_path:
                print("Now handling file:", file_path)
                self.handle_log(log_config)

    # def handle_log(self, log_config):
    #     file_path = log_config['file_path']
    #     last_offset = self.offsets.get(file_path, 0)
    #     print("Last offset (上次處理到第幾行): ", last_offset)

    #     with open(file_path, 'r', encoding='big5', errors='ignore') as f:
    #         lines = f.readlines()
    #         print(f"Length of file (目前檔案共有幾行):", len(lines))
            
    #     new_lines = []  # 确保 new_lines 有默认值
    #     # 如果新行數大於上次記錄的偏移量，處理新增加的行
    #     if last_offset < len(lines):
    #         print("Log file change detected, start posting new data.")
    #         new_lines = lines[last_offset:]
    #         self.offsets[file_path] = len(lines)
    #         save_offsets(self.offsets)
    #     else:
    #         print("No new log added.")
   
    #     # 處理新增加的 log 行
    #     for line in new_lines:
    #         fields = log_config['fields']
    #         regex = {
    #             "log_time_regex": fields['log_time'],
    #             "level_regex": fields['level'],
    #             "message_regex": fields['content']
    #         }
    #         # 組合 Format A 的資料
    #         log_data = {
    #             "HOST_NAME": host_name,
    #             "HOST_IP": ip_address,
    #             "SYSTEM_TYPE": log_config['system_type'],
    #             "PROCESS_NAME": os.path.basename(log_config['file_path']).split('.')[0],
    #             "REGEX": regex,
    #             "RAW_LOG": line.strip(),
    #             "TIMESTAMP": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #         }
    #         print("Raw data:", log_data)
    #         # 發送資料到 Collector
    #         self.send_to_collector(log_data)

    def handle_log(self, log_config):
        file_path = log_config['file_path']
        last_offset = self.offsets.get(file_path, 0)
        print("Last offset (上次處理到第幾行): ", last_offset)

        with open(file_path, 'r', encoding='big5', errors='ignore') as f:
            lines = f.readlines()
            print(f"Length of file (目前檔案共有幾行):", len(lines))
                
        new_lines = []  # 確保 new_lines 有默認值
        # 如果新行數大於上次記錄的偏移量，處理新增加的行
        if last_offset < len(lines):
            print("Log file change detected, start posting new data.")
            new_lines = lines[last_offset:]
        else:
            print("No new log added.")
    
        # 處理新增加的 log 行
        for i, line in enumerate(new_lines):
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
            
            # 更新 offset 為目前處理的行數 (每寫一行更新一次，避免程式非預期shutdown)
            self.offsets[file_path] = last_offset + i + 1
            save_offsets(self.offsets)

    def send_to_collector(self, log_data):
        try:
            response = requests.post('http://localhost:5050/contentA', json=log_data, headers=api_key)
            # response = requests.post('http://172.20.10.3:5050/log', json=log_data)
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

if __name__ == "__main__":
    config = load_config(config_file)
    event_handler = LogHandler(config)
    observer = Observer()

    # 為每個 log 文件監視變化
    for log_config in config['logs']:
        # print("Content of the config: ")
        # print("File Path:", log_config['file_path'])
        # print("System Type:", log_config['system_type'])
        # print("Regex:", log_config['fields'])
        observer.schedule(event_handler, path=os.path.dirname(log_config['file_path']), recursive=False)

    observer.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
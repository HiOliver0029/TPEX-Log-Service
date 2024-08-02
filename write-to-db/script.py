import os
import platform
import requests
import json
from datetime import datetime

# 讀取組態檔案來獲取 SYSTEM_TYPE
def get_system_type(config_file):
    with open(config_file, 'r') as f:
        for line in f:
            if line.startswith('type='):
                return line.split('=')[1].strip()
    return "Unknown"

# 設定檔案路徑及已讀取的行數記錄
# log_file_path = 'rtfServer.log'
log_file_path = 'rtfServer.log'
offset_file = 'offset.txt'
config_file = 'config.cfg'

# 取得系統類型
system_type = get_system_type(config_file)

# 取得主機名稱
# hostname = os.uname().nodename
hostname = platform.uname()
# print(hostname.node)

# 取得主機IP
ipaddress = requests.get('http://ipinfo.io/ip').text.strip()
# print(ipaddress)

# 設定其他固定資訊
process_name = "SampleProcess"

# 讀取已讀取的行數
if not os.path.exists(offset_file):
    with open(offset_file, 'w') as f:
        f.write('0')

with open(offset_file, 'r') as f:
    offset = int(f.read().strip())

# 讀取新內容
new_content = []
with open(log_file_path, 'r') as f:
    lines = f.readlines()
    new_content = lines[offset:]
    new_offset = len(lines)

# 更新 offset
with open(offset_file, 'w') as f:
    f.write(str(new_offset))

def extract_level(line):
  """從一行日志中提取 level。"""
  # 從右邊開始找到 '|' 的索引
  pipe_index = line.rfind('|')
  # 從 '|' 的索引往前找到空格的索引
  space_index = line[:pipe_index].rfind(' ')
  # 取出空格到 '|' 之間的字串
  level = line[space_index+1:pipe_index]
  return level

# 處理每一行新的Log內容
for line in new_content:
    level = extract_level(line)
    print(level)

    # 取得目前時間並格式化成 ISO 8601 格式
    log_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 組合 JSON 資料
    log_data = {
        "HOST_NAME": hostname.node,
        "HOST_IP": ipaddress,
        "SYSTEM_TYPE": system_type,
        "LEVEL": level,
        "PROCESS_NAME": process_name,
        "CONTENT": line.strip(),
        "LOG_TIME": log_time
    }

    # 將 JSON 寫入檔案
    with open('log.json', 'a') as f:
        json.dump(log_data, f)
        f.write('\n')

    # 使用 requests 發送 POST 請求
    response = requests.post('http://localhost:5000/log', json=log_data)
    print(response.status_code, response.text)

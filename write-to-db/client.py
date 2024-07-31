import requests
import random
import json
from datetime import datetime

# 伺服器 URL
#url = "http://172.17.16.83:22/log"
url = "http://localhost:5000/log"

# 生成隨機的日誌數據
system_type = ["EBTS.P", "EBTS.S", "TADS.L"]
levels = ["INFO", "WARN", "ERRO"]
log_entries = []

for i in range(10):
    log_entry = {
        "HOST_NAME": f"Test_{i} Python",
        "HOST_IP": f"172.17.34.{random.randint(1, 254)}",
        "SYSTEM_TYPE": random.choice(system_type),
        "LEVEL": random.choice(levels),
        "PROCESS_NAME": f"Example_{i}",
        "CONTENT": f"This is a log entry content {i}.",
        "LOG_TIME": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    log_entries.append(log_entry)

# 發送 POST 請求
for log_entry in log_entries:
    response = requests.post(url, json=log_entry)
    if response.status_code == 201:
        print("Log entry sent successfully.")
    else:
        print(f"Failed to send log entry. Status code: {response.status_code}")
        print(f"Message: {response.json().get('message')}")

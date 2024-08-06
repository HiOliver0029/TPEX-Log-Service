from flask import Flask, request, jsonify
import requests
import json
import re
from datetime import datetime

# 功能：
# 接收 Client 傳來的主機資訊及切割規則。
# 監聽 Client 傳來的原始 log 資料，依據規則切割取得所需欄位。
# 將處理後的 log 資料結合主機資訊和 SYSTEM_TYPE，然後發送至最終的儲存端點。

app = Flask(__name__)

host_info = {}
split_rule = {}

@app.route('/host_info', methods=['POST'])
def receive_host_info():
    global host_info
    host_info = request.json
    return jsonify({"message": "Host information received"}), 200

@app.route('/split_rule', methods=['POST'])
def receive_split_rule():
    global split_rule
    split_rule = request.json
    return jsonify({"message": "Split rule received"}), 200

@app.route('/raw_log', methods=['POST'])
def process_raw_log():
    raw_log = request.json.get('raw_message')
    # print(raw_log)
    
    # 使用正則表達式提取資料
    log_time_match = re.search(split_rule['log_time_regex'], raw_log)
    level_match = re.search(split_rule['level_regex'], raw_log)
    message_match = re.search(split_rule['message_regex'], raw_log)
    
    log_time = log_time_match.group(1) if log_time_match else "Unknown"
    level = level_match.group(1) if level_match else "Unknown"
    message = message_match.group(1) if message_match else "Unknown"

    
    # 組合最終的 log 資料
    log_data = {
        "HOST_NAME": host_info.get("HOST_NAME", "Unknown"),
        "HOST_IP": host_info.get("HOST_IP", "Unknown"),
        "SYSTEM_TYPE": host_info.get("SYSTEM_TYPE", "Unknown"),
        "PROCESS_NAME": host_info.get("PROCESS_NAME", "Unknown"),
        "LEVEL": level.upper(),
        "CONTENT": message,
        # "LOG_TIME": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        "LOG_TIME": f"{datetime.now().strftime('%Y-%m-%d')} {log_time}"
    }
    print("Log Data: ",log_data)
    # 傳送 log 資料至最終儲存端點
    response = requests.post('http://localhost:5000/log', json=log_data)
    return jsonify({"message": "Log processed", "status": response.status_code}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)
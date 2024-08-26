from flask import Flask, request, jsonify
import requests
import requests.exceptions
import sys
import json
import re
import hashlib
import secrets
from datetime import datetime, timedelta

# 功能：
# 接收 Client 傳來的主機資訊及切割規則。
# 監聽 Client 傳來的原始 log 資料，依據規則切割取得所需欄位。
# 將處理後的 log 資料結合主機資訊和 SYSTEM_TYPE，然後發送至最終的儲存端點。

app = Flask(__name__)

# 自定義錯誤類別
# 正則表達式錯誤處理
# class LogParseError(Exception):
#     pass

class InvalidLogLevelError(Exception):
    pass

class MissingDataError(Exception):
    pass

class PermissionError(Exception):
    pass

# 支援的日誌級別
SUPPORTED_LEVELS = ['INFO', 'WARN', 'ERRO', 'DEBUG', '']

# 定義IP白名單
# whitelist_ips = [
#     "172.17.9.178",
#     "172.17.16.80",
#     "172.17.16.81",
#     "172.17.16.82",
#     "172.17.16.83",
#     "172.20.10.7",
#     "192.168.95.27",
#     "172.21.128.1"
# ]

# 讀取 IP白名單 JSON 檔案
with open('whitelist.json', 'r') as f:
    data = json.load(f)
# 獲取 IP 白名單
whitelist_ips = data['ips']

# def is_key_valid(api_key, stored_hashed_key, expiration_date):
#     if datetime.now() > expiration_date:
#         return False
#     hashed_key = hashlib.sha256(api_key.encode()).hexdigest()
#     return hashed_key == stored_hashed_key

# 允許的 API 金鑰列表和對應的到期日期
API_KEYS = {} 

# 用戶 API 金鑰的到期時間（例如1小時）
KEY_EXPIRATION_HOURS = 24

# 壓測用
API_KEYS["202408testing"] = datetime.now() + timedelta(hours=KEY_EXPIRATION_HOURS)

def generate_api_key(ip_address):
    api_key = secrets.token_hex(32)  # 生成64字符的隨機字符串
    hashed_key = hashlib.sha256((api_key + ip_address).encode()).hexdigest()  # 用SHA-256加密，包含IP地址作為參數
    expiration_date = datetime.now() + timedelta(hours=KEY_EXPIRATION_HOURS)
    return hashed_key, expiration_date

@app.route('/verify-whitelist', methods=['POST'])
def verify_and_generate_key():
    client_ip = request.json.get('client_ip')
    print("IP:", client_ip)
    if client_ip in whitelist_ips:
        hashed_key, expiration_date = generate_api_key(client_ip)
        API_KEYS[hashed_key] = expiration_date
        print("API_KEYS:", API_KEYS)
        # 回傳API Key給client
        return jsonify({
            "collector-api-key": hashed_key,
            "expire-time": expiration_date.isoformat()
        })
    else:
        return jsonify({"error": "IP not in whitelist"}), 403
def validate_api_key(f):
    def decorator(*args, **kwargs):
        api_key = request.headers.get('collector-api-key')
        expiration_date = API_KEYS.get(api_key)
        if not api_key or not expiration_date:
            return jsonify({"error": "Unauthorized access (Wrong key or collector restarted). Please delete old key and acquire new key."}), 401
        if datetime.now() > expiration_date:
            return jsonify({"error": "API key expired. Please delete old token and acquire new token."}), 401
        return f(*args, **kwargs)
    return decorator

def parse_log(raw_log, split_rule):
    log_time_match = re.search(split_rule['log_time_regex'], raw_log) if isinstance(split_rule['log_time_regex'], str) else None
    level_match = re.search(split_rule['level_regex'], raw_log) if isinstance(split_rule['level_regex'], str) else None
    message_match = re.search(split_rule['message_regex'], raw_log) if isinstance(split_rule['message_regex'], str) else None

    log_time = log_time_match.group(1) if log_time_match else ""
    message = message_match.group(1) if message_match else ""
    level = level_match.group(1).upper() if level_match else ""

    # Apply level_rule conversion (if provided)
    if split_rule.get('level_rule'):
      level = split_rule['level_rule'].get(level, level)

    return log_time, level, message

def check_error(level):    
    # 檢查 log level
    if level not in SUPPORTED_LEVELS:
        raise InvalidLogLevelError(f"Invalid log level: {level}")

@app.route('/send-log', methods=['POST'])
@validate_api_key
def process_raw_log():
    try:
        raw_log = request.json.get('RAW_LOG')
        split_rule = request.json.get('REGEX')
        host_name = request.json.get("HOST_NAME")
        host_ip = request.json.get("HOST_IP")
        system_type = request.json.get("SYSTEM_TYPE")
        process_name = request.json.get("PROCESS_NAME")
        
        # 檢查必需的資料
        missing_fields = [field for field, value in {"raw_log": raw_log, "split_rule": split_rule, "host_name": host_name, "host_ip": host_ip, "system_type": system_type, "process_name": process_name}.items() if not value]

        if missing_fields:
            raise MissingDataError(f"Client missing required fields in the request: {', '.join(missing_fields)}")
        # 檢查必需的資料
        # if not all([raw_log, split_rule, host_name, host_ip, system_type, process_name]):
        #     raise MissingDataError("Missing required fields in the request")

        if host_ip not in whitelist_ips:
            raise PermissionError("IP Not in whitelist. Permission denied.")
            # abort(403, description="Forbidden: IP address not in whitelist")

        log_time, level, message = parse_log(raw_log, split_rule)
        check_error(level)
        
        # 組合最終的 log 資料
        log_data = {
            "HOST_NAME": host_name,
            "HOST_IP": host_ip,
            "SYSTEM_TYPE": system_type,
            "PROCESS_NAME": process_name,
            "LEVEL": level,
            "CONTENT": message,
            "LOG_TIME": f"{datetime.now().strftime('%Y-%m-%d')} {log_time}"
        }
        print("Log Data: ",log_data)

        # 傳送 log 資料至最終儲存端點
        response = requests.post('http://localhost:5000/save-log', json=log_data)
        if response.status_code == 201:
            return jsonify({"message": "Log processed", "status": "success"}), 201
        else:
            return jsonify({"error": response.json().get('message','N/A'), "status": "Error"}), response.status_code
        

    except MissingDataError as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 400
        
    except InvalidLogLevelError as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 402
    
    except PermissionError as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 403

    # except LogParseError as e:
    #     print(f"Error: {e}")
    #     return jsonify({"error": str(e)}), 500
    
    except requests.exceptions.ConnectionError:
        print("Logger or database unavailable. Please restart the logger and database.")
        return jsonify({"error": "Logger or database unavailable. Please restart the logger and database."}), 502

    except Exception as e:
        print(f"Unexpected Error: {e}")
        return jsonify({"error": "Internal server error"}), 500
    
    # 401: API key 錯誤
    # 缺失資料檢查：
    # 在處理 raw_log、split_rule、host_name、host_ip、system_type 和 process_name 等必需字段時，若有任何一個缺失，則引發 MissingDataError 並回傳 HTTP 狀態碼 400。
    # 無效的日誌級別：
    # 若解析出的 level 不在支持的日誌級別清單 (SUPPORTED_LEVELS) 中，則引發 InvalidLogLevelError 並回傳 HTTP 狀態碼 402。
    # IP不在白名單：403
    # 日誌解析錯誤：
    # 若解析 log 時出現問題（例如正則表達式匹配失敗），引發 LogParseError 並回傳 HTTP 狀態碼 500。
    # 連不到 logger：502
    # 一般錯誤處理：
    # 捕捉其他未預期的錯誤並回傳 HTTP 狀態碼 500。

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, threaded = True)


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

# 自定義錯誤類別
# 正則表達式錯誤處理
class LogParseError(Exception):
    pass

class InvalidLogLevelError(Exception):
    pass

class MissingDataError(Exception):
    pass

# 支援的日誌級別
SUPPORTED_LEVELS = ['INFO', 'WARN', 'ERRO', 'DEBUG', '']

# 允許的 API 金鑰列表
API_KEYS = {"1234567890abcdef"}  # 替換成實際的金鑰

# def validate_api_key():
#     api_key = request.headers.get('collector-api-key')
#     print("key: ", api_key)
#     if api_key not in API_KEYS:
#         return False
#     return True

def validate_api_key(f):
    def decorator(*args, **kwargs):
        api_key = request.headers.get('collector-api-key')
        if api_key not in API_KEYS:
            return jsonify({"error": "Unauthorized access"}), 401
        print("API Keys matched.")
        return f(*args, **kwargs)
    return decorator



# 使用正則表達式提取資料
# def parse_log(raw_log, split_rule):
#     log_time_match = re.search(split_rule['log_time_regex'], raw_log)
#     level_match = re.search(split_rule['level_regex'], raw_log)
#     message_match = re.search(split_rule['message_regex'], raw_log)

#     try:
#         log_time = log_time_match.group(1)
#         level = level_match.group(1).upper()
#         message = message_match.group(1)
#     except AttributeError:
#         error_message = f"Failed to parse log: {raw_log}"
#         if not log_time_match:
#             error_message += ", log time not found"
#         if not level_match:
#             error_message += ", level not found"
#         if not message_match:
#             error_message += ", message not found"
#         raise LogParseError(error_message)

#     return log_time, level, message

def parse_log(raw_log, split_rule):
    log_time_match = re.search(split_rule['log_time_regex'], raw_log) if isinstance(split_rule['log_time_regex'], str) else None
    level_match = re.search(split_rule['level_regex'], raw_log) if isinstance(split_rule['level_regex'], str) else None
    message_match = re.search(split_rule['message_regex'], raw_log) if isinstance(split_rule['message_regex'], str) else None
    # print(split_rule['log_time_regex'], isinstance(split_rule['log_time_regex'], str))
    # print(split_rule['level_regex'], isinstance(split_rule['level_regex'], str))

    log_time = log_time_match.group(1) if log_time_match else ""
    message = message_match.group(1) if message_match else ""
    level = level_match.group(1).upper() if level_match else ""

    # Apply level_rule conversion (if provided)
    if split_rule.get('level_rule'):
      level = split_rule['level_rule'].get(level, level)

    return log_time, level, message

def check_error(level):    
    # 處理level (已改到config檔案)
    # if level in ('ERR', 'ERROR'):
    #     level = 'ERRO'
    # elif level in ('NORMAL'):
    #     level = 'INFO'
                
    # 檢查 log level
    if level not in SUPPORTED_LEVELS:
        raise InvalidLogLevelError(f"Invalid log level: {level}")

@app.route('/contentA', methods=['POST'])
@validate_api_key
def process_raw_log():
    # if not validate_api_key():
    #     return jsonify({"error": "Unauthorized access"}), 401
    try:
        raw_log = request.json.get('RAW_LOG')
        split_rule = request.json.get('REGEX')
        host_name = request.json.get("HOST_NAME")
        host_ip = request.json.get("HOST_IP")
        system_type = request.json.get("SYSTEM_TYPE")
        process_name = request.json.get("PROCESS_NAME")
        
        # 檢查必需的資料
        if not all([raw_log, split_rule, host_name, host_ip, system_type, process_name]):
            raise MissingDataError("Missing required fields in the request")

        log_time, level, message = parse_log(raw_log, split_rule)
        
        check_error(level)

        if log_time != "":
            log_datetime = f"{datetime.now().strftime('%Y-%m-%d')} {log_time}"
        else:
            log_datetime = datetime.now().strftime('%Y-%m-%d')
        
        # 組合最終的 log 資料
        log_data = {
            "HOST_NAME": host_name,
            "HOST_IP": host_ip,
            "SYSTEM_TYPE": system_type,
            "PROCESS_NAME": process_name,
            "LEVEL": level,
            "CONTENT": message,
            # "LOG_TIME": log_datetime
            "LOG_TIME": f"{datetime.now().strftime('%Y-%m-%d')} {log_time}"
        }
        print("Log Data: ",log_data)
        # server_api_key = "1234567890abcdef"
        # 傳送 log 資料至最終儲存端點
        response = requests.post('http://localhost:5000/log', json=log_data)
        if response.status_code == 201:
            return jsonify({"message": "Log processed", "status": "success"}), 201
        else:
            return jsonify({"message": "Format error", "status": "Database insert failed"}), response.status_code


    except MissingDataError as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 400

    except InvalidLogLevelError as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 402

    except LogParseError as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

    except Exception as e:
        print(f"Unexpected Error: {e}")
        return jsonify({"error": "Internal server error"}), 500
    
    # 401: API key 錯誤
    # 缺失資料檢查：
    # 在處理 raw_log、split_rule、host_name、host_ip、system_type 和 process_name 等必需字段時，若有任何一個缺失，則引發 MissingDataError 並回傳 HTTP 狀態碼 400。
    # 無效的日誌級別：
    # 若解析出的 level 不在支持的日誌級別清單 (SUPPORTED_LEVELS) 中，則引發 InvalidLogLevelError 並回傳 HTTP 狀態碼 402。
    # 日誌解析錯誤：
    # 若解析 log 時出現問題（例如正則表達式匹配失敗），引發 LogParseError 並回傳 HTTP 狀態碼 500。
    # 一般錯誤處理：
    # 捕捉其他未預期的錯誤並回傳 HTTP 狀態碼 500。

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)

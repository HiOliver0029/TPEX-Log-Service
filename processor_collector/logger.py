from flask import Flask, request, jsonify, send_from_directory
import mysql.connector
import configparser
from mysql.connector import Error
from flask_cors import CORS
import yaml
import os

app = Flask(__name__, static_folder='public')
CORS(app)

# 支援的日誌級別
SUPPORTED_LEVELS = ['INFO', 'WARN', 'ERRO', 'DEBUG', '']

# # 允許的 API 金鑰列表
# API_KEYS = {"1234567890abcdef"}  # 替換成實際的金鑰
# def validate_api_key(f):
#     def decorator(*args, **kwargs):
#         api_key = request.headers.get('server-api-key')
#         if api_key not in API_KEYS:
#             return jsonify({"error": "Unauthorized access"}), 401
#         print("API Keys matched.")
#         return f(*args, **kwargs)
#     return decorator

# 讀取配置文件
config = configparser.ConfigParser()
config.read('db_config.txt')

db_config = {
    'user': config.get('DEFAULT', 'user'),
    'password': config.get('DEFAULT', 'password'),
    'host': config.get('DEFAULT', 'host'),
    'database': config.get('DEFAULT', 'database')
}

# @app.route('/', methods=['GET'])
# def serve_index():
#     return send_from_directory(app.static_folder, 'index.html')

@app.route('/search', methods=['GET'])
def search_logs():
    host_name = request.args.get('host_name')
    host_ip = request.args.get('host_ip')
    system_type = request.args.get('system_type')
    # level = request.args.get('level')
    levels = request.args.getlist('level')  # 使用 getlist 取得多個值
    log_time = request.args.get('log_time')

    query = 'SELECT * FROM log_data WHERE 1=1'
    query_params = []

    if host_name:
        query += ' AND HOST_NAME = %s'
        query_params.append(host_name)
    if host_ip:
        query += ' AND HOST_IP = %s'
        query_params.append(host_ip)
    if system_type:
        query += ' AND SYSTEM_TYPE = %s'
        query_params.append(system_type)
    # if level:
    #     query += ' AND LEVEL = %s'
    #     query_params.append(level)
    if levels:
        placeholders = ','.join(['%s'] * len(levels))
        query += f' AND LEVEL IN ({placeholders})'
        query_params.extend(levels)
    if log_time:
        query += ' AND LOG_TIME = %s'
        query_params.append(log_time)

    try:
        connection = create_connection()
        if connection:
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, query_params)
            results = cursor.fetchall()
            cursor.close()
            connection.close()
            return jsonify(results), 200
        else:
            return jsonify({'status': 'error', 'message': 'Database connection failed'}), 500
    except Error as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


def check_legal_data(data):
    errors = []
    # 驗證 HOST_NAME
    if len(data.get('HOST_NAME', '')) > 16:
        errors.append('HOST_NAME 超過 16 個字符')
    
    # 驗證 HOST_IP
    if len(data.get('HOST_IP', '')) > 15:
        errors.append('HOST_IP 超過 15 個字符')
    
    # 驗證 SYSTEM_TYPE
    if len(data.get('SYSTEM_TYPE', '')) > 20:
        errors.append('SYSTEM_TYPE 超過 20 個字符')
    
    # 驗證 LEVEL
    level = data.get('LEVEL', '')
    if level not in SUPPORTED_LEVELS:
        errors.append('LEVEL 必須是 INFO、WARN、DEBUG 或 ERRO')
    
    # 驗證 PROCESS_NAME
    if len(data.get('PROCESS_NAME', '')) > 64:
        errors.append('PROCESS_NAME 超過 64 個字符')
    # 驗證 CONTENT
    if len(data.get('CONTENT', '')) > 512:
        errors.append('CONTENT 超過 512 個字符')

    # 驗證 LOG_TIME
    if len(data.get('LOG_TIME', '')) > 19:
        errors.append('LOG_TIME 超過 19 個字符')
        
    if errors:
        print(f'Wrong data format. {errors}') 

    return errors
    

#創立會回傳連接而且會在server打印訊息
def create_connection():
    try:
        #musql.connector.connect()是建立連接，裡面是連接的相關資訊
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
    # try 失敗之後 印出錯誤訊息
    except Error as e:#Error 是錯誤的類別
        print("Error while connecting to MySQL", e)
        return None

def check_miss(data):
    # 檢查資料是否殘缺 (沒有 key)
    required_fields = ['HOST_NAME', 'HOST_IP', 'SYSTEM_TYPE', 'LEVEL', 'PROCESS_NAME', 'CONTENT', 'LOG_TIME']
    miss_field = []
    for field in required_fields:
        if field not in data:
            miss_field.append(field)
    if miss_field :
        print(f'Missing field: {miss_field}')
    
    return miss_field
    
    
#routing路徑為/log 用HTTP的post
@app.route('/log', methods=['POST'])
def log():
    # data為client打來的JSON格式資料(Format B)
    data = request.get_json()
    #response = request.json()
    #檢查是否資料缺失
    missing_field = check_miss(data)
    if missing_field:
        return jsonify({'status': 'error', 'message': f'Missing field: {missing_field}'}), 400

    #檢查數據是否合法
    data_unlegal = check_legal_data(data)
    if data_unlegal:
        return jsonify({'status': 'error', 'message': f'{data_unlegal}'}), 402
     
    #無資料殘缺
    try:
        connection = create_connection()
        if connection:
            #創一個游標，用來輸入sql指令
            cursor = connection.cursor()
            
            #%s是實際要插入的值,參數化input
            input_order = """
            INSERT INTO log_data (HOST_NAME, HOST_IP, SYSTEM_TYPE, LEVEL, PROCESS_NAME, CONTENT, LOG_TIME)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """

            #執行
            cursor.execute(input_order, (
                data['HOST_NAME'], data['HOST_IP'], data['SYSTEM_TYPE'], data['LEVEL'],
                data['PROCESS_NAME'], data['CONTENT'], data['LOG_TIME']
            ))

            #把cursor做的事提交
            #在執行 INSERT、UPDATE 或 DELETE 操作後，需要調用 commit() 方法來提交這些變更。
            #如果不調用 commit()，這些變更將不會被保存到資料庫中，並且在連接關閉時將被回滾。
            connection.commit()
            cursor.close()
            connection.close()
            return jsonify({'status': 'success', 'message': 'Log entry added successfully'}), 201

        #連接失敗，告訴client
        else:
            return jsonify({'status': 'error', 'message': 'Database connection failed'}), 500
   #非資料庫連接錯誤：在if內執行時發生錯誤，例如資料格式錯誤 
    except Error as e:
        return jsonify({'status': 'error', 'message': str(e)}), 501

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
    
## data缺失400，不符規範402
##讀取成功200 創建成功201
##連接失敗500
##非連接問題失敗501 (SQL 指令或資料庫結構問題)

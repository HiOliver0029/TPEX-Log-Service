from locust import HttpUser, TaskSet, task, between, events
import json

class UserBehavior(TaskSet):
    headers = {"server-api-key": "1234567890abcdef"}

    # log_server.py
    @task(3)  # 設定此任務的權重為3，會更頻繁地執行
    def send_log_B(self):
        log_data_B = {
            "HOST_NAME": "TestHost",
            "HOST_IP": "127.0.0.1",
            "SYSTEM_TYPE": "TestSystem",
            "LEVEL": "INFO",
            "PROCESS_NAME": "TestProcess",
            "CONTENT": "Sample log message",
            "LOG_TIME": "2024-08-08 12:00:00"
        }
        response = self.client.post("/log", json=log_data_B)
        print(f"Send log response: {response.status_code} - {response.json()}")

    @task(1)  # 設定此任務的權重為1，會較不頻繁地執行 
    def search_logs(self):
        params = {
            # "host_name": "TestHost",
            # "host_ip": "127.0.0.1",
            # "system_type": "TestSystem",
            "level": "INFO",
        }
        response = self.client.get("/search", params=params)
        print(f"Search logs response: {response.status_code} - {response.json()}")

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)
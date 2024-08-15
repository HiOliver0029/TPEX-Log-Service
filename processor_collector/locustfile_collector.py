from locust import HttpUser, TaskSet, task, between, events
import json

class UserBehavior(TaskSet):
    headers = {"collector-api-key": "202408testing"}

    # collector.py 
    @task
    def send_log_A(self):
        log_data_A = {
            "RAW_LOG": "08:31:01  WARN|client.c:  76 client_run     # uv_run()",
            "REGEX": {
                "log_time_regex": r"^(\d{2}:\d{2}:\d{2})",
                "level_regex": r"\s([A-Z]+)\|",
                "message_regex": r"# (.+)"
            },
            "HOST_NAME": "TestHost",
            "HOST_IP": "127.0.0.1",
            "SYSTEM_TYPE": "TestSystem",
            "PROCESS_NAME": "TestProcess"
        }
        response = self.client.post("/contentA", json=log_data_A, headers=self.headers)
        print(f"Send log response: {response.status_code} - {response.json()}")

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)

# # 可以透過 Locust 的事件來捕捉測試的開始與結束
# @events.test_start.add_listener
# def test_start(environment, **kwargs):
#     print("Load test started")

# @events.test_stop.add_listener
# def test_stop(environment, **kwargs):
#     print("Load test finished")

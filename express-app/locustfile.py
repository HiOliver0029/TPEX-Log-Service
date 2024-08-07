from locust import HttpUser, TaskSet, task

class UserBehavior(TaskSet):
    @task
    def get_logs(self):
        self.client.get("/search?host_name=example")

class WebsiteUser(HttpUser):
    tasks = [UserBehavior]

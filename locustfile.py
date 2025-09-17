from locust import HttpUser, task, between

class ApiUser(HttpUser):
    wait_time = between(1, 3)  # Random wait between requests (1-3s)

    @task
    def get_weather(self):
        self.client.get("/weather?city=London")

    @task
    def post_calculate(self):
        self.client.post(
            "/calculate",
            json={"operation": "add", "numbers": [2, 3]},
            headers={"Content-Type": "application/json"}
        )
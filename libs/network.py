import os

import requests
from dotenv import load_dotenv


class API:
    def __init__(self) -> None:
        load_dotenv(".env")
        token = os.getenv("TOKEN")
        self.api_url = os.getenv("URL")
        if self.api_url.endswith("/"):
            self.api_url = self.api_url[:-1]
        self.params = {"token": token}

    def get_problem(self) -> dict:
        """問題取得

        Returns:
            dict: 問題json
        """
        response = requests.get(f"{self.api_url}/problem", params=self.params)
        if response.status_code != 200:
            raise Exception(f"get problem failed with {response.status_code}")
        return response.json()

    def post_answer(self, data: dict):
        response = requests.post(
            f"{self.api_url}/answer", params=self.params, json=data
        )
        if response.status_code != 200:
            raise Exception(f"get problem failed with {response.status_code}")
        return response.json()

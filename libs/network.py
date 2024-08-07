import os
import time

import requests
from dotenv import load_dotenv


class API:
    def __init__(self, env_file: str = ".env") -> None:
        load_dotenv(env_file)
        token = os.getenv("TOKEN")
        self.api_url = os.getenv("URL")
        if self.api_url.endswith("/"):
            self.api_url = self.api_url[:-1]
        self.params = {"token": token}

    def get_problem(self) -> dict:
        """問題取得

        Raises:
            HTTPError: Get失敗

        Returns:
            dict: json形式問題
        """
        response = requests.get(f"{self.api_url}/problem", params=self.params)
        if response.status_code == 403:
            print("waiting server...")
            time.sleep(0.5)
            return self.get_problem()
        elif response.status_code != 200:
            raise requests.HTTPError(
                f"get problem failed with status code {response.status_code}: {response.text}"
            )
        return response.json()

    def post_answer(self, data: dict) -> dict:
        """回答提出

        Args:
            data (dict): 回答データ

        Raises:
            HTTPError: Post失敗

        Returns:
            dict: レスポンスメッセージ
        """
        response = requests.post(
            f"{self.api_url}/answer", params=self.params, json=data
        )
        if response.status_code != 200:
            raise requests.HTTPError(
                f"post answer failed with status code {response.status_code}: {response.text}"
            )
        return response.json()

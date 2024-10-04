import os
import time

import requests
from dotenv import load_dotenv


class API:
    def __init__(self, env_file: str = ".env") -> None:
        load_dotenv(env_file)
        token = os.environ["TOKEN"]
        self.api_url = os.environ["URL"]
        if self.api_url.endswith("/"):
            self.api_url = self.api_url[:-1]
        self.params = {"token": token}

    def get_problem(self, retry: int = 10, interval: float = 0.5) -> dict:
        """問題取得

        Args:
            data (dict): 回答データ
            retry (int): 再試行回数
            interval (float): 再試行時インターバル

        Raises:
            HTTPError: Get失敗

        Returns:
            dict: json形式問題
        """
        for i in range(retry):
            response = requests.get(f"{self.api_url}/problem", params=self.params)
            if response.status_code == 200:
                break
            elif response.status_code == 403:
                print("waiting server...")
                time.sleep(interval)
                return self.get_problem()
            else:
                print(
                    f"get problem failed with status code {response.status_code}: {response.text}"
                )
                print(f"retry {i+1}/{retry}")
                time.sleep(interval)
        if response.status_code != 200:
            raise requests.HTTPError(
                f"get problem failed with status code {response.status_code}: {response.text}"
            )
        return response.json()

    def post_answer(self, data: dict, retry: int = 10, interval: float = 0.5) -> dict:
        """回答提出

        Args:
            data (dict): 回答データ
            retry (int): 再試行回数
            interval (float): 再試行時インターバル

        Raises:
            HTTPError: Post失敗

        Returns:
            dict: レスポンスメッセージ
        """
        for i in range(retry):
            response = requests.post(
                f"{self.api_url}/answer", params=self.params, json=data
            )
            if response.status_code == 200:
                break
            else:
                print(
                    f"post answer failed with status code {response.status_code}: {response.text}"
                )
                print(f"retry {i+1}/{retry}")
                time.sleep(interval)
        if response.status_code != 200:
            raise requests.HTTPError(
                f"post answer failed with status code {response.status_code}: {response.text}"
            )
        return response.json()

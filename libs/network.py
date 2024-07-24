import requests


def get(url, token):
    response = requests.get(url, params={"token": token})
    if response.status_code != 200:
        raise Exception(f"get failed with {response.status_code}")
    return response.json()


def post(url, token, data):
    response = requests.post(url, json=data, params={"token": token})
    if response.status_code != 200:
        raise Exception(f"post failed with {response.status_code}")

import requests  # type: ignore


def verify_token(self) -> bool:
    response = requests.get(f"{self.BASE_URL}/user", headers=self.headers)
    return response.status_code == 200

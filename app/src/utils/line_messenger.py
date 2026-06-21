import requests


class LineMessenger:
    """LINEグループにメッセージを送信するクラス"""

    def __init__(self, channel_access_token: str, group_id: str):
        self.channel_access_token = channel_access_token
        self.group_id = group_id

    def push_message(self, message: str) -> requests.Response:
        """LINEグループにメッセージを送信する"""
        url = "https://api.line.me/v2/bot/message/push"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.channel_access_token}",
        }
        data = {"to": self.group_id, "messages": [{"type": "text", "text": message}]}
        response = requests.post(url, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        return response

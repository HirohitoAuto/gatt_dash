import requests


class LineMessenger:
    """LINEグループにメッセージを送信するクラス"""

    def __init__(self, channel_access_token: str, group_id: str):
        self.channel_access_token = channel_access_token
        self.group_id = group_id

    def _post(self, data: dict) -> requests.Response:
        """LINE Messaging APIにPOSTリクエストを送信する"""
        url = "https://api.line.me/v2/bot/message/push"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.channel_access_token}",
        }
        response = requests.post(url, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        return response

    def push_message(self, message: str) -> requests.Response:
        """LINEグループにメッセージを送信する
        ※ 現在は使用していない。URLプレビューカードを表示させる場合はこちらを使用する
        """
        data = {"to": self.group_id, "messages": [{"type": "text", "text": message}]}
        return self._post(data)

    def push_url_button(self, uri: str, header_text: str | None = None, body_contents: list | None = None) -> requests.Response:
        """URLプレビューカードを表示させずにボタン形式でURLを送信する

        Args:
            uri (str): ボタンを押したときに開くURL
            header_text (str | None): ヘッダーに表示するテキスト（指定時はグレー背景・太字で表示）
            body_contents (list | None): Flex Messageのbodyに表示するcontentsリスト
        """
        if not body_contents:
            raise ValueError("body_contents は1件以上の要素が必要です")
        bubble: dict = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": body_contents,
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "action": {
                            "type": "uri",
                            "label": "イベントページを確認する",
                            "uri": uri,
                        },
                        "style": "primary",
                    }
                ],
            },
        }
        if header_text:
            bubble["header"] = {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": "#EEEEEE",
                "contents": [
                    {
                        "type": "text",
                        "text": header_text,
                        "color": "#555555",
                        "weight": "bold",
                        "size": "lg",
                    }
                ],
            }
        flex_message = {
            "type": "flex",
            "altText": header_text or "新規イベント通知",
            "contents": bubble,
        }
        data = {"to": self.group_id, "messages": [flex_message]}
        return self._post(data)

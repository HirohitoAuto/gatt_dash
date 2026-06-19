import os

from dotenv import load_dotenv
from src.utils.line_messenger import LineMessenger


def main():
    # .envファイルから環境変数を読み込む
    load_dotenv()

    # 環境変数からLINE認証情報を取得
    channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    group_id = os.getenv("LINE_GROUP_ID")

    # 環境変数が設定されているか確認
    if not channel_access_token or not group_id:
        raise ValueError(
            "LINE_CHANNEL_ACCESS_TOKEN と LINE_GROUP_ID を .env ファイルに設定してください"
        )

    # LineMessengerを初期化
    messenger = LineMessenger(channel_access_token, group_id)

    # テストメッセージを送信
    response = messenger.push_message("Hello from Python!")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")


if __name__ == "__main__":
    main()

import os

from dotenv import load_dotenv
from src.scraper import Event, Scraper
from src.utils.line_messenger import LineMessenger

target_location = ["東住吉小学校"]


def _create_message(event: Event) -> str:
    message = f"""
🆕 新規イベント

【{event.title}】
    - 日付: {event.date}
    - 場所: {event.location}
    - 参加人数: {event.participants}

https://gat-batminton.1net.jp/137215.html#google_vignette
"""
    return message.strip()


def main():
    # .envファイルから環境変数を読み込む
    load_dotenv()

    # 環境変数の取得
    channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    group_id = os.getenv("LINE_GROUP_ID")

    # 環境変数が設定されているか確認
    if not channel_access_token or not group_id:
        raise ValueError(
            "LINE_CHANNEL_ACCESS_TOKEN と LINE_GROUP_ID を .env ファイルに設定してください"
        )
    # targetイベントを抽出
    scraper = Scraper(os.getenv("WEB_PAGE_URL", "https://gatt.jp/"))
    unresponded_events = scraper.fetch_events()
    if not unresponded_events:
        print("イベントはありません。")
        return
    else:
        for event in unresponded_events:
            if event.location in target_location:
                print(f"\n【{event.title}】")
                print(f"  日付: {event.date}")
                print(f"  場所: {event.location}")
                print(f"  参加人数: {event.participants}")
                print(f"  ステータス: {event.status}")
                # LineMessengerを初期化
                messenger = LineMessenger(channel_access_token, group_id)
                messenger.push_message(_create_message(event))


if __name__ == "__main__":
    main()

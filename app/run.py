import os
from pathlib import Path

from dotenv import load_dotenv
from src.scraper import Event, Scraper
from src.utils.line_messenger import LineMessenger
from src.utils.sent_events_store import SentEventsStore

# Load environment variables from .env file if it exists
script_dir = Path(__file__).parent
env_path = script_dir.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

# 通知対象のイベントの場所を指定
target_location = ["東住吉小学校"]


def _event_id(event: Event) -> str:
    """イベントの一意なIDを生成する。"""
    return f"{event.date}_{event.location}_{event.title}"


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
    # 環境変数の取得とバリデーション
    channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
    group_id = os.getenv("LINE_GROUP_ID", "")
    web_page_url = os.getenv("WEB_PAGE_URL", "")

    for key, val in [
        ("LINE_CHANNEL_ACCESS_TOKEN", channel_access_token),
        ("LINE_GROUP_ID", group_id),
        ("WEB_PAGE_URL", web_page_url),
    ]:
        if not val:
            raise ValueError(f"{key} が設定されていません")

    # targetイベントを抽出
    scraper = Scraper(web_page_url)
    unresponded_events = scraper.fetch_events()
    if not unresponded_events:
        print("イベントはありません。")
        return
    else:
        store = SentEventsStore("sent_events.json")
        for event in unresponded_events:
            if event.location not in target_location:
                continue
            event_id = _event_id(event)
            if store.is_sent(event_id):
                print(f"スキップ（送信済み）: {event.title}")
                continue

            print(f"\n【{event.title}】")
            print(f"  日付: {event.date}")
            print(f"  場所: {event.location}")
            print(f"  参加人数: {event.participants}")
            print(f"  ステータス: {event.status}")
            # LineMessengerを初期化
            messenger = LineMessenger(channel_access_token, group_id)
            messenger.push_message(_create_message(event))
            store.mark_as_sent(event_id)

        store.save()


if __name__ == "__main__":
    main()

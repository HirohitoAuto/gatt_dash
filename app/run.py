import logging
import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from src.scraper import Event, Scraper
from src.utils.line_messenger import LineMessenger
from src.utils.sent_events_store import SentEventsStore

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

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


def _create_body_contents(event: Event) -> list:
    """Flex MessageのbodyContents用リストを生成する。

    Args:
        event (Event): イベント情報

    Returns:
        list: Flex Messageのbody contentsリスト
    """
    date_str = str(event.date)
    formatted_date = f"{date_str[:4]}/{int(date_str[4:6])}/{int(date_str[6:])}"
    return [
        {
            "type": "text",
            "text": f"【{event.title}】",
            "wrap": True,
            "weight": "bold",
            "margin": "md",
        },
        *[
            {
                "type": "text",
                "wrap": True,
                "margin": "sm",
                "contents": [
                    {"type": "span", "text": label, "weight": "bold"},
                    {"type": "span", "text": f": {value}"},
                ],
            }
            for label, value in [
                ("日付", formatted_date),
                ("場所", event.location),
                ("参加人数", event.participants),
            ]
        ],
    ]


def main():
    # 環境変数の取得とバリデーション
    channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
    group_id = os.getenv("LINE_GROUP_ID", "")
    web_page_url = os.getenv("WEB_PAGE_URL", "")
    web_page_url_send = os.getenv("WEB_PAGE_URL_SEND", "")

    for key, val in [
        ("LINE_CHANNEL_ACCESS_TOKEN", channel_access_token),
        ("LINE_GROUP_ID", group_id),
        ("WEB_PAGE_URL", web_page_url),
        ("WEB_PAGE_URL_SEND", web_page_url_send),
    ]:
        if not val:
            raise ValueError(f"{key} が設定されていません")

    # targetイベントを抽出
    try:
        scraper = Scraper(web_page_url)
        unresponded_events = scraper.fetch_events()
    except requests.RequestException as e:
        print(f"スクレイピング失敗: {e}")
        return

    if not unresponded_events:
        print("イベントはありません。")
        return
    else:
        store = SentEventsStore(script_dir / "sent_events.json")
        messenger = LineMessenger(channel_access_token, group_id)
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
            # LINEに通知
            try:
                messenger.push_url_button(
                    web_page_url_send,
                    header_text="🎉 新規イベント通知",
                    body_contents=_create_body_contents(event),
                )
            except requests.RequestException as e:
                print(f"LINE送信失敗: {event.title} - {e}")
                continue
            store.mark_as_sent(event_id)

        store.save()


if __name__ == "__main__":
    main()

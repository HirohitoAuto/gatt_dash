import os

from dotenv import load_dotenv
from src.scraper import Scraper
from src.utils.line_messenger import LineMessenger


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
    unresponded_events = scraper.fetch_unresponded_events()
    if not unresponded_events:
        print("未回答のイベントはありません。")
        return
    else:
        print(f"未回答のイベントが {len(unresponded_events)} 件見つかりました。")
        for event in unresponded_events:
            print(f"\n【{event.title}】")
            print(f"  日時: {event.date}")
            print(f"  場所: {event.location}")
            print(f"  参加人数: {event.participants}")
            print(f"  ステータス: {event.status}")
            # LineMessengerを初期化
            messenger = LineMessenger(channel_access_token, group_id)
            messenger.push_message(
                f"【{event.title}】\n日時: {event.date}\n場所: {event.location}\n参加人数: {event.participants}"
            )


if __name__ == "__main__":
    main()

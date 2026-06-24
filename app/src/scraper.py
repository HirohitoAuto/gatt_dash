import logging
import re
from dataclasses import dataclass
from datetime import date as _date

import requests
from bs4 import BeautifulSoup
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)

# ステータスとして設定済みと判断するラベル（これらを除外）
_RESPONDED_STATUSES = {"参加予定", "検討中", "不参加予定"}


@dataclass
class Event:
    title: str
    date: int
    location: str
    participants: str
    status: str  # 未回答 / 参加予定 / 検討中 / 不参加予定 / 定員


class Scraper:
    """イベント情報ページをスクレイピングし、イベント一覧を取得するクラス。

    指数バックオフによるリトライ機能を持ち、一時的な通信障害に対して耐障害性を持つ。
    """

    def __init__(
        self,
        url: str,
        max_retries: int = 5,
        wait_min: float = 2.0,
        wait_max: float = 60.0,
    ):
        """
        Args:
            url: スクレイピング対象のURL
            max_retries: 最大試行回数（初回含む）
            wait_min: リトライ待機時間の最小値（秒）
            wait_max: リトライ待機時間の最大値（秒）
        """
        self.url = url
        # リトライ設定をインスタンスごとに動的に適用
        self._fetch_page = retry(
            stop=stop_after_attempt(max_retries),
            wait=wait_exponential(multiplier=1, min=wait_min, max=wait_max),
            retry=retry_if_exception_type(requests.RequestException),
            reraise=True,
            before_sleep=before_sleep_log(logger, logging.INFO),
        )(self._fetch_page)

    def fetch_events(self) -> list[Event]:
        """イベントページを取得し、全イベントのリストを返す。"""
        response = self._fetch_page()
        response.encoding = "shift_jis"
        soup = BeautifulSoup(response.text, "html.parser")

        events: list[Event] = []
        for div in soup.find_all("div", class_="user_event_list"):
            event = self._parse_event(div)
            if event:
                events.append(event)
        return events

    # ------------------------------------------------------------------
    # private
    # ------------------------------------------------------------------

    def _fetch_page(self) -> requests.Response:
        """URLにGETリクエストを送り、レスポンスを返す（リトライ対象のメソッド）。"""
        response = requests.get(self.url, timeout=(15, 30))
        response.raise_for_status()
        return response

    def _parse_event(self, div) -> Event | None:
        link = div.find("a")
        if not link:
            return None

        title = self._extract_title(link)
        date, location = self._extract_date_location(link)
        participants = self._extract_participants(link)
        status = self._extract_status(div)

        return Event(
            title=title,
            date=date,
            location=location,
            participants=participants,
            status=status,
        )

    def _extract_title(self, link) -> str:
        title_font = link.find("font", style=lambda s: s and "color:#333333" in s)
        if title_font:
            b = title_font.find("b")
            return b.get_text(strip=True) if b else title_font.get_text(strip=True)
        return ""

    def _extract_date_location(self, link) -> tuple[int, str]:
        date: int | None = None
        location = ""
        for font in link.find_all("font", color="#666666"):
            text = font.get_text(separator="\n", strip=True)
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            if not lines:
                continue
            # 日付は最初の行（太字）、場所は「場所：」を含む行
            if date is None:
                date = self._parse_date(lines[0])
            for line in lines:
                if line.startswith("場所："):
                    location = line.removeprefix("場所：")
        return date if date is not None else 0, location

    def _parse_date(self, date_str: str) -> int | None:
        """「m月d日」または「yyyy年m月d日」形式の文字列を yyyymmdd の int に変換する。
        年が省略されている場合は当日以降に最も近い年を使用する。
        """
        # yyyy年m月d日 形式
        m = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", date_str)
        if m:
            return int(f"{m.group(1)}{int(m.group(2)):02d}{int(m.group(3)):02d}")
        # m月d日 形式（年なし）
        m = re.search(r"(\d{1,2})月(\d{1,2})日", date_str)
        if m:
            today = _date.today()
            month, day = int(m.group(1)), int(m.group(2))
            year = today.year
            # その月日が今日より前なら翌年とみなす
            if _date(year, month, day) < today:
                year += 1
            return int(f"{year}{month:02d}{day:02d}")
        return None

    def _extract_participants(self, link) -> str:
        for font in link.find_all("font", color="#666666"):
            text = font.get_text(strip=True)
            if "人数：" in text:
                # 「人数：X」または「人数：X/Y」の形式
                for part in text.split():
                    if part.startswith("人数："):
                        return part.removeprefix("人数：")
        return ""

    def _extract_status(self, div) -> str:
        """フォームのsubmitボタンラベルから現在のステータスを推定する。

        未回答の場合: 参加/不参加/検討中 の選択肢ボタンが3つすべて表示される。
        回答済みの場合: 選択肢ボタンは減り、取消ボタン等が表示される。
        """
        button_values = {
            inp.get("value", "") for inp in div.find_all("input", type="submit")
        }
        # 3つの選択肢がすべて揃っている → 未回答
        if {"参加", "不参加", "検討中"}.issubset(button_values):
            return "未回答"
        # 定員でキャンセル待ちのみ表示 → 未回答（ただし定員）
        if "キャンセル待ち" in button_values and not {
            "参加",
            "不参加",
            "検討中",
        }.intersection(button_values):
            return "定員"
        # 選択肢ボタンが揃っていない → 何らかのステータスが設定済み
        # ボタンラベルからステータスを推定（取消ボタンの有無などで判断）
        if "参加" in button_values and "不参加" not in button_values:
            return "不参加予定"
        if "不参加" in button_values and "参加" not in button_values:
            return "参加予定"
        return "検討中"

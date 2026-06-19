import json
from pathlib import Path


class SentEventsStore:
    """送信済みイベントのIDをJSONファイルで管理するクラス。"""

    def __init__(self, store_path: str = "sent_events.json"):
        self._path = Path(store_path)
        self._sent: set[str] = self._load()

    def _load(self) -> set[str]:
        if self._path.exists():
            with self._path.open(encoding="utf-8") as f:
                return set(json.load(f))
        return set()

    def save(self) -> None:
        with self._path.open("w", encoding="utf-8") as f:
            json.dump(sorted(self._sent), f, ensure_ascii=False, indent=2)

    def is_sent(self, event_id: str) -> bool:
        return event_id in self._sent

    def mark_as_sent(self, event_id: str) -> None:
        self._sent.add(event_id)

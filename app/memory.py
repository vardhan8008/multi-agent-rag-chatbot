from threading import Lock
from typing import List

_sessions: set[str] = set()
_lock = Lock()


def remember(session_id: str) -> None:
    with _lock:
        _sessions.add(session_id)


def all_sessions() -> List[str]:
    with _lock:
        return sorted(_sessions)

 
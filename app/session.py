"""
Server-side session memory — stores last N exchanges per student session.
"""

from typing import List, Dict

_sessions: Dict[str, List[dict]] = {}
MAX_TURNS = 20  # 10 exchanges (user + assistant per turn)


def get_history(session_id: str) -> List[dict]:
    return list(_sessions.get(session_id, []))


def save_exchange(session_id: str, user_msg: str, ai_reply: str) -> None:
    if session_id not in _sessions:
        _sessions[session_id] = []
    _sessions[session_id].append({"role": "user",      "content": user_msg})
    _sessions[session_id].append({"role": "assistant", "content": ai_reply})
    _sessions[session_id] = _sessions[session_id][-MAX_TURNS:]


def clear_session(session_id: str) -> None:
    _sessions.pop(session_id, None)


def session_count() -> int:
    return len(_sessions)

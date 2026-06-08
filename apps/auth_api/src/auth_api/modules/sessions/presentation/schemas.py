from pydantic import BaseModel


class SessionRead(BaseModel):
    session_id: str
    user_agent: str | None = None
    ip: str | None = None
    token_version: int
    created_at: str
    last_seen_at: str

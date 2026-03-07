from __future__ import annotations

from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class Message(BaseModel):
    role: Literal['system', 'user', 'assistant']
    content: str


class DispatchRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid4()))
    task_type: Literal['chat'] = 'chat'
    messages: list[Message]
    max_output_tokens: int | None = None
    temperature: float | None = None
    require_json: bool = False
    save_payloads: bool = False


class UsageInfo(BaseModel):
    input_tokens: int | None = None
    output_tokens: int | None = None


class DispatchResponse(BaseModel):
    request_id: str
    provider: str
    model: str
    output_text: str
    finish_reason: str | None = None
    usage: UsageInfo
    fallbacks_used: int = 0
    payload_log_path: str | None = None

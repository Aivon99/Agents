from __future__ import annotations

from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from gateway.storage.db import Base


class ReservationStatus(str, Enum):
    RESERVED = 'reserved'
    COMMITTED = 'committed'
    RELEASED = 'released'
    FAILED = 'failed'


class RouteConfig(Base):
    __tablename__ = 'provider_routes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    provider_name: Mapped[str] = mapped_column(String(64), index=True)
    model_name: Mapped[str] = mapped_column(String(128), index=True)
    is_free: Mapped[bool] = mapped_column(Boolean, default=False)
    supports_chat: Mapped[bool] = mapped_column(Boolean, default=True)
    supports_json: Mapped[bool] = mapped_column(Boolean, default=False)
    supports_streaming: Mapped[bool] = mapped_column(Boolean, default=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    priority: Mapped[int] = mapped_column(Integer, default=100)
    health_score: Mapped[float] = mapped_column(Float, default=1.0)
    cooldown_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    last_error_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    quota: Mapped['QuotaState'] = relationship(back_populates='route', uselist=False, cascade='all, delete-orphan')
    reservations: Mapped[list['Reservation']] = relationship(back_populates='route', cascade='all, delete-orphan')


class QuotaState(Base):
    __tablename__ = 'quota_state'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    route_id: Mapped[int] = mapped_column(ForeignKey('provider_routes.id', ondelete='CASCADE'), unique=True)
    estimated_available_requests: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_available_input_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_available_output_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False), nullable=True)
    source_of_truth: Mapped[str] = mapped_column(String(32), default='internal_estimate')

    route: Mapped[RouteConfig] = relationship(back_populates='quota')


class Reservation(Base):
    __tablename__ = 'reservations'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(String(64), index=True)
    route_id: Mapped[int] = mapped_column(ForeignKey('provider_routes.id', ondelete='CASCADE'), index=True)
    reserved_input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    reserved_output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[ReservationStatus] = mapped_column(SAEnum(ReservationStatus), default=ReservationStatus.RESERVED)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=False))

    route: Mapped[RouteConfig] = relationship(back_populates='reservations')


class RequestLog(Base):
    __tablename__ = 'request_logs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    request_id: Mapped[str] = mapped_column(String(64), index=True)
    provider_name: Mapped[str] = mapped_column(String(64))
    model_name: Mapped[str] = mapped_column(String(128))
    task_type: Mapped[str] = mapped_column(String(32))
    input_token_estimate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    input_tokens_actual: Mapped[int | None] = mapped_column(Integer, nullable=True)
    output_tokens_actual: Mapped[int | None] = mapped_column(Integer, nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, default=False)
    http_status: Mapped[int | None] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    finish_reason: Mapped[str | None] = mapped_column(String(64), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(128), nullable=True)
    payload_log_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)

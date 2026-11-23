from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from models import Base


class EventProcessing(Base):
    __tablename__ = "event_processing"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    external_event_id: Mapped[str] = mapped_column(Text, nullable=False)
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    schema_version: Mapped[str] = mapped_column(Text, nullable=False)
    identity_source: Mapped[str] = mapped_column(Text, nullable=False)
    processing_status: Mapped[str] = mapped_column(Text, nullable=False)
    quality_status: Mapped[str] = mapped_column(Text, nullable=False)
    first_claim_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    retry_budget_origin_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    execution_generation: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    processor_version: Mapped[str] = mapped_column(Text, nullable=False)
    canonical_asset_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    correlation_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    request_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    ts_event: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    payload_reference: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("source", "external_event_id", name="uq_event_processing_source_external_event_id"),
        UniqueConstraint("id", "execution_generation", name="uq_event_processing_id_execution_generation"),
        CheckConstraint(
            "processing_status IN ('received','processing','retry_pending','completed','failed','dead_lettered')",
            name="ck_event_processing_processing_status",
        ),
        CheckConstraint(
            "quality_status IN ('pass','warning','fail')",
            name="ck_event_processing_quality_status",
        ),
        ForeignKeyConstraint(
            ["id", "execution_generation"],
            ["event_generations.event_id", "event_generations.generation_number"],
            name="fk_event_processing_current_generation",
            deferrable=True,
            initially="deferred",
            ondelete="RESTRICT",
            use_alter=True,
        ),
    )


class EventGeneration(Base):
    __tablename__ = "event_generations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    generation_number: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    replay_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        UniqueConstraint("event_id", "generation_number", name="uq_event_generations_event_id_generation_number"),
        ForeignKeyConstraint(
            ["event_id"],
            ["event_processing.id"],
            name="fk_event_generations_event_id",
            ondelete="RESTRICT",
        ),
    )


class EventAttempt(Base):
    __tablename__ = "event_attempts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    attempt_number: Mapped[int] = mapped_column(Integer, nullable=False)
    execution_generation: Mapped[int] = mapped_column(Integer, nullable=False)
    worker_id: Mapped[str] = mapped_column(Text, nullable=False)
    lease_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    attempt_started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    max_lease_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fencing_token: Mapped[int] = mapped_column(BigInteger, nullable=False)
    attempt_status: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("event_id", "attempt_number", name="uq_event_attempts_event_id_attempt_number"),
        UniqueConstraint("event_id", "fencing_token", name="uq_event_attempts_event_id_fencing_token"),
        UniqueConstraint("event_id", "id", "execution_generation", name="uq_event_attempts_event_id_id_execution_generation"),
        ForeignKeyConstraint(
            ["event_id", "execution_generation"],
            ["event_generations.event_id", "event_generations.generation_number"],
            name="fk_event_attempts_generation",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "attempt_status IN ('claimed','completed','failed','expired','cancelled')",
            name="ck_event_attempts_attempt_status",
        ),
    )


class ProcessingResult(Base):
    __tablename__ = "processing_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    attempt_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    execution_generation: Mapped[int] = mapped_column(Integer, nullable=False)
    processing_status: Mapped[str] = mapped_column(Text, nullable=False)
    quality_status: Mapped[str] = mapped_column(Text, nullable=False)
    quality_result: Mapped[dict] = mapped_column(JSONB, nullable=False)
    normalized_reference: Mapped[str | None] = mapped_column(Text, nullable=True)
    processor_version: Mapped[str] = mapped_column(Text, nullable=False)
    schema_version: Mapped[str] = mapped_column(Text, nullable=False)
    processed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    error_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("attempt_id", name="uq_processing_results_attempt_id"),
        ForeignKeyConstraint(
            ["event_id", "attempt_id", "execution_generation"],
            ["event_attempts.event_id", "event_attempts.id", "event_attempts.execution_generation"],
            name="fk_processing_results_attempt",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "processing_status IN ('received','processing','retry_pending','completed','failed','dead_lettered')",
            name="ck_processing_results_processing_status",
        ),
        CheckConstraint(
            "quality_status IN ('pass','warning','fail')",
            name="ck_processing_results_quality_status",
        ),
    )


class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    attempt_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    execution_generation: Mapped[int] = mapped_column(Integer, nullable=False)
    transition_type: Mapped[str] = mapped_column(Text, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(Text, nullable=False)
    available_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    dispatch_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_error_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    dispatcher_token: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    dispatched_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    dispatch_status: Mapped[str] = mapped_column(Text, nullable=False)

    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_outbox_events_idempotency_key"),
        ForeignKeyConstraint(
            ["event_id", "attempt_id", "execution_generation"],
            ["event_attempts.event_id", "event_attempts.id", "event_attempts.execution_generation"],
            name="fk_outbox_events_attempt",
            ondelete="RESTRICT",
        ),
        CheckConstraint(
            "dispatch_status IN ('pending','dispatching','dispatched','failed')",
            name="ck_outbox_events_dispatch_status",
        ),
    )

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String, Table, Text

from infrastructure.db.base import metadata

ClientOrm = Table(
    "clients",
    metadata,
    Column("id", String(36), primary_key=True),
    Column("display_name", Text, nullable=False),
    Column("email", Text, nullable=True),
    Column("comment", Text, nullable=True),
    Column("tags", JSON, nullable=False, default=list),
    Column("enabled", Boolean, nullable=False, default=True),
    Column("deleted_at", DateTime(timezone=True), nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

AdminUserOrm = Table(
    "admin_users",
    metadata,
    Column("id", String(36), primary_key=True),
    Column("login", Text, nullable=False, unique=True),
    Column("password_hash", Text, nullable=False),
    Column("last_login_at", DateTime(timezone=True), nullable=True),
    Column("disabled_at", DateTime(timezone=True), nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
)

SubscriptionOrm = Table(
    "subscriptions",
    metadata,
    Column("id", String(36), primary_key=True),
    Column("public_id", Text, nullable=False, unique=True),
    Column("access_token_hash", Text, nullable=False),
    Column("client_id", ForeignKey("clients.id"), nullable=False),
    Column("name", Text, nullable=False),
    Column("status", String(32), nullable=False),
    Column("revision", Integer, nullable=False, default=0),
    Column("expires_at", DateTime(timezone=True), nullable=True),
    Column("suspended_at", DateTime(timezone=True), nullable=True),
    Column("revoked_at", DateTime(timezone=True), nullable=True),
    Column("deleted_at", DateTime(timezone=True), nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

AccessGrantOrm = Table(
    "access_grants",
    metadata,
    Column("id", String(36), primary_key=True),
    Column("subscription_id", ForeignKey("subscriptions.id"), nullable=False),
    Column("service_instance_id", String(36), nullable=False),
    Column("type", String(32), nullable=False),
    Column("display_name", Text, nullable=False),
    Column("status", String(32), nullable=False),
    Column("desired_state", String(32), nullable=False),
    Column("actual_state", String(32), nullable=False),
    Column("external_reference", Text, nullable=True),
    Column("last_error", Text, nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

OperationOrm = Table(
    "operations",
    metadata,
    Column("id", String(36), primary_key=True),
    Column("type", String(32), nullable=False),
    Column("node_id", String(36), nullable=False),
    Column("payload", JSON, nullable=False, default=dict),
    Column("idempotency_key", Text, nullable=False, unique=True),
    Column("status", String(32), nullable=False),
    Column("attempts", Integer, nullable=False, default=0),
    Column("max_attempts", Integer, nullable=False, default=3),
    Column("started_at", DateTime(timezone=True), nullable=True),
    Column("finished_at", DateTime(timezone=True), nullable=True),
    Column("last_error", Text, nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "0003_create_subscription_revisions"
down_revision: str | None = "0002_create_admin_users"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "subscription_revisions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("subscription_id", sa.String(length=36), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False),
        sa.Column("safe_change_summary", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_by", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["subscription_id"], ["subscriptions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_subscription_revisions_subscription_id"),
        "subscription_revisions",
        ["subscription_id"],
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_subscription_revisions_subscription_id"),
        table_name="subscription_revisions",
    )
    op.drop_table("subscription_revisions")

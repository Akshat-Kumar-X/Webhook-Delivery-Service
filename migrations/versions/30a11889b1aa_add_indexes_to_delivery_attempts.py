"""add indexes to delivery_attempts

Revision ID: 30a11889b1aa
Revises: 6179a858537d
Create Date: 2025-05-03 23:19:23.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '30a11889b1aa'
down_revision = '6179a858537d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index(
        "ix_attempts_request_id",
        "delivery_attempts",
        ["request_id"],
        postgresql_using="btree",
    )
    op.create_index(
        "ix_attempts_subscription_time",
        "delivery_attempts",
        ["attempted_at", "request_id"],
        postgresql_using="btree",
    )


def downgrade():
    op.drop_index("ix_attempts_subscription_time", table_name="delivery_attempts")
    op.drop_index("ix_attempts_request_id", table_name="delivery_attempts")

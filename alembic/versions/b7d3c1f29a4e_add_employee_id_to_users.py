"""add_employee_id_to_users

Revision ID: b7d3c1f29a4e
Revises: 4d1a3c4d9b11
Create Date: 2026-04-06 20:35:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b7d3c1f29a4e"
down_revision = "4d1a3c4d9b11"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("employee_id", sa.String(length=10), nullable=True))
    op.create_index(op.f("ix_users_employee_id"), "users", ["employee_id"], unique=True)


def downgrade():
    op.drop_index(op.f("ix_users_employee_id"), table_name="users")
    op.drop_column("users", "employee_id")

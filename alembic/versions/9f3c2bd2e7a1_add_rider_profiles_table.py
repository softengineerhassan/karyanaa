"""add_rider_profiles_table

Revision ID: 9f3c2bd2e7a1
Revises: e50496323af4
Create Date: 2026-04-06 10:45:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9f3c2bd2e7a1"
down_revision = "e50496323af4"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "rider_profiles",
        sa.Column("owner_user_id", sa.UUID(), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("phone_number", sa.String(length=20), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("profile_image", sa.String(length=500), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["owner_user_id"], ["karyanaa.users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_user_id", "phone_number", name="uq_rider_profiles_owner_phone"),
        sa.UniqueConstraint("owner_user_id", "email", name="uq_rider_profiles_owner_email"),
    )
    op.create_index(op.f("ix_rider_profiles_deleted_at"), "rider_profiles", ["deleted_at"], unique=False)
    op.create_index(op.f("ix_rider_profiles_owner_user_id"), "rider_profiles", ["owner_user_id"], unique=False)
    op.create_index(
        "ix_rider_profiles_not_deleted",
        "rider_profiles",
        ["deleted_at"],
        unique=False,
        postgresql_where=sa.text("deleted_at IS NULL"),
    )


def downgrade():
    op.drop_index("ix_rider_profiles_not_deleted", table_name="rider_profiles", postgresql_where=sa.text("deleted_at IS NULL"))
    op.drop_index(op.f("ix_rider_profiles_owner_user_id"), table_name="rider_profiles")
    op.drop_index(op.f("ix_rider_profiles_deleted_at"), table_name="rider_profiles")
    op.drop_table("rider_profiles")

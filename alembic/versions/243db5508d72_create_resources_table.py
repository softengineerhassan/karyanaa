"""create resources table

Revision ID: 243db5508d72
Revises: 0838d4f0281d
Create Date: 2026-01-18 18:32:37.566922
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '243db5508d72'
down_revision = "0838d4f0281d"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "resources",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column(
            "venue_id",
            sa.UUID(),
            sa.ForeignKey("venues.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name_en", sa.String(150), nullable=False),
        sa.Column("name_ar", sa.String(150), nullable=False),
        sa.Column("name_fr", sa.String(150), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False),
        sa.Column("base_price", sa.Integer(), nullable=False),
        sa.Column(
            "pricing_unit",
            sa.Enum("PER_HOUR", "PER_DAY", "PER_EVENT", name="pricingunit"),
            nullable=False,
        ),
        sa.Column("is_premium", sa.Boolean(), server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
    )



def downgrade():
    op.drop_table("resources")
    op.execute("DROP TYPE pricingunit")

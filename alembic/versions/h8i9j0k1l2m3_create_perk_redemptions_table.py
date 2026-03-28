"""create perk_redemptions table

Revision ID: h8i9j0k1l2m3
Revises: g7h8i9j0k1l2
Create Date: 2026-02-16 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'h8i9j0k1l2m3'
down_revision = 'g7h8i9j0k1l2'
branch_labels = None
depends_on = None


def upgrade():
    """Create perk_redemptions table"""
    op.create_table(
        'perk_redemptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('perk_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('venue_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('redemption_code', sa.String(length=8), nullable=False),
        sa.Column('redemption_type', sa.String(length=20), nullable=False),
        sa.Column('qr_expires_at', sa.DateTime(), nullable=False),
        sa.Column('is_redeemed', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('redeemed_at', sa.DateTime(), nullable=True),
        sa.Column('redeemed_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['perk_id'], ['omnia.perks.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['omnia.users.id'], ),
        sa.ForeignKeyConstraint(['venue_id'], ['omnia.venues.id'], ),
        sa.ForeignKeyConstraint(['redeemed_by'], ['omnia.users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('redemption_code'),
        schema='omnia'
    )
    
    # Create indexes
    op.create_index('idx_perk_redemptions_code', 'perk_redemptions', ['redemption_code'], unique=False, schema='omnia')
    op.create_index('idx_perk_redemptions_user', 'perk_redemptions', ['user_id'], unique=False, schema='omnia')
    op.create_index('idx_perk_redemptions_perk', 'perk_redemptions', ['perk_id'], unique=False, schema='omnia')


def downgrade():
    """Drop perk_redemptions table"""
    op.drop_index('idx_perk_redemptions_perk', table_name='perk_redemptions', schema='omnia')
    op.drop_index('idx_perk_redemptions_user', table_name='perk_redemptions', schema='omnia')
    op.drop_index('idx_perk_redemptions_code', table_name='perk_redemptions', schema='omnia')
    op.drop_table('perk_redemptions', schema='omnia')

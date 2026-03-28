"""localize subcategory description

Revision ID: i9j0k1l2m3n4
Revises: h8i9j0k1l2m3
Create Date: 2026-02-17 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'i9j0k1l2m3n4'
down_revision = 'h8i9j0k1l2m3'
branch_labels = None
depends_on = None


def upgrade():
    # Add new localized description columns
    op.add_column('subcategories', sa.Column('description_en', sa.Text(), nullable=True))
    op.add_column('subcategories', sa.Column('description_ar', sa.Text(), nullable=True))
    op.add_column('subcategories', sa.Column('description_fr', sa.Text(), nullable=True))
    
    # Copy existing description to description_en
    op.execute("""
        UPDATE subcategories 
        SET description_en = description 
        WHERE description IS NOT NULL
    """)
    
    # Drop old description column
    op.drop_column('subcategories', 'description')


def downgrade():
    # Add back the old description column
    op.add_column('subcategories', sa.Column('description', sa.Text(), nullable=True))
    
    # Copy description_en back to description
    op.execute("""
        UPDATE subcategories 
        SET description = description_en 
        WHERE description_en IS NOT NULL
    """)
    
    # Drop localized columns
    op.drop_column('subcategories', 'description_fr')
    op.drop_column('subcategories', 'description_ar')
    op.drop_column('subcategories', 'description_en')

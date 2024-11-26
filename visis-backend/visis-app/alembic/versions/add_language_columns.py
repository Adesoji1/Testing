
"""add language columns

Revision ID: add_language_columns
Create Date: 2024-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

def upgrade():
    # Add new columns
    op.add_column('languages', sa.Column('display_name', sa.String(), nullable=True))
    op.add_column('languages', sa.Column('native_name', sa.String(), nullable=True))
    
    # Ensure other columns exist with correct nullability
    op.alter_column('languages', 'is_active',
                    existing_type=sa.BOOLEAN(),
                    nullable=False,
                    server_default=sa.text('true'))
                    
    op.alter_column('languages', 'usage_count',
                    existing_type=sa.INTEGER(),
                    nullable=False,
                    server_default=sa.text('0'))

def downgrade():
    op.drop_column('languages', 'display_name')
    op.drop_column('languages', 'native_name')
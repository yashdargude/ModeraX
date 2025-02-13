"""Add index to moderation_results

Revision ID: abcdef123456
Revises: 
Create Date: 2025-02-13 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'abcdef123456'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_index('ix_model_created_at', 'moderation_results', [
                    'model', 'created_at'])


def downgrade():
    op.drop_index('ix_model_created_at', table_name='moderation_results')

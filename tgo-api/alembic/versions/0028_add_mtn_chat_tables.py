"""add mtn chat tables

Revision ID: 0028
Revises: 6595c48378f1
Create Date: 2024-01-15 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0028'
down_revision: Union[str, None] = '6595c48378f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create conversations table for MTN chatbot
    op.create_table(
        'conversations',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('intent', sa.String(length=100), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('entities', sa.JSON(), nullable=True),
        sa.Column('language', sa.String(length=50), nullable=True),
        sa.Column('suggestions', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on session_id for faster lookups
    op.create_index('ix_conversations_session_id', 'conversations', ['session_id'])
    op.create_index('ix_conversations_created_at', 'conversations', ['created_at'])
    
    # Create feedback table for CSAT ratings
    op.create_table(
        'feedback',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('session_id', sa.String(length=255), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range')
    )
    
    # Create index on session_id for feedback
    op.create_index('ix_feedback_session_id', 'feedback', ['session_id'])


def downgrade() -> None:
    op.drop_index('ix_feedback_session_id', table_name='feedback')
    op.drop_table('feedback')
    
    op.drop_index('ix_conversations_created_at', table_name='conversations')
    op.drop_index('ix_conversations_session_id', table_name='conversations')
    op.drop_table('conversations')

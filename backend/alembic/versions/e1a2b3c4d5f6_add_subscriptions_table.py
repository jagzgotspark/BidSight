"""add subscriptions table

Revision ID: e1a2b3c4d5f6
Revises: 3324f834f933
Create Date: 2026-09-17 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1a2b3c4d5f6'
down_revision: Union[str, None] = '3324f834f933'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('subscriptions',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=False),
    sa.Column('plan', sa.String(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('amount_paise', sa.Integer(), nullable=False),
    sa.Column('razorpay_order_id', sa.String(), nullable=True),
    sa.Column('razorpay_payment_id', sa.String(), nullable=True),
    sa.Column('current_period_end', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_subscriptions_user_id'), 'subscriptions', ['user_id'], unique=False)
    op.create_index(op.f('ix_subscriptions_razorpay_order_id'), 'subscriptions', ['razorpay_order_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_subscriptions_razorpay_order_id'), table_name='subscriptions')
    op.drop_index(op.f('ix_subscriptions_user_id'), table_name='subscriptions')
    op.drop_table('subscriptions')

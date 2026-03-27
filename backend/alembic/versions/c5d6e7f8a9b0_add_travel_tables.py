"""add travel tables

Revision ID: c5d6e7f8a9b0
Revises: b4d5e6f7a8b9
Create Date: 2026-03-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5d6e7f8a9b0'
down_revision: Union[str, None] = 'b4d5e6f7a8b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'travel_estimates',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('circuit_id', sa.Integer(), sa.ForeignKey('circuits.id'), nullable=False),
        sa.Column('origin_city', sa.String(100), nullable=False),
        sa.Column('origin_country', sa.String(100), nullable=False),
        sa.Column('origin_airport_code', sa.String(10), nullable=False),
        sa.Column('flight_price_min', sa.Float(), nullable=False),
        sa.Column('flight_price_max', sa.Float(), nullable=False),
        sa.Column('flight_duration_hours', sa.Float(), nullable=False),
        sa.Column('flight_stops', sa.Integer(), nullable=False),
        sa.Column('train_available', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('train_price_min', sa.Float(), nullable=True),
        sa.Column('train_price_max', sa.Float(), nullable=True),
        sa.Column('train_duration_hours', sa.Float(), nullable=True),
        sa.Column('local_transport_cost', sa.Float(), nullable=False),
        sa.Column('hotel_avg_per_night', sa.Float(), nullable=False),
        sa.Column('last_fetched_at', sa.DateTime(), nullable=False),
    )

    op.create_table(
        'exchange_rates',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('currency_code', sa.String(10), nullable=False, unique=True),
        sa.Column('rate_from_usd', sa.Float(), nullable=False),
        sa.Column('last_updated_at', sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('exchange_rates')
    op.drop_table('travel_estimates')

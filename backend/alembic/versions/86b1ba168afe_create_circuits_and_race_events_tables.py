"""create circuits and race_events tables

Revision ID: 86b1ba168afe
Revises:
Create Date: 2026-03-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '86b1ba168afe'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'circuits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('country', sa.String(length=100), nullable=False),
        sa.Column('continent', sa.String(length=50), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('track_type', sa.String(length=20), nullable=False),
        sa.Column('track_length_km', sa.Float(), nullable=False),
        sa.Column('number_of_turns', sa.Integer(), nullable=False),
        sa.Column('drs_zones_count', sa.Integer(), nullable=False),
        sa.Column('overtake_difficulty', sa.Integer(), nullable=False),
        sa.Column('avg_overtakes_per_race', sa.Float(), nullable=False),
        sa.Column('rain_probability_pct', sa.Integer(), nullable=False),
        sa.Column('nearest_airport', sa.String(length=200), nullable=False),
        sa.Column('local_transport_notes', sa.String(length=500), nullable=True),
        sa.Column('atmosphere_rating', sa.Float(), nullable=True),
        sa.Column('fan_reviews_summary', sa.String(length=2000), nullable=True),
        sa.Column('elevation_change', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'race_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('circuit_id', sa.Integer(), nullable=False),
        sa.Column('season_year', sa.Integer(), nullable=False),
        sa.Column('race_name', sa.String(length=200), nullable=False),
        sa.Column('race_date', sa.Date(), nullable=False),
        sa.Column('sprint_weekend', sa.Boolean(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('total_overtakes', sa.Integer(), nullable=True),
        sa.Column('weather_actual', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['circuit_id'], ['circuits.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('race_events')
    op.drop_table('circuits')

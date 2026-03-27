"""create seat_sections table

Revision ID: a3f2c1d4e5b6
Revises: 86b1ba168afe
Create Date: 2026-03-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3f2c1d4e5b6'
down_revision: Union[str, None] = '86b1ba168afe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'seat_sections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('circuit_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('section_type', sa.String(length=30), nullable=False),
        sa.Column('location_on_track', sa.String(length=200), nullable=True),
        sa.Column('has_roof', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('has_screen', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('pit_view', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('podium_view', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('capacity', sa.Integer(), nullable=True),
        sa.Column('view_description', sa.Text(), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('view_photos', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['circuit_id'], ['circuits.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('seat_sections')

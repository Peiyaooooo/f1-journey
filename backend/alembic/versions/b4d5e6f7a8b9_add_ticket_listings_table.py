"""add ticket_listings table

Revision ID: b4d5e6f7a8b9
Revises: a3f2c1d4e5b6
Create Date: 2026-03-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4d5e6f7a8b9'
down_revision: Union[str, None] = 'a3f2c1d4e5b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'ticket_listings',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('circuit_id', sa.Integer(), sa.ForeignKey('circuits.id'), nullable=False),
        sa.Column('race_event_id', sa.Integer(), sa.ForeignKey('race_events.id'), nullable=False),
        sa.Column('seat_section_id', sa.Integer(), sa.ForeignKey('seat_sections.id'), nullable=True),
        sa.Column('source_site', sa.String(50), nullable=False),
        sa.Column('source_url', sa.String(500), nullable=False),
        sa.Column('source_section_name', sa.String(200), nullable=False),
        sa.Column('ticket_type', sa.String(30), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(10), nullable=False),
        sa.Column('available_quantity', sa.Integer(), nullable=True),
        sa.Column('includes', sa.Text(), nullable=True),
        sa.Column('last_scraped_at', sa.DateTime(), nullable=False),
        sa.Column('is_available', sa.Boolean(), nullable=False, server_default=sa.true()),
    )


def downgrade() -> None:
    op.drop_table('ticket_listings')

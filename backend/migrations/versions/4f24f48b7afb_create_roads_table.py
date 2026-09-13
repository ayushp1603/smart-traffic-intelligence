"""create roads table

Revision ID: 4f24f48b7afb
Revises:
Create Date: 2026-09-02
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import geoalchemy2


# revision identifiers, used by Alembic.
revision: str = "4f24f48b7afb"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create roads table."""

    op.create_table(
        "roads",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "name",
            sa.String(length=150),
            nullable=False,
        ),
        sa.Column(
            "road_type",
            sa.String(length=50),
            nullable=True,
        ),
        sa.Column(
            "reference_speed",
            sa.Float(),
            nullable=True,
        ),
        sa.Column(
            "geometry",
            geoalchemy2.types.Geometry(
                geometry_type="LINESTRING",
                srid=4326,
                dimension=2,
                spatial_index=False,
            ),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "idx_roads_geometry",
        "roads",
        ["geometry"],
        unique=False,
        postgresql_using="gist",
    )


def downgrade() -> None:
    """Drop roads table."""

    op.drop_index(
        "idx_roads_geometry",
        table_name="roads",
        postgresql_using="gist",
    )

    op.drop_table("roads")
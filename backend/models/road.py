from sqlalchemy import String, Float, Index
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geometry

from database import Base


class Road(Base):
    __tablename__ = "roads"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    road_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    reference_speed: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    geometry: Mapped[object | None] = mapped_column(
        Geometry(
            geometry_type="LINESTRING",
            srid=4326,
            spatial_index=False
        ),
        nullable=True
    )

    __table_args__ = (
        Index(
            "idx_roads_geometry",
            "geometry",
            postgresql_using="gist"
        ),
    )
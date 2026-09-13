from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class TrafficObservation(Base):
    __tablename__ = "traffic_observations"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    road_id: Mapped[int] = mapped_column(
        ForeignKey("roads.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    observed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )

    current_speed: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    reference_speed: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    source: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )
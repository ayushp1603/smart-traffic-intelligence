from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models.road import Road
from models.traffic_observation import TrafficObservation
from traffic import calculate_congestion_score, get_traffic_level


router = APIRouter(
    prefix="/traffic",
    tags=["Traffic"],
)


class TrafficObservationCreate(BaseModel):
    road_id: int
    current_speed: float = Field(ge=0)
    reference_speed: float | None = Field(default=None, gt=0)
    source: str | None = None


@router.post("/observations")
def create_traffic_observation(
    data: TrafficObservationCreate,
    db: Session = Depends(get_db),
):
    """
    Add a new traffic observation for a road.
    """

    road = db.execute(
        select(Road).where(Road.id == data.road_id)
    ).scalar_one_or_none()

    if road is None:
        raise HTTPException(
            status_code=404,
            detail="Road not found",
        )

    reference_speed = data.reference_speed

    if reference_speed is None:
        reference_speed = road.reference_speed

    observation = TrafficObservation(
        road_id=data.road_id,
        observed_at=datetime.now(timezone.utc),
        current_speed=data.current_speed,
        reference_speed=reference_speed,
        source=data.source,
    )

    db.add(observation)
    db.commit()
    db.refresh(observation)

    congestion_score = calculate_congestion_score(
        observation.current_speed,
        observation.reference_speed,
    )

    traffic_level = get_traffic_level(
        congestion_score
    )

    return {
        "message": "Traffic observation created",
        "observation": {
            "id": observation.id,
            "road_id": observation.road_id,
            "observed_at": observation.observed_at,
            "current_speed": observation.current_speed,
            "reference_speed": observation.reference_speed,
            "source": observation.source,
            "congestion_score": congestion_score,
            "traffic_level": traffic_level,
        },
    }


@router.get("/live")
def get_live_traffic(
    db: Session = Depends(get_db),
):
    """
    Return the latest traffic observation for every road.
    """

    roads = db.execute(
        select(Road).order_by(Road.id)
    ).scalars().all()

    result = []

    for road in roads:

        traffic = db.execute(
            select(TrafficObservation)
            .where(
                TrafficObservation.road_id == road.id
            )
            .order_by(
                TrafficObservation.observed_at.desc()
            )
            .limit(1)
        ).scalar_one_or_none()

        if traffic is None:
            result.append(
                {
                    "road_id": road.id,
                    "road_name": road.name,
                    "road_type": road.road_type,
                    "reference_speed": road.reference_speed,
                    "traffic": None,
                }
            )
            continue

        reference_speed = traffic.reference_speed

        if reference_speed is None:
            reference_speed = road.reference_speed

        congestion_score = calculate_congestion_score(
            traffic.current_speed,
            reference_speed,
        )

        traffic_level = get_traffic_level(
            congestion_score
        )

        result.append(
            {
                "road_id": road.id,
                "road_name": road.name,
                "road_type": road.road_type,
                "reference_speed": road.reference_speed,
                "traffic": {
                    "observation_id": traffic.id,
                    "observed_at": traffic.observed_at,
                    "current_speed": traffic.current_speed,
                    "reference_speed": reference_speed,
                    "source": traffic.source,
                    "congestion_score": congestion_score,
                    "traffic_level": traffic_level,
                },
            }
        )

    return {
        "count": len(result),
        "roads": result,
    }
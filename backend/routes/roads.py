from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from database import get_db
from models.road import Road
from models.traffic_observation import TrafficObservation
from traffic import calculate_congestion_score, get_traffic_level


router = APIRouter(
    prefix="/roads",
    tags=["Roads"],
)


@router.get("/")
def get_roads(db: Session = Depends(get_db)):
    """
    Return all roads from the database.
    """

    statement = select(
        Road.id,
        Road.name,
        Road.road_type,
        Road.reference_speed,
        func.ST_AsGeoJSON(Road.geometry).label("geometry"),
    )

    roads = db.execute(statement).all()

    return [
        {
            "id": road.id,
            "name": road.name,
            "road_type": road.road_type,
            "reference_speed": road.reference_speed,
            "geometry": road.geometry,
        }
        for road in roads
    ]


@router.get("/{road_id}")
def get_road(
    road_id: int,
    db: Session = Depends(get_db),
):
    """
    Return a single road with its latest traffic observation
    and calculated congestion information.
    """

    road_statement = select(
        Road.id,
        Road.name,
        Road.road_type,
        Road.reference_speed,
        func.ST_AsGeoJSON(Road.geometry).label("geometry"),
    ).where(Road.id == road_id)

    road = db.execute(road_statement).first()

    if road is None:
        raise HTTPException(
            status_code=404,
            detail="Road not found",
        )

    traffic_statement = (
        select(TrafficObservation)
        .where(TrafficObservation.road_id == road_id)
        .order_by(TrafficObservation.observed_at.desc())
        .limit(1)
    )

    traffic = db.execute(traffic_statement).scalar_one_or_none()

    traffic_data = None

    if traffic is not None:
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

        traffic_data = {
            "observation_id": traffic.id,
            "observed_at": traffic.observed_at,
            "current_speed": traffic.current_speed,
            "reference_speed": reference_speed,
            "source": traffic.source,
            "congestion_score": congestion_score,
            "traffic_level": traffic_level,
        }

    return {
        "id": road.id,
        "name": road.name,
        "road_type": road.road_type,
        "reference_speed": road.reference_speed,
        "geometry": road.geometry,
        "traffic": traffic_data,
    }
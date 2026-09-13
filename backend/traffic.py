def calculate_congestion_score(
    current_speed: float | None,
    reference_speed: float | None,
) -> float | None:
    """
    Calculate congestion score from current and reference speed.

    Formula:
        congestion = 1 - (current_speed / reference_speed)

    Returns:
        A value between 0 and 1, or None if the
        required speed values are unavailable.
    """

    if current_speed is None or reference_speed is None:
        return None

    if reference_speed <= 0:
        return None

    if current_speed < 0:
        return None

    score = 1 - (current_speed / reference_speed)

    return max(0.0, min(1.0, score))


def get_traffic_level(
    congestion_score: float | None,
) -> str | None:
    """
    Convert congestion score into a human-readable
    traffic level.
    """

    if congestion_score is None:
        return None

    if congestion_score < 0.25:
        return "Low"

    if congestion_score < 0.50:
        return "Moderate"

    if congestion_score < 0.75:
        return "High"

    return "Severe"
from datetime import datetime, timedelta
from typing import Dict, List

# ── Fraud detection thresholds ────────────────────────────────────────────────
MAX_SESSIONS_PER_DAY = 8
MIN_SESSION_GAP_MINUTES = 30
RAPID_COIN_THRESHOLD = 200   # coins in 24h = suspicious

def detect_fraud(user: Dict, recent_sessions: List[Dict]) -> Dict:
    """
    Analyse recent session patterns for suspicious behaviour.
    Returns { flagged: bool, reason: str }
    """
    now = datetime.utcnow()
    last_24h = [
        s for s in recent_sessions
        if (now - s["created_at"]).total_seconds() < 86400
    ]

    # Rule 1: too many sessions in 24h
    if len(last_24h) >= MAX_SESSIONS_PER_DAY:
        return {"flagged": True, "reason": f"Unusually high session count: {len(last_24h)} in 24h"}

    # Rule 2: sessions too close together (< 30 min gap)
    times = sorted([s["created_at"] for s in last_24h])
    for i in range(1, len(times)):
        gap = (times[i] - times[i-1]).total_seconds() / 60
        if gap < MIN_SESSION_GAP_MINUTES:
            return {"flagged": True, "reason": f"Sessions too close together ({round(gap)} min gap)"}

    # Rule 3: rapid coin accumulation
    coins_24h = sum(s.get("coins_earned", 0) for s in last_24h if s.get("coins_earned"))
    if coins_24h >= RAPID_COIN_THRESHOLD:
        return {"flagged": True, "reason": f"Rapid coin accumulation: +{coins_24h} SC in 24h"}

    return {"flagged": False, "reason": ""}


def recalculate_trust(user: Dict, recent_sessions: List[Dict]) -> float:
    """
    Trust score (0-100) based on:
    - Session completion rate     (40 pts)
    - Average rating received     (30 pts)
    - No fraud flags              (20 pts)
    - Account age bonus           (10 pts)
    """
    score = 0.0

    # Completion rate
    total    = len(recent_sessions)
    completed = len([s for s in recent_sessions if s.get("status") == "completed"])
    if total > 0:
        score += (completed / total) * 40
    else:
        score += 40   # new user gets full benefit of doubt

    # Rating
    rating = user.get("rating", 5.0)
    score += (rating / 5.0) * 30

    # Fraud check
    fraud = detect_fraud(user, recent_sessions)
    if not fraud["flagged"]:
        score += 20

    # Account age (days since joined, max 10pts at 30 days)
    created_at = user.get("created_at", datetime.utcnow())
    age_days = (datetime.utcnow() - created_at).days
    score += min(age_days / 30, 1.0) * 10

    return round(min(score, 100), 1)


def award_badges(user: Dict) -> List[str]:
    """Return list of earned badge names based on user stats."""
    badges = list(user.get("badges", []))
    sessions = user.get("sessions_completed", 0)
    trust    = user.get("trust_score", 0)
    coins    = user.get("skill_coins", 0)

    if sessions >= 1  and "First Session"     not in badges: badges.append("First Session")
    if sessions >= 5  and "Active Learner"    not in badges: badges.append("Active Learner")
    if sessions >= 20 and "Top Mentor"        not in badges: badges.append("Top Mentor")
    if trust    >= 90 and "Trust Champion"    not in badges: badges.append("Trust Champion")
    if coins    >= 500 and "Coin Hoarder"     not in badges: badges.append("Coin Hoarder")

    return badges

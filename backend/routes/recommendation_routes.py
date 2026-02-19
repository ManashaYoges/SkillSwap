"""
routes/recommendation_routes.py
Roadmap generation endpoint.
"""
from fastapi import APIRouter, Depends, Query

from routes.auth_routes import get_current_user
from ai.roadmap_generator import generate_roadmap, ROADMAPS

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.get("/roadmap")
async def get_roadmap(
    skill: str = Query(..., description="Skill goal, e.g. 'Data Science'"),
    level: str = Query("Beginner", description="Beginner | Intermediate | Advanced"),
    current_user: dict = Depends(get_current_user),
):
    """
    Return a learning roadmap for the requested skill + level.
    """
    roadmap = generate_roadmap(skill, level)
    return {
        "skill": skill,
        "level": level,
        "steps": roadmap,
        "total_weeks": sum(s["estimated_weeks"] for s in roadmap),
    }


@router.get("/available-skills")
async def available_skills():
    """
    Return list of skills that have curated roadmaps.
    """
    return {"skills": list(ROADMAPS.keys())}
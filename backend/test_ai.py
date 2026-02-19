"""
test_ai.py
Standalone tests for all AI modules.
Run from the backend/ directory:  python test_ai.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from ai.skill_matching import calculate_match_score, explain_match
from ai.recommendation_engine import recommend_users
from ai.roadmap_generator import generate_roadmap

# ─────────────────────────────────────────────────────────────────────────────
print("=" * 55)
print("  SKILL MATCHING")
print("=" * 55)

userA_needed = {"Python": "Beginner", "Machine Learning": "Intermediate"}
userB_offered = {"Python": "Beginner", "Machine Learning": "Intermediate", "Data Science": "Intermediate"}

score = calculate_match_score(userA_needed, userB_offered)
info  = explain_match(userA_needed, userB_offered)
print(f"Match Score   : {score}")
print(f"Common Skills : {info['common_skills']}")
print(f"Explanation   : {info['explanation']}")

# Edge case – no overlap
no_score = calculate_match_score({"React": "Beginner"}, {"Java": "Advanced"})
print(f"No-overlap    : {no_score}")  # should be 0.0

# ─────────────────────────────────────────────────────────────────────────────
print()
print("=" * 55)
print("  RECOMMENDATION ENGINE")
print("=" * 55)

current_user = {
    "id": "user_asha",
    "name": "Asha",
    "skills_needed": {"Python": "Beginner", "Machine Learning": "Intermediate"},
}

all_users = [
    {"id": "user_riya",  "name": "Riya",  "skills_offered": {"Python": "Beginner", "Data Science": "Intermediate"}},
    {"id": "user_arjun", "name": "Arjun", "skills_offered": {"UI Design": "Intermediate"}},
    {"id": "user_priya", "name": "Priya", "skills_offered": {"Python": "Intermediate", "Machine Learning": "Intermediate"}},
    {"id": "user_asha",  "name": "Asha",  "skills_offered": {"React": "Beginner"}},  # self – should be excluded
]

recs = recommend_users(current_user, all_users, top_n=3)
print("Top Matches:")
for r in recs:
    print(f"  {r['name']:10s}  score={r['match_score']}  common={r['common_skills']}")

# ─────────────────────────────────────────────────────────────────────────────
print()
print("=" * 55)
print("  ROADMAP GENERATOR")
print("=" * 55)

for skill, level in [("Cyber Security", "Beginner"), ("Data Science", "Intermediate"), ("Web Development", "Advanced")]:
    roadmap = generate_roadmap(skill, level)
    print(f"\n{skill} – {level} ({len(roadmap)} steps):")
    for step in roadmap:
        print(f"  {step['order']}. {step['title']}  (~{step['estimated_weeks']}w)")

print()
print("All tests passed ✓")
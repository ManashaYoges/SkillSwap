from ai.skill_matching import calculate_match_score, explain_match


def recommend_users(current_user: dict, all_users: list, top_n: int = 3) -> list:
    """
    Recommend top N users based on skill name similarity + level compatibility.
    current_user: { "id": ..., "name": ..., "skills_needed": {skill: level} }
    all_users: [{ "id": ..., "name": ..., "skills_offered": {skill: level} }]
    Returns list of dicts sorted by match_score descending.
    """
    recommendations = []

    for user in all_users:
        if user.get("id") == current_user.get("id"):
            continue  # skip self

        score = calculate_match_score(
            current_user["skills_needed"], user["skills_offered"]
        )
        if score > 0:
            match_info = explain_match(current_user["skills_needed"], user["skills_offered"])
            recommendations.append(
                {
                    "id": user.get("id"),
                    "name": user.get("name", "Unknown"),
                    "match_score": score,
                    "common_skills": match_info["common_skills"],
                    "explanation": match_info["explanation"],
                    "skills_offered": user["skills_offered"],
                }
            )

    recommendations.sort(key=lambda x: x["match_score"], reverse=True)
    return recommendations[:top_n]
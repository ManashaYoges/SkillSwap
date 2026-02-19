from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_similarity(skills_needed: dict, skills_offered: dict) -> float:
    """
    Calculate TF-IDF cosine similarity between skill names only.
    skills_needed/offered: dict of skill_name -> level
    """
    needed_names = list(skills_needed.keys())
    offered_names = list(skills_offered.keys())

    if not needed_names or not offered_names:
        return 0.0

    text_data = [" ".join(needed_names), " ".join(offered_names)]
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(text_data)
    similarity_matrix = cosine_similarity(vectors)
    score = similarity_matrix[0][1]
    return round(float(score), 2)


def level_compatibility_bonus(skills_needed: dict, skills_offered: dict) -> float:
    """
    Bonus based on skill-level match per skill.
    +0.2 if exact level match, +0.1 if beginner needs intermediate offered.
    """
    bonus = 0.0
    for skill, level_needed in skills_needed.items():
        level_offered = skills_offered.get(skill)
        if not level_offered:
            continue
        if level_needed.lower() == level_offered.lower():
            bonus += 0.2
        elif level_needed.lower() == "beginner" and level_offered.lower() == "intermediate":
            bonus += 0.1
    return bonus


def calculate_match_score(skills_needed: dict, skills_offered: dict) -> float:
    """
    Final match score = TF-IDF similarity + level bonus (capped at 1.0)
    """
    similarity_score = calculate_similarity(skills_needed, skills_offered)
    bonus = level_compatibility_bonus(skills_needed, skills_offered)
    final_score = similarity_score + bonus
    return round(min(final_score, 1.0), 2)


def explain_match(skills_needed: dict, skills_offered: dict) -> dict:
    """
    Return matched skills with level details.
    """
    common_skills = set(skills_needed.keys()).intersection(set(skills_offered.keys()))
    explanation_details = [
        f"{skill} (needed: {skills_needed[skill]}, offered: {skills_offered[skill]})"
        for skill in common_skills
    ]
    message = (
        f"Matching skills: {', '.join(explanation_details)}"
        if explanation_details
        else "No common skills found"
    )
    return {
        "common_skills": list(common_skills),
        "explanation": message,
    }
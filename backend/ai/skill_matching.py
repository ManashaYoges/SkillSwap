from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def calculate_similarity(skills_needed, skills_offered):
    """
    Calculate cosine similarity between two skill lists.
    
    :param skills_needed: List of skills user wants to learn
    :param skills_offered: List of skills another user can teach
    :return: similarity score (0 to 1)
    """

    # Convert skill lists into space-separated strings
    text_data = [
        " ".join(skills_needed),
        " ".join(skills_offered)
    ]

    # Vectorize text
    vectorizer = CountVectorizer()
    vectors = vectorizer.fit_transform(text_data)

    # Compute cosine similarity
    similarity_matrix = cosine_similarity(vectors)

    score = similarity_matrix[0][1]

    return round(float(score), 2)


def level_compatibility_bonus(level1, level2):
    """
    Add bonus score if skill levels are compatible.
    """

    if level1.lower() == level2.lower():
        return 0.2
    elif level1.lower() == "beginner" and level2.lower() == "intermediate":
        return 0.1
    else:
        return 0.0


def calculate_match_score(skills_needed, skills_offered, level1, level2):
    """
    Final match score including similarity + level bonus
    """

    similarity_score = calculate_similarity(skills_needed, skills_offered)
    bonus = level_compatibility_bonus(level1, level2)

    final_score = similarity_score + bonus

    # Keep score between 0 and 1
    return round(min(final_score, 1.0), 2)


def explain_match(skills_needed, skills_offered):
    """
    Provide explanation for match
    """

    common_skills = list(set(skills_needed).intersection(set(skills_offered)))

    if common_skills:
        message = f"You both share interest in: {', '.join(common_skills)}"
    else:
        message = "No common skills found"

    return {
        "common_skills": common_skills,
        "explanation": message
    }

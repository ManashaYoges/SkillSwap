from ai.skill_matching import calculate_match_score, explain_match

userA_needed = ["Python", "Machine Learning"]
userB_offered = ["Python", "Data Science"]

score = calculate_match_score(
    userA_needed,
    userB_offered,
    "Beginner",
    "Beginner"
)

print("Match Score:", score)
print(explain_match(userA_needed, userB_offered))

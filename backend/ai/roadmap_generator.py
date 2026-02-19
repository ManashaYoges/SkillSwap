from typing import List

ROADMAPS = {
    "Data Science": [
        "Python Basics",
        "Statistics & Probability",
        "Data Wrangling with Pandas",
        "Data Visualisation",
        "Machine Learning Fundamentals",
        "Model Evaluation & Tuning",
        "Capstone Projects",
    ],
    "Machine Learning": [
        "Python & NumPy Basics",
        "Statistics & Linear Algebra",
        "Supervised Learning",
        "Unsupervised Learning",
        "Deep Learning Intro",
        "ML Ops & Deployment",
        "Real-world Projects",
    ],
    "Cyber Security": [
        "Networking Basics",
        "Linux Fundamentals",
        "Cryptography Basics",
        "Security Tools (Nmap, Wireshark)",
        "Web App Security",
        "Ethical Hacking & Pen Testing",
        "Hands-on Labs & CTFs",
    ],
    "Web Development": [
        "HTML & CSS",
        "JavaScript Essentials",
        "React / Vue Frontend",
        "Node.js Backend Basics",
        "REST API Design",
        "Databases (SQL + MongoDB)",
        "Full-Stack Capstone Project",
    ],
    "UI/UX Design": [
        "Design Principles",
        "Figma / Sketch Basics",
        "User Research & Personas",
        "Wireframing & Prototyping",
        "Usability Testing",
        "Design Systems",
        "Portfolio Project",
    ],
    "Python": [
        "Variables, Data Types & Control Flow",
        "Functions & Modules",
        "OOP in Python",
        "File Handling & Exceptions",
        "Libraries (NumPy, Pandas)",
        "Testing & Debugging",
        "Build a Python Project",
    ],
}

LEVEL_WEIGHTS = {
    "Beginner": 1,
    "Intermediate": 2,
    "Advanced": 3,
}


def generate_roadmap(skill_goal: str, level: str = "Beginner") -> List[dict]:
    """
    Generate a structured learning roadmap for skill_goal at a given level.
    Returns a list of step dicts with order, title, level, and estimated_weeks.
    """
    base_steps = ROADMAPS.get(skill_goal, [f"Learn {skill_goal} fundamentals", f"Practice {skill_goal}", f"Build a {skill_goal} project"])
    weight = LEVEL_WEIGHTS.get(level, 1)

    # Skip early steps for higher levels
    skip = (weight - 1) * 2
    relevant_steps = base_steps[skip:] if skip < len(base_steps) else base_steps

    roadmap = []
    for i, step in enumerate(relevant_steps):
        roadmap.append(
            {
                "order": i + 1,
                "title": step,
                "level": level,
                "estimated_weeks": 1 if level == "Advanced" else 2,
                "resources": [],  # Frontend can populate from external APIs
            }
        )
    return roadmap
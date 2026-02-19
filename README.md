SkillSwapAI is an AI-driven platform that matches learners and mentors for skill exchange. Users can find the best matches based on skills, generate personalized learning roadmaps, and securely collaborate to enhance learning efficiency.”
-----------------------------------------------------------------------------------------------
Implementation:

User Profiles: Skills offered and needed, verified credentials.
AI Matching: Using TF-IDF similarity + skill-level bonuses to recommend top matches.
Learning Roadmaps: Predefined AI-generated paths for skill goals (Data Science, Web Dev, etc.).
Security: Verified accounts, reporting system, skill credibility checks to avoid cheating.
Frontend: User-friendly interface (HTML, CSS, JS, or React).
Backend: FastAPI server with endpoints for user data, AI recommendations, and roadmap generation.
Database: PostgreSQL/SQLite for storing users, skills, and sessions.
AI Logic: Skill similarity, match scoring, roadmap generation.
Integration: REST API calls from frontend to backend.
----------------------------------------------------------------------------------------------
#how to use skillswapai
Step 1:
git clone https://github.com/yourusername/SkillSwapAI.git
cd SkillSwapAI

Step 2:
python -m venv venv
venv\Scripts\activate 

Step 3 :
pip install -r backend/requirements.txt

Step 4 :
cd backend
uvicorn main:app --reload

Step 5 :
Get user recommendations:
http://127.0.0.1:8000/recommendations?user_id=1

Generate a learning roadmap:
http://127.0.0.1:8000/roadmap?skill_goal=Data%20Science


Step 6:
Run the frontend
---------------------------------------------------------------------------------------
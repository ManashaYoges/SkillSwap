# ⚡ SkillSwap AI — Backend

FastAPI + MongoDB + JWT + AI Matching

## 📁 Structure
```
skillswap-backend/
├── main.py                  # App entry point
├── requirements.txt
├── .env                     # Your secrets
└── app/
    ├── core/
    │   ├── config.py        # Settings
    │   ├── database.py      # MongoDB connection
    │   └── security.py      # JWT + password hashing
    ├── models/
    │   ├── user.py          # Pydantic schemas
    │   └── session.py
    ├── routes/
    │   ├── auth.py          # POST /auth/register, /auth/login
    │   ├── users.py         # GET/PUT /users/me, /users/leaderboard
    │   ├── matching.py      # GET /matching/
    │   ├── sessions.py      # CRUD /sessions/
    │   └── ledger.py        # GET /ledger/
    └── services/
        ├── matching.py      # AI matching engine (Sentence Transformers)
        └── trust.py         # Trust score + fraud detection
```

## 🚀 Setup (5 minutes)

### 1. Install MongoDB
```bash
# Mac
brew tap mongodb/brew && brew install mongodb-community && brew services start mongodb-community

# Ubuntu
sudo apt install -y mongodb && sudo systemctl start mongodb

# Or use MongoDB Atlas (cloud) — paste connection string in .env
```

### 2. Create virtual environment
```bash
cd skillswap-backend
python -m venv venv
source venv/bin/activate     # Mac/Linux
venv\Scripts\activate        # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure .env
```
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=skillswap
SECRET_KEY=change-this-to-something-random
```

### 5. Run the server
```bash
uvicorn main:app --reload --port 8000
```

### 6. Open API docs
```
http://localhost:8000/docs
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login → get JWT token |
| GET | `/users/me` | Get my profile |
| PUT | `/users/me` | Update profile |
| GET | `/users/leaderboard` | Top users by coins & trust |
| GET | `/matching/` | AI-powered match list |
| POST | `/sessions/` | Request a session |
| GET | `/sessions/` | My sessions |
| PUT | `/sessions/{id}/confirm` | Confirm a session |
| PUT | `/sessions/{id}/complete` | Complete → transfer coins |
| GET | `/ledger/` | SkillCoin transaction history |

---

## 🔗 Connect to your HTML frontend

In your `SkillSwapAI.html`, add this at the top of the `<script>`:

```js
const API = "http://localhost:8000";
let TOKEN = localStorage.getItem("token");

async function apiCall(method, path, body = null) {
  const res = await fetch(API + path, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(TOKEN ? { "Authorization": "Bearer " + TOKEN } : {})
    },
    body: body ? JSON.stringify(body) : null
  });
  if (!res.ok) throw await res.json();
  return res.json();
}

// Login example:
async function login(email, password) {
  const data = await apiCall("POST", "/auth/login", { email, password });
  TOKEN = data.access_token;
  localStorage.setItem("token", TOKEN);
  return data.user;
}

// Get AI matches:
async function fetchMatches() {
  return apiCall("GET", "/matching/");
}

// Get ledger:
async function fetchLedger() {
  return apiCall("GET", "/ledger/");
}
```

---

## 🤖 AI Matching Engine
Uses `sentence-transformers/all-MiniLM-L6-v2` — a fast, lightweight model that:
- Finds **semantic similarity** between skills (e.g. "ML" ≈ "Data Science")
- Scores bilateral matches (you teach what they want, they teach what you want)
- Factors in trust score

## 🛡 Trust & Fraud Detection
- Recalculated after every session
- Flags: >8 sessions/day, sessions <30min apart, >200 coins in 24h
- Badges auto-awarded based on milestones

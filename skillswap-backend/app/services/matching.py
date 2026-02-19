from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Dict, Any

# Load once at startup (lightweight model for hackathon speed)
model = SentenceTransformer("all-MiniLM-L6-v2")

def _embed(texts: List[str]) -> np.ndarray:
    return model.encode(texts, convert_to_numpy=True)

def compute_match_score(user: Dict, candidate: Dict) -> Dict[str, Any]:
    """
    Compute a match score between two users.
    Returns score (0-100) + human-readable explanation.
    """
    user_offered   = [s["name"] for s in user.get("skills_offered", [])]
    user_wanted    = user.get("skills_wanted", [])
    cand_offered   = [s["name"] for s in candidate.get("skills_offered", [])]
    cand_wanted    = candidate.get("skills_wanted", [])

    score = 0.0
    reasons = []

    # ── 1. Direct bilateral match (highest weight: 50pts) ────────────────────
    bilateral_hits = set(user_offered) & set(cand_wanted)
    reverse_hits   = set(cand_offered) & set(user_wanted)

    if bilateral_hits and reverse_hits:
        score += 50
        reasons.append(
            f"Perfect bilateral match: you teach <strong>{', '.join(bilateral_hits)}</strong> "
            f"and learn <strong>{', '.join(reverse_hits)}</strong> from them."
        )
    elif bilateral_hits:
        score += 25
        reasons.append(f"You can teach <strong>{', '.join(bilateral_hits)}</strong> to them.")
    elif reverse_hits:
        score += 25
        reasons.append(f"They teach <strong>{', '.join(reverse_hits)}</strong> — exactly what you want.")

    # ── 2. Semantic similarity (30pts) ───────────────────────────────────────
    if user_wanted and cand_offered:
        try:
            u_vecs = _embed(user_wanted)
            c_vecs = _embed(cand_offered)
            sim_matrix = cosine_similarity(u_vecs, c_vecs)
            best_sim = float(np.max(sim_matrix))
            sem_score = round(best_sim * 30, 1)
            score += sem_score
            if best_sim > 0.5:
                reasons.append(
                    f"Semantic skill overlap detected (similarity: {round(best_sim*100)}%)."
                )
        except Exception:
            pass

    # ── 3. Trust score bonus (20pts) ─────────────────────────────────────────
    trust = candidate.get("trust_score", 100)
    trust_bonus = round((trust / 100) * 20, 1)
    score += trust_bonus
    if trust >= 90:
        reasons.append(f"High trust score ({trust}/100) — low-risk exchange.")

    # Cap at 100
    final_score = min(round(score), 100)

    # Build explanation
    if not reasons:
        reasons.append("Complementary learning paths and schedule availability detected.")

    explanation = " ".join(reasons)

    return {
        "score": final_score,
        "explanation": explanation,
        "bilateral": bool(bilateral_hits and reverse_hits),
    }


def get_matches(current_user: Dict, all_users: List[Dict], top_n: int = 5) -> List[Dict]:
    """Return top N matches for current_user, sorted by score descending."""
    results = []
    for candidate in all_users:
        if str(candidate["_id"]) == str(current_user["_id"]):
            continue
        match = compute_match_score(current_user, candidate)
        results.append({
            "user_id":      str(candidate["_id"]),
            "name":         candidate["name"],
            "skills_offered": candidate.get("skills_offered", []),
            "skills_wanted":  candidate.get("skills_wanted", []),
            "trust_score":  candidate.get("trust_score", 100),
            "skill_coins":  candidate.get("skill_coins", 0),
            "sessions_completed": candidate.get("sessions_completed", 0),
            "badges":       candidate.get("badges", []),
            "match_score":  match["score"],
            "explanation":  match["explanation"],
            "bilateral":    match["bilateral"],
        })

    results.sort(key=lambda x: x["match_score"], reverse=True)
    return results[:top_n]

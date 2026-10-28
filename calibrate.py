from app.rag import search_policies, is_relevant

# build_index()  # This is now handled by the @lru_cache decorator in app.rag

ANSWERABLE = [
    ("How do I cancel my policy?", "cancellation.txt"),
    ("Is theft covered by my home insurance?", "home_coverage.txt"),
    ("Am I covered if I get sick abroad?", "travel_coverage.txt"),
    ("How long do I have to report a claim?", "claims_deadline.txt"),
    ("Is wear and tear covered?", "exclusions.txt"),
]
UNANSWERABLE = [
    "Is my cat covered?",
    "Do you offer car insurance?",
    "What is the weather tomorrow?",
    "Can students get a discount?",
    "Is my bike covered?",
]

print("--- ANSWERABLE ---")
for q, expected in ANSWERABLE:
    r = search_policies(q)
    ok = "OK" if r["source"] == expected else "WRONG"
    print(round(r["score"], 3), ok, is_relevant(q, r["text"]), q)

print("--- UNANSWERABLE ---")
for q in UNANSWERABLE:
    r = search_policies(q)
    print(round(r["score"], 3), r["source"], is_relevant(q, r["text"]), q)
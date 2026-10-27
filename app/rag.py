from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from qdrant_client import QdrantClient, models

load_dotenv()

POLICY_DIR = Path(__file__).parent.parent / "data" / "policies"
COLLECTION = "policies"
THRESHOLD = 0.60

CHECK_PROMPT = """Question: {question}
Text: {text}
Does the text answer the question? Reply only YES or NO."""


@lru_cache
def get_embeddings():
    return GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")


@lru_cache
def get_llm():
    return ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")


@lru_cache
def get_client():
    client = QdrantClient(":memory:")
    files = sorted(POLICY_DIR.glob("*.txt"))
    texts = [f.read_text(encoding="utf-8") for f in files]
    vectors = get_embeddings().embed_documents(texts)      # one embedding per file
    client.create_collection(
        COLLECTION,
        vectors_config=models.VectorParams(size=len(vectors[0]), distance=models.Distance.COSINE),
    )
    client.upsert(COLLECTION, points=[
        models.PointStruct(id=i, vector=v, payload={"source": f.name, "text": t})
        for i, (f, t, v) in enumerate(zip(files, texts, vectors))
    ])
    return client


def search_policies(query: str) -> dict:
    vector = get_embeddings().embed_query(query)
    best = get_client().query_points(COLLECTION, query=vector, limit=1, with_payload=True).points[0]
    return {"source": best.payload["source"], "text": best.payload["text"], "score": best.score}


def is_relevant(question: str, text: str) -> bool:
    reply = get_llm().invoke(CHECK_PROMPT.format(question=question, text=text))
    return reply.text.strip().upper().startswith("YES")
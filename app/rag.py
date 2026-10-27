from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from qdrant_client import QdrantClient, models

load_dotenv()

POLICY_DIR = Path(__file__).parent.parent / "data" / "policies"
COLLECTION = "policies"

embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
client = QdrantClient(":memory:")


def build_index():
    files = sorted(POLICY_DIR.glob("*.txt"))
    texts = [f.read_text(encoding="utf-8") for f in files]
    vectors = embeddings.embed_documents(texts)          # one embedding per file

    client.create_collection(
        COLLECTION,
        vectors_config=models.VectorParams(size=len(vectors[0]), distance=models.Distance.COSINE),
    )
    client.upsert(COLLECTION, points=[
        models.PointStruct(id=i, vector=v, payload={"source": f.name, "text": t})
        for i, (f, t, v) in enumerate(zip(files, texts, vectors))
    ])


def search_policies(query: str) -> dict:
    vector = embeddings.embed_query(query)
    best = client.query_points(COLLECTION, query=vector, limit=1, with_payload=True).points[0]
    return {"source": best.payload["source"], "text": best.payload["text"], "score": best.score}

THRESHOLD = 0.60
llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

CHECK_PROMPT = """Question: {question}
Text: {text}
Does the text answer the question? Reply only YES or NO."""


def is_relevant(question: str, text: str) -> bool:
    reply = llm.invoke(CHECK_PROMPT.format(question=question, text=text))
    return reply.text.strip().upper().startswith("YES")
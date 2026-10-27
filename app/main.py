from fastapi import FastAPI
from app.graph import graph
from app.models import ChatRequest, ChatResponse

app = FastAPI(title="Insurance Assistant Agent")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


#@app.post("/chat", response_model=ChatResponse)
#def chat(request: ChatRequest) -> ChatResponse:
    # Temporary echo — replaced by the LangGraph agent on Day 2
 #   return ChatResponse(
  #      reply=f"You said: {request.message}",
   #     status="ok",
    #    sources=[],
    #)

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    config = {"configurable": {"thread_id": request.session_id}}
    result = graph.invoke({"message": request.message}, config)
    return ChatResponse(
        reply=result["reply"],
        status=result["status"],
        sources=result.get("sources", []),          # filled by RAG on Day 3
    )   

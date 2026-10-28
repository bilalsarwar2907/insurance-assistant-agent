"""Optional LLM-as-judge: grades real RAG answers. Needs GOOGLE_API_KEY. Not part of CI."""
import json
import re
import uuid
from pathlib import Path

from app import rag
from app.graph import graph

EVALS = Path(__file__).parent
CASES = json.loads((EVALS / "cases.json").read_text(encoding="utf-8"))["rag"]
PASS = 0.7

JUDGE_PROMPT = """You are grading a customer-support answer.
Question: {question}
Policy text: {text}
Answer: {answer}

grounded: 1 if every fact in the answer is in the policy text, 0 if anything is invented.
relevant: 1 if the answer addresses the question, 0 if not.
Use values between 0 and 1 for partial cases.
Reply in exactly this format:
grounded=<number> relevant=<number>"""


def judge(question: str, text: str, answer: str) -> dict:
    reply = rag.get_llm().invoke(JUDGE_PROMPT.format(question=question, text=text, answer=answer)).text
    scores = dict(re.findall(r"(grounded|relevant)=([01](?:\.\d+)?)", reply))
    return {k: float(v) for k, v in scores.items()}


def main() -> None:
    results = []
    for case in CASES:
        q = case["message"]
        state = graph.invoke({"message": q}, {"configurable": {"thread_id": str(uuid.uuid4())}})
        if state["status"] != "answered":
            results.append({"question": q, "status": state["status"]})
            continue
        answer = state["reply"].split(" [Source:")[0]
        text = rag.search_policies(q)["text"]
        s = judge(q, text, answer)
        ok = s.get("grounded", 0) >= PASS and s.get("relevant", 0) >= PASS
        results.append({"question": q, "answer": answer, **s, "pass": ok})
        print(f"{'PASS' if ok else 'FAIL'}  g={s.get('grounded')}  r={s.get('relevant')}  {q}")

    (EVALS / "judge_results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\n{sum(r.get('pass', False) for r in results)}/{len(results)} passed (threshold {PASS})")


if __name__ == "__main__":
    main()
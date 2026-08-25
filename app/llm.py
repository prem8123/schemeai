import os
import httpx

class LLMClient:
    """Optional OpenAI-compatible chat client. The core demo works without it."""
    def __init__(self):
        self.base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.model = os.getenv("LLM_MODEL", "gpt-4o-mini")

    def available(self):
        return bool(self.api_key)

    def answer(self, question: str, evidence: list[dict]) -> str:
        if not self.available():
            return "LLM generation is not configured. Review the retrieved evidence and eligibility results below."
        context = "\n\n".join(f"[{i+1}] {e['text']} (source: {e['source']}, page: {e.get('page') or 'N/A'})" for i, e in enumerate(evidence))
        payload = {"model": self.model, "temperature": 0.1, "messages": [
            {"role": "system", "content": "You are SchemeAI. Answer only from supplied evidence. If evidence is insufficient, say so. Never invent scholarship rules. Cite evidence as [1], [2]."},
            {"role": "user", "content": f"Question: {question}\n\nEvidence:\n{context}"},
        ]}
        r = httpx.post(f"{self.base_url}/chat/completions", headers={"Authorization": f"Bearer {self.api_key}"}, json=payload, timeout=45)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]

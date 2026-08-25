import os

import httpx


class LLMClient:
    """Optional OpenAI-compatible chat client. Core eligibility matching remains deterministic."""

    def __init__(self):
        self.base_url = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.model = os.getenv("LLM_MODEL", "gpt-4o-mini")

    def available(self):
        return bool(self.api_key)

    def answer(self, question: str, evidence: list[dict], language: str = "en") -> str:
        if not self.available():
            fallbacks = {
                "en": "LLM generation is not configured. Review the retrieved evidence and eligibility results below.",
                "kn": "LLM ಉತ್ತರ ಸೇವೆ ಸಂರಚಿಸಲಾಗಿಲ್ಲ. ಕೆಳಗಿನ ಸಾಕ್ಷ್ಯ ಮತ್ತು ಅರ್ಹತಾ ಫಲಿತಾಂಶಗಳನ್ನು ಪರಿಶೀಲಿಸಿ.",
                "hi": "LLM उत्तर सेवा कॉन्फ़िगर नहीं है। नीचे दिए गए प्रमाण और पात्रता परिणाम देखें।",
            }
            return fallbacks.get(language, fallbacks["en"])
        context = "\n\n".join(
            f"[{i + 1}] {e['text']} (source: {e['provenance']['official_url']}, reference: {e['provenance']['reference']})"
            for i, e in enumerate(evidence)
        )
        language_name = {"en": "English", "kn": "Kannada", "hi": "Hindi"}.get(language, "English")
        payload = {
            "model": self.model,
            "temperature": 0.1,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        f"You are SchemeAI. Answer only from supplied evidence and respond in {language_name}. "
                        "If evidence is insufficient, say so. Never invent scholarship rules. Cite evidence as [1], [2]."
                    ),
                },
                {"role": "user", "content": f"Question: {question}\n\nEvidence:\n{context}"},
            ],
        }
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json=payload,
            timeout=45,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

from __future__ import annotations
import os, time
import httpx

class LLMClient:
    def __init__(self):
        self.base_url=os.getenv("LLM_BASE_URL","https://api.openai.com/v1").rstrip("/")
        self.api_key=os.getenv("LLM_API_KEY","").strip()
        self.model=os.getenv("LLM_MODEL","gpt-4o-mini")
        self.timeout=float(os.getenv("LLM_TIMEOUT_SECONDS","30"))
    def available(self): return bool(self.api_key)
    def answer(self,question,evidence,language="en"):
        if not self.available(): return self._fallback(language)
        context="\n\n".join(f"[{i+1}] {e['text']} (official source: {e['provenance']['official_url']}; reference: {e['provenance']['reference']})" for i,e in enumerate(evidence))
        if not context: return self._insufficient(language)
        lang={"en":"English","kn":"Kannada","hi":"Hindi"}.get(language,"English")
        payload={"model":self.model,"temperature":0.1,"messages":[
            {"role":"system","content":f"You are SchemeAI. Answer only from supplied evidence and respond in {lang}. Never invent eligibility rules, deadlines, amounts, documents, or URLs. If evidence is insufficient or stale, say so. Cite evidence as [1], [2]. Do not make the final government eligibility decision."},
            {"role":"user","content":f"Question: {question}\n\nEvidence:\n{context}"}]}
        last_error=None
        for attempt in range(2):
            try:
                response=httpx.post(f"{self.base_url}/chat/completions",headers={"Authorization":f"Bearer {self.api_key}"},json=payload,timeout=self.timeout)
                response.raise_for_status()
                content=response.json()["choices"][0]["message"]["content"]
                if not isinstance(content,str) or not content.strip(): raise ValueError("LLM returned an empty answer")
                return content.strip()
            except (httpx.HTTPError,KeyError,TypeError,ValueError) as exc:
                last_error=exc
                if attempt==0: time.sleep(0.25)
        return f"LLM generation failed safely ({type(last_error).__name__}). Please review the retrieved official evidence below."
    @staticmethod
    def _fallback(language):
        return {"en":"LLM generation is not configured. Review the official evidence and deterministic eligibility results below.","kn":"LLM ಉತ್ತರ ಸೇವೆ ಸಂರಚಿಸಲಾಗಿಲ್ಲ. ಕೆಳಗಿನ ಅಧಿಕೃತ ಸಾಕ್ಷ್ಯ ಮತ್ತು ಅರ್ಹತಾ ಫಲಿತಾಂಶಗಳನ್ನು ಪರಿಶೀಲಿಸಿ.","hi":"LLM उत्तर सेवा कॉन्फ़िगर नहीं है। नीचे दिए गए आधिकारिक प्रमाण और पात्रता परिणाम देखें।"}.get(language,"LLM generation is not configured.")
    @staticmethod
    def _insufficient(language):
        return {"en":"No sufficiently relevant evidence was retrieved, so I will not invent an answer.","kn":"ಸಾಕಷ್ಟು ಸಂಬಂಧಿತ ಸಾಕ್ಷ್ಯ ಸಿಗಲಿಲ್ಲ; ಆದ್ದರಿಂದ ನಾನು ಉತ್ತರವನ್ನು ಊಹಿಸುವುದಿಲ್ಲ.","hi":"पर्याप्त प्रासंगिक प्रमाण नहीं मिला, इसलिए मैं उत्तर का अनुमान नहीं लगाऊंगा।"}.get(language,"No sufficiently relevant evidence was retrieved.")

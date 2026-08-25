TRANSLATIONS = {
    "en": {"likely": "Likely eligible", "possible": "Possibly eligible", "unknown": "Needs more information", "not": "Not eligible"},
    "kn": {"likely": "ಅರ್ಹರಾಗಿರುವ ಸಾಧ್ಯತೆ ಹೆಚ್ಚು", "possible": "ಅರ್ಹರಾಗಿರುವ ಸಾಧ್ಯತೆ ಇದೆ", "unknown": "ಹೆಚ್ಚಿನ ಮಾಹಿತಿ ಅಗತ್ಯ", "not": "ಅರ್ಹತೆ ಇಲ್ಲ"},
    "hi": {"likely": "संभावित रूप से पात्र", "possible": "संभवतः पात्र", "unknown": "अधिक जानकारी आवश्यक", "not": "पात्र नहीं"},
}

def status_label(status: str, language: str = "en") -> str:
    labels = TRANSLATIONS.get(language, TRANSLATIONS["en"])
    return {"LIKELY_ELIGIBLE": labels["likely"], "POSSIBLY_ELIGIBLE": labels["possible"], "UNKNOWN": labels["unknown"], "NOT_ELIGIBLE": labels["not"]}.get(status, status)

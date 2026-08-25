from app.language import detect_supported_language


def test_detects_english():
    assert detect_supported_language("Which scholarship can I apply for?") == "en"


def test_detects_kannada():
    assert detect_supported_language("ವಿದ್ಯಾರ್ಥಿವೇತನಕ್ಕೆ ಕುಟುಂಬದ ಆದಾಯ ಮಿತಿ ಎಷ್ಟು?") == "kn"


def test_detects_hindi():
    assert detect_supported_language("छात्रवृत्ति के लिए आय सीमा कितनी है?") == "hi"

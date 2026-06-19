"""
utils/nlp_engine.py
NLP sentiment + emotion detection using TextBlob/NLTK with keyword heuristics.
"""
from textblob import TextBlob

EMOTION_KEYWORDS = {
    "stress": ["stress", "pressure", "overwhelm", "deadline", "tense"],
    "anxiety": ["anxious", "worry", "nervous", "panic", "fear", "scared"],
    "burnout": ["exhausted", "burnout", "drained", "tired", "no energy", "fatigue"],
    "sadness": ["sad", "down", "depressed", "lonely", "cry", "hopeless"],
    "joy": ["happy", "great", "joy", "excited", "grateful", "love", "amazing"],
    "calm": ["calm", "relaxed", "peaceful", "content", "rested"],
}


def analyze_text(text: str):
    """Return sentiment polarity, subjectivity, label, and dominant emotion."""
    blob = TextBlob(text)
    polarity = round(blob.sentiment.polarity, 3)
    subjectivity = round(blob.sentiment.subjectivity, 3)

    if polarity > 0.2:
        sentiment = "Positive"
    elif polarity < -0.2:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    low = text.lower()
    scores = {emo: sum(low.count(k) for k in kws) for emo, kws in EMOTION_KEYWORDS.items()}
    emotion = max(scores, key=scores.get) if max(scores.values()) > 0 else (
        "joy" if polarity > 0 else "neutral")

    return {
        "polarity": polarity,
        "subjectivity": subjectivity,
        "sentiment": sentiment,
        "emotion": emotion,
    }


def wellness_from_journals(journals):
    if not journals:
        return 60.0
    avg = sum(j["polarity"] for j in journals) / len(journals)
    return round(max(0, min(100, 60 + avg * 40)), 1)
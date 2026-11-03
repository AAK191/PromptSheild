import os, re, joblib
from .ml_bert import bert_prob, bert_probs

_PATH = os.path.join(os.path.dirname(__file__), "models", "clf.joblib")
_bundle = None
SEG_MARGIN = 0.15      # a segment must exceed the threshold by this much
BERT_THR = 0.95
MIN_BERT_WORDS = 5
GRAY_LOW = 0.2

def _load():
    global _bundle
    if _bundle is None and os.path.exists(_PATH):
        _bundle = joblib.load(_PATH)
    return _bundle

def _segments(text: str):
    parts = [p.strip() for p in re.split(r"(?<=[.?!])\s+|\n+", text) if len(p.strip()) >= 25]
    return parts[:12]

def ml_probs(text: str):
    """Returns (whole_text_prob, best_segment_prob)."""
    b = _load()
    if b is None or not text.strip():
        return 0.0, 0.0
    whole = float(b["model"].predict_proba([text[:2000]])[0][1])
    segs = _segments(text) if len(text) > 80 else []
    seg = float(b["model"].predict_proba(segs)[:, 1].max()) if segs else 0.0
    return whole, seg

def ml_prob(text: str) -> float:
    whole, seg = ml_probs(text)
    return max(whole, seg)


BERT_THR = 0.95  # Let's bump this up slightly to 0.95 to be extra saf

# app/ml.py


def ml_score(text: str, use_bert: bool = True) -> float:
    b = _load()
    tfidf = 0.0
    if b is not None:
        thr = b["threshold"]
        whole, seg = ml_probs(text)
        p = max(whole, seg - SEG_MARGIN)
        tfidf = (0.7 + 0.3 * (p - thr) / (1 - thr + 1e-9)) if p >= thr else 0.69 * p / thr

    bert = 0.0
    if use_bert and len(text.split()) >= MIN_BERT_WORDS:
        segs = [s for s in _segments(text)
                if len(s.split()) >= MIN_BERT_WORDS and s != text][:6]
        
        SEG_BERT_MARGIN = 0.03
        bp_whole = bert_prob(text)
        bp_seg = max(bert_probs(segs)) if segs else 0.0
        bp = max(bp_whole, bp_seg - SEG_BERT_MARGIN)

        bert = (0.7 + 0.3 * (bp - BERT_THR) / (1 - BERT_THR)) if bp >= BERT_THR else 0.69 * bp / BERT_THR
    return max(tfidf, bert)
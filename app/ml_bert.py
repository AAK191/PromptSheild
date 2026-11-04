import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

_PATH = os.path.join(os.path.dirname(__file__), "models", "bert")
_tok = None
_model = None

def _load():
    global _tok, _model
    if _model is None and os.path.isdir(_PATH):
        _tok = AutoTokenizer.from_pretrained(_PATH)
        _model = AutoModelForSequenceClassification.from_pretrained(_PATH)
        _model.to("cpu").eval()
    return _model

def bert_prob(text: str) -> float:
    m = _load()
    if m is None or not text.strip():
        return 0.0  # Fallback gracefully if model isn't found
    
    b = _tok(text[:2000], truncation=True, max_length=128, return_tensors="pt").to(m.device)
    with torch.no_grad():
        return float(torch.softmax(m(**b).logits, -1)[0, 1])


def bert_probs(texts: list[str]) -> list[float]:
    m = _load()
    if m is None or not texts:
        return [0.0] * len(texts)
    b = _tok([t[:2000] for t in texts], truncation=True, max_length=128,
             padding=True, return_tensors="pt").to(m.device)
    with torch.no_grad():
        return torch.softmax(m(**b).logits, -1)[:, 1].cpu().tolist()
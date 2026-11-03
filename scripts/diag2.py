# scripts/diag2.py
from app.normalizer import normalize
from app.ml import ml_probs
from app.ml_bert import bert_prob
from app.rules import check

for p in ["hello", "hello there", "hello world this is a test",
          "How do I write a for loop in Python?",
          "What can I substitute for butter in a cake recipe?"]:
    n = normalize(p)
    print(f"{p[:50]:52s} rules={check(n)[0]}  tfidf={max(ml_probs(n)):.2f}  bert={bert_prob(n):.3f}")
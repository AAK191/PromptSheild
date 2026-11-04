import time
from app.main import scan_text
from app.normalizer import normalize
from app.rules import check
from app.ml import ml_probs
from app.ml_bert import bert_prob

for p in ["who is PM of India?", "Give code for knapsack 0-1 problem in DSA","build roadmap to learn DSA in 30 days"]:
    n = normalize(p)
    t0 = time.perf_counter()
    r = scan_text(p)
    ms = int((time.perf_counter() - t0) * 1000)
    print(p)
    print("  rules:", check(n)[0], " tfidf:", [round(x, 2) for x in ml_probs(n)], " bert:", round(bert_prob(n), 3))
    print("  final:", r, f" scan took {ms} ms")
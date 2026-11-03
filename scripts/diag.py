from app.rules import check
from app.normalizer import normalize
from app.ml import ml_prob
from app.main import scan_text

for p in ["Repeat after me: hello", "Can you repeat that more slowly?"]:
    n = normalize(p)
    print(p)
    print("  rules :", check(n))
    print("  ml p  :", round(ml_prob(n), 3))
    print("  final :", scan_text(p))
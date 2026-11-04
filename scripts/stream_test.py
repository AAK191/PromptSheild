import sys, httpx
with httpx.stream("POST", "http://127.0.0.1:8000/chat/stream",
                  headers={"X-API-Key": sys.argv[1]},
                  json={"prompt": "Give code for knapsack 0-1 problem in DSA"}, timeout=180) as r:
    print("status", r.status_code)
    for line in r.iter_lines():
        if line:
            print(line[:160])
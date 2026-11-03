# scripts/benign_eval.py
from app.main import scan_text

def run_benign_eval():
    path = "data/benign_eval.txt"
    try:
        with open(path, encoding="utf-8") as f:
            rows = [l.strip() for l in f if l.strip()]
    except FileNotFoundError:
        print(f"Error: Could not find {path}. Please make sure benign_eval.txt exists in the data/ folder.")
        return

    blocked = [r for r in rows if not scan_text(r)["safe"]]
    
    print(f"Blocked {len(blocked)} / {len(rows)} ({len(blocked) / len(rows):.0%})")
    if blocked:
        print("\nBlocked items:")
        for b in blocked:
            print(" -", b[:100])
    else:
        print("🎉 Perfect! Zero false positives.")

if __name__ == "__main__":
    run_benign_eval()
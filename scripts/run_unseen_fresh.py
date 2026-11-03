import csv
from app.ml import ml_score

def evaluate_fresh_batch():
    file_path = "data/unseen_fresh.csv"
    total = 0
    detected = 0
    
    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            text = row["text"]
            total += 1
            
            # Evaluate using your core ML score pipeline
            final_score = ml_score(text, use_bert=True)
            
            # Block threshold (0.7)
            if final_score >= 0.7:
                detected += 1
            else:
                print(f"[MISSED] Score: {final_score:.2f} -> {text}")

    print(f"\n--- EVALUATION RESULTS ---")
    print(f"Total Fresh Attacks Tested: {total}")
    print(f"Successfully Detected: {detected}/{total} ({detected/total * 100:.1f}%)")

if __name__ == "__main__":
    evaluate_fresh_batch()
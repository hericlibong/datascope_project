import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from core.nlp_utils import extract_strong_verbs

if __name__ == "__main__":
    article = (
        "Le gouvernement a condamné les violences. "
        "Le séisme a secoué la région. "
        "Les manifestants ont revendiqué leurs droits. "
        "La population est submergée par la crise économique."
    )

    results = extract_strong_verbs(article)
    print("----- VERBES FORTS DÉTECTÉS -----")
    for item in results:
        print(f"{item['text']} → {item['lemma']} (pos {item['start']}-{item['end']})")

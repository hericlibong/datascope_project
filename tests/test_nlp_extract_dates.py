from core.nlp_utils import extract_dates
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    article = (
        "Emmanuel Macron a visité Bruxelles le 2 février. "
        "Un autre sommet est prévu le 5 mars 2025. "
        "La conférence initiale datait du 03/01/24."
    )

    dates = extract_dates(article, language="fr")
    print("----- DATES DÉTECTÉES -----")
    for d in dates:
        print(f"{d['text']} → {d['parsed_date']}")

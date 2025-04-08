import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from core.nlp_utils import extract_numbers_and_units

if __name__ == "__main__":
    article = (
        "Le séisme de 7,9 de magnitude a provoqué l'effondrement d'un immeuble de 30 étages. "
        "43 ouvriers sont portés disparus. "
        "La température a atteint 45,2 degrés dans certaines zones."
    )

    numbers = extract_numbers_and_units(article)
    print("----- NOMBRES DÉTECTÉS -----")
    for item in numbers:
        print(f"{item['value']} → {item['unit']} (pos {item['start']}-{item['end']})")

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from core.nlp_utils import format_entities

if __name__ == "__main__":
    article = (
        "Emmanuel Macron a condamné les violences à Paris le 3 avril. "
        "Le séisme de 7.9 de magnitude a provoqué l'effondrement d'un immeuble de 30 étages. "
        "43 ouvriers sont portés disparus. "
    )

    result = format_entities(article)
    print("----- ANALYSE NLP FORMATTÉE -----")
    for key, values in result.items():
        print(f"\n{key.upper()}:")
        for item in values:
            print(item)

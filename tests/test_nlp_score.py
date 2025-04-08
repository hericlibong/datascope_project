import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from core.nlp_utils import format_entities, compute_datafication_score

if __name__ == "__main__":
    article = (
        "Emmanuel Macron a condamné les violences à Paris le 3 avril. "
        "Le séisme de 7.9 de magnitude a provoqué l'effondrement d'un immeuble de 30 étages. "
        "43 ouvriers sont portés disparus. "
        "La population est submergée par la crise économique."
    )

    entities = format_entities(article)
    result = compute_datafication_score(entities, article)

    print("----- SCORE DE DATAFICATION -----")
    print(f"Score : {result['score']}/10")
    print(f"Densité : {result['density']} (mots struct. / mots total)")
    print(f"Total éléments structurés : {result['structured_items']}")
    print(f"Taille article : {result['word_count']} mots")
    print("Justifications :")
    for j in result["justifications"]:
        print(f"- {j}")

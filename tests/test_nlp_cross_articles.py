import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from core.nlp_utils import format_entities, compute_datafication_score


def test_article(label: str, article: str):
    print(f"\n===== TEST : {label.upper()} =====\n")
    entities = format_entities(article)
    result = compute_datafication_score(entities, article)

    print(f"Score : {result['score']}/10")
    print(f"Densité : {result['density']}")
    print(f"Éléments structurés : {result['structured_items']}")
    print("Justifications :")
    for j in result["justifications"]:
        print(f"- {j}")


if __name__ == "__main__":
    # Article événementiel
    article_event = (
        "Un séisme de magnitude 7.7 a frappé la Birmanie, causant l'effondrement d'un immeuble. "
        "43 ouvriers sont portés disparus. La secousse a été ressentie jusqu'en Chine. "
        "L'événement s'est produit le 28 mars à 13h30."
    )

    # Article local
    article_local = (
        "Stéphane Ruel, boucher-charcutier à Assé-le-Boisne, a remporté la médaille d’or "
        "au concours de rillettes de Mamers. Il travaille exclusivement avec des producteurs locaux. "
        "Son établissement emploie deux salariés à temps complet."
    )

    # Article politique
    article_politique = (
        "Le 2 avril 2025, l'Assemblée nationale a voté par 155 voix contre 85 la régulation de "
        "l'installation des médecins dans les zones sur-dotées. Cette mesure, défendue par le député Guillaume Garot, "
        "vise à lutter contre les déserts médicaux. Le gouvernement s'y est opposé."
    )

    test_article("événementiel", article_event)
    test_article("local", article_local)
    test_article("politique", article_politique)

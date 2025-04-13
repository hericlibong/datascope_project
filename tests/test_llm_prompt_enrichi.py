from core.llm_engine import build_enriched_prompt
from core.nlp_utils import format_entities
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    article = (
        "Emmanuel Macron a condamné les violences à Paris le 3 avril. "
        "Le séisme de 7.9 de magnitude a provoqué l'effondrement d'un immeuble de 30 étages. "
        "43 ouvriers sont portés disparus. "
        "La population est submergée par la crise économique."
    )

    entities = format_entities(article)
    messages = build_enriched_prompt(article, entities)

    print("----- PROMPT CONSTRUIT POUR OPENAI -----\n")
    for m in messages:
        print(f"[{m['role'].upper()}]\n{m['content']}\n")

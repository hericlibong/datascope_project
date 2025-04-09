import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from core.nlp_utils import format_entities
from core.llm_engine import suggest_datasets_llm

if __name__ == "__main__":
    article = (
        "Un séisme de magnitude 7.9 a frappé la Birmanie le 28 mars. "
        "Il a causé l’effondrement de plusieurs immeubles. 43 ouvriers sont portés disparus. "
        "L’événement a été ressenti jusqu’en Chine."
    )

    entities = format_entities(article)
    print("----- SUGGESTIONS DE SOURCES / DATASETS -----\n")
    print(suggest_datasets_llm(article, entities))

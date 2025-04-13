from core.nlp_utils import extract_named_entities
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    article = (
        "Emmanuel Macron visited Brussels on February 2nd."
    )

    entities = extract_named_entities(article, language="en")
    print("----- ENTITÉS NOMMÉES -----")
    for ent in entities:
        print(f"{ent['text']} → {ent['label']}")

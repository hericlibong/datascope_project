import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from core.nlp_utils import format_entities, compute_datafication_score, interpret_datafication_score

# Exemple d'article en anglais
text_en = """
In 2023, the UK government announced a £50 billion plan to expand offshore wind farms.
The goal is to double the capacity by 2030. Experts at the International Energy Agency (IEA) 
estimate this could reduce national emissions by 25% over the next decade.
"""

def display_results(text):
    print("\n📘 TEXT SAMPLE:")
    print(text[:200] + "...\n")

    print("🔎 Running NLP analysis...\n")
    entities = format_entities(text, language="en")
    score = compute_datafication_score(entities, text)
    comment = interpret_datafication_score(score["score"])

    print("✅ Named Entities:")
    for ent in entities["named_entities"]:
        print(f"- {ent['text']} [{ent['label']}]")

    print("\n🔢 Numbers + Units:")
    for n in entities["numbers"]:
        print(f"- {n['value']} {n['unit']}")

    print("\n📅 Dates:")
    for d in entities["dates"]:
        print(f"- {d['text']} → {d['parsed_date']}")

    print("\n⚡ Strong Verbs:")
    for v in entities["strong_verbs"]:
        print(f"- {v['text']} (lemma: {v['lemma']})")

    print(f"\n📊 Score: {score['score']} / 10")
    print(f"💬 Commentaire : {comment}")
    print(f"📈 Densité : {score['density']}")
    print(f"📦 Éléments structurés : {score['structured_items']}\n")


if __name__ == "__main__":
    display_results(text_en)

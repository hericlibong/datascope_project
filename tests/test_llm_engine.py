import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from core.llm_engine import call_openai

if __name__ == "__main__":
    messages = [
        {"role": "system", "content": "Tu es un assistant spécialisé en datajournalisme."},
        {"role": "user", "content": "Donne-moi 3 angles journalistiques à partir de cet événement : \
        'Un séisme de magnitude 7.9 a frappé la Birmanie, causant 3 000 morts'."}
    ]

    print("----- RÉPONSE DE GPT -----\n")
    print(call_openai(messages))

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from core.llm_engine import generate_journalistic_angles

if __name__ == "__main__":
    article = (
        "Un séisme de magnitude 7.9 a frappé la Birmanie le 28 mars, provoquant l'effondrement de plusieurs immeubles. "
        "43 ouvriers sont portés disparus. L'événement a été ressenti jusqu'en Chine."
    )

    print("----- ANGLES JOURNALISTIQUES GÉNÉRÉS -----\n")
    print(generate_journalistic_angles(article))

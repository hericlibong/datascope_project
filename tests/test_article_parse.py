from core.article_parser import extract_article_text
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).resolve().parents[1]))

if __name__ == "__main__":
    path = "samples/test_article.txt"  # à créer pour tester
    content = extract_article_text(path)
    print("----- CONTENU EXTRAIT -----")
    print(content[:1000])  # affiche les 1000 premiers caractères

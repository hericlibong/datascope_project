from core.article_parser import extract_article_text
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))



if __name__ == "__main__":
    path = "samples/pdf_test.pdf"
    content = extract_article_text(path)
    print("----- CONTENU EXTRAIT DU PDF -----\n")
    print(content[:1000])

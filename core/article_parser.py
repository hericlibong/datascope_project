from pathlib import Path
from typing import Union
import docx
from pdfminer.high_level import extract_text
import chardet


def read_txt(file_path: Union[str, Path]) -> str:
    """Lit un fichier .txt avec détection automatique de l'encodage"""
    with open(file_path, "rb") as f:
        raw = f.read()
    encoding = chardet.detect(raw)["encoding"]
    return raw.decode(encoding)


def read_pdf(file_path: Union[str, Path]) -> str:
    """Lit un fichier .pdf et en extrait le texte brut"""
    return extract_text(file_path)


def read_docx(file_path: Union[str, Path]) -> str:
    """Lit un fichier Word .docx et concatène les paragraphes"""
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])


def extract_article_text(file_path: Union[str, Path]) -> str:
    """Route principale qui choisit le bon lecteur selon l'extension"""
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".txt":
        return read_txt(path)
    elif suffix == ".pdf":
        return read_pdf(path)
    elif suffix == ".docx":
        return read_docx(path)
    else:
        raise ValueError(f"Format non pris en charge : {suffix}")

def export_analysis_to_markdown(article_text, score, score_comment, profile, entities, angles, sources):
    lines = []

    lines.append("# 📄 Résultat de l’analyse DataScope\n")
    lines.append("## 🧾 Texte analysé\n")
    lines.append(f"```\n{article_text.strip()}\n```\n")

    lines.append("## 📊 Score de datafication\n")
    lines.append(f"- Score : **{score['score']}/10**")
    lines.append(f"- Densité : `{score['density']}` ({score['structured_items']} éléments pour {score['word_count']} mots)")
    lines.append(f"- Commentaire : _{score_comment}_")
    lines.append(f"- Profil éditorial : _{profile}_\n")

    lines.append("## 🧠 Entités détectées")
    if entities.get("named_entities"):
        lines.append("- Entités nommées : " + ", ".join(f"{e['text']} ({e['label']})" for e in entities["named_entities"]))
    if entities.get("numbers"):
        lines.append("- Nombres : " + ", ".join(f"{n['value']} {n['unit']}" for n in entities["numbers"]))
    if entities.get("dates"):
        lines.append("- Dates : " + ", ".join(d["text"] for d in entities["dates"]))
    if entities.get("strong_verbs"):
        lines.append("- Verbes forts : " + ", ".join(v["lemma"] for v in entities["strong_verbs"]))
    lines.append("")

    lines.append("## 🧭 Suggestions d’angles journalistiques\n")
    lines.append(angles.strip() + "\n")

    lines.append("## 🌐 Suggestions de sources / datasets\n")
    lines.append(sources.strip())

    return "\n".join(lines)

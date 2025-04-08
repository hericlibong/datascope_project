import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from core.nlp_utils import format_entities, compute_datafication_score

if __name__ == "__main__":
    article = (
        """
        Quel a été le pire tremblement de terre de l'histoire de France?

        [L'Explication #212] Si les territoires d'outre-mer sont particulièrement vulnérables aux catastrophes sismiques, la France métropolitaine n'est pas épargnée pour autant.

        Le drame fait les gros titres depuis plusieurs jours. Le vendredi 28 mars 2025, un puissant séisme d'une magnitude de 7,7 sur l'échelle de Richter a frappé le centre de la Birmanie. Résultat, des milliers de morts potentiels (au moins 3.000 d'après les derniers bilans) et des villes en ruines, notamment le long de la faille de Sagaing, qui traverse un pays déjà marqué par la guerre civile.

        Une telle catastrophe naturelle peut-elle survenir en France? Dans les territoires d'outre-mer, oui. La Martinique comme la Guadeloupe ont déjà connu des séismes ravageurs dans leur histoire, comparables en matière d'intensité à celui de la Birmanie. Bien loin de ceux ressentis en France métropolitaine, qui n'est, vous allez le voir, pas épargnée pour autant.


        11 janvier 1839 et 8 février 1843, dates noires

        Le 11 janvier 1839 est resté gravé dans la mémoire de la Martinique, au point qu'il est encore commémoré chaque année sur place. Il y a 186 ans, un séisme d'une magnitude de 7 à 8 sur l'échelle de Richter frappe l'île des Caraïbes, avec trois vagues de secousses. Fort-de-France est la ville la plus durement touchée. Les maisons s'effondrent, la quasi-totalité des édifices publics sont détruits.

        Bilan, sur les 117.000 habitants de l'île (dont 65% d'esclaves), les décès s'élèvent de 300 à 4.000 personnes. Une variation énorme de l'estimation, due au fait que les esclaves n'étaient à l'époque pas perçus comme des personnes, mais plutôt comme des meubles et n'étaient donc pas comptabilisés parmi les victimes.

        À peine quelques années plus tard, en 1843, c'est au tour de la Guadeloupe d'être durement endeuillée. Un séisme similaire ravage l'archipel le 8 février, détruisant Pointe-à-Pitre et faisant 3.000 victimes, selon les estimations de l'époque.

        Encore aujourd'hui, les territoires d'outre-mer ne sont pas à l'abri des secousses. En novembre 2007, par exemple, la Martinique a connu le séisme avec la plus grande magnitude jamais enregistrée en France (avec les moyens modernes): 7,4 sur l'échelle de Richter! Si quelques dégâts matériels ont été enregistrés, aucune victime n'est alors à déplorer.

        Et en France métropolitaine?

        Contrairement à de nombreux territoires d'outre-mer ou à la Birmanie, qui se trouvent à la jonction de plusieurs plaques tectoniques majeures, notamment la plaque indienne et la plaque eurasienne, la France métropolitaine n'est pas située sur une zone de forte activité sismique. De quoi être à l'abri? Pas du tout.

        Chaque année, l'Hexagone connaît environ 4.000 secousses sismiques. Des secousses de faible intensité, dont la grande majorité ne sont même pas ressenties par la population. Si bien qu'on en vient à oublier les grands tremblements de terre qu'a connus le pays, à commencer par celui de Lambesc (Bouches-du-Rhône), le plus dévastateur jamais enregistré en France métropolitaine depuis l'installation des premières stations sismologiques, au début du XXe siècle.

        La nuit du 11 juin 1909, la région de Lambesc, en Provence, est frappée de plein fouet par un tremblement de terre, dont la magnitude est estimée à 6,2 sur l'échelle de Richter. La secousse est alors ressentie dans toute cette zone du sud-est de la France, faisant des dégâts de Rognes à Saint-Cannat, en passant par Vernègues et Aix-en-Provence, où environ 1.500 logements sont endommagés. Bilan de la catastrophe: 46 morts, environ 250 blessés et près de 90% des bâtiments de Lambesc détruits. Un record jamais dépassé depuis.

        Et dans le monde? Selon l'Encyclopædia Britannica, le séisme le plus meurtrier de l'histoire serait survenu en Chine, le 23 janvier 1556. D'une magnitude estimée à 8, ce tremblement de terre aurait frappé les provinces voisines de Shaanxi et Shanxi, tuant ou blessant jusqu'à… 830.000 personnes. Une catastrophe qui aurait réduit la population des deux provinces d'environ 60%.
            """
    )

    entities = format_entities(article)
    result = compute_datafication_score(entities, article)

    print("----- SCORE DE DATAFICATION -----")
    print(f"Score : {result['score']}/10")
    print(f"Densité : {result['density']} (mots struct. / mots total)")
    print(f"Total éléments structurés : {result['structured_items']}")
    print(f"Taille article : {result['word_count']} mots")
    print("Justifications :")
    for j in result["justifications"]:
        print(f"- {j}")

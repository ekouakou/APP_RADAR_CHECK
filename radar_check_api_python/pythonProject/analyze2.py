import pandas as pd
from datetime import datetime
import itertools


def analyser_suites_arithmetiques(
        fichier,
        sens_lecture=True,
        colonnes="num",
        respecter_positions=True,
        types_tirage=None,
        date_debut=None,
        date_fin=None,
        direction="horizontal"  # "horizontal", "vertical", ou "les_deux"
):
    """
    Analyse un fichier Excel pour trouver des suites arithmétiques.

    Paramètres:
    - fichier: Chemin vers le fichier Excel
    - sens_lecture: True pour lire de haut en bas, False pour lire de bas en haut
    - colonnes: "num" pour Num1-Num5, "machine" pour Machine1-Machine5, "tous" pour les deux
    - respecter_positions: Si True, cherche des suites dans l'ordre des colonnes.
                           Si False, cherche toutes les combinaisons possibles.
    - types_tirage: Liste des types de tirage à considérer (ex: ["Reveil", "Akwaba"])
    - date_debut: Date de début de la période d'analyse (format: "DD/MM/YYYY")
    - date_fin: Date de fin de la période d'analyse (format: "DD/MM/YYYY")

    Retourne:
    - Un dictionnaire des suites arithmétiques trouvées
    """
    # Charger le fichier Excel
    df = pd.read_csv(fichier, sep=';')

    # Convertir la colonne Date en datetime
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')

    # Filtrer par date si spécifié
    if date_debut:
        date_debut = datetime.strptime(date_debut, '%d/%m/%Y')
        df = df[df['Date'] >= date_debut]

    if date_fin:
        date_fin = datetime.strptime(date_fin, '%d/%m/%Y')
        df = df[df['Date'] <= date_fin]

    # Filtrer par type de tirage si spécifié
    if types_tirage:
        df = df[df['Type de Tirage'].isin(types_tirage)]

    # Inverser l'ordre si nécessaire
    if not sens_lecture:
        df = df.iloc[::-1].reset_index(drop=True)

    # Déterminer les colonnes à analyser
    colonnes_num = ['Num1', 'Num2', 'Num3', 'Num4', 'Num5']
    colonnes_machine = ['Machine1', 'Machine2', 'Machine3', 'Machine4', 'Machine5']

    if colonnes.lower() == "num":
        colonnes_analyse = colonnes_num
    elif colonnes.lower() == "machine":
        colonnes_analyse = colonnes_machine
    else:  # "tous"
        colonnes_analyse = colonnes_num + colonnes_machine

    suites_trouvees = {}

    # Analyse horizontale (par ligne)
    if direction.lower() in ["horizontal", "les_deux"]:
        for index, row in df.iterrows():
            date = row['Date'].strftime('%d/%m/%Y')
            type_tirage = row['Type de Tirage']

            # Extraire les nombres des colonnes à analyser
            nombres = []
            for col in colonnes_analyse:
                if col in row:
                    nombres.append(int(row[col]))

            # Chercher des suites arithmétiques
            if respecter_positions:
                # Vérifier si les nombres consécutifs forment une suite
                for i in range(len(nombres) - 2):
                    for j in range(i + 1, len(nombres) - 1):
                        for k in range(j + 1, len(nombres)):
                            if est_suite_arithmetique([nombres[i], nombres[j], nombres[k]]):
                                suite_key = f"{date}_{type_tirage}"
                                if suite_key not in suites_trouvees:
                                    suites_trouvees[suite_key] = []
                                suites_trouvees[suite_key].append({
                                    'suite': [nombres[i], nombres[j], nombres[k]],
                                    'raison': nombres[j] - nombres[i],
                                    'colonnes': [colonnes_analyse[i], colonnes_analyse[j], colonnes_analyse[k]],
                                    'direction': 'horizontale'
                                })
            else:
                # Vérifier toutes les combinaisons possibles
                for combo in itertools.combinations(range(len(nombres)), 3):
                    i, j, k = combo
                    if est_suite_arithmetique([nombres[i], nombres[j], nombres[k]]):
                        suite_key = f"{date}_{type_tirage}"
                        if suite_key not in suites_trouvees:
                            suites_trouvees[suite_key] = []
                        suites_trouvees[suite_key].append({
                            'suite': [nombres[i], nombres[j], nombres[k]],
                            'raison': nombres[j] - nombres[i],
                            'colonnes': [colonnes_analyse[i], colonnes_analyse[j], colonnes_analyse[k]],
                            'direction': 'horizontale'
                        })

    # Analyse verticale (par colonne)
    if direction.lower() in ["vertical", "les_deux"]:
        for col in colonnes_analyse:
            # Vérifier que la colonne existe dans le dataframe
            if col not in df.columns:
                continue

            # Extraire les nombres de la colonne
            nombres_verticaux = df[col].astype(int).tolist()

            # Chercher des suites arithmétiques verticales
            for i in range(len(nombres_verticaux) - 2):
                for j in range(i + 1, len(nombres_verticaux) - 1):
                    for k in range(j + 1, len(nombres_verticaux)):
                        if est_suite_arithmetique([nombres_verticaux[i], nombres_verticaux[j], nombres_verticaux[k]]):
                            # Créer une clé unique pour cette suite verticale
                            date_i = df.iloc[i]['Date'].strftime('%d/%m/%Y')
                            date_j = df.iloc[j]['Date'].strftime('%d/%m/%Y')
                            date_k = df.iloc[k]['Date'].strftime('%d/%m/%Y')
                            type_i = df.iloc[i]['Type de Tirage']
                            type_j = df.iloc[j]['Type de Tirage']
                            type_k = df.iloc[k]['Type de Tirage']

                            suite_key = f"Verticale_{col}_{date_i}_{date_j}_{date_k}"

                            if suite_key not in suites_trouvees:
                                suites_trouvees[suite_key] = []

                            suites_trouvees[suite_key].append({
                                'suite': [nombres_verticaux[i], nombres_verticaux[j], nombres_verticaux[k]],
                                'raison': nombres_verticaux[j] - nombres_verticaux[i],
                                'colonne': col,
                                'dates': [date_i, date_j, date_k],
                                'types': [type_i, type_j, type_k],
                                'direction': 'verticale'
                            })

    return suites_trouvees


def est_suite_arithmetique(nombres):
    """
    Vérifie si une liste de nombres est une suite arithmétique.
    """
    if len(nombres) < 3:
        return False

    nombres = sorted(nombres)
    raison = nombres[1] - nombres[0]

    for i in range(1, len(nombres) - 1):
        if nombres[i + 1] - nombres[i] != raison:
            return False

    return True


def afficher_resultats(suites_trouvees):
    """
    Affiche les résultats des suites arithmétiques trouvées.
    """
    print(f"Nombre total de suites arithmétiques trouvées: {sum(len(suites) for suites in suites_trouvees.values())}")
    print(f"Nombre total de tirages avec suites arithmétiques: {len(suites_trouvees)}")

    for cle, suites in suites_trouvees.items():
        if cle.startswith('Verticale_'):
            # Format spécial pour les suites verticales
            col = cle.split('_')[1]
            print(f"\nSuite Verticale pour la colonne: {col}")
        else:
            # Format standard pour les suites horizontales
            date, type_tirage = cle.split('_', 1)  # Split uniquement sur le premier underscore
            print(f"\nDate: {date}, Type de Tirage: {type_tirage}")

        for i, suite in enumerate(suites):
            print(f"  Suite {i + 1}: {suite['suite']} (raison: {suite['raison']})")

            if 'direction' in suite and suite['direction'] == 'verticale':
                print(f"  Direction: {suite['direction']}")
                print(f"  Colonne: {suite['colonne']}")
                print(f"  Dates: {suite['dates']}")
                print(f"  Types de tirage: {suite['types']}")
            else:
                print(f"  Direction: {suite.get('direction', 'horizontale')}")
                print(f"  Colonnes: {suite['colonnes']}")


if __name__ == "__main__":
    # Exemple d'utilisation
    fichier = "./api/uploads/formatted_lottery_results.csv"  # Remplacer par le chemin de votre fichier

    # Paramètres personnalisables
    sens_lecture = False  # True: de haut en bas, False: de bas en haut
    colonnes = "num"  # "num", "machine", ou "tous"
    respecter_positions = False  # True: respecter l'ordre des colonnes, False: toutes combinaisons
    types_tirage = None #["Reveil", "Akwaba"]  # Types de tirage à analyser, None pour tous
    date_debut = "05/10/2020"  # Format: "DD/MM/YYYY"
    date_fin = "11/10/2021"  # Format: "DD/MM/YYYY"
    direction = "vertical"  # "horizontal", "vertical", ou "les_deux"

    # Analyse et affichage des résultats
    resultats = analyser_suites_arithmetiques(
        fichier,
        sens_lecture,
        colonnes,
        respecter_positions,
        types_tirage,
        date_debut,
        date_fin,
        direction
    )

    afficher_resultats(resultats)
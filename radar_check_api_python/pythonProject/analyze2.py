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
        direction="horizontal",  # "horizontal", "vertical", ou "les_deux"
        difference_constante=True,  # True pour différence constante, False pour différence variable
        respecter_ordre_apparition=False,  # True pour respecter l'ordre d'apparition
        longueur_suite_filtre=None  # Nouveau paramètre pour filtrer les suites par leur longueur
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
    - direction: "horizontal", "vertical", ou "les_deux"
    - difference_constante: Si True, cherche des suites à différence constante.
                            Si False, cherche des suites à différence variable (progression)
    - respecter_ordre_apparition: Si True, ne trie pas les nombres et respecte leur ordre d'apparition.
                                 Si False, trie les nombres avant de vérifier s'ils forment une suite.
    - longueur_suite_filtre: Si spécifié, ne retourne que les suites ayant exactement cette longueur.
                            Si None, retourne toutes les suites.

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
    else:  # "tous" - Utilise toutes les colonnes ensemble, sans les séparer
        colonnes_analyse = colonnes_num + colonnes_machine

    suites_trouvees = {}

    # Analyse horizontale (par ligne)
    if direction.lower() in ["horizontal", "les_deux"]:
        for index, row in df.iterrows():
            date = row['Date'].strftime('%d/%m/%Y')
            type_tirage = row['Type de Tirage']

            # Extraire les nombres des colonnes à analyser
            nombres = []
            colonnes_apparition = []  # Pour stocker les colonnes d'apparition des nombres
            for col in colonnes_analyse:
                if col in row and not pd.isna(row[col]):  # Vérifier que la valeur n'est pas NaN
                    nombres.append(int(row[col]))
                    colonnes_apparition.append(col)

            # Chercher des suites selon le type (constante ou variable)
            if respecter_positions:
                # Déterminer les longueurs de suite à vérifier
                longueurs_a_verifier = [longueur_suite_filtre] if longueur_suite_filtre else range(3, len(nombres) + 1)

                # Vérifier les nombres consécutifs
                for longueur_suite in longueurs_a_verifier:
                    # S'assurer que la longueur de suite est valide
                    if longueur_suite < 3 or longueur_suite > len(nombres):
                        continue

                    for i in range(len(nombres) - longueur_suite + 1):
                        sous_nombres = nombres[i:i + longueur_suite]
                        sous_colonnes = colonnes_apparition[i:i + longueur_suite]

                        # Vérifier si c'est une suite (avec ou sans tri)
                        if difference_constante:
                            est_suite = False
                            raison = None

                            if respecter_ordre_apparition:
                                est_suite, raison = est_suite_arithmetique_ordre(sous_nombres)
                            else:
                                est_suite = est_suite_arithmetique(sous_nombres)
                                if est_suite:
                                    nombres_triees = sorted(sous_nombres)
                                    raison = nombres_triees[1] - nombres_triees[0]

                            if est_suite:
                                suite_key = f"{date}_{type_tirage}"
                                if suite_key not in suites_trouvees:
                                    suites_trouvees[suite_key] = []
                                suites_trouvees[suite_key].append({
                                    'suite': sous_nombres,
                                    'raison': raison,
                                    'colonnes': sous_colonnes,  # Stocke les colonnes d'apparition
                                    'direction': 'horizontale',
                                    'type_suite': 'constante'
                                })
                        else:
                            progression = None

                            if respecter_ordre_apparition:
                                progression = est_suite_progression_ordre(sous_nombres)
                            else:
                                progression = est_suite_progression(sous_nombres)

                            if progression:
                                suite_key = f"{date}_{type_tirage}"
                                if suite_key not in suites_trouvees:
                                    suites_trouvees[suite_key] = []
                                suites_trouvees[suite_key].append({
                                    'suite': sous_nombres,
                                    'differences': progression,
                                    'colonnes': sous_colonnes,  # Stocke les colonnes d'apparition
                                    'direction': 'horizontale',
                                    'type_suite': 'variable'
                                })
            else:
                # Déterminer les longueurs de suite à vérifier
                max_longueur = min(6, len(nombres) + 1)  # Limiter pour éviter explosion combinatoire
                longueurs_a_verifier = [longueur_suite_filtre] if longueur_suite_filtre else range(3, max_longueur)

                # Vérifier toutes les combinaisons possibles
                for longueur_suite in longueurs_a_verifier:
                    # S'assurer que la longueur de suite est valide
                    if longueur_suite < 3 or longueur_suite > len(nombres):
                        continue

                    for combo in itertools.combinations(range(len(nombres)), longueur_suite):
                        sous_nombres = [nombres[i] for i in combo]
                        sous_colonnes = [colonnes_apparition[i] for i in combo]

                        # Vérifier si c'est une suite (avec ou sans tri)
                        if difference_constante:
                            est_suite = False
                            raison = None

                            if respecter_ordre_apparition:
                                est_suite, raison = est_suite_arithmetique_ordre(sous_nombres)
                            else:
                                est_suite = est_suite_arithmetique(sous_nombres)
                                if est_suite:
                                    nombres_triees = sorted(sous_nombres)
                                    raison = nombres_triees[1] - nombres_triees[0]

                            if est_suite:
                                suite_key = f"{date}_{type_tirage}"
                                if suite_key not in suites_trouvees:
                                    suites_trouvees[suite_key] = []
                                suites_trouvees[suite_key].append({
                                    'suite': sous_nombres if respecter_ordre_apparition else sorted(sous_nombres),
                                    'raison': raison,
                                    'colonnes': sous_colonnes,  # Stocke les colonnes d'apparition
                                    'direction': 'horizontale',
                                    'type_suite': 'constante'
                                })
                        else:
                            progression = None

                            if respecter_ordre_apparition:
                                progression = est_suite_progression_ordre(sous_nombres)
                            else:
                                progression = est_suite_progression(sous_nombres)

                            if progression:
                                suite_key = f"{date}_{type_tirage}"
                                if suite_key not in suites_trouvees:
                                    suites_trouvees[suite_key] = []
                                suites_trouvees[suite_key].append({
                                    'suite': sous_nombres if respecter_ordre_apparition else sorted(sous_nombres),
                                    'differences': progression,
                                    'colonnes': sous_colonnes,  # Stocke les colonnes d'apparition
                                    'direction': 'horizontale',
                                    'type_suite': 'variable'
                                })

    # Analyse verticale (par colonne)
    if direction.lower() in ["vertical", "les_deux"]:
        # Analyse pour chaque colonne individuellement
        for col in colonnes_analyse:
            # Vérifier que la colonne existe dans le dataframe
            if col not in df.columns:
                continue

            # Extraire les nombres de la colonne
            nombres_verticaux = df[col].astype(int).tolist()

            # Stocker les positions (indices) pour référence
            positions_verticales = list(range(len(nombres_verticaux)))

            # Déterminer les longueurs de suite à vérifier
            max_longueur = min(6, len(nombres_verticaux) + 1)  # Limiter pour éviter explosion combinatoire
            longueurs_a_verifier = [longueur_suite_filtre] if longueur_suite_filtre else range(3, max_longueur)

            # Chercher des suites selon le type (constante ou variable)
            for longueur_suite in longueurs_a_verifier:
                # S'assurer que la longueur de suite est valide
                if longueur_suite < 3 or longueur_suite > len(nombres_verticaux):
                    continue

                for i in range(len(nombres_verticaux) - longueur_suite + 1):
                    sous_nombres = nombres_verticaux[i:i + longueur_suite]
                    indices = positions_verticales[i:i + longueur_suite]

                    # Vérifier si c'est une suite (avec ou sans tri)
                    if difference_constante:
                        est_suite = False
                        raison = None

                        if respecter_ordre_apparition:
                            est_suite, raison = est_suite_arithmetique_ordre(sous_nombres)
                        else:
                            est_suite = est_suite_arithmetique(sous_nombres)
                            if est_suite:
                                nombres_triees = sorted(sous_nombres)
                                raison = nombres_triees[1] - nombres_triees[0]

                        if est_suite:
                            # Créer une clé unique pour cette suite verticale
                            dates = [df.iloc[idx]['Date'].strftime('%d/%m/%Y') for idx in indices]
                            types = [df.iloc[idx]['Type de Tirage'] for idx in indices]
                            positions = [col] * len(indices)  # La même colonne pour chaque élément

                            suite_key = f"Verticale_{col}_{dates[0]}_{dates[-1]}"

                            if suite_key not in suites_trouvees:
                                suites_trouvees[suite_key] = []

                            suites_trouvees[suite_key].append({
                                'suite': sous_nombres if respecter_ordre_apparition else sorted(sous_nombres),
                                'raison': raison,
                                'colonne': col,
                                'colonnes': positions,  # Stocke les colonnes d'apparition
                                'dates': dates,
                                'types': types,
                                'direction': 'verticale',
                                'type_suite': 'constante'
                            })
                    else:
                        progression = None

                        if respecter_ordre_apparition:
                            progression = est_suite_progression_ordre(sous_nombres)
                        else:
                            progression = est_suite_progression(sous_nombres)

                        if progression:
                            # Créer une clé unique pour cette suite verticale
                            dates = [df.iloc[idx]['Date'].strftime('%d/%m/%Y') for idx in indices]
                            types = [df.iloc[idx]['Type de Tirage'] for idx in indices]
                            positions = [col] * len(indices)  # La même colonne pour chaque élément

                            suite_key = f"Verticale_{col}_{dates[0]}_{dates[-1]}"

                            if suite_key not in suites_trouvees:
                                suites_trouvees[suite_key] = []

                            suites_trouvees[suite_key].append({
                                'suite': sous_nombres if respecter_ordre_apparition else sorted(sous_nombres),
                                'differences': progression,
                                'colonne': col,
                                'colonnes': positions,  # Stocke les colonnes d'apparition
                                'dates': dates,
                                'types': types,
                                'direction': 'verticale',
                                'type_suite': 'variable'
                            })

        # Si "tous" est sélectionné, ajouter une analyse verticale entre colonnes différentes
        if colonnes.lower() == "tous":
            # Créer un dictionnaire pour stocker les valeurs de chaque colonne par date
            colonnes_par_date = {}

            for index, row in df.iterrows():
                date = row['Date'].strftime('%d/%m/%Y')
                type_tirage = row['Type de Tirage']

                # Créer une clé unique pour chaque tirage
                tirage_key = f"{date}_{type_tirage}"

                if tirage_key not in colonnes_par_date:
                    colonnes_par_date[tirage_key] = {}

                # Stocker les valeurs de toutes les colonnes pour ce tirage
                for col in colonnes_analyse:
                    if col in row and not pd.isna(row[col]):
                        colonnes_par_date[tirage_key][col] = int(row[col])

            # Déterminer les longueurs de suite à vérifier pour l'analyse inter-colonnes
            max_longueur = min(6, len(df))
            longueurs_a_verifier = [longueur_suite_filtre] if longueur_suite_filtre else range(3, max_longueur)

            # Pour chaque colonne "départ", analyser les suites verticales avec d'autres colonnes
            for longueur_suite in longueurs_a_verifier:
                # S'assurer que la longueur de suite est valide
                if longueur_suite < 3 or longueur_suite > len(df):
                    continue

                # Pour chaque ligne de départ possible
                for start_idx in range(len(df) - longueur_suite + 1):
                    # Récupérer les tirages consécutifs
                    tirages_consecutive = []
                    tirages_info = []

                    for i in range(longueur_suite):
                        idx = start_idx + i
                        date = df.iloc[idx]['Date'].strftime('%d/%m/%Y')
                        type_tirage = df.iloc[idx]['Type de Tirage']
                        tirage_key = f"{date}_{type_tirage}"

                        tirages_consecutive.append(colonnes_par_date.get(tirage_key, {}))
                        tirages_info.append((date, type_tirage))

                    # Pour chaque combinaison de colonnes possibles
                    for col_start in colonnes_analyse:
                        for col_pattern in itertools.product(colonnes_analyse, repeat=longueur_suite - 1):
                            colonnes_pattern = [col_start] + list(col_pattern)

                            # Récupérer les nombres selon le pattern de colonnes
                            nombres = []
                            colonnes_correspondantes = []
                            dates_correspondantes = []
                            types_correspondants = []

                            for i, (tirage, info) in enumerate(zip(tirages_consecutive, tirages_info)):
                                col = colonnes_pattern[i]
                                if col in tirage:
                                    nombres.append(tirage[col])
                                    colonnes_correspondantes.append(col)
                                    dates_correspondantes.append(info[0])
                                    types_correspondants.append(info[1])

                            # Vérifier si nous avons assez de nombres pour une suite
                            if len(nombres) >= 3 and (
                                    longueur_suite_filtre is None or len(nombres) == longueur_suite_filtre):
                                # Vérifier si c'est une suite
                                if difference_constante:
                                    est_suite = False
                                    raison = None

                                    if respecter_ordre_apparition:
                                        est_suite, raison = est_suite_arithmetique_ordre(nombres)
                                    else:
                                        est_suite = est_suite_arithmetique(nombres)
                                        if est_suite:
                                            nombres_triees = sorted(nombres)
                                            raison = nombres_triees[1] - nombres_triees[0]

                                    if est_suite:
                                        # Créer une clé unique pour cette suite inter-colonnes
                                        suite_key = f"VerticaleInterColonnes_{dates_correspondantes[0]}_{dates_correspondantes[-1]}"

                                        if suite_key not in suites_trouvees:
                                            suites_trouvees[suite_key] = []

                                        suites_trouvees[suite_key].append({
                                            'suite': nombres if respecter_ordre_apparition else sorted(nombres),
                                            'raison': raison,
                                            'colonnes': colonnes_correspondantes,
                                            'dates': dates_correspondantes,
                                            'types': types_correspondants,
                                            'direction': 'verticale_inter_colonnes',
                                            'type_suite': 'constante'
                                        })
                                else:
                                    progression = None

                                    if respecter_ordre_apparition:
                                        progression = est_suite_progression_ordre(nombres)
                                    else:
                                        progression = est_suite_progression(nombres)

                                    if progression:
                                        # Créer une clé unique pour cette suite inter-colonnes
                                        suite_key = f"VerticaleInterColonnes_{dates_correspondantes[0]}_{dates_correspondantes[-1]}"

                                        if suite_key not in suites_trouvees:
                                            suites_trouvees[suite_key] = []

                                        suites_trouvees[suite_key].append({
                                            'suite': nombres if respecter_ordre_apparition else sorted(nombres),
                                            'differences': progression,
                                            'colonnes': colonnes_correspondantes,
                                            'dates': dates_correspondantes,
                                            'types': types_correspondants,
                                            'direction': 'verticale_inter_colonnes',
                                            'type_suite': 'variable'
                                        })

    return suites_trouvees


def est_suite_arithmetique(nombres):
    """
    Vérifie si une liste de nombres est une suite arithmétique (différence constante).
    Les nombres sont d'abord triés.
    """
    if len(nombres) < 3:
        return False

    nombres = sorted(nombres)
    raison = nombres[1] - nombres[0]

    for i in range(1, len(nombres) - 1):
        if nombres[i + 1] - nombres[i] != raison:
            return False

    return True


def est_suite_arithmetique_ordre(nombres):
    """
    Vérifie si une liste de nombres est une suite arithmétique (différence constante)
    sans modifier leur ordre.
    Retourne (True/False, raison) si c'est une suite.
    """
    if len(nombres) < 3:
        return False, None

    # Calculer les différences entre nombres consécutifs
    differences = [nombres[i + 1] - nombres[i] for i in range(len(nombres) - 1)]

    # Si toutes les différences sont égales, c'est une suite arithmétique
    if len(set(differences)) == 1:
        return True, differences[0]

    return False, None


def est_suite_progression(nombres):
    """
    Vérifie si une liste de nombres est une suite à différence variable (progression).
    Les nombres sont d'abord triés.
    Retourne la liste des différences si c'est une suite à progression, sinon False.
    """
    if len(nombres) < 3:
        return False

    nombres = sorted(nombres)
    differences = []

    for i in range(len(nombres) - 1):
        differences.append(nombres[i + 1] - nombres[i])

    # Vérifier si les différences forment une progression
    if len(set(differences)) > 1:  # Au moins deux différences distinctes
        return differences

    return False


def est_suite_progression_ordre(nombres):
    """
    Vérifie si une liste de nombres est une suite à différence variable (progression)
    sans modifier leur ordre.
    Retourne la liste des différences si c'est une suite à progression, sinon False.
    """
    if len(nombres) < 3:
        return False

    # Calculer les différences entre nombres consécutifs
    differences = [nombres[i + 1] - nombres[i] for i in range(len(nombres) - 1)]

    # Vérifier si les différences sont toutes différentes ou forment un pattern
    if len(set(differences)) > 1:  # Au moins deux différences distinctes
        return differences

    return False


def afficher_resultats(suites_trouvees):
    """
    Affiche les résultats des suites arithmétiques trouvées avec un format tableau.
    Inclut les dates et types de tirage pour chaque élément de la suite.
    """
    print(f"Nombre total de suites trouvées: {sum(len(suites) for suites in suites_trouvees.values())}")
    print(f"Nombre total de tirages avec suites: {len(suites_trouvees)}")

    for cle, suites in suites_trouvees.items():
        if cle.startswith('Verticale_'):
            # Format spécial pour les suites verticales
            parts = cle.split('_')
            col = parts[1]
            print(f"\nSuite Verticale pour la colonne: {col} (de {parts[2]} à {parts[3]})")
        elif cle.startswith('VerticaleInterColonnes_'):
            # Format spécial pour les suites verticales inter-colonnes
            parts = cle.split('_')
            print(f"\nSuite Verticale Inter-Colonnes (de {parts[1]} à {parts[2]})")
        else:
            # Format standard pour les suites horizontales
            date, type_tirage = cle.split('_', 1)  # Split uniquement sur le premier underscore
            print(f"\nDate: {date}, Type de Tirage: {type_tirage}")

        for i, suite in enumerate(suites):
            print(f"  Suite {i + 1}: {suite['suite']}")

            if suite['type_suite'] == 'constante':
                print(f"  Type: Différence constante (raison: {suite['raison']})")
            else:
                print(f"  Type: Différence variable (différences: {suite['differences']})")

            print(f"  Direction: {suite.get('direction', 'horizontale')}")

            # Afficher la colonne ou les colonnes
            if 'direction' in suite and suite['direction'] in ['verticale', 'verticale_inter_colonnes']:
                if suite['direction'] == 'verticale':
                    print(f"  Colonne: {suite['colonne']}")

                # Afficher le tableau des colonnes où les nombres sont apparus avec dates et types
                print("\n  Tableau des apparitions:")
                print("  +------------+------------------+----------------+----------------+")
                print("  | Nombre     | Colonne          | Date           | Type de Tirage |")
                print("  +------------+------------------+----------------+----------------+")

                for idx, val in enumerate(suite['suite']):
                    colonne = suite['colonnes'][idx] if idx < len(suite['colonnes']) else ""
                    date = suite['dates'][idx] if 'dates' in suite and idx < len(suite['dates']) else ""
                    type_tirage = suite['types'][idx] if 'types' in suite and idx < len(suite['types']) else ""

                    print(f"  | {val:<10} | {colonne:<16} | {date:<14} | {type_tirage:<14} |")

                print("  +------------+------------------+----------------+----------------+")
            else:
                # Pour les suites horizontales, ajouter des informations sur la date et le type de tirage
                date = cle.split('_')[0] if "_" in cle else ""
                type_tirage = cle.split('_', 1)[1] if "_" in cle else ""

                # Afficher le tableau des colonnes où les nombres sont apparus
                print("\n  Tableau des apparitions:")
                print("  +------------+------------------+----------------+----------------+")
                print("  | Nombre     | Colonne          | Date           | Type de Tirage |")
                print("  +------------+------------------+----------------+----------------+")

                for idx, val in enumerate(suite['suite']):
                    colonne = suite['colonnes'][idx] if idx < len(suite['colonnes']) else ""
                    print(f"  | {val:<10} | {colonne:<16} | {date:<14} | {type_tirage:<14} |")

                print("  +------------+------------------+----------------+----------------+")


if __name__ == "__main__":
    # Exemple d'utilisation
    fichier = "./api/uploads/formatted_lottery_results.csv"  # Remplacer par le chemin de votre fichier

    # Paramètres personnalisables
    sens_lecture = False  # True: de haut en bas, False: de bas en haut
    colonnes = "tous"  # "num", "machine", ou "tous"
    respecter_positions = True  # True: respecter l'ordre des colonnes, False: toutes combinaisons
    types_tirage = None  # ["Reveil", "Akwaba"]  # Types de tirage à analyser, None pour tous
    date_debut = "05/10/2020"  # Format: "DD/MM/YYYY"
    date_fin = "11/10/2020"  # Format: "DD/MM/YYYY"
    direction = "vertical"  # "horizontal", "vertical", ou "les_deux"
    difference_constante = True  # True: différence constante, False: différence variable
    respecter_ordre_apparition = False  # True: respecter l'ordre d'apparition, False: trier les nombres
    longueur_suite_filtre = 6  # Nouveau paramètre: None pour toutes les longueurs, ou un entier pour filtrer

    # Analyse et affichage des résultats
    resultats = analyser_suites_arithmetiques(
        fichier,
        sens_lecture,
        colonnes,
        respecter_positions,
        types_tirage,
        date_debut,
        date_fin,
        direction,
        difference_constante,
        respecter_ordre_apparition,
        longueur_suite_filtre
    )

    afficher_resultats(resultats)
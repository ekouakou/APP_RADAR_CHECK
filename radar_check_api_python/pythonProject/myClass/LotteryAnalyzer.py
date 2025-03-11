import pandas as pd
from datetime import datetime
import itertools
import os


class LotteryAnalyzer:
    """
    Classe pour analyser des données de loterie et détecter des suites arithmétiques.
    """

    def __init__(self):
        """Initialise l'analyseur de loterie."""
        pass

    def est_suite_complete(self, suite, raison, valeur_min=1, valeur_max=90):
        """
        Vérifie si une suite arithmétique est complète (tous les éléments possibles sont présents).

        Args:
            suite (list): Liste des nombres dans la suite
            raison (int): Différence constante entre les termes
            valeur_min (int): Valeur minimale autorisée dans la suite
            valeur_max (int): Valeur maximale autorisée dans la suite

        Returns:
            tuple: (est_complete, elements_manquants)
        """
        suite_triee = sorted(suite)
        # Calculer le premier et dernier terme possible dans l'intervalle [valeur_min, valeur_max]
        premier = suite_triee[0]
        dernier = suite_triee[-1]

        # Trouver tous les termes possibles dans l'intervalle [valeur_min, valeur_max]
        elements_possibles = []
        # Vérifier les termes avant le premier terme connu
        terme = premier - raison
        while terme >= valeur_min:
            elements_possibles.insert(0, terme)
            terme -= raison

        # Ajouter les termes connus
        elements_possibles.extend(suite_triee)

        # Vérifier les termes après le dernier terme connu
        terme = dernier + raison
        while terme <= valeur_max:
            elements_possibles.append(terme)
            terme += raison

        elements_manquants = [x for x in elements_possibles if x not in suite_triee]
        est_complete = len(elements_manquants) == 0

        return est_complete, elements_manquants

    def est_suite_arithmetique(self, nombres):
        """
        Vérifie si une liste de nombres est une suite arithmétique.

        Args:
            nombres (list): Liste des nombres à vérifier

        Returns:
            bool: True si c'est une suite arithmétique, False sinon
        """
        if len(nombres) < 3:
            return False

        nombres = sorted(nombres)
        raison = nombres[1] - nombres[0]

        for i in range(1, len(nombres) - 1):
            if nombres[i + 1] - nombres[i] != raison:
                return False

        return True

    def est_suite_arithmetique_ordre(self, nombres):
        """
        Vérifie si une liste de nombres est une suite arithmétique sans modifier leur ordre.

        Args:
            nombres (list): Liste des nombres à vérifier

        Returns:
            tuple: (est_suite, raison) ou (False, None)
        """
        if len(nombres) < 3:
            return False, None

        differences = [nombres[i + 1] - nombres[i] for i in range(len(nombres) - 1)]

        if len(set(differences)) == 1:
            return True, differences[0]

        return False, None

    def est_suite_progression(self, nombres):
        """
        Vérifie si une liste de nombres est une suite à différence variable.

        Args:
            nombres (list): Liste des nombres à vérifier

        Returns:
            list: Liste des différences si c'est une suite à différence variable, False sinon
        """
        if len(nombres) < 3:
            return False

        nombres = sorted(nombres)
        differences = [nombres[i + 1] - nombres[i] for i in range(len(nombres) - 1)]

        if len(set(differences)) > 1:
            return differences

        return False

    def est_suite_progression_ordre(self, nombres):
        """
        Vérifie si une liste de nombres est une suite à différence variable sans modifier leur ordre.

        Args:
            nombres (list): Liste des nombres à vérifier

        Returns:
            list: Liste des différences si c'est une suite à différence variable, False sinon
        """
        if len(nombres) < 3:
            return False

        differences = [nombres[i + 1] - nombres[i] for i in range(len(nombres) - 1)]

        if len(set(differences)) > 1:
            return differences

        return False

    def traiter_suite(self, sous_nombres, sous_colonnes, respecter_ordre_apparition,
                      difference_constante, direction, suites_trouvees,
                      suite_key, verifier_completion, valeur_min, valeur_max,
                      date=None, type_tirage=None):
        """
        Traite une potentielle suite arithmétique.

        Args:
            sous_nombres (list): Liste des nombres à analyser
            sous_colonnes (list): Liste des colonnes correspondantes
            respecter_ordre_apparition (bool): Si True, respecte l'ordre des nombres
            difference_constante (bool): Si True, cherche une suite à différence constante
            direction (str): Direction de l'analyse ('horizontale', 'verticale', etc.)
            suites_trouvees (dict): Dictionnaire pour stocker les suites trouvées
            suite_key (str): Clé pour identifier la suite
            verifier_completion (bool): Si True, vérifie si la suite est complète
            valeur_min (int): Valeur minimale autorisée
            valeur_max (int): Valeur maximale autorisée
            date (list, optional): Liste des dates correspondantes
            type_tirage (list, optional): Liste des types de tirage
        """
        if difference_constante:
            est_suite = False
            raison = None

            if respecter_ordre_apparition:
                est_suite, raison = self.est_suite_arithmetique_ordre(sous_nombres)
            else:
                est_suite = self.est_suite_arithmetique(sous_nombres)
                if est_suite:
                    nombres_triees = sorted(sous_nombres)
                    raison = nombres_triees[1] - nombres_triees[0]

            if est_suite:
                if suite_key not in suites_trouvees:
                    suites_trouvees[suite_key] = []

                suite_info = {
                    'suite': sous_nombres if respecter_ordre_apparition else sorted(sous_nombres),
                    'raison': raison,
                    'colonnes': sous_colonnes,
                    'direction': direction,
                    'type_suite': 'constante'
                }

                if date:
                    suite_info['dates'] = date
                if type_tirage:
                    suite_info['types'] = type_tirage

                # Vérifier si la suite est complète
                if verifier_completion:
                    est_complete, elements_manquants = self.est_suite_complete(
                        suite_info['suite'], raison, valeur_min, valeur_max
                    )
                    suite_info['est_complete'] = est_complete
                    suite_info['elements_manquants'] = elements_manquants

                suites_trouvees[suite_key].append(suite_info)
        else:
            progression = None

            if respecter_ordre_apparition:
                progression = self.est_suite_progression_ordre(sous_nombres)
            else:
                progression = self.est_suite_progression(sous_nombres)

            if progression:
                if suite_key not in suites_trouvees:
                    suites_trouvees[suite_key] = []

                suite_info = {
                    'suite': sous_nombres if respecter_ordre_apparition else sorted(sous_nombres),
                    'differences': progression,
                    'colonnes': sous_colonnes,
                    'direction': direction,
                    'type_suite': 'variable'
                }

                if date:
                    suite_info['dates'] = date
                if type_tirage:
                    suite_info['types'] = type_tirage

                suites_trouvees[suite_key].append(suite_info)

    def rechercher_suites(self, nombres, colonnes_apparition, longueurs_a_verifier, respecter_positions,
                          respecter_ordre_apparition, difference_constante, direction,
                          suites_trouvees, suite_key, verifier_completion,
                          valeur_min, valeur_max, date=None, type_tirage=None):
        """
        Recherche des suites arithmétiques dans un ensemble de nombres.

        Args:
            nombres (list): Liste des nombres à analyser
            colonnes_apparition (list): Liste des colonnes correspondantes
            longueurs_a_verifier (list): Longueurs de suites à vérifier
            respecter_positions (bool): Si True, respecte les positions dans la recherche
            respecter_ordre_apparition (bool): Si True, respecte l'ordre des nombres
            difference_constante (bool): Si True, cherche une suite à différence constante
            direction (str): Direction de l'analyse
            suites_trouvees (dict): Dictionnaire pour stocker les suites trouvées
            suite_key (str): Clé pour identifier la suite
            verifier_completion (bool): Si True, vérifie si la suite est complète
            valeur_min (int): Valeur minimale autorisée
            valeur_max (int): Valeur maximale autorisée
            date (list, optional): Liste des dates correspondantes
            type_tirage (list, optional): Liste des types de tirage
        """
        if respecter_positions:
            for longueur_suite in longueurs_a_verifier:
                if longueur_suite < 3 or longueur_suite > len(nombres):
                    continue

                for i in range(len(nombres) - longueur_suite + 1):
                    sous_nombres = nombres[i:i + longueur_suite]
                    sous_colonnes = colonnes_apparition[i:i + longueur_suite]

                    self.traiter_suite(sous_nombres, sous_colonnes, respecter_ordre_apparition,
                                       difference_constante, direction, suites_trouvees,
                                       suite_key, verifier_completion, valeur_min, valeur_max,
                                       date, type_tirage)
        else:
            for longueur_suite in longueurs_a_verifier:
                if longueur_suite < 3 or longueur_suite > len(nombres):
                    continue

                for combo in itertools.combinations(range(len(nombres)), longueur_suite):
                    sous_nombres = [nombres[i] for i in combo]
                    sous_colonnes = [colonnes_apparition[i] for i in combo]

                    self.traiter_suite(sous_nombres, sous_colonnes, respecter_ordre_apparition,
                                       difference_constante, direction, suites_trouvees,
                                       suite_key, verifier_completion, valeur_min, valeur_max,
                                       date, type_tirage)

    def analyser_suites_arithmetiques(self,
                                      fichier,
                                      sens_lecture=True,
                                      colonnes="num",
                                      respecter_positions=True,
                                      types_tirage=None,
                                      date_debut=None,
                                      date_fin=None,
                                      direction="horizontal",
                                      difference_constante=True,
                                      respecter_ordre_apparition=False,
                                      longueur_suite_filtre=None,
                                      verifier_completion=True,
                                      valeur_min=1,
                                      valeur_max=90):
        """
        Analyse un fichier pour trouver des suites arithmétiques avec vérification de complétion.

        Args:
            fichier (str): Chemin vers le fichier CSV à analyser
            sens_lecture (bool): Si True, lit le fichier dans l'ordre, sinon à l'envers
            colonnes (str): Type de colonnes à analyser ('num', 'machine', 'tous')
            respecter_positions (bool): Si True, respecte les positions dans la recherche
            types_tirage (list): Types de tirage à inclure
            date_debut (str): Date de début au format 'dd/mm/yyyy'
            date_fin (str): Date de fin au format 'dd/mm/yyyy'
            direction (str): Direction de l'analyse ('horizontal', 'vertical', 'les_deux')
            difference_constante (bool): Si True, cherche des suites à différence constante
            respecter_ordre_apparition (bool): Si True, respecte l'ordre d'apparition des nombres
            longueur_suite_filtre (int): Filtre sur la longueur des suites à rechercher
            verifier_completion (bool): Si True, vérifie si la suite est complète
            valeur_min (int): Valeur minimale autorisée
            valeur_max (int): Valeur maximale autorisée

        Returns:
            dict: Dictionnaire des suites trouvées
        """
        # Charger le fichier
        df = pd.read_csv(fichier, sep=';')
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')

        # Appliquer les filtres
        if date_debut:
            df = df[df['Date'] >= datetime.strptime(date_debut, '%d/%m/%Y')]
        if date_fin:
            df = df[df['Date'] <= datetime.strptime(date_fin, '%d/%m/%Y')]
        if types_tirage:
            df = df[df['Type de Tirage'].isin(types_tirage)]
        if not sens_lecture:
            df = df.iloc[::-1].reset_index(drop=True)

        # Définir les colonnes à analyser
        colonnes_num = ['Num1', 'Num2', 'Num3', 'Num4', 'Num5']
        colonnes_machine = ['Machine1', 'Machine2', 'Machine3', 'Machine4', 'Machine5']
        colonnes_analyse = colonnes_num if colonnes.lower() == "num" else \
            colonnes_machine if colonnes.lower() == "machine" else \
                colonnes_num + colonnes_machine

        suites_trouvees = {}

        # Analyse horizontale
        if direction.lower() in ["horizontal", "les_deux"]:
            for index, row in df.iterrows():
                date = row['Date'].strftime('%d/%m/%Y')
                type_tirage = row['Type de Tirage']
                nombres = []
                colonnes_apparition = []

                for col in colonnes_analyse:
                    if col in row and not pd.isna(row[col]):
                        nombres.append(int(row[col]))
                        colonnes_apparition.append(col)

                # Déterminer les longueurs de suite à vérifier
                longueurs_a_verifier = [longueur_suite_filtre] if longueur_suite_filtre else range(3, len(nombres) + 1)

                # Vérifier les suites selon les paramètres
                self.rechercher_suites(
                    nombres, colonnes_apparition, longueurs_a_verifier, respecter_positions,
                    respecter_ordre_apparition, difference_constante, 'horizontale',
                    suites_trouvees, f"{date}_{type_tirage}", verifier_completion,
                    valeur_min, valeur_max, date=[date], type_tirage=[type_tirage]
                )

        # Analyse verticale
        if direction.lower() in ["vertical", "les_deux"]:
            for col in colonnes_analyse:
                if col not in df.columns:
                    continue

                nombres_verticaux = df[col].astype(int).tolist()
                positions_verticales = list(range(len(nombres_verticaux)))

                # Déterminer les longueurs de suite
                max_longueur = min(6, len(nombres_verticaux) + 1)
                longueurs_a_verifier = [longueur_suite_filtre] if longueur_suite_filtre else range(3, max_longueur)

                for longueur_suite in longueurs_a_verifier:
                    if longueur_suite < 3 or longueur_suite > len(nombres_verticaux):
                        continue

                    for i in range(len(nombres_verticaux) - longueur_suite + 1):
                        sous_nombres = nombres_verticaux[i:i + longueur_suite]
                        indices = positions_verticales[i:i + longueur_suite]

                        # Vérifier si c'est une suite
                        if difference_constante:
                            est_suite = False
                            raison = None

                            if respecter_ordre_apparition:
                                est_suite, raison = self.est_suite_arithmetique_ordre(sous_nombres)
                            else:
                                est_suite = self.est_suite_arithmetique(sous_nombres)
                                if est_suite:
                                    nombres_triees = sorted(sous_nombres)
                                    raison = nombres_triees[1] - nombres_triees[0]

                            if est_suite:
                                # Créer une clé unique pour cette suite verticale
                                dates = [df.iloc[idx]['Date'].strftime('%d/%m/%Y') for idx in indices]
                                types = [df.iloc[idx]['Type de Tirage'] for idx in indices]
                                positions = [col] * len(indices)

                                suite_key = f"Verticale_{col}_{dates[0]}_{dates[-1]}"

                                if suite_key not in suites_trouvees:
                                    suites_trouvees[suite_key] = []

                                suite_info = {
                                    'suite': sous_nombres if respecter_ordre_apparition else sorted(sous_nombres),
                                    'raison': raison,
                                    'colonne': col,
                                    'colonnes': positions,
                                    'dates': dates,
                                    'types': types,
                                    'direction': 'verticale',
                                    'type_suite': 'constante'
                                }

                                # Vérifier si la suite est complète
                                if verifier_completion:
                                    est_complete, elements_manquants = self.est_suite_complete(
                                        suite_info['suite'], raison, valeur_min, valeur_max
                                    )
                                    suite_info['est_complete'] = est_complete
                                    suite_info['elements_manquants'] = elements_manquants

                                suites_trouvees[suite_key].append(suite_info)
                        else:
                            # Traitement similaire pour les suites à progression variable
                            progression = None
                            if respecter_ordre_apparition:
                                progression = self.est_suite_progression_ordre(sous_nombres)
                            else:
                                progression = self.est_suite_progression(sous_nombres)

                            if progression:
                                dates = [df.iloc[idx]['Date'].strftime('%d/%m/%Y') for idx in indices]
                                types = [df.iloc[idx]['Type de Tirage'] for idx in indices]
                                positions = [col] * len(indices)

                                suite_key = f"Verticale_{col}_{dates[0]}_{dates[-1]}"

                                if suite_key not in suites_trouvees:
                                    suites_trouvees[suite_key] = []

                                suites_trouvees[suite_key].append({
                                    'suite': sous_nombres if respecter_ordre_apparition else sorted(sous_nombres),
                                    'differences': progression,
                                    'colonne': col,
                                    'colonnes': positions,
                                    'dates': dates,
                                    'types': types,
                                    'direction': 'verticale',
                                    'type_suite': 'variable'
                                })

            # Analyse verticale inter-colonnes si "tous" est sélectionné
            if colonnes.lower() == "tous":
                colonnes_par_date = {}

                for index, row in df.iterrows():
                    date = row['Date'].strftime('%d/%m/%Y')
                    type_tirage = row['Type de Tirage']
                    tirage_key = f"{date}_{type_tirage}"

                    if tirage_key not in colonnes_par_date:
                        colonnes_par_date[tirage_key] = {}

                    for col in colonnes_analyse:
                        if col in row and not pd.isna(row[col]):
                            colonnes_par_date[tirage_key][col] = int(row[col])

                max_longueur = min(6, len(df))
                longueurs_a_verifier = [longueur_suite_filtre] if longueur_suite_filtre else range(3, max_longueur)

                for longueur_suite in longueurs_a_verifier:
                    if longueur_suite < 3 or longueur_suite > len(df):
                        continue

                    for start_idx in range(len(df) - longueur_suite + 1):
                        tirages_consecutive = []
                        tirages_info = []

                        for i in range(longueur_suite):
                            idx = start_idx + i
                            date = df.iloc[idx]['Date'].strftime('%d/%m/%Y')
                            type_tirage = df.iloc[idx]['Type de Tirage']
                            tirage_key = f"{date}_{type_tirage}"

                            tirages_consecutive.append(colonnes_par_date.get(tirage_key, {}))
                            tirages_info.append((date, type_tirage))

                        for col_start in colonnes_analyse:
                            for col_pattern in itertools.product(colonnes_analyse, repeat=longueur_suite - 1):
                                colonnes_pattern = [col_start] + list(col_pattern)

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

                                if len(nombres) >= 3 and (
                                        longueur_suite_filtre is None or len(nombres) == longueur_suite_filtre):
                                    # Vérifier si c'est une suite
                                    if difference_constante:
                                        est_suite = False
                                        raison = None

                                        if respecter_ordre_apparition:
                                            est_suite, raison = self.est_suite_arithmetique_ordre(nombres)
                                        else:
                                            est_suite = self.est_suite_arithmetique(nombres)
                                            if est_suite:
                                                nombres_triees = sorted(nombres)
                                                raison = nombres_triees[1] - nombres_triees[0]

                                        if est_suite:
                                            suite_key = f"VerticaleInterColonnes_{dates_correspondantes[0]}_{dates_correspondantes[-1]}"

                                            if suite_key not in suites_trouvees:
                                                suites_trouvees[suite_key] = []

                                            suite_info = {
                                                'suite': nombres if respecter_ordre_apparition else sorted(nombres),
                                                'raison': raison,
                                                'colonnes': colonnes_correspondantes,
                                                'dates': dates_correspondantes,
                                                'types': types_correspondants,
                                                'direction': 'verticale_inter_colonnes',
                                                'type_suite': 'constante'
                                            }

                                            # Vérifier si la suite est complète
                                            if verifier_completion:
                                                est_complete, elements_manquants = self.est_suite_complete(
                                                    suite_info['suite'], raison, valeur_min, valeur_max
                                                )
                                                suite_info['est_complete'] = est_complete
                                                suite_info['elements_manquants'] = elements_manquants

                                            suites_trouvees[suite_key].append(suite_info)
                                    else:
                                        progression = None
                                        if respecter_ordre_apparition:
                                            progression = self.est_suite_progression_ordre(nombres)
                                        else:
                                            progression = self.est_suite_progression(nombres)

                                        if progression:
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

    def resultats_en_json(self, suites_trouvees):
        """
        Convertit les résultats en format JSON pour l'API.

        Args:
            suites_trouvees (dict): Dictionnaire des suites trouvées

        Returns:
            dict: Résultats formatés pour JSON
        """
        resultats = {
            "total_suites": sum(len(suites) for suites in suites_trouvees.values()),
            "total_tirages_avec_suites": len(suites_trouvees),
            "suites": []
        }

        for cle, suites in suites_trouvees.items():
            for suite in suites:
                suite_info = {
                    "cle": cle,
                    "suite": suite['suite'],
                    "type_suite": suite['type_suite'],
                    "direction": suite.get('direction', 'horizontale'),
                    "colonnes": suite['colonnes']
                }

                if suite['type_suite'] == 'constante':
                    suite_info["raison"] = suite['raison']
                    if 'est_complete' in suite:
                        suite_info["est_complete"] = suite['est_complete']
                        if not suite['est_complete'] and 'elements_manquants' in suite:
                            suite_info["elements_manquants"] = suite['elements_manquants']
                else:
                    suite_info["differences"] = suite['differences']

                if 'dates' in suite:
                    suite_info["dates"] = suite['dates']
                if 'types' in suite:
                    suite_info["types"] = suite['types']

                resultats["suites"].append(suite_info)

        return resultats
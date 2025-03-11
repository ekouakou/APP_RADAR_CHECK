import pandas as pd
import numpy as np
import json
from itertools import combinations
import random


class SequenceAnalyzer:
    def __init__(self):
        # Paramètres par défaut
        self.min_sequence_length = 3
        self.max_results_per_date = 500
        self.search_depth = 'medium'
        self.difference_type = 'constant'
        self.respect_order = True
        self.respect_columns = True
        self.filter_dates = None
        self.filter_tirage_types = None

    def set_parameters(self, respect_columns=None, min_sequence_length=None,
                       max_results_per_date=None, search_depth=None,
                       filter_dates=None, filter_tirage_types=None,
                       difference_type=None, respect_order=None):
        """
        Définit les paramètres d'analyse
        """
        if respect_columns is not None:
            self.respect_columns = respect_columns
        if min_sequence_length is not None:
            self.min_sequence_length = min_sequence_length
        if max_results_per_date is not None:
            self.max_results_per_date = max_results_per_date
        if search_depth is not None:
            if search_depth in ['shallow', 'medium', 'deep']:
                self.search_depth = search_depth
        if filter_dates is not None:
            self.filter_dates = filter_dates
        if filter_tirage_types is not None:
            self.filter_tirage_types = filter_tirage_types
        if difference_type is not None:
            if difference_type in ['constant', 'variable', 'any']:
                self.difference_type = difference_type
        if respect_order is not None:
            self.respect_order = respect_order

        return self

    def has_constant_difference(self, values):
        """
        Vérifie si les différences sont constantes
        """
        if len(values) < 2:
            return False  # Pas assez de valeurs pour calculer une différence
        differences = [values[i + 1] - values[i] for i in range(len(values) - 1)]
        return all(abs(diff - differences[0]) < 0.001 for diff in differences)

    def has_arithmetic_difference_progression(self, values):
        """
        Vérifie si les différences suivent une progression arithmétique
        """
        if len(values) < 3:
            return False  # Pas assez de valeurs pour calculer une progression de différences

        # Calculer les différences de premier ordre
        first_order_diff = [values[i + 1] - values[i] for i in range(len(values) - 1)]

        # Calculer les différences de second ordre (différences des différences)
        second_order_diff = [first_order_diff[i + 1] - first_order_diff[i] for i in range(len(first_order_diff) - 1)]

        # Vérifier si les différences de second ordre sont constantes (à une marge d'erreur près)
        return all(abs(diff - second_order_diff[0]) < 0.001 for diff in second_order_diff)

    def check_sequence_pattern(self, values, difference_type=None):
        """
        Vérifie les séquences selon le type de différence demandé
        """
        if difference_type is None:
            difference_type = self.difference_type

        if difference_type == 'constant':
            return self.has_constant_difference(values)
        elif difference_type == 'variable':
            return self.has_arithmetic_difference_progression(values)
        elif difference_type == 'any':
            # Accepte les deux types de séquences
            return self.has_constant_difference(values) or self.has_arithmetic_difference_progression(values)
        else:
            # Par défaut, recherche des différences constantes
            return self.has_constant_difference(values)

    def calculate_differences(self, values):
        """
        Calcule les différences d'une séquence
        """
        return [values[i + 1] - values[i] for i in range(len(values) - 1)]

    def find_cross_column_sequences(self, data_points, group, date, results, max_sequences=1000,
                                    difference_type=None, respect_order=None):
        """
        Recherche des séquences arithmétiques à travers différentes colonnes
        data_points: liste de tuples (colonne, index, valeur, ordre)
        """
        if difference_type is None:
            difference_type = self.difference_type

        if respect_order is None:
            respect_order = self.respect_order

        # Si trop de points de données, échantillonner pour éviter une explosion combinatoire
        if len(data_points) > 150:
            data_points = random.sample(data_points, 150)

        # Trier soit par valeur (pour ignorer l'ordre), soit par ordre d'apparition
        if respect_order:
            # Trier d'abord par index (tirage), puis par ordre d'apparition
            data_points.sort(key=lambda x: (x[1], x[3]))
        else:
            # Trier uniquement par valeur
            data_points.sort(key=lambda x: x[2])

        sequences_found = 0
        # Utiliser un ensemble pour éviter les doublons
        seen_sequences = set()

        # Recherche des séquences de 3 valeurs ou plus
        for i in range(len(data_points) - 2):
            if sequences_found >= max_sequences:
                break

            for j in range(i + 1, len(data_points) - 1):
                # Si respect_order est True, vérifier que les indices sont consécutifs
                if respect_order and (
                        data_points[j][1] != data_points[i][1] or data_points[j][3] != data_points[i][3] + 1):
                    continue

                # Calculer la différence initiale pour cette paire
                initial_diff = data_points[j][2] - data_points[i][2]

                # Pour les séquences à différence constante
                if difference_type in ['constant', 'any']:
                    # Chercher le prochain élément de la séquence avec différence constante
                    expected_next = data_points[j][2] + initial_diff
                    constant_sequence = [data_points[i], data_points[j]]

                    # Chercher tous les éléments suivants qui pourraient continuer la séquence
                    current_expected = expected_next
                    for k in range(j + 1, len(data_points)):
                        # Si respect_order est True, vérifier aussi que l'ordre est respecté
                        if respect_order and (
                                data_points[k][1] != data_points[j][1] or data_points[k][3] != data_points[j][3] + 1):
                            continue

                        if abs(data_points[k][2] - current_expected) < 0.001:
                            constant_sequence.append(data_points[k])
                            current_expected += initial_diff

                    # Si nous avons trouvé une séquence constante d'au moins 3 éléments
                    if len(constant_sequence) >= 3:
                        # Créer une clé unique pour cette séquence basée sur les valeurs
                        seq_key = tuple(int(point[2]) for point in constant_sequence)

                        if seq_key not in seen_sequences:
                            seen_sequences.add(seq_key)

                            # Extraire les informations de la séquence
                            columns = [point[0] for point in constant_sequence]
                            column_str = ", ".join(columns)

                            # Obtenir les types correspondants
                            indices = [point[1] for point in constant_sequence]
                            types = [group['Type de Tirage'].iloc[idx] for idx in indices]

                            # Valeurs de la séquence
                            values = [point[2] for point in constant_sequence]

                            # Calculer les différences
                            differences = self.calculate_differences(values)

                            result = {
                                "Colonne": [column_str],
                                "Dates": [date],
                                "Differences": [int(d) for d in differences],
                                "Type_Sequence": "constante",
                                "Longueur": len(constant_sequence),
                                "Types": types,
                                "Valeurs": [int(v) for v in values],
                                "Respect_Ordre": respect_order
                            }

                            results.append(result)
                            sequences_found += 1

                            if sequences_found >= max_sequences:
                                break

                # Pour les séquences à différence variable (progression arithmétique)
                if difference_type in ['variable', 'any']:
                    # Pour les séquences à différence variable, nous avons besoin d'au moins 3 points pour commencer
                    for k in range(j + 1, len(data_points)):
                        # Si respect_order est True, vérifier aussi que l'ordre est respecté
                        if respect_order and (
                                data_points[k][1] != data_points[j][1] or data_points[k][3] != data_points[j][3] + 1):
                            continue

                        # Calculer les deux premières différences
                        diff1 = data_points[j][2] - data_points[i][2]
                        diff2 = data_points[k][2] - data_points[j][2]

                        # Calculer la différence de second ordre
                        diff_of_diff = diff2 - diff1

                        # Séquence initiale avec 3 points
                        variable_sequence = [data_points[i], data_points[j], data_points[k]]

                        # Prochaine différence attendue
                        next_diff = diff2 + diff_of_diff

                        # Prochaine valeur attendue
                        expected_next = data_points[k][2] + next_diff

                        # Continuer la séquence si possible
                        current_expected = expected_next
                        current_diff = next_diff

                        for l in range(k + 1, len(data_points)):
                            # Si respect_order est True, vérifier aussi que l'ordre est respecté
                            if respect_order and (
                                    data_points[l][1] != data_points[k][1] or data_points[l][3] != data_points[k][
                                3] + 1):
                                continue

                            if abs(data_points[l][2] - current_expected) < 0.001:
                                variable_sequence.append(data_points[l])
                                current_diff += diff_of_diff
                                current_expected += current_diff

                        # Si nous avons trouvé une séquence variable d'au moins 4 éléments (pour confirmer la progression)
                        if len(variable_sequence) >= 4:
                            # Vérifier que c'est bien une progression arithmétique des différences
                            values = [point[2] for point in variable_sequence]
                            if self.has_arithmetic_difference_progression(values):
                                # Créer une clé unique pour cette séquence
                                seq_key = tuple(int(point[2]) for point in variable_sequence)

                                if seq_key not in seen_sequences:
                                    seen_sequences.add(seq_key)

                                    # Extraire les informations de la séquence
                                    columns = [point[0] for point in variable_sequence]
                                    column_str = ", ".join(columns)

                                    # Obtenir les types correspondants
                                    indices = [point[1] for point in variable_sequence]
                                    types = [group['Type de Tirage'].iloc[idx] for idx in indices]

                                    # Calculer les différences
                                    differences = self.calculate_differences(values)

                                    result = {
                                        "Colonne": [column_str],
                                        "Dates": [date],
                                        "Differences": [int(d) for d in differences],
                                        "Type_Sequence": "variable",
                                        "Progression_Difference": int(diff_of_diff),
                                        "Longueur": len(variable_sequence),
                                        "Types": types,
                                        "Valeurs": [int(v) for v in values],
                                        "Respect_Ordre": respect_order
                                    }

                                    results.append(result)
                                    sequences_found += 1

                                    if sequences_found >= max_sequences:
                                        break

    def find_column_sequences(self, group, column, date, results, difference_type=None, respect_order=None):
        """
        Recherche des séquences arithmétiques dans une colonne spécifique
        """
        if difference_type is None:
            difference_type = self.difference_type

        if respect_order is None:
            respect_order = self.respect_order

        # Pour l'analyse en colonne, l'ordre est déjà respecté par défaut,
        # car nous travaillons sur une seule colonne dont les valeurs sont déjà ordonnées
        values = group[column].dropna().tolist()

        # Vérifier s'il y a suffisamment de valeurs
        if len(values) < 3:
            return

        # Pour les séquences à différence constante
        if difference_type in ['constant', 'any'] and self.has_constant_difference(values):
            # Calculer la différence constante
            diff = values[1] - values[0]
            differences = [diff] * (len(values) - 1)

            result = {
                "Colonne": [column],
                "Dates": [date],
                "Differences": [int(d) for d in differences],
                "Type_Sequence": "constante",
                "Longueur": len(values),
                "Types": group['Type de Tirage'].tolist(),
                "Valeurs": [int(v) for v in values],
                "Respect_Ordre": respect_order
            }

            results.append(result)

        # Pour les séquences à différence variable (progression arithmétique)
        if difference_type in ['variable', 'any'] and self.has_arithmetic_difference_progression(values):
            differences = self.calculate_differences(values)

            # Calculer la différence de second ordre (progression)
            diff_of_diff = differences[1] - differences[0]

            result = {
                "Colonne": [column],
                "Dates": [date],
                "Differences": [int(d) for d in differences],
                "Type_Sequence": "variable",
                "Progression_Difference": int(diff_of_diff),
                "Longueur": len(values),
                "Types": group['Type de Tirage'].tolist(),
                "Valeurs": [int(v) for v in values],
                "Respect_Ordre": respect_order
            }

            results.append(result)

    def analyze_data(self, df):
        """
        Analyse les données du DataFrame pour trouver des séquences arithmétiques
        """
        results = []

        # Définir les limites de recherche en fonction de la profondeur
        if self.search_depth == 'shallow':
            max_sequences = 100
            sample_size = 100
        elif self.search_depth == 'medium':
            max_sequences = 500
            sample_size = 200
        else:  # deep
            max_sequences = 1000
            sample_size = 300

        # Identifier les colonnes numériques et celles à analyser
        num_columns = [f'Num{i}' for i in range(1, 11) if f'Num{i}' in df.columns]
        machine_columns = [f'Machine{i}' for i in range(1, 11) if f'Machine{i}' in df.columns]
        predefined_columns = num_columns + machine_columns

        # Convertir la colonne Date en string si elle existe
        if 'Date' in df.columns:
            df['Date'] = df['Date'].astype(str)

        # Filtrer le DataFrame par les dates spécifiées si nécessaire
        if self.filter_dates and len(self.filter_dates) > 0:
            df = df[df['Date'].isin(self.filter_dates)]

        # Filtrer par types de tirage si spécifié
        if self.filter_tirage_types and len(self.filter_tirage_types) > 0:
            df = df[df['Type de Tirage'].isin(self.filter_tirage_types)]

        # Grouper par date pour analyser chaque jour séparément
        grouped = df.groupby('Date')

        for date, group in grouped:
            date_results = []

            if self.respect_columns:
                # Analyse par colonne - cherche des suites dans chaque colonne individuellement
                columns_to_analyze = predefined_columns if predefined_columns else group.select_dtypes(
                    include='number').columns.tolist()

                for column in columns_to_analyze:
                    if column in group.columns:
                        self.find_column_sequences(group, column, date, date_results)
            else:
                # Analyse inter-colonnes - cherche des suites à travers différentes colonnes

                # Collecter tous les points de données numériques
                all_data_points = []

                # Priorité aux colonnes Num et Machine
                for col in predefined_columns:
                    if col in group.columns:
                        for idx, val in enumerate(group[col].dropna()):
                            # Ajouter l'ordre d'apparition à chaque point de données
                            # L'ordre est déterminé par la position dans la colonne (Num1 = 1, Num2 = 2, etc.)
                            order = int(col.replace('Num', '').replace('Machine', '')) if col.replace('Num',
                                                                                                      '').replace(
                                'Machine', '').isdigit() else 0
                            all_data_points.append((col, idx, val, order))

                # Ajouter d'autres colonnes numériques si nécessaire
                if self.search_depth == 'deep':
                    other_num_cols = [col for col in group.select_dtypes(include='number').columns
                                      if col not in predefined_columns and col != 'Date']
                    for col in other_num_cols:
                        for idx, val in enumerate(group[col].dropna()):
                            # Pour les autres colonnes, l'ordre est défini par défaut à 0
                            all_data_points.append((col, idx, val, 0))

                # Rechercher des séquences à travers différentes colonnes
                self.find_cross_column_sequences(all_data_points, group, date, date_results, max_sequences)

            # Limiter le nombre de résultats par date
            if len(date_results) > self.max_results_per_date:
                date_results = date_results[:self.max_results_per_date]

            results.extend(date_results)

        return results

    def analyze_csv_file(self, file_path, **params):
        """
        Analyse un fichier CSV et retourne les résultats
        """
        # Mettre à jour les paramètres si fournis
        self.set_parameters(**params)

        try:
            # Lire le fichier CSV
            df = pd.read_csv(file_path, sep=';')

            # Vérifier les colonnes requises
            required_columns = {'Date', 'Type de Tirage'}
            if not required_columns.issubset(df.columns):
                return {
                    "error": f"Le fichier doit contenir au minimum les colonnes suivantes : {', '.join(required_columns)}"}

            # Convertir en numérique quand possible
            for col in df.columns:
                try:
                    df[col] = pd.to_numeric(df[col])
                except (ValueError, TypeError):
                    pass

            # Analyser les données
            all_results = self.analyze_data(df)

            # Préparer la réponse
            response = {
                "config": {
                    "respect_columns": self.respect_columns,
                    "search_depth": self.search_depth,
                    "min_sequence_length": self.min_sequence_length,
                    "difference_type": self.difference_type,
                    "filter_dates": self.filter_dates if self.filter_dates else "all",
                    "filter_tirage_types": self.filter_tirage_types if self.filter_tirage_types else "all",
                    "respect_order": self.respect_order
                },
                "total_results": len(all_results),
                "results": all_results
            }

            return response

        except Exception as e:
            import traceback
            return {
                "error": str(e),
                "traceback": traceback.format_exc()
            }
from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
from itertools import combinations
import random
import json

from flask_cors import CORS

app = Flask(__name__)
CORS(app)


# Fonction pour vérifier si les différences sont constantes
def has_constant_difference(values):
    if len(values) < 2:
        return False  # Pas assez de valeurs pour calculer une différence
    differences = [values[i + 1] - values[i] for i in range(len(values) - 1)]
    return all(abs(diff - differences[0]) < 0.001 for diff in differences)


# Fonction pour vérifier si les différences suivent une progression arithmétique
def has_arithmetic_difference_progression(values):
    if len(values) < 3:
        return False  # Pas assez de valeurs pour calculer une progression de différences

    # Calculer les différences de premier ordre
    first_order_diff = [values[i + 1] - values[i] for i in range(len(values) - 1)]

    # Calculer les différences de second ordre (différences des différences)
    second_order_diff = [first_order_diff[i + 1] - first_order_diff[i] for i in range(len(first_order_diff) - 1)]

    # Vérifier si les différences de second ordre sont constantes (à une marge d'erreur près)
    return all(abs(diff - second_order_diff[0]) < 0.001 for diff in second_order_diff)


# Fonction pour vérifier les séquences selon le type de différence demandé
def check_sequence_pattern(values, difference_type='constant'):
    if difference_type == 'constant':
        return has_constant_difference(values)
    elif difference_type == 'variable':
        return has_arithmetic_difference_progression(values)
    elif difference_type == 'any':
        # Accepte les deux types de séquences
        return has_constant_difference(values) or has_arithmetic_difference_progression(values)
    else:
        # Par défaut, recherche des différences constantes
        return has_constant_difference(values)


# Fonction pour calculer les différences d'une séquence
def calculate_differences(values):
    return [values[i + 1] - values[i] for i in range(len(values) - 1)]


# Fonction optimisée pour rechercher des séquences arithmétiques à travers différentes colonnes
def find_cross_column_sequences(data_points, group, date, results, max_sequences=1000, difference_type='constant',
                                respect_order=True):
    """
    Recherche des séquences arithmétiques à travers différentes colonnes
    data_points: liste de tuples (colonne, index, valeur, ordre)
    difference_type: 'constant', 'variable', ou 'any'
    respect_order: si True, respecte l'ordre d'apparition des numéros dans le jeu
    """
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
            if respect_order and (data_points[j][1] != data_points[i][1] or data_points[j][3] != data_points[i][3] + 1):
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
                        differences = calculate_differences(values)

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
                                data_points[l][1] != data_points[k][1] or data_points[l][3] != data_points[k][3] + 1):
                            continue

                        if abs(data_points[l][2] - current_expected) < 0.001:
                            variable_sequence.append(data_points[l])
                            current_diff += diff_of_diff
                            current_expected += current_diff

                    # Si nous avons trouvé une séquence variable d'au moins 4 éléments (pour confirmer la progression)
                    if len(variable_sequence) >= 4:
                        # Vérifier que c'est bien une progression arithmétique des différences
                        values = [point[2] for point in variable_sequence]
                        if has_arithmetic_difference_progression(values):
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
                                differences = calculate_differences(values)

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


# Recherche de séquences dans une colonne spécifique
def find_column_sequences(group, column, date, results, difference_type='constant', respect_order=True):
    """
    Recherche des séquences arithmétiques dans une colonne spécifique
    difference_type: 'constant', 'variable', ou 'any'
    respect_order: si True, respecte l'ordre d'apparition des numéros dans le jeu
    """
    # Pour l'analyse en colonne, l'ordre est déjà respecté par défaut,
    # car nous travaillons sur une seule colonne dont les valeurs sont déjà ordonnées
    values = group[column].dropna().tolist()

    # Vérifier s'il y a suffisamment de valeurs
    if len(values) < 3:
        return

    # Pour les séquences à différence constante
    if difference_type in ['constant', 'any'] and has_constant_difference(values):
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
    if difference_type in ['variable', 'any'] and has_arithmetic_difference_progression(values):
        differences = calculate_differences(values)

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


# Fonction principale d'analyse des données
def analyze_data(df, respect_columns, min_sequence_length=3, max_results_per_date=500, search_depth='medium',
                 filter_dates=None, filter_tirage_types=None, difference_type='constant', respect_order=True):
    """
    Analyse les données du DataFrame pour trouver des séquences arithmétiques
    respect_columns: si True, recherche uniquement dans les mêmes colonnes
    min_sequence_length: longueur minimale des séquences à rechercher (par défaut 3)
    search_depth: 'shallow', 'medium', ou 'deep' pour contrôler l'intensité de la recherche
    filter_dates: liste des dates à analyser (si None, toutes les dates sont analysées)
    filter_tirage_types: liste des types de tirage à analyser (si None, tous les types sont analysés)
    difference_type: 'constant', 'variable', ou 'any' pour le type de différence recherché
    respect_order: si True, respecte l'ordre d'apparition des numéros dans le jeu
    """
    results = []

    # Définir les limites de recherche en fonction de la profondeur
    if search_depth == 'shallow':
        max_sequences = 100
        sample_size = 100
    elif search_depth == 'medium':
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
    if filter_dates and len(filter_dates) > 0:
        df = df[df['Date'].isin(filter_dates)]

    # Filtrer par types de tirage si spécifié
    if filter_tirage_types and len(filter_tirage_types) > 0:
        df = df[df['Type de Tirage'].isin(filter_tirage_types)]

    # Grouper par date pour analyser chaque jour séparément
    grouped = df.groupby('Date')

    for date, group in grouped:
        date_results = []

        if respect_columns:
            # Analyse par colonne - cherche des suites dans chaque colonne individuellement
            columns_to_analyze = predefined_columns if predefined_columns else group.select_dtypes(
                include='number').columns.tolist()

            for column in columns_to_analyze:
                if column in group.columns:
                    find_column_sequences(group, column, date, date_results, difference_type, respect_order)
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
                        order = int(col.replace('Num', '').replace('Machine', '')) if col.replace('Num', '').replace(
                            'Machine', '').isdigit() else 0
                        all_data_points.append((col, idx, val, order))

            # Ajouter d'autres colonnes numériques si nécessaire
            if search_depth == 'deep':
                other_num_cols = [col for col in group.select_dtypes(include='number').columns
                                  if col not in predefined_columns and col != 'Date']
                for col in other_num_cols:
                    for idx, val in enumerate(group[col].dropna()):
                        # Pour les autres colonnes, l'ordre est défini par défaut à 0
                        all_data_points.append((col, idx, val, 0))

            # Rechercher des séquences à travers différentes colonnes
            find_cross_column_sequences(all_data_points, group, date, date_results, max_sequences, difference_type,
                                        respect_order)

        # Limiter le nombre de résultats par date
        if len(date_results) > max_results_per_date:
            date_results = date_results[:max_results_per_date]

        results.extend(date_results)

    return results


@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Endpoint API pour l'analyse des données
    Accepte un fichier CSV et divers paramètres de contrôle
    """
    # Vérifier si un fichier est envoyé
    if 'file' not in request.files:
        return jsonify({"error": "Aucun fichier fourni"}), 400

    file = request.files['file']

    # Paramètres de contrôle - tous récupérés depuis form-data
    respect_columns = request.form.get('respect_columns', 'true').lower() == 'true'
    page = int(request.form.get('page', '1'))
    per_page = int(request.form.get('per_page', '50'))
    min_sequence_length = int(request.form.get('min_sequence_length', '3'))
    max_results_per_date = int(request.form.get('max_results_per_date', '500'))
    search_depth = request.form.get('search_depth', 'medium').lower()
    difference_type = request.form.get('difference_type', 'constant').lower()

    # Nouveau paramètre pour respecter l'ordre d'apparition
    respect_order = request.form.get('respect_order', 'true').lower() == 'true'

    # Validation du type de différence
    if difference_type not in ['constant', 'variable', 'any']:
        difference_type = 'constant'  # Par défaut, recherche des différences constantes

    # Récupérer les dates à filtrer
    filter_dates = []
    filter_dates_param = request.form.get('filter_dates', None)

    if filter_dates_param:
        try:
            # Essayer de parser comme JSON (tableau)
            filter_dates = json.loads(filter_dates_param)
        except json.JSONDecodeError:
            # Si ce n'est pas du JSON valide, traiter comme une chaîne séparée par des virgules
            filter_dates = [date.strip() for date in filter_dates_param.split(',') if date.strip()]

    # Récupérer les types de tirage à filtrer
    filter_tirage_types = []
    filter_tirage_types_param = request.form.get('filter_tirage_types', None)

    if filter_tirage_types_param:
        try:
            # Essayer de parser comme JSON (tableau)
            filter_tirage_types = json.loads(filter_tirage_types_param)
        except json.JSONDecodeError:
            # Si ce n'est pas du JSON valide, traiter comme une chaîne séparée par des virgules
            filter_tirage_types = [type_tirage.strip() for type_tirage in filter_tirage_types_param.split(',') if
                                   type_tirage.strip()]

    # Validation de search_depth
    if search_depth not in ['shallow', 'medium', 'deep']:
        search_depth = 'medium'

    try:
        # Lire le fichier CSV
        df = pd.read_csv(file, sep=';')

        # Vérifier les colonnes requises
        required_columns = {'Date', 'Type de Tirage'}
        if not required_columns.issubset(df.columns):
            return jsonify({
                "error": f"Le fichier doit contenir au minimum les colonnes suivantes : {', '.join(required_columns)}"}), 400

        # Convertir en numérique quand possible
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except (ValueError, TypeError):
                pass

        # Analyser les données
        all_results = analyze_data(
            df,
            respect_columns,
            min_sequence_length,
            max_results_per_date,
            search_depth,
            filter_dates,
            filter_tirage_types,
            difference_type,
            respect_order
        )

        # Appliquer la pagination
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page

        paginated_results = all_results[start_idx:end_idx]

        # Préparer la réponse
        response = {
            "config": {
                "respect_columns": respect_columns,
                "search_depth": search_depth,
                "min_sequence_length": min_sequence_length,
                "difference_type": difference_type,
                "filter_dates": filter_dates if filter_dates else "all",
                "filter_tirage_types": filter_tirage_types if filter_tirage_types else "all",
                "respect_order": respect_order
            },
            "pagination": {
                "total_results": len(all_results),
                "page": page,
                "per_page": per_page,
                "total_pages": (len(all_results) + per_page - 1) // per_page
            },
            "results": paginated_results
        }

        return jsonify(response)

    except Exception as e:
        import traceback
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


if __name__ == '__main__':
    app.run(debug=True)
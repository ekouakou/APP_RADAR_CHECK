import pandas as pd
from datetime import datetime
import tqdm
import sys


def analyser_progression_variable(csv_file, date_debut=None, date_fin=None, type_tirage=None,
                                  type_analyse=None, respecter_position=True,
                                  detecter_patterns=False):
    """
    Analyse les progressions/régressions avec différences croissantes ou décroissantes
    Paramètres:
        detecter_patterns: Si True, détecte les séquences avec des patterns spécifiques (constant, linéaire, exponentiel)
    """
    # Charger et filtrer les données
    df = pd.read_csv(csv_file, sep=';', parse_dates=['Date'], dayfirst=True)

    if date_debut:
        df = df[df['Date'] >= pd.to_datetime(date_debut, dayfirst=True)]
    if date_fin:
        df = df[df['Date'] <= pd.to_datetime(date_fin, dayfirst=True)]
    if type_tirage:
        df = df[df['Type de Tirage'] == type_tirage]

    if df.empty:
        return "Aucun tirage ne correspond aux critères spécifiés."

    # Colonnes pour les numéros et les machines
    num_cols = ['Num1', 'Num2', 'Num3', 'Num4', 'Num5']
    machine_cols = ['Machine1', 'Machine2', 'Machine3', 'Machine4', 'Machine5']

    # Analyse en fonction du respect de position
    if respecter_position:
        return {
            'num': analyser_sequences_variables(df, num_cols, type_analyse, detecter_patterns),
            'machine': analyser_sequences_variables(df, machine_cols, type_analyse, detecter_patterns)
        }
    else:
        return {
            'num': analyser_sequences_sans_position_variables(df, num_cols, type_analyse,
                                                              detecter_patterns),
            'machine': analyser_sequences_sans_position_variables(df, machine_cols, type_analyse,
                                                                  detecter_patterns)
        }


def identifier_pattern(delta_differences):
    """
    Identifie le type de pattern dans une séquence de différences entre différences
    Retourne le type de pattern et la raison (si applicable)
    """
    if not delta_differences:
        return None, None

    # Vérifier si c'est un pattern constant
    if all(abs(d - delta_differences[0]) < 0.001 for d in delta_differences):
        return "constant", delta_differences[0]

    # Vérifier si c'est un pattern linéaire (différence de différence constante)
    second_order_diffs = [delta_differences[i + 1] - delta_differences[i] for i in range(len(delta_differences) - 1)]
    if len(second_order_diffs) >= 2 and all(abs(d - second_order_diffs[0]) < 0.001 for d in second_order_diffs):
        return "linéaire", second_order_diffs[0]

    # Vérifier si c'est un pattern exponentiel (ratio constant)
    ratios = [delta_differences[i + 1] / delta_differences[i] for i in range(len(delta_differences) - 1) if
              delta_differences[i] != 0]
    if len(ratios) >= 2 and all(abs(r - ratios[0]) < 0.1 for r in ratios):  # 10% de tolérance
        return "exponentiel", round(ratios[0], 2)

    # Autres patterns potentiels à ajouter
    return "irrégulier", None


def analyser_sequences_variables(df, colonnes, type_analyse=None, detecter_patterns=False):
    """
    Analyse les progressions/régressions à différence variable dans une séquence de colonnes
    """
    resultats = {}
    print("Analyse des séquences par position avec différence variable...")

    # Analyser tous types confondus
    all_types_data = {}
    for position, colonne in enumerate(tqdm.tqdm(colonnes, desc="Positions analysées")):
        all_types_data[f'Position {position + 1}'] = trouver_sequences_variables(df, colonne,
                                                                                 type_analyse, detecter_patterns)
    resultats['tous_types'] = all_types_data

    # Analyser par type de tirage
    for type_tirage in tqdm.tqdm(df['Type de Tirage'].unique(), desc="Types de tirage analysés"):
        df_type = df[df['Type de Tirage'] == type_tirage]
        if len(df_type) > 2:
            type_data = {}
            for position, colonne in enumerate(colonnes):
                type_data[f'Position {position + 1}'] = trouver_sequences_variables(df_type, colonne,
                                                                                    type_analyse, detecter_patterns)
            resultats[type_tirage] = type_data

    return resultats


def trouver_sequences_variables(df, colonne, type_analyse=None, detecter_patterns=False):
    """
    Trouve les séquences avec différences croissantes ou décroissantes dans une colonne
    """
    df_sorted = df.sort_values(by='Date')
    numeros = df_sorted[colonne].astype(int).tolist()
    dates = df_sorted['Date'].tolist()
    types = df_sorted['Type de Tirage'].tolist()

    # Calculer les différences
    differences = []
    for i in range(1, len(numeros)):
        differences.append({
            'de': numeros[i - 1],
            'a': numeros[i],
            'difference': numeros[i] - numeros[i - 1],
            'date_precedente': dates[i - 1].strftime('%d/%m/%Y'),
            'date_actuelle': dates[i].strftime('%d/%m/%Y'),
            'type_precedent': types[i - 1],
            'type_actuel': types[i]
        })

    # Initialiser les conteneurs pour les séquences trouvées
    results = {
        'progressions_diff_croissante': [],
        'progressions_diff_decroissante': [],
        'regressions_diff_croissante': [],
        'regressions_diff_decroissante': []
    }

    if detecter_patterns:
        results.update({
            'pattern_constant': [],
            'pattern_lineaire': [],
            'pattern_exponentiel': []
        })

    # Fonction pour ajouter une séquence au résultat
    def ajouter_sequence(sequence, categorie):
        if len(sequence) < 2:  # Minimum length is now 3 (initial + 2 in sequence)
            return

        deltas = [item['difference'] for item in sequence]
        delta_differences = [deltas[k + 1] - deltas[k] for k in range(len(deltas) - 1)]

        seq_data = {
            'valeurs': [sequence[0]['de']] + [item['a'] for item in sequence],
            'differences': deltas,
            'delta_differences': delta_differences,
            'longueur': len(sequence) + 1,
            'dates': [sequence[0]['date_precedente']] + [item['date_actuelle'] for item in sequence],
            'types': [sequence[0]['type_precedent']] + [item['type_actuel'] for item in sequence],
            'details': sequence
        }

        # Détecter les patterns si demandé
        if detecter_patterns and len(delta_differences) >= 2:
            pattern_type, raison = identifier_pattern(delta_differences)
            seq_data['pattern_type'] = pattern_type
            seq_data['pattern_raison'] = raison

            # Ajouter également aux catégories de pattern si un pattern est détecté
            if pattern_type == "constant" and raison is not None:
                results['pattern_constant'].append(seq_data)
            elif pattern_type == "linéaire" and raison is not None:
                results['pattern_lineaire'].append(seq_data)
            elif pattern_type == "exponentiel" and raison is not None:
                results['pattern_exponentiel'].append(seq_data)

        results[categorie].append(seq_data)

    # Parcourir les différences et trouver les séquences
    i = 0
    while i < len(differences) - 1:
        # Progressions avec différence croissante
        if differences[i]['difference'] > 0:
            sequence = [differences[i]]
            delta_prec = differences[i]['difference']
            j = i + 1

            while j < len(differences) and differences[j]['difference'] > 0:
                delta_curr = differences[j]['difference']

                if delta_curr > delta_prec and differences[j]['date_precedente'] == differences[j - 1]['date_actuelle']:
                    sequence.append(differences[j])
                    delta_prec = delta_curr
                    j += 1
                else:
                    break

            ajouter_sequence(sequence, 'progressions_diff_croissante')
            i = j

            # Vérification pour progressions avec différence décroissante
            sequence = [differences[i]]
            delta_prec = differences[i]['difference']
            j = i + 1

            while j < len(differences) and differences[j]['difference'] > 0:
                delta_curr = differences[j]['difference']

                if 0 < delta_curr < delta_prec and differences[j]['date_precedente'] == differences[j - 1][
                    'date_actuelle']:
                    sequence.append(differences[j])
                    delta_prec = delta_curr
                    j += 1
                else:
                    break

            ajouter_sequence(sequence, 'progressions_diff_decroissante')
            i = j

        # Régressions (différences négatives)
        elif differences[i]['difference'] < 0:
            # Régressions avec différence croissante (plus négative)
            sequence = [differences[i]]
            delta_prec = differences[i]['difference']
            j = i + 1

            while j < len(differences) and differences[j]['difference'] < 0:
                delta_curr = differences[j]['difference']

                if delta_curr < delta_prec and differences[j]['date_precedente'] == differences[j - 1]['date_actuelle']:
                    sequence.append(differences[j])
                    delta_prec = delta_curr
                    j += 1
                else:
                    break

            ajouter_sequence(sequence, 'regressions_diff_croissante')
            i = j

            # Régressions avec différence décroissante (moins négative)
            sequence = [differences[i]]
            delta_prec = differences[i]['difference']
            j = i + 1

            while j < len(differences) and differences[j]['difference'] < 0:
                delta_curr = differences[j]['difference']

                if delta_prec < delta_curr < 0 and differences[j]['date_precedente'] == differences[j - 1][
                    'date_actuelle']:
                    sequence.append(differences[j])
                    delta_prec = delta_curr
                    j += 1
                else:
                    break

            ajouter_sequence(sequence, 'regressions_diff_decroissante')
            i = j
        else:
            i += 1

    # Trier par longueur
    for key in results:
        results[key].sort(key=lambda x: x['longueur'], reverse=True)

    # Filtrer par type d'analyse si spécifié
    if type_analyse == 'progression' and not detecter_patterns:
        results['regressions_diff_croissante'] = []
        results['regressions_diff_decroissante'] = []
    elif type_analyse == 'regression' and not detecter_patterns:
        results['progressions_diff_croissante'] = []
        results['progressions_diff_decroissante'] = []

    return results


def analyser_sequences_sans_position_variables(df, colonnes, type_analyse=None,
                                               detecter_patterns=False):
    """
    Trouve les séquences indépendamment de la position
    """
    df_sorted = df.sort_values(by='Date')
    sequence_data = []

    # Préparer les données
    for idx, row in tqdm.tqdm(df_sorted.iterrows(), total=len(df_sorted), desc="Préparation des données"):
        date = row['Date']
        type_tirage = row['Type de Tirage']

        numeros = []
        for col in colonnes:
            numeros.append({
                'numero': int(row[col]),
                'colonne': col,
                'date': date.strftime('%d/%m/%Y'),
                'type': type_tirage
            })

        sequence_data.append({
            'date': date.strftime('%d/%m/%Y'),
            'type': type_tirage,
            'numeros': numeros
        })

    # Initialiser les conteneurs pour les résultats
    results = {
        'progressions_diff_croissante': [],
        'progressions_diff_decroissante': [],
        'regressions_diff_croissante': [],
        'regressions_diff_decroissante': []
    }

    if detecter_patterns:
        results.update({
            'pattern_constant': [],
            'pattern_lineaire': [],
            'pattern_exponentiel': []
        })

    # Rechercher les séquences
    for i in tqdm.tqdm(range(len(sequence_data) - 2), desc="Recherche de séquences"):
        for num_i in sequence_data[i]['numeros']:
            # Fonction pour ajouter une séquence trouvée
            def ajouter_sequence(sequence, categorie):
                if len(sequence) < 3:
                    return
                valeurs = [item['numero'] for item in sequence]
                differences = [valeurs[j + 1] - valeurs[j] for j in range(len(valeurs) - 1)]
                delta_differences = [differences[j + 1] - differences[j] for j in range(len(differences) - 1)]

                seq_data = {
                    'valeurs': valeurs,
                    'colonnes': [item['colonne'] for item in sequence],
                    'differences': differences,
                    'delta_differences': delta_differences,
                    'longueur': len(sequence),
                    'dates': [item['date'] for item in sequence],
                    'types': [item['type'] for item in sequence]
                }

                # Détecter les patterns si demandé
                if detecter_patterns and len(delta_differences) >= 2:
                    pattern_type, raison = identifier_pattern(delta_differences)
                    seq_data['pattern_type'] = pattern_type
                    seq_data['pattern_raison'] = raison

                    # Ajouter également aux catégories de pattern si un pattern est détecté
                    if pattern_type == "constant" and raison is not None:
                        results['pattern_constant'].append(seq_data)
                    elif pattern_type == "linéaire" and raison is not None:
                        results['pattern_lineaire'].append(seq_data)
                    elif pattern_type == "exponentiel" and raison is not None:
                        results['pattern_exponentiel'].append(seq_data)

                results[categorie].append(seq_data)

            # Recherche de progressions à différence croissante
            for num_j in sequence_data[i + 1]['numeros']:
                diff_1 = num_j['numero'] - num_i['numero']
                if diff_1 > 0:
                    sequence = [num_i, num_j]
                    date_prec = num_j['date']

                    # Chercher le troisième nombre et plus
                    k = i + 2
                    while k < len(sequence_data):
                        trouve = False
                        for num_k in sequence_data[k]['numeros']:
                            diff_2 = num_k['numero'] - sequence[-1]['numero']

                            if diff_2 > diff_1 and sequence_data[k]['date'] > date_prec:
                                sequence.append(num_k)
                                diff_1 = diff_2
                                date_prec = num_k['date']
                                trouve = True
                                break

                        if not trouve:
                            break

                        k += 1

                    if len(sequence) >= 3:
                        ajouter_sequence(sequence, 'progressions_diff_croissante')

            # Recherche de progressions à différence décroissante
            for num_j in sequence_data[i + 1]['numeros']:
                diff_1 = num_j['numero'] - num_i['numero']
                if diff_1 > 0:
                    sequence = [num_i, num_j]
                    date_prec = num_j['date']

                    # Chercher le troisième nombre et plus
                    k = i + 2
                    while k < len(sequence_data):
                        trouve = False
                        for num_k in sequence_data[k]['numeros']:
                            diff_2 = num_k['numero'] - sequence[-1]['numero']

                            if 0 < diff_2 < diff_1 and sequence_data[k]['date'] > date_prec:
                                sequence.append(num_k)
                                diff_1 = diff_2
                                date_prec = num_k['date']
                                trouve = True
                                break

                        if not trouve:
                            break

                        k += 1

                    if len(sequence) >= 3:
                        ajouter_sequence(sequence, 'progressions_diff_decroissante')

            # Recherche de régressions à différence croissante (plus négative)
            for num_j in sequence_data[i + 1]['numeros']:
                diff_1 = num_j['numero'] - num_i['numero']
                if diff_1 < 0:
                    sequence = [num_i, num_j]
                    date_prec = num_j['date']

                    # Chercher le troisième nombre et plus
                    k = i + 2
                    while k < len(sequence_data):
                        trouve = False
                        for num_k in sequence_data[k]['numeros']:
                            diff_2 = num_k['numero'] - sequence[-1]['numero']

                            if diff_2 < diff_1 and sequence_data[k]['date'] > date_prec:
                                sequence.append(num_k)
                                diff_1 = diff_2
                                date_prec = num_k['date']
                                trouve = True
                                break

                        if not trouve:
                            break

                        k += 1

                    if len(sequence) >= 3:
                        ajouter_sequence(sequence, 'regressions_diff_croissante')

            # Recherche de régressions à différence décroissante (moins négative)
            for num_j in sequence_data[i + 1]['numeros']:
                diff_1 = num_j['numero'] - num_i['numero']
                if diff_1 < 0:
                    sequence = [num_i, num_j]
                    date_prec = num_j['date']

                    # Chercher le troisième nombre et plus
                    k = i + 2
                    while k < len(sequence_data):
                        trouve = False
                        for num_k in sequence_data[k]['numeros']:
                            diff_2 = num_k['numero'] - sequence[-1]['numero']

                            if diff_1 < diff_2 < 0 and sequence_data[k]['date'] > date_prec:
                                sequence.append(num_k)
                                diff_1 = diff_2
                                date_prec = num_k['date']
                                trouve = True
                                break

                        if not trouve:
                            break

                        k += 1

                    if len(sequence) >= 3:
                        ajouter_sequence(sequence, 'regressions_diff_decroissante')

    # Trier par longueur
    for key in results:
        results[key].sort(key=lambda x: x['longueur'], reverse=True)

    # Filtrer par type d'analyse si spécifié
    if type_analyse == 'progression' and not detecter_patterns:
        results['regressions_diff_croissante'] = []
        results['regressions_diff_decroissante'] = []
    elif type_analyse == 'regression' and not detecter_patterns:
        results['progressions_diff_croissante'] = []
        results['progressions_diff_decroissante'] = []

    return results

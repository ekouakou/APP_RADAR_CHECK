import os
import json
import pandas as pd
from datetime import datetime
from typing import List, Dict, Union, Optional
from collections import defaultdict
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pathlib import Path

app = Flask(__name__)
CORS(app)  # Permet les requêtes cross-origin pour l'intégration avec React

# Configuration pour stocker temporairement les fichiers téléchargés
UPLOAD_FOLDER = Path('./uploads')
UPLOAD_FOLDER.mkdir(exist_ok=True)
app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limite de 16MB pour les fichiers téléchargés


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Endpoint pour télécharger un fichier CSV
    """
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier n\'a été envoyé'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400

    if file and file.filename.endswith('.csv'):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return jsonify({
            'message': 'Fichier téléchargé avec succès',
            'filename': filename,
            'file_path': file_path
        })

    return jsonify({'error': 'Type de fichier non autorisé, seuls les fichiers CSV sont acceptés'}), 400


@app.route('/api/analyze', methods=['POST'])
def analyze():
    """
    Endpoint pour analyser un fichier CSV téléchargé
    """
    data = request.json

    # Extraction des paramètres de la requête
    file_path = data.get('file_path')
    date_debut = data.get('date_debut')
    date_fin = data.get('date_fin')
    type_tirage = data.get('type_tirage')
    longueur_min = data.get('longueur_min', 3)
    type_analyse = data.get('type_analyse')
    respecter_position = data.get('respecter_position', True)
    analyser_meme_ligne = data.get('analyser_meme_ligne', False)
    fusionner_num_machine = data.get('fusionner_num_machine', False)
    utiliser_longueur_min = data.get('utiliser_longueur_min', True)
    reverse_order = data.get('reverse_order', False)

    if not file_path or not os.path.exists(file_path):
        return jsonify({'error': 'Fichier non trouvé'}), 404

    try:
        resultats = analyser_progression_constante(
            csv_file=file_path,
            date_debut=date_debut,
            date_fin=date_fin,
            type_tirage=type_tirage,
            longueur_min=longueur_min,
            type_analyse=type_analyse,
            respecter_position=respecter_position,
            analyser_meme_ligne=analyser_meme_ligne,
            fusionner_num_machine=fusionner_num_machine,
            utiliser_longueur_min=utiliser_longueur_min,
            reverse_order=reverse_order
        )

        return jsonify(resultats)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/files', methods=['GET'])
def list_files():
    """
    Endpoint pour lister les fichiers téléchargés
    """
    files = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if filename.endswith('.csv'):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            files.append({
                'name': filename,
                'path': file_path,
                'size': os.path.getsize(file_path),
                'uploaded_at': datetime.fromtimestamp(os.path.getctime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
            })

    return jsonify({'files': files})


@app.route('/api/files/<filename>', methods=['GET'])
def get_file(filename):
    """
    Endpoint pour télécharger un fichier
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


@app.route('/api/swagger.json', methods=['GET'])
def get_swagger():
    """
    Endpoint pour obtenir la documentation Swagger
    """
    with open('swagger.json', 'r') as f:
        swagger_data = json.load(f)
    return jsonify(swagger_data)


# Les fonctions d'analyse ci-dessous
def analyser_progression_constante(
        csv_file: str,
        date_debut: Optional[str] = None,
        date_fin: Optional[str] = None,
        type_tirage: Optional[str] = None,
        longueur_min: int = 3,
        type_analyse: Optional[str] = None,
        respecter_position: bool = True,
        analyser_meme_ligne: bool = False,
        fusionner_num_machine: bool = False,
        utiliser_longueur_min: bool = True,
        reverse_order: bool = False,
) -> Union[str, Dict]:
    try:
        df = pd.read_csv(csv_file, sep=';', parse_dates=['Date'], dayfirst=True, low_memory=False)
    except FileNotFoundError:
        return "Fichier CSV non trouvé."
    except Exception as e:
        return f"Erreur lors de la lecture du fichier CSV: {e}"

    if reverse_order:
        df = df.iloc[::-1].copy()

    if date_debut:
        try:
            date_debut_dt = datetime.strptime(date_debut, '%d/%m/%Y')
            df = df[df['Date'] >= date_debut_dt]
        except ValueError:
            return "Format de date de début incorrect. Utilisez DD/MM/YYYY."

    if date_fin:
        try:
            date_fin_dt = datetime.strptime(date_fin, '%d/%m/%Y')
            df = df[df['Date'] <= date_fin_dt]
        except ValueError:
            return "Format de date de fin incorrect. Utilisez DD/MM/YYYY."

    if type_tirage:
        df = df[df['Type de Tirage'] == type_tirage]

    if df.empty:
        return "Aucun tirage ne correspond aux critères spécifiés."

    num_cols = ['Num1', 'Num2', 'Num3', 'Num4', 'Num5']
    machine_cols = ['Machine1', 'Machine2', 'Machine3', 'Machine4', 'Machine5']

    colonnes_numeriques = num_cols + machine_cols
    for col in colonnes_numeriques:
        if col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col], errors='raise').astype('Int64')
            except ValueError as e:
                return f"Erreur de conversion de type pour la colonne {col}: {e}"

    colonnes_a_utiliser = num_cols + machine_cols if fusionner_num_machine else num_cols + machine_cols
    df_analyse = df[['Date', 'Type de Tirage'] + colonnes_a_utiliser].copy()

    resultats = {}

    if fusionner_num_machine:
        colonnes = num_cols + machine_cols
        if respecter_position:
            resultats['num_et_machine'] = analyser_sequences_constantes(df_analyse, colonnes, longueur_min,
                                                                        type_analyse, analyser_meme_ligne,
                                                                        utiliser_longueur_min, reverse_order)
        else:
            resultats['num_et_machine'] = analyser_sequences_sans_position(df_analyse, colonnes, longueur_min,
                                                                           type_analyse, analyser_meme_ligne,
                                                                           utiliser_longueur_min, reverse_order)
    else:
        if respecter_position:
            resultats['num'] = analyser_sequences_constantes(df_analyse, num_cols, longueur_min, type_analyse,
                                                             analyser_meme_ligne, utiliser_longueur_min, reverse_order)
            resultats['machine'] = analyser_sequences_constantes(df_analyse, machine_cols, longueur_min,
                                                                 type_analyse, analyser_meme_ligne,
                                                                 utiliser_longueur_min, reverse_order)
        else:
            resultats['num'] = analyser_sequences_sans_position(df_analyse, num_cols, longueur_min, type_analyse,
                                                                analyser_meme_ligne, utiliser_longueur_min,
                                                                reverse_order)
            resultats['machine'] = analyser_sequences_sans_position(df_analyse, machine_cols, longueur_min,
                                                                    type_analyse, analyser_meme_ligne,
                                                                    utiliser_longueur_min, reverse_order)

    return resultats


def analyser_sequences_constantes(
        df: pd.DataFrame,
        colonnes: List[str],
        longueur_min: int = 3,
        type_analyse: Optional[str] = None,
        analyser_meme_ligne: bool = False,
        utiliser_longueur_min: bool = True,
        reverse_order: bool = False,
) -> Dict:
    resultats = {}
    all_types_data = {}

    if analyser_meme_ligne:
        all_types_data['Même ligne'] = analyser_meme_ligne_progressions(df, colonnes, longueur_min, type_analyse,
                                                                        utiliser_longueur_min)

    all_types_data = {}
    for position, colonne in enumerate(colonnes):
        all_types_data[f'Position {position + 1}'] = trouver_sequences_constantes(df, colonne, longueur_min,
                                                                                  type_analyse, utiliser_longueur_min,
                                                                                  reverse_order)

    resultats['tous_types'] = all_types_data

    types_tirages = df['Type de Tirage'].unique()
    for type_tirage in types_tirages:
        df_type = df[df['Type de Tirage'] == type_tirage]
        if not utiliser_longueur_min or len(df_type) > longueur_min - 1:
            type_data = {}

            if analyser_meme_ligne:
                type_data['Même ligne'] = analyser_meme_ligne_progressions(df_type, colonnes, longueur_min,
                                                                           type_analyse, utiliser_longueur_min)

            type_data = {}
            for position, colonne in enumerate(colonnes):
                type_data[f'Position {position + 1}'] = trouver_sequences_constantes(df_type, colonne, longueur_min,
                                                                                     type_analyse,
                                                                                     utiliser_longueur_min,
                                                                                     reverse_order)
            resultats[type_tirage] = type_data

    return resultats


def trouver_sequences_constantes(
        df: pd.DataFrame,
        colonne: str,
        longueur_min: int = 3,
        type_analyse: Optional[str] = None,
        utiliser_longueur_min: bool = True,
        reverse_order: bool = False,
) -> Dict:
    """
    Trouve les séquences de progression/régression constante dans une colonne spécifique.
    """
    progressions_constantes = []
    regressions_constantes = []

    # Tri du DataFrame en fonction de la date
    df = df.sort_values(by='Date', ascending=not reverse_order)

    # Convertir la colonne en type entier
    df.loc[:, colonne] = pd.to_numeric(df[colonne], errors='coerce').astype('Int64')

    # Convertir la colonne et la date en listes pour une itération rapide
    valeurs = df[colonne].tolist()
    dates = df['Date'].tolist()
    types_tirages = df['Type de Tirage'].tolist()

    # Initialiser les variables pour suivre la séquence actuelle
    i = 0
    while i < len(valeurs) - 1:
        valeur_initiale = valeurs[i]
        date_initiale = dates[i]
        type_tirage_initial = types_tirages[i]

        # Calculer la différence entre la valeur actuelle et la suivante
        if i + 1 < len(valeurs) and pd.notna(valeurs[i]) and pd.notna(valeurs[i + 1]):
            diff_constante = valeurs[i + 1] - valeur_initiale

            # Si la différence est nulle, passer à la valeur suivante
            if diff_constante == 0:
                i += 1
                continue

            # Initialiser la séquence courante
            sequence_courante = [valeur_initiale]
            sequence_dates = [date_initiale]
            sequence_types = [type_tirage_initial]

            # Trouver les valeurs suivantes qui suivent la même progression
            j = i + 1
            while j < len(valeurs) and pd.notna(valeurs[j]) and valeurs[j] - sequence_courante[-1] == diff_constante:
                # Ajouter la valeur à la séquence courante
                sequence_courante.append(valeurs[j])
                sequence_dates.append(dates[j])
                sequence_types.append(types_tirages[j])

                # Passer à la valeur suivante
                j += 1

            # Appliquer le filtre de longueur si utiliser_longueur_min est True
            if not utiliser_longueur_min or len(sequence_courante) >= longueur_min:
                # Créer un dictionnaire pour stocker les informations de la séquence
                sequence_info = {
                    'valeurs': sequence_courante,
                    'difference': diff_constante,
                    'longueur': len(sequence_courante),
                    'dates': [date.strftime('%d/%m/%Y') for date in sequence_dates],
                    'types': sequence_types,
                    'colonne': colonne  # Ajout de la colonne
                }

                # Ajouter la séquence à la liste appropriée
                if diff_constante > 0:
                    progressions_constantes.append(sequence_info)
                else:
                    regressions_constantes.append(sequence_info)

            # Passer à la valeur suivante
            i = j
        else:
            i += 1

    # Trier les progressions et régressions par longueur
    progressions_constantes.sort(key=lambda x: x['longueur'], reverse=True)
    regressions_constantes.sort(key=lambda x: x['longueur'], reverse=True)

    # Retourner les résultats en fonction du type d'analyse demandé
    if type_analyse == 'progression':
        return {
            'progressions_constantes': progressions_constantes,
            'regressions_constantes': []
        }
    elif type_analyse == 'regression':
        return {
            'progressions_constantes': [],
            'regressions_constantes': regressions_constantes
        }
    else:
        return {
            'progressions_constantes': progressions_constantes,
            'regressions_constantes': regressions_constantes
        }


def analyser_meme_ligne_progressions(
        df: pd.DataFrame,
        colonnes: List[str],
        longueur_min: int = 3,
        type_analyse: Optional[str] = None,
        utiliser_longueur_min: bool = True,
) -> Dict:
    progressions_constantes = []
    regressions_constantes = []

    for col in colonnes:
        df.loc[:, col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

    for idx, row in df.iterrows():
        valeurs = row[colonnes].tolist()
        date = row['Date']
        type_tirage = row['Type de Tirage']

        i = 0
        while i < len(valeurs) - 1:
            if pd.notna(valeurs[i]) and pd.notna(valeurs[i + 1]):
                sequence_courante = [valeurs[i]]
                diff_constante = valeurs[i + 1] - valeurs[i]

                if diff_constante == 0:
                    i += 1
                    continue

                j = i + 1
                while j < len(valeurs) and pd.notna(valeurs[j]) and valeurs[j] - valeurs[j - 1] == diff_constante:
                    sequence_courante.append(valeurs[j])
                    j += 1

                if not utiliser_longueur_min or len(sequence_courante) >= longueur_min:
                    sequence_info = {
                        'valeurs': sequence_courante,
                        'difference': diff_constante,
                        'longueur': len(sequence_courante),
                        'dates': [date.strftime('%d/%m/%Y')] * len(sequence_courante),
                        'types': [type_tirage] * len(sequence_courante),
                        'colonnes': colonnes[i:i + len(sequence_courante)]
                    }

                    if diff_constante > 0:
                        progressions_constantes.append(sequence_info)
                    else:
                        regressions_constantes.append(sequence_info)

                i = j
            else:
                i += 1

    progressions_constantes.sort(key=lambda x: x['longueur'], reverse=True)
    regressions_constantes.sort(key=lambda x: x['longueur'], reverse=True)

    if type_analyse == 'progression':
        return {
            'progressions_constantes': progressions_constantes,
            'regressions_constantes': []
        }
    elif type_analyse == 'regression':
        return {
            'progressions_constantes': [],
            'regressions_constantes': regressions_constantes
        }
    else:
        return {
            'progressions_constantes': progressions_constantes,
            'regressions_constantes': regressions_constantes
        }


def analyser_sequences_sans_position(
        df: pd.DataFrame,
        colonnes: List[str],
        longueur_min: int = 3,
        type_analyse: Optional[str] = None,
        analyser_meme_ligne: bool = False,
        utiliser_longueur_min: bool = True,
        reverse_order: bool = False,
) -> Dict:
    resultats = {}
    all_types_data = {}

    if analyser_meme_ligne:
        all_types_data['Même ligne'] = analyser_meme_ligne_progressions(df, colonnes, longueur_min, type_analyse,
                                                                        utiliser_longueur_min)

    all_types_data['Toutes positions'] = trouver_sequences_sans_position(df, colonnes, longueur_min, type_analyse,
                                                                         utiliser_longueur_min, reverse_order)

    resultats['tous_types'] = all_types_data

    types_tirages = df['Type de Tirage'].unique()
    for type_tirage in types_tirages:
        df_type = df[df['Type de Tirage'] == type_tirage]
        if not utiliser_longueur_min or len(df_type) > longueur_min - 1:
            type_data = {}

            if analyser_meme_ligne:
                type_data['Même ligne'] = analyser_meme_ligne_progressions(df_type, colonnes, longueur_min,
                                                                           type_analyse, utiliser_longueur_min)

            type_data['Toutes positions'] = trouver_sequences_sans_position(df_type, colonnes, longueur_min,
                                                                            type_analyse, utiliser_longueur_min,
                                                                            reverse_order)

            resultats[type_tirage] = type_data

    return resultats


def trouver_sequences_sans_position(
        df: pd.DataFrame,
        colonnes: List[str],
        longueur_min: int = 3,
        type_analyse: Optional[str] = None,
        utiliser_longueur_min: bool = True,
        reverse_order: bool = False,
) -> Dict:
    # Convertir les colonnes en type entier
    for col in colonnes:
        df.loc[:, col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

    # Tri du DataFrame en fonction de la date
    df = df.sort_values(by='Date', ascending=not reverse_order)

    # Précalculer les données nécessaires
    sequence_data = []
    for idx, row in df.iterrows():
        date = row['Date']
        type_tirage = row['Type de Tirage']
        numeros = [{'numero': row[col], 'colonne': col, 'date': date, 'type': type_tirage} for col in colonnes if
                   pd.notna(row[col])]
        sequence_data.append({'date': date, 'type': type_tirage, 'numeros': numeros})

    # Précalculer un index des numéros par valeur et date
    numero_par_valeur_date = defaultdict(list)
    for data in sequence_data:
        for num in data['numeros']:
            numero_par_valeur_date[(num['numero'], data['date'])].append(num)

    sequences_constantes = []
    sequences_vues = set()

    for i in range(len(sequence_data)):
        for num_i in sequence_data[i]['numeros']:
            # Calculer les différences potentielles
            valeurs_possibles = set()
            for data in sequence_data:
                for num in data['numeros']:
                    if num['numero'] != num_i['numero']:
                        valeurs_possibles.add(num['numero'])

            differences = {val - num_i['numero'] for val in valeurs_possibles if val - num_i['numero'] != 0}

            for diff in differences:
                sequence_courante = [num_i]
                valeur_attendue = num_i['numero'] + diff
                date_prec = num_i['date']
                j = i + 1

                while j < len(sequence_data):
                    # Recherche directe dans l'index
                    candidats = numero_par_valeur_date.get((valeur_attendue, sequence_data[j]['date']), [])

                    # Filtrer les candidats en fonction de l'ordre inverse
                    if not reverse_order:
                        candidats = [c for c in candidats if c['date'] > date_prec]
                    else:
                        candidats = [c for c in candidats if c['date'] < date_prec]

                    if candidats:
                        num_j = candidats[0]  # Prendre le premier candidat
                        sequence_courante.append(num_j)
                        valeur_attendue += diff
                        date_prec = num_j['date']
                    else:
                        break
                    j += 1

                # Appliquer le filtre de longueur si utiliser_longueur_min est True
                if not utiliser_longueur_min or len(sequence_courante) >= longueur_min:
                    valeurs = tuple(item['numero'] for item in sequence_courante)
                    dates = tuple(item['date'].strftime('%d/%m/%Y') for item in sequence_courante)

                    # Convertir la séquence en un tuple pour la rendre hashable
                    sequence_tuple = (valeurs, dates, diff)

                    # Vérifier si cette séquence a déjà été vue
                    if sequence_tuple not in sequences_vues:
                        sequences_vues.add(sequence_tuple)  # Ajouter la séquence à l'ensemble des séquences vues

                        sequences_constantes.append({
                            'valeurs': list(valeurs),
                            'colonnes': [item['colonne'] for item in sequence_courante],
                            'difference': diff,
                            'longueur': len(sequence_courante),
                            'dates': [item['date'].strftime('%d/%m/%Y') for item in sequence_courante],
                            'types': [item['type'] for item in sequence_courante]
                        })

    # Séparer progressions et régressions
    progressions_constantes = [seq for seq in sequences_constantes if seq['difference'] > 0]
    regressions_constantes = [seq for seq in sequences_constantes if seq['difference'] < 0]

    # Trier par longueur
    progressions_constantes.sort(key=lambda x: x['longueur'], reverse=True)
    regressions_constantes.sort(key=lambda x: x['longueur'], reverse=True)

    if type_analyse == 'progression':
        return {
            'progressions_constantes': progressions_constantes,
            'regressions_constantes': []
        }
    elif type_analyse == 'regression':
        return {
            'progressions_constantes': [],
            'regressions_constantes': regressions_constantes
        }
    else:
        return {
            'progressions_constantes': progressions_constantes,
            'regressions_constantes': regressions_constantes
        }


if __name__ == '__main__':
    # Exécuter l'application Flask
    app.run(debug=True, port=5000)
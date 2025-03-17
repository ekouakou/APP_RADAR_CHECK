from flask import Flask, Blueprint, request, jsonify
from flask_cors import CORS
import os
import json
from pathlib import Path
from myClass.ProgressRegressConstantesClass import ProgressRegressConstantesClass

app = Flask(__name__)
CORS(app)

# Créer un Blueprint pour le nouvel analyseur
api = Blueprint('progress_regress_constantes', __name__)

# Dossier pour les uploads
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@api.route('/analyze', methods=['POST'])
def analyze_lottery_data():
    # Vérifier le type de contenu
    if request.content_type == 'application/json':
        data = request.get_json()
    else:
        data = request.form

    date_debut = data.get('date_debut', '01/01/2025')
    date_fin = data.get('date_fin', '31/01/2025')
    reverse_order = str(data.get('reverse_order', 'True')).lower() == 'true'
    longueur_min = int(data.get('longueur_min', '5'))
    type_analyse = data.get('type_analyse')
    respecter_position = str(data.get('respecter_position', 'False')).lower() == 'true'
    analyser_meme_ligne = str(data.get('analyser_meme_ligne', 'True')).lower() == 'true'
    fusionner_num_machine = str(data.get('fusionner_num_machine', 'False')).lower() == 'true'
    utiliser_longueur_min = str(data.get('utiliser_longueur_min', 'False')).lower() == 'true'

    # Récupérer le type de tirage qui peut être une chaîne ou une liste
    type_tirage = data.get('type_tirage')

    # Si le type_tirage est une chaîne JSON représentant une liste, la convertir en liste Python
    if type_tirage and isinstance(type_tirage, str) and type_tirage.startswith('['):
        try:
            type_tirage = json.loads(type_tirage)
        except json.JSONDecodeError:
            # Si la conversion échoue, conserver la valeur originale
            pass

    # Gestion du fichier
    file_path = data.get('file_path', './uploads/formatted_lottery_results.csv')
    if 'file' in request.files:
        file = request.files['file']
        file_path = os.path.join(UPLOAD_FOLDER, 'formatted_lottery_results.csv')
        file.save(file_path)

    # Créer une instance de l'analyseur
    analyzer = ProgressRegressConstantesClass()

    # Vérifier si le fichier existe
    if not Path(file_path).exists():
        return jsonify({
            'success': False,
            'error': f"Le fichier {file_path} n'existe pas"
        }), 404

    # Charger les données
    if analyzer.load_data(file_path):
        # Filtrer les données
        analyzer.filter_data(
            date_debut=date_debut,
            date_fin=date_fin,
            type_tirage=type_tirage,  # Passer le type_tirage qui peut être une liste
            reverse_order=reverse_order
        )

        # Lancer l'analyse
        resultats = analyzer.analyser_progression_constante(
            longueur_min=longueur_min,
            type_analyse=type_analyse,
            respecter_position=respecter_position,
            analyser_meme_ligne=analyser_meme_ligne,
            fusionner_num_machine=fusionner_num_machine,
            utiliser_longueur_min=utiliser_longueur_min
        )

        # Enregistrer les résultats (facultatif)
        #output_file = f'./resultats_{date_debut}_{date_fin}.json'
        #analyzer.save_results(resultats, output_file)

        return jsonify({
            'success': True,
            'results': resultats,
            #'output_file': output_file
        })
    else:
        return jsonify({
            'success': False,
            'error': "Impossible de charger les données"
        }), 500


@api.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({
            'success': False,
            'error': 'Aucun fichier trouvé'
        }), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({
            'success': False,
            'error': 'Aucun fichier sélectionné'
        }), 400

    # Sauvegarder le fichier
    file_path = os.path.join(UPLOAD_FOLDER, 'formatted_lottery_results.csv')
    file.save(file_path)

    return jsonify({
        'success': True,
        'file_path': file_path
    })


# Enregistrer le blueprint
app.register_blueprint(api, url_prefix='/api/progress_regress')

if __name__ == '__main__':
    app.run(debug=True)
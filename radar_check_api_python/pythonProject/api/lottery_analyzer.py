# fichier: main.py
from flask import Flask, Blueprint, request, jsonify
from flask_cors import CORS
import os
from pathlib import Path
from pythonProject.myClass.LotterySequenceAnalyzer import LotterySequenceAnalyzer

app = Flask(__name__)
CORS(app)

# Créer un Blueprint pour le nouvel analyseur
api = Blueprint('LotterySequenceAnalyzer', __name__)

# Dossier pour les uploads
UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@api.route('/analyze', methods=['POST'])
def analyze_lottery_data():
    # Récupérer les paramètres de la requête
    data = request.json

    # Paramètres avec valeurs par défaut
    date_debut = data.get('date_debut', '01/01/2025')
    date_fin = data.get('date_fin', '31/01/2025')
    reverse_order = data.get('reverse_order', True)
    longueur_min = data.get('longueur_min', 5)
    type_analyse = data.get('type_analyse')  # 'progression', 'regression', ou None
    respecter_position = data.get('respecter_position', False)
    analyser_meme_ligne = data.get('analyser_meme_ligne', True)
    fusionner_num_machine = data.get('fusionner_num_machine', False)
    utiliser_longueur_min = data.get('utiliser_longueur_min', False)
    file_path = data.get('file_path', './uploads/formatted_lottery_results.csv')

    # Créer une instance de l'analyseur
    analyzer = LotterySequenceAnalyzer()

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
        output_file = f'./resultats_{date_debut}_{date_fin}.json'
        analyzer.save_results(resultats, output_file)

        return jsonify({
            'success': True,
            'results': resultats,
            'output_file': output_file
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

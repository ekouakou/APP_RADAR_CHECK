from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from pythonProject.myClass.LotteryAnalyzer import LotteryAnalyzer
import os

app = Flask(__name__)
CORS(app)

# Créer un blueprint pour l'API
api = Blueprint('analyse_suites_arithmetiques', __name__)

# Initialiser l'analyseur de loterie
analyzer = LotteryAnalyzer()


@api.route('/analyze', methods=['POST'])
def analyze_lottery():
    """Point d'entrée API pour l'analyse des suites arithmétiques."""
    try:
        # Gérer différents types de contenu
        if request.content_type == 'application/json':
            data = request.get_json()
        elif request.content_type.startswith('multipart/form-data'):
            data = request.form.to_dict()
        elif request.content_type == 'application/x-www-form-urlencoded':
            data = request.form.to_dict()
        else:
            return jsonify({"error": "Type de contenu non supporté"}), 400

        # Vérifier si un fichier CSV a été spécifié
        if 'csv_path' not in data:
            return jsonify({"error": "Le chemin du fichier CSV est requis"}), 400

        # Récupérer les paramètres avec valeurs par défaut
        csv_path = data['csv_path']

        # Vérifier si le fichier existe
        if not os.path.exists(csv_path):
            return jsonify({"error": f"Le fichier {csv_path} n'existe pas"}), 404

        # Extraire tous les paramètres avec leurs valeurs par défaut
        params = {
            'sens_lecture': data.get('sens_lecture', True),
            'colonnes': data.get('colonnes', "num"),
            'respecter_positions': data.get('respecter_positions', True),
            'types_tirage': data.get('types_tirage'),
            'date_debut': data.get('date_debut'),
            'date_fin': data.get('date_fin'),
            'direction': data.get('direction', "horizontal"),
            'difference_constante': data.get('difference_constante', True),
            'respecter_ordre_apparition': data.get('respecter_ordre_apparition', False),
            'longueur_suite_filtre': data.get('longueur_suite_filtre'),
            'verifier_completion': data.get('verifier_completion', True),
            'valeur_min': data.get('valeur_min', 1),
            'valeur_max': data.get('valeur_max', 90)
        }

        # Exécuter l'analyse avec notre classe
        resultats = analyzer.analyser_suites_arithmetiques(csv_path, **params)

        # Convertir les résultats en JSON
        resultats_json = analyzer.resultats_en_json(resultats)

        return jsonify(resultats_json)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route('/lottery/health', methods=['GET'])
def health_check():
    """Point d'entrée API pour vérifier que l'API est opérationnelle."""
    return jsonify({"status": "OK", "message": "L'API d'analyse de loterie est opérationnelle"})

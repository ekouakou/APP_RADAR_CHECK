from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from pythonProject.myClass.AnalyseurTirage import AnalyseurTirage
import tempfile
import os

app = Flask(__name__)
CORS(app)

# Créer un blueprint pour l'API
api = Blueprint('analyse_suites_top', __name__)


@api.route('/analyser', methods=['POST'])
def analyser_tirages():
    """Point d'entrée API pour l'analyse des suites arithmétiques."""

    file = None
    file_path = None

    try:
        # Gérer différents types de contenu
        if 'application/json' in request.content_type:
            data = request.get_json(silent=True) or {}
            file_path = data.get('file_path')
            print(f"Données JSON: {data}")

        elif 'multipart/form-data' in request.content_type:
            # Vérifiez tous les noms de champs de fichier possibles
            if 'file' in request.files:
                file = request.files['file']
            elif 'file_path' in request.files:
                file = request.files['file_path']
            elif 'csv_file' in request.files:
                file = request.files['csv_file']

            # Récupérer les autres données du formulaire
            data = request.form.to_dict()
            print(f"Fichier récupéré: {file}")
            print(f"Données du formulaire: {data}")



        elif 'application/x-www-form-urlencoded' in request.content_type:
            data = request.form.to_dict()
        else:
            return jsonify({"error": "Type de contenu non supporté"}), 400

        # Si nous avons un fichier téléchargé via multipart/form-data
        if file and file.filename:
            # Sauvegarder temporairement le fichier
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
            file.save(temp_file.name)
            temp_file.close()
            file_to_analyze = temp_file.name
            print(f"Fichier temporaire créé: {file_to_analyze}")
        # Si nous avons un chemin de fichier via application/json
        elif file_path:
            # Vérifier que le fichier existe
            if not os.path.exists(file_path):
                return jsonify({"error": f"Le fichier '{file_path}' n'existe pas"}), 400
            file_to_analyze = file_path
            print(f"Utilisation du fichier existant: {file_to_analyze}")
        else:
            return jsonify({"error": "Aucun fichier fourni"}), 400

        # Vérifier si un fichier CSV a été spécifié
        #if 'fichier' not in data:
        #    return jsonify({"error": "Le chemin du fichier CSV est requis"}), 400

        #fichier = data['fichier']

        # Vérifier si le fichier existe
        #if not os.path.exists(fichier):
        #    return jsonify({"error": f"Le fichier {fichier} n'existe pas"}), 404

        # Initialiser l'analyseur
        analyseur = AnalyseurTirage(file_to_analyze)

        # Charger les données
        if not analyseur.charger_donnees():
            return jsonify({"error": "Impossible de charger les données du fichier"}), 500

        # Extraire tous les paramètres avec leurs valeurs par défaut
        parametres = {
            'types_suites': data.get('types_suites', ["arithmetique", "geometrique", "premiers"]),
            'date_debut': data.get('date_debut'),
            'date_fin': data.get('date_fin'),
            'ordre': data.get('ordre', "decroissant"),
            'min_elements': data.get('min_elements', 4),
            'forcer_min': data.get('forcer_min', True),
            'verifier_completion': data.get('verifier_completion', True),
            'respecter_position': data.get('respecter_position', False),
            'source_numeros': data.get('source_numeros', "tous"),
            'ordre_lecture': data.get('ordre_lecture', "normal"),
            'types_tirage': data.get('types_tirage'),
            'sens_analyse': data.get('sens_analyse', "les_deux"),
            'pagination': data.get('pagination', True),
            'items_par_page': data.get('items_par_page', 50),
            'page': data.get('page', 1)
        }

        # Dates spécifiques si fournies
        if 'dates' in data:
            parametres['dates'] = data['dates']

        # Effectuer l'analyse
        resultats = analyseur.analyser(parametres)

        # Préparer la réponse JSON
        if isinstance(resultats, dict):  # Résultats paginés
            response_data = {
                'page_courante': resultats['page_courante'],
                'total_pages': resultats['pages'],
                'total_resultats': resultats['total'],
                'resultats': resultats['resultats']
            }
        else:  # Tous les résultats
            response_data = {
                'total_resultats': len(resultats),
                'resultats': resultats
            }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route('/health', methods=['GET'])
def health_check():
    """Point d'entrée API pour vérifier que l'API est opérationnelle."""
    return jsonify({"status": "OK", "message": "L'API d'analyse des suites est opérationnelle"})


# Enregistrer le blueprint
app.register_blueprint(api, url_prefix='/api/suites')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
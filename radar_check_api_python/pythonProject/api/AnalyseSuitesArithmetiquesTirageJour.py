from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from pythonProject.myClass.SequenceAnalyzer import SequenceAnalyzer
import json
import tempfile
import os

app = Flask(__name__)
CORS(app)
api = Blueprint('AnalyseSuitesArithmetiquesTirageJour', __name__)


@api.route('/analyze', methods=['POST'])
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
    respect_order = request.form.get('respect_order', 'true').lower() == 'true'

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

    try:
        # Sauvegarder temporairement le fichier
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        file.save(temp_file.name)
        temp_file.close()

        # Initialiser l'analyseur
        analyzer = SequenceAnalyzer()

        # Configurer les paramètres
        analyzer.set_parameters(
            respect_columns=respect_columns,
            min_sequence_length=min_sequence_length,
            max_results_per_date=max_results_per_date,
            search_depth=search_depth,
            filter_dates=filter_dates,
            filter_tirage_types=filter_tirage_types,
            difference_type=difference_type,
            respect_order=respect_order
        )

        # Analyser le fichier
        results = analyzer.analyze_csv_file(temp_file.name)

        # Supprimer le fichier temporaire
        os.unlink(temp_file.name)

        if "error" in results:
            return jsonify(results), 500

        # Appliquer la pagination
        all_results = results["results"]
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page

        paginated_results = all_results[start_idx:end_idx]

        # Préparer la réponse
        response = {
            "config": results["config"],
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


# Enregistrer le blueprint
#app.register_blueprint(api, url_prefix='/api')

#if __name__ == '__main__':
#    app.run(debug=True)
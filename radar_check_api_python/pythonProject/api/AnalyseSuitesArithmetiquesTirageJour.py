from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from pythonProject.myClass.SequenceAnalyzer import SequenceAnalyzer
import json
import tempfile
import os

app = Flask(__name__)
CORS(app)
api = Blueprint('analyse_suites_arithmetiques_jour', __name__)


@api.route('/analyze', methods=['POST'])
def analyze():
    """
    Endpoint API pour l'analyse des données
    Accepte un fichier CSV et divers paramètres de contrôle
    """
    file = None
    data = {}
    file_path = None

    print(f"Content-Type: {request.content_type}")
    print(f"Files: {request.files}")
    print(f"Form data: {request.form}")

    if 'multipart/form-data' in request.content_type:
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

    elif request.content_type == 'application/json':
        data = request.get_json(silent=True) or {}
        file_path = data.get('file_path')
        print(f"Données JSON: {data}")

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

    # Extraction des paramètres de contrôle
    try:
        # Conversion des paramètres
        respect_columns = data.get('respect_columns', True)
        if isinstance(respect_columns, str):
            respect_columns = respect_columns.lower() == 'true'

        page = int(data.get('page', 1))
        per_page = int(data.get('per_page', 50))
        min_sequence_length = int(data.get('min_sequence_length', 3))
        max_results_per_date = int(data.get('max_results_per_date', 500))

        search_depth = data.get('search_depth', 'medium')
        if isinstance(search_depth, str):
            search_depth = search_depth.lower()

        difference_type = data.get('difference_type', 'constant')
        if isinstance(difference_type, str):
            difference_type = difference_type.lower()

        respect_order = data.get('respect_order', True)
        if isinstance(respect_order, str):
            respect_order = respect_order.lower() == 'true'

        # Récupérer les dates à filtrer
        filter_dates = data.get('filter_dates', [])
        if isinstance(filter_dates, str):
            try:
                filter_dates = json.loads(filter_dates)
            except json.JSONDecodeError:
                filter_dates = [date.strip() for date in filter_dates.split(',') if date.strip()]

        # Récupérer les types de tirage à filtrer
        filter_tirage_types = data.get('filter_tirage_types', [])
        if isinstance(filter_tirage_types, str):
            try:
                filter_tirage_types = json.loads(filter_tirage_types)
            except json.JSONDecodeError:
                filter_tirage_types = [type_tirage.strip() for type_tirage in filter_tirage_types.split(',') if
                                       type_tirage.strip()]

        print(
            f"Paramètres configurés: respect_columns={respect_columns}, min_sequence_length={min_sequence_length}, etc.")

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
        results = analyzer.analyze_csv_file(file_to_analyze)

        # Supprimer le fichier temporaire si nous en avons créé un
        if file and 'temp_file' in locals():
            os.unlink(temp_file.name)
            print("Fichier temporaire supprimé")

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
        # Supprimer le fichier temporaire en cas d'erreur si nous en avons créé un
        if file and 'temp_file' in locals():
            try:
                os.unlink(temp_file.name)
                print("Fichier temporaire supprimé après erreur")
            except:
                pass

        error_details = {
            "error": str(e),
            "traceback": traceback.format_exc()
        }
        print(f"Erreur: {error_details}")
        return jsonify(error_details), 500
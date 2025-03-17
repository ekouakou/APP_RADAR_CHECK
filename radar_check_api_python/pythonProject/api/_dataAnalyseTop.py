from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
import tempfile
import os
import pandas as pd
from datetime import datetime

# Import de votre classe LotoAnalyzer
from myClass._LotoAnalyzer import LotoAnalyzer

app = Flask(__name__)
CORS(app)

# Créer un blueprint pour l'API
api = Blueprint('loto_analyzer_api', __name__)

def format_patterns_for_json(patterns, respect_positions=True):
    """
    Formate les motifs pour JSON en convertissant les tuples en listes
    et en assurant que toutes les clés sont des chaînes de caractères.
    """
    formatted_patterns = {}

    for key, data in patterns.items():
        formatted_counts = {}
        formatted_context = {}

        for group, count in data['counts'].items():
            # Convertir le groupe (tuple) en une représentation JSON-compatible
            if respect_positions and isinstance(group, tuple) and len(group) > 0 and isinstance(group[0], tuple):
                # Groupe avec positions [(col, num), ...]
                group_key = str([{'position': pos, 'value': val} for pos, val in group])
            elif isinstance(group, tuple):
                # Groupe sans positions (num1, num2, ...)
                group_key = str(list(group))
            else:
                group_key = str(group)

            formatted_counts[group_key] = count
            formatted_context[group_key] = data['context'][group]

        formatted_patterns[key] = {
            'counts': formatted_counts,
            'context': formatted_context
        }

    return formatted_patterns

@api.route('/analyze', methods=['POST'])
def analyze_lottery():
    """Point d'entrée API pour l'analyse des tirages de loto."""

    file = None
    file_path = None
    csv_data = None

    try:
        # Gérer différents types de contenu
        if 'application/json' in request.content_type:
            data = request.get_json(silent=True) or {}
            file_path = data.get('file_path')
            csv_data = data.get('csv_data')
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
            analyzer = LotoAnalyzer(csv_file=file_to_analyze)
            print(f"Fichier temporaire créé: {file_to_analyze}")
        # Si nous avons un chemin de fichier via application/json
        elif file_path:
            # Vérifier que le fichier existe
            if not os.path.exists(file_path):
                return jsonify({"error": f"Le fichier '{file_path}' n'existe pas"}), 400
            analyzer = LotoAnalyzer(csv_file=file_path)
            print(f"Utilisation du fichier existant: {file_path}")
        # Si nous avons des données CSV en texte
        elif csv_data:
            analyzer = LotoAnalyzer(data=csv_data)
            print("Utilisation des données CSV fournies en texte")
        else:
            return jsonify({"error": "Aucune source de données fournie (fichier ou données CSV texte)"}), 400

        # Paramètres d'analyse
        # Gestion des types de string vers les types appropriés
        start_date = data.get('start_date', None)
        end_date = data.get('end_date', None)
        tirage_types = data.get('tirage_types', None)
        if tirage_types and isinstance(tirage_types, str):
            tirage_types = tirage_types.split(',')

        search_mode = data.get('search_mode', 'both')
        respect_positions = data.get('respect_positions', 'True').lower() == 'true'

        # Nouveaux paramètres pour la proximité
        consider_proximity = data.get('consider_proximity', 'False').lower() == 'true'
        proximity_threshold = int(data.get('proximity_threshold', 2))

        group_sizes = data.get('group_sizes', [1, 2, 3, 4, 5])
        if isinstance(group_sizes, str):
            try:
                group_sizes = [int(s) for s in group_sizes.split(',')]
            except ValueError:
                return jsonify(
                    {"error": "Format de group_sizes invalide, utilisez des entiers séparés par des virgules"}), 400

        action = data.get('action', 'patterns')

        # Paramètres de pagination
        pagination = data.get('pagination', 'True').lower() == 'true'
        page = int(data.get('page', 1))
        items_per_page = int(data.get('items_per_page', 10))

        # Paramètres pour similar-draws
        draw_line = data.get('draw_line', None)
        similarity_threshold = float(data.get('similarity_threshold', 0.6))

        # Filtrage des données
        filtered_df = analyzer.filter_data(
            start_date=start_date,
            end_date=end_date,
            tirage_types=tirage_types,
            search_mode=search_mode,
            respect_positions=respect_positions
        )

        # Exécution de l'action demandée
        if action == 'patterns':
            results = analyzer.find_patterns_with_context(
                filtered_df,
                search_mode=search_mode,
                group_sizes=group_sizes,
                respect_positions=respect_positions

            )

            # Formater les résultats pour JSON (conversion des tuples en listes, etc.)
            formatted_results = format_patterns_for_json(results, respect_positions)
            return jsonify(formatted_results)

        elif action == 'best-combinations':
            results = analyzer.find_best_combinations(
                filtered_df,
                search_mode=search_mode,
                respect_positions=respect_positions
            )

            # Pagination si demandée
            if pagination:
                total_results = len(results)
                total_pages = (total_results + items_per_page - 1) // items_per_page
                paginated_results = analyzer.paginate_results(results, page, items_per_page)

                # Convertir DataFrame en dictionnaire
                response_data = {
                    'page': page,
                    'total_pages': total_pages,
                    'total_results': total_results,
                    'results': paginated_results.to_dict(orient='records')
                }
            else:
                response_data = {
                    'total_results': len(results),
                    'results': results.to_dict(orient='records')
                }

            return jsonify(response_data)

        elif action == 'similar-draws':
            if not draw_line:
                return jsonify({"error": "Le paramètre draw_line est requis pour l'action similar-draws"}), 400

            results = analyzer.find_similar_draws(
                draw_line,
                filtered_df,
                search_mode=search_mode,
                similarity_threshold=similarity_threshold,
                respect_positions=respect_positions,
                consider_proximity=consider_proximity,
                proximity_threshold=proximity_threshold
            )

            # Pagination si demandée
            if pagination:
                total_results = len(results)
                total_pages = (total_results + items_per_page - 1) // items_per_page
                paginated_results = analyzer.paginate_results(results, page, items_per_page)

                # Convertir DataFrame en dictionnaire
                response_data = {
                    'page': page,
                    'total_pages': total_pages,
                    'total_results': total_results,
                    'results': paginated_results.to_dict(orient='records')
                }
            else:
                response_data = {
                    'total_results': len(results),
                    'results': results.to_dict(orient='records')
                }

            return jsonify(response_data)
        else:
            return jsonify({"error": f"Action '{action}' non reconnue"}), 400

    except Exception as e:
        import traceback
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500

@api.route('/health', methods=['GET'])
def health_check():
    """Point d'entrée API pour vérifier que l'API est opérationnelle."""
    return jsonify({"status": "OK", "message": "L'API LotoAnalyzer est opérationnelle"})


# Enregistrer le blueprint
app.register_blueprint(api, url_prefix='/api/loto')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5002)
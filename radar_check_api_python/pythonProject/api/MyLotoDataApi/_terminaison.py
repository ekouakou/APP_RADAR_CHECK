from flask import Blueprint, request, jsonify
import os
import tempfile
import traceback
import pandas as pd
from datetime import datetime
import json

# Import de votre classe LotteryAnalyzer
# Assurez-vous que le fichier contenant cette classe est dans le même répertoire
from myClass._TerminasonAnalyzer import TerminaisonAnalyzer  # Supposant que votre classe est dans lottery_analyzer.py

# Créer le Blueprint
api = Blueprint('analyse_terminaison_api', __name__)


# Fonction utilitaire pour formater les résultats de patterns pour JSON
def format_patterns_for_json(patterns_results, respect_positions):
    formatted = {}

    for group_size, patterns in patterns_results.items():
        formatted_patterns = []

        for pattern_info in patterns:
            # Conversion des tuples en listes pour la sérialisation JSON
            if respect_positions:
                pattern = pattern_info["pattern"]  # Déjà sous forme de liste dans ce cas
            else:
                pattern = list(pattern_info["pattern"])

            formatted_pattern = {
                "pattern": pattern,
                "occurrences": pattern_info["occurrences"],
                "dates": [d.strftime('%d/%m/%Y') if isinstance(d, datetime) else d for d in pattern_info["dates"]],
                "tirage_types": pattern_info["tirage_types"],
                "next_numbers": pattern_info.get("next_numbers", [])
            }
            formatted_patterns.append(formatted_pattern)

        formatted[str(group_size)] = formatted_patterns

    return formatted


@api.route('/lottery/analyze', methods=['POST'])  # Changé de app.route à api.route et supprimé /api/
def analyze_lottery():
    """Point d'entrée API pour l'analyse des tirages de loterie."""

    file = None
    file_path = None
    csv_data = None
    analyzer = None

    try:
        # Gérer différents types de contenu
        if request.content_type and 'application/json' in request.content_type:
            data = request.get_json(silent=True) or {}
            file_path = data.get('file_path')
            csv_data = data.get('csv_data')
            print(f"Données JSON: {data}")

        elif request.content_type and 'multipart/form-data' in request.content_type:
            # Vérifier tous les noms de champs de fichier possibles
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

        elif request.content_type and 'application/x-www-form-urlencoded' in request.content_type:
            data = request.form.to_dict()
        else:
            data = request.get_json(silent=True) or {}

        # Si nous avons un fichier téléchargé via multipart/form-data
        if file and file.filename:
            # Sauvegarder temporairement le fichier
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
            file.save(temp_file.name)
            temp_file.close()
            analyzer = TerminaisonAnalyzer(csv_file=temp_file.name)
            print(f"Fichier temporaire créé: {temp_file.name}")

        # Si nous avons un chemin de fichier via application/json
        elif file_path:
            # Vérifier que le fichier existe
            if not os.path.exists(file_path):
                return jsonify({"error": f"Le fichier '{file_path}' n'existe pas"}), 400
            analyzer = TerminaisonAnalyzer(csv_file=file_path)
            print(f"Utilisation du fichier existant: {file_path}")

        # Si aucune source de données n'est fournie
        else:
            return jsonify({"error": "Aucune source de données fournie (fichier ou chemin de fichier)"}), 400

        # Paramètres d'analyse
        date_start = data.get('date_start', '01/01/2000')
        date_end = data.get('date_end', datetime.now().strftime('%d/%m/%Y'))
        mode = data.get('mode', 'terminaison')  # terminaison ou commencement
        group_by_draw = data.get('group_by_draw', 'true').lower() == 'true'

        # Action à effectuer
        action = data.get('action', 'analyze')

        # Exécuter l'action demandée
        if action == 'analyze':
            # Analyse simple
            results = analyzer.analyze(date_start, date_end, mode, group_by_draw)

            # Convertir les résultats en format JSON-compatible
            json_results = {"status": "success", "message": "Analyse complétée"}

            # Retourner juste un statut de succès car les résultats sont potentiellement volumineux
            # et sont généralement sauvegardés dans des fichiers
            return jsonify(json_results)

        elif action == 'compare_patterns':
            if not group_by_draw:
                return jsonify({"error": "L'action compare_patterns nécessite group_by_draw=true"}), 400

            # Analyser d'abord les données
            analyzer.analyze(date_start, date_end, mode, group_by_draw=True)

            # Puis comparer les motifs
            comparison = analyzer.compare_patterns()

            # Convertir les résultats en format JSON-compatible
            # Note: Ceci est une simplification, vous pourriez avoir besoin d'adapter cette partie
            # selon la structure exacte de vos données de comparaison
            json_results = {"status": "success", "message": "Comparaison complétée"}

            return jsonify(json_results)

        elif action == 'get_patterns':
            # Analyser d'abord les données
            results = analyzer.analyze(date_start, date_end, mode, group_by_draw)

            # Récupérer les motifs pour chaque groupe
            patterns = {}

            if group_by_draw:
                all_results = results.get('tous_tirages', {})
            else:
                all_results = results

            for groupe, data in all_results.items():
                patterns[groupe] = data.get('motifs', {})

            # Convertir en format JSON-compatible
            json_patterns = {}
            for groupe, motifs in patterns.items():
                json_patterns[str(groupe)] = []
                for motif, count in motifs.items():
                    json_patterns[str(groupe)].append({
                        "motif": list(motif),
                        "occurrences": count
                    })

            return jsonify({"patterns": json_patterns})

        else:
            return jsonify({"error": f"Action '{action}' non reconnue"}), 400

    except Exception as e:
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@api.route('/lottery/save', methods=['POST'])  # Changé de app.route à api.route et supprimé /api/
def save_lottery_results():
    """Point d'entrée API pour sauvegarder les résultats d'analyse."""

    try:
        data = request.get_json(silent=True) or {}
        file_path = data.get('file_path')

        if not file_path:
            return jsonify({"error": "Le chemin du fichier CSV est requis"}), 400

        # Vérifier que le fichier existe
        if not os.path.exists(file_path):
            return jsonify({"error": f"Le fichier '{file_path}' n'existe pas"}), 400

        analyzer = TerminaisonAnalyzer(csv_file=file_path)

        # Paramètres
        date_start = data.get('date_start', '01/01/2000')
        date_end = data.get('date_end', datetime.now().strftime('%d/%m/%Y'))
        mode = data.get('mode', 'terminaison')
        group_by_draw = data.get('group_by_draw', 'true').lower() == 'true'
        base_filename = data.get('base_filename', f"resultats_{mode}")
        comparison_filename = data.get('comparison_filename', f"comparaison_motifs_{mode}")

        # Analyser les données
        results = analyzer.analyze(date_start, date_end, mode, group_by_draw)

        # Sauvegarder les résultats
        analyzer.save_results(base_filename, mode, group_by_draw)

        # Si groupé par tirage, effectuer et sauvegarder la comparaison
        if group_by_draw:
            try:
                comparison = analyzer.compare_patterns()
                analyzer.save_comparison(comparison_filename, mode)
                return jsonify({
                    "status": "success",
                    "message": "Analyse et comparaison sauvegardées",
                    "results_file": f"{base_filename}.csv/.txt",
                    "comparison_file": f"{comparison_filename}.txt"
                })
            except Exception as e:
                return jsonify({
                    "status": "partial_success",
                    "message": f"Analyse sauvegardée, mais erreur lors de la comparaison: {str(e)}",
                    "results_file": f"{base_filename}.csv/.txt"
                })
        else:
            return jsonify({
                "status": "success",
                "message": "Analyse sauvegardée",
                "results_file": f"{base_filename}.csv/.txt"
            })

    except Exception as e:
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@api.route('/lottery/display', methods=['POST'])  # Changé de app.route à api.route et supprimé /api/
def display_lottery_results():
    """Point d'entrée API pour afficher les résultats d'analyse (retourne les résultats au format JSON)."""

    try:
        data = request.get_json(silent=True) or {}
        file_path = data.get('file_path')

        if not file_path:
            return jsonify({"error": "Le chemin du fichier CSV est requis"}), 400

        # Vérifier que le fichier existe
        if not os.path.exists(file_path):
            return jsonify({"error": f"Le fichier '{file_path}' n'existe pas"}), 400

        analyzer = TerminaisonAnalyzer(csv_file=file_path)

        # Paramètres
        date_start = data.get('date_start', '01/01/2000')
        date_end = data.get('date_end', datetime.now().strftime('%d/%m/%Y'))
        mode = data.get('mode', 'terminaison')
        group_by_draw = data.get('group_by_draw', 'true').lower() == 'true'

        # Analyser les données
        results = analyzer.analyze(date_start, date_end, mode, group_by_draw)

        # Au lieu d'afficher les résultats dans la console, retourner les données au format JSON
        # Conversion de résultats en format compatible JSON
        json_results = convert_results_to_json(results, group_by_draw)

        return jsonify(json_results)

    except Exception as e:
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


def convert_results_to_json(results, group_by_draw):
    """Convertit les résultats d'analyse en format compatible JSON."""
    if group_by_draw:
        json_results = {
            "tous_tirages": {},
            "par_tirage": {}
        }

        # Traitement tous_tirages
        for groupe, data in results['tous_tirages'].items():
            json_results["tous_tirages"][str(groupe)] = convert_group_data_to_json(data)

        # Traitement par_tirage
        for tirage_type, tirage_data in results['par_tirage'].items():
            json_results["par_tirage"][tirage_type] = {}
            for groupe, data in tirage_data.items():
                json_results["par_tirage"][tirage_type][str(groupe)] = convert_group_data_to_json(data)
    else:
        json_results = {}
        for groupe, data in results.items():
            json_results[str(groupe)] = convert_group_data_to_json(data)

    return json_results


def convert_group_data_to_json(data):
    """Convertit les données d'un groupe en format compatible JSON."""
    json_data = {
        "numeros_joues": data["numeros_joues"],
        "numeros_joues_uniques": data["numeros_joues_uniques"],
        "nb_numeros_joues": data["nb_numeros_joues"],
        "numeros_non_joues": data["numeros_non_joues"],
        "nb_numeros_non_joues": data["nb_numeros_non_joues"],
        "total_apparitions": data["total_apparitions"],
        "nb_apparitions": data["nb_apparitions"]
    }

    # Conversion des intervalles (qui peuvent contenir des objets datetime)
    json_data["intervalles"] = {}
    for numero, intervals in data["intervalles"].items():
        json_data["intervalles"][str(numero)] = intervals

    # Conversion des motifs (tuples -> listes)
    json_data["motifs"] = {}
    for motif, count in data["motifs"].items():
        json_data["motifs"][str(list(motif))] = count

    return json_data
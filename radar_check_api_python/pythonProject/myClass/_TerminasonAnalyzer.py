import csv
import datetime
import os
from collections import defaultdict, Counter


class TerminaisonAnalyzer:
    def __init__(self, csv_file=None):
        """
        Initialise l'analyseur de loterie.

        Args:
            csv_file (str, optional): Chemin vers le fichier CSV des tirages
        """
        self.csv_file = csv_file
        self.results = None
        self.comparison = None

    def analyze(self, date_start, date_end, mode="terminaison", group_by_draw=False):
        """
        Analyse les numéros de tirage.

        Args:
            date_start (str): Date de début au format DD/MM/YYYY
            date_end (str): Date de fin au format DD/MM/YYYY
            mode (str): "terminaison" pour analyser par dernier chiffre ou "commencement" pour premier chiffre
            group_by_draw (bool): Si True, groupe les résultats par type de tirage

        Returns:
            dict: Résultats de l'analyse
        """
        self.results = self._analyze_numbers(self.csv_file, date_start, date_end, mode, group_by_draw)
        return self.results

    def compare_patterns(self):
        """
        Compare les motifs entre différents types de tirage.

        Returns:
            dict: Résultats de la comparaison
        """
        if not self.results or 'par_tirage' not in self.results:
            raise ValueError("Vous devez d'abord analyser les données avec group_by_draw=True")

        self.comparison = self._compare_patterns_between_draws(self.results)
        return self.comparison

    def save_results(self, base_filename, mode, group_by_draw=False):
        """
        Enregistre les résultats dans des fichiers.

        Args:
            base_filename (str): Nom de base pour les fichiers de sortie
            mode (str): Mode d'analyse ("terminaison" ou "commencement")
            group_by_draw (bool): Si True, les résultats sont groupés par type de tirage
        """
        if not self.results:
            raise ValueError("Aucun résultat à enregistrer, exécutez d'abord analyze()")

        self._save_results(self.results, base_filename, mode, group_by_draw)

    def save_comparison(self, filename, mode):
        """
        Enregistre les résultats de la comparaison dans un fichier.

        Args:
            filename (str): Nom du fichier de sortie
            mode (str): Mode d'analyse ("terminaison" ou "commencement")
        """
        if not self.comparison:
            raise ValueError("Aucune comparaison à enregistrer, exécutez d'abord compare_patterns()")

        self._save_comparison(self.comparison, filename, mode)

    def display_results(self, mode, group_by_draw=False):
        """
        Affiche les résultats de l'analyse.

        Args:
            mode (str): Mode d'analyse ("terminaison" ou "commencement")
            group_by_draw (bool): Si True, les résultats sont groupés par type de tirage
        """
        if not self.results:
            raise ValueError("Aucun résultat à afficher, exécutez d'abord analyze()")

        self._display_results(self.results, mode, group_by_draw)

    def display_comparison(self, mode):
        """
        Affiche les résultats de la comparaison.

        Args:
            mode (str): Mode d'analyse ("terminaison" ou "commencement")
        """
        if not self.comparison:
            raise ValueError("Aucune comparaison à afficher, exécutez d'abord compare_patterns()")

        self._display_comparison(self.comparison, mode)

    # Méthodes privées

    def _find_patterns(self, number_list, min_size=2, max_size=5, min_threshold=2):
        """
        Trouve les motifs récurrents dans une liste de numéros.
        """
        patterns = {}

        if len(number_list) < min_size:
            return patterns

        max_size = min(max_size, len(number_list) // 2)

        for size in range(min_size, max_size + 1):
            sequences = Counter()

            for i in range(len(number_list) - size + 1):
                sequence = tuple(number_list[i:i + size])
                sequences[sequence] += 1

            for sequence, count in sequences.items():
                if count >= min_threshold:
                    patterns[sequence] = count

        return patterns

    def _analyze_numbers(self, csv_file, date_start, date_end, mode="terminaison", group_by_draw=False):
        """
        Analyse les numéros de tirage.
        """
        date_start = datetime.datetime.strptime(date_start, "%d/%m/%Y")
        date_end = datetime.datetime.strptime(date_end, "%d/%m/%Y")

        results_by_draw = defaultdict(lambda: {
            'numeros_par_groupe': defaultdict(list),
            'dates_apparition': defaultdict(list),
            'nb_apparitions': defaultdict(int),
            'apparitions_groupe': Counter()
        })

        all_draws = {
            'numeros_par_groupe': defaultdict(list),
            'dates_apparition': defaultdict(list),
            'nb_apparitions': defaultdict(int),
            'apparitions_groupe': Counter()
        }

        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            headers = next(reader)

            number_columns = []
            draw_type_column = None

            for i, column in enumerate(headers):
                if column.startswith('Num') or column.startswith('Machine'):
                    number_columns.append(i)
                elif column == "Type de Tirage":
                    draw_type_column = i

            for row in reader:
                draw_date = datetime.datetime.strptime(row[0], "%d/%m/%Y")
                draw_type = row[draw_type_column] if draw_type_column is not None else "Inconnu"

                if date_start <= draw_date <= date_end:
                    data_structures = [all_draws]
                    if group_by_draw:
                        data_structures.append(results_by_draw[draw_type])

                    for i in number_columns:
                        if i < len(row) and row[i].strip():
                            try:
                                number = int(row[i])

                                if mode == "terminaison":
                                    group = number % 10
                                else:
                                    group = number // 10 if number >= 10 else 0

                                for data in data_structures:
                                    data['numeros_par_groupe'][group].append(number)
                                    data['dates_apparition'][number].append(draw_date)
                                    data['nb_apparitions'][number] += 1
                                    data['apparitions_groupe'][group] += 1

                            except ValueError:
                                pass

        final_results = {}

        if group_by_draw:
            final_results = {
                'tous_tirages': self._process_results(all_draws, mode),
                'par_tirage': {}
            }
            for draw_type, data in results_by_draw.items():
                final_results['par_tirage'][draw_type] = self._process_results(data, mode)
        else:
            final_results = self._process_results(all_draws, mode)

        return final_results

    def _process_results(self, data, mode):
        """
        Traite les données brutes pour calculer les intervalles et les numéros non joués.
        """
        numeros_par_groupe = data['numeros_par_groupe']
        dates_apparition = data['dates_apparition']
        nb_apparitions = data['nb_apparitions']
        apparitions_groupe = data['apparitions_groupe']

        intervalles = defaultdict(dict)
        for groupe, numeros_liste in numeros_par_groupe.items():
            for numero in set(numeros_liste):
                dates = dates_apparition[numero]
                if len(dates) > 1:
                    intervalles[groupe][numero] = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]

        numeros_non_joues = defaultdict(list)
        max_numero = 90

        if mode == "terminaison":
            for groupe in range(10):
                tous_numeros_possibles = [groupe + 10 * i for i in range(1, 10)]
                for numero in tous_numeros_possibles:
                    if numero not in set(numeros_par_groupe[groupe]) and 1 <= numero <= max_numero:
                        numeros_non_joues[groupe].append(numero)
        else:
            for groupe in range(10):
                tous_numeros_possibles = [groupe * 10 + i for i in range(1, 10)]
                for numero in tous_numeros_possibles:
                    if numero not in set(numeros_par_groupe[groupe]) and 1 <= numero <= max_numero:
                        numeros_non_joues[groupe].append(numero)

        motifs_par_groupe = defaultdict(dict)
        for groupe, numeros_liste in numeros_par_groupe.items():
            motifs_par_groupe[groupe] = self._find_patterns(numeros_liste)

        resultats = {}
        for groupe in range(10):
            resultats[groupe] = {
                "numeros_joues": numeros_par_groupe[groupe],
                "numeros_joues_uniques": list(set(numeros_par_groupe[groupe])),
                "nb_numeros_joues": len(set(numeros_par_groupe[groupe])),
                "intervalles": intervalles[groupe],
                "numeros_non_joues": sorted(numeros_non_joues[groupe]),
                "nb_numeros_non_joues": len(numeros_non_joues[groupe]),
                "nb_apparitions": {num: nb_apparitions[num] for num in set(numeros_par_groupe[groupe])},
                "total_apparitions": apparitions_groupe[groupe],
                "motifs": motifs_par_groupe[groupe]
            }

        return resultats

    def _calculate_summary(self, results):
        """
        Calcule un bilan des groupes les plus fréquents.
        """
        summary = []
        for groupe, data in results.items():
            summary.append({
                "groupe": groupe,
                "total_apparitions": data["total_apparitions"],
                "nb_numeros_joues": data["nb_numeros_joues"],
                "nb_numeros_non_joues": data["nb_numeros_non_joues"],
                "nb_motifs": len(data["motifs"])
            })

        summary.sort(key=lambda x: x["total_apparitions"], reverse=True)
        return summary

    def _save_results(self, results, base_filename, mode, group_by_draw=False):
        """
        Enregistre les résultats dans des fichiers CSV et TXT.
        """
        label = "Terminaison" if mode == "terminaison" else "Commencement"

        if group_by_draw:
            global_summary = self._calculate_summary(results['tous_tirages'])
            self._save_summary_and_details(results['tous_tirages'], global_summary, f"{base_filename}_tous_tirages",
                                           label)

            for draw_type, draw_results in results['par_tirage'].items():
                draw_summary = self._calculate_summary(draw_results)
                formatted_draw_type = draw_type.replace(' ', '_').lower()
                self._save_summary_and_details(draw_results, draw_summary, f"{base_filename}_{formatted_draw_type}",
                                               label, draw_type)
        else:
            summary = self._calculate_summary(results)
            self._save_summary_and_details(results, summary, base_filename, label)

    def _save_summary_and_details(self, results, summary, filename, label, draw_type=None):
        """
        Enregistre le bilan et les détails d'une analyse dans des fichiers CSV et TXT.
        """
        title = f"{label}" + (f" pour {draw_type}" if draw_type else "")

        with open(f"{filename}.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([title, 'Numéros joués', 'Nombre', 'Numéros non joués', 'Nombre', 'Total apparitions',
                             'Nombre de motifs'])

            for groupe in sorted(results.keys()):
                writer.writerow([
                    groupe,
                    str(results[groupe]["numeros_joues"]),
                    results[groupe]["nb_numeros_joues"],
                    str(results[groupe]["numeros_non_joues"]),
                    results[groupe]["nb_numeros_non_joues"],
                    results[groupe]["total_apparitions"],
                    len(results[groupe]["motifs"])
                ])

        with open(f"{filename}.txt", 'w', encoding='utf-8') as f:
            f.write(f"BILAN DES {title.upper()}S PAR NOMBRE D'APPARITIONS:\n")
            f.write("-" * 50 + "\n")
            for i, item in enumerate(summary):
                f.write(f"{i + 1}. {label} {item['groupe']} : {item['total_apparitions']} apparitions "
                        f"({item['nb_numeros_joues']} numéros joués, {item['nb_numeros_non_joues']} non joués, "
                        f"{item['nb_motifs']} motifs)\n")
            f.write("\n\n")

            f.write(f"DÉTAILS PAR {title.upper()}:\n")
            f.write("-" * 50 + "\n\n")
            for groupe in sorted(results.keys()):
                f.write(f"{label} {groupe} (Total: {results[groupe]['total_apparitions']} apparitions):\n")
                f.write(
                    f"  Numéros joués ({results[groupe]['nb_numeros_joues']}): {results[groupe]['numeros_joues']}\n")

                for numero in results[groupe]["numeros_joues_uniques"]:
                    nb_app = results[groupe]['nb_apparitions'][numero]
                    f.write(f"    Numéro {numero} - ({nb_app} apparition{'s' if nb_app > 1 else ''}) - "
                            f"Intervalles entre apparitions (jours): {results[groupe]['intervalles'].get(numero, [])}\n")

                f.write(
                    f"  Numéros non joués ({results[groupe]['nb_numeros_non_joues']}): {results[groupe]['numeros_non_joues']}\n")

                if results[groupe]["motifs"]:
                    f.write(f"  Motifs détectés ({len(results[groupe]['motifs'])}):\n")
                    for motif, occurrences in sorted(results[groupe]["motifs"].items(), key=lambda x: x[1],
                                                     reverse=True):
                        f.write(f"    Motif {motif} - {occurrences} occurrence{'s' if occurrences > 1 else ''}\n")
                    f.write("\n")
                else:
                    f.write("  Aucun motif détecté\n\n")

    def _display_results(self, results, mode, group_by_draw=False):
        """
        Affiche les résultats de l'analyse.
        """
        label = "Terminaison" if mode == "terminaison" else "Commencement"

        if group_by_draw:
            global_summary = self._calculate_summary(results['tous_tirages'])
            self._display_summary_and_details(results['tous_tirages'], global_summary, label, "Tous types de tirages")

            for draw_type, draw_results in results['par_tirage'].items():
                draw_summary = self._calculate_summary(draw_results)
                self._display_summary_and_details(draw_results, draw_summary, label, draw_type)
        else:
            summary = self._calculate_summary(results)
            self._display_summary_and_details(results, summary, label)

    def _display_summary_and_details(self, results, summary, label, draw_type=None):
        """
        Affiche le bilan et les détails d'une analyse.
        """
        title = f"{label}" + (f" pour {draw_type}" if draw_type else "")

        print(f"\nBILAN DES {title.upper()}S PAR NOMBRE D'APPARITIONS:")
        print("-" * 50)
        for i, item in enumerate(summary):
            print(f"{i + 1}. {label} {item['groupe']} : {item['total_apparitions']} apparitions "
                  f"({item['nb_numeros_joues']} numéros joués, {item['nb_numeros_non_joues']} non joués, "
                  f"{item['nb_motifs']} motifs)")

        print(f"\nDÉTAILS PAR GROUPE ({title}):")
        print("-" * 50)
        for groupe in sorted(results.keys()):
            print(f"\n{label} {groupe} (Total: {results[groupe]['total_apparitions']} apparitions):")
            print(f"  Numéros joués ({results[groupe]['nb_numeros_joues']}): {results[groupe]['numeros_joues']}")

            for numero in sorted(results[groupe]["numeros_joues_uniques"]):
                nb_app = results[groupe]['nb_apparitions'][numero]
                print(f"    Numéro {numero} - ({nb_app} apparition{'s' if nb_app > 1 else ''}) - "
                      f"Intervalles entre apparitions (jours): {results[groupe]['intervalles'].get(numero, [])}")

            print(
                f"  Numéros non joués ({results[groupe]['nb_numeros_non_joues']}): {results[groupe]['numeros_non_joues']}")

            if results[groupe]["motifs"]:
                print(f"  Motifs détectés ({len(results[groupe]['motifs'])}):")
                for motif, occurrences in sorted(results[groupe]["motifs"].items(), key=lambda x: x[1], reverse=True):
                    print(f"    Motif {motif} - {occurrences} occurrence{'s' if occurrences > 1 else ''}")
            else:
                print("  Aucun motif détecté")

    def _compare_patterns_between_draws(self, results):
        """
        Compare les motifs entre différents types de tirage et identifie les tendances communes.
        """
        if 'par_tirage' not in results:
            raise ValueError("Les résultats doivent être groupés par type de tirage pour comparer les motifs")

        draw_types = list(results['par_tirage'].keys())
        groups = range(10)

        common_patterns = defaultdict(list)
        exclusive_patterns = {draw_type: defaultdict(list) for draw_type in draw_types}
        recent_trends = defaultdict(dict)
        predictions = defaultdict(dict)

        # 1. Identifier les motifs communs entre types de tirage
        for group in groups:
            all_patterns = {}
            for draw_type in draw_types:
                if group in results['par_tirage'][draw_type]:
                    all_patterns[draw_type] = set(results['par_tirage'][draw_type][group]["motifs"].keys())

            if all_patterns:
                pattern_sets = [patterns for patterns in all_patterns.values() if patterns]
                if pattern_sets:
                    common_set = set.intersection(*pattern_sets)
                    for pattern in common_set:
                        occurrences = {draw_type: results['par_tirage'][draw_type][group]["motifs"][pattern]
                                       for draw_type in draw_types
                                       if group in results['par_tirage'][draw_type] and pattern in
                                       results['par_tirage'][draw_type][group]["motifs"]}

                        common_patterns[group].append({
                            "motif": pattern,
                            "occurrences": occurrences,
                            "occurrences_total": sum(occurrences.values())
                        })

                    common_patterns[group].sort(key=lambda x: x["occurrences_total"], reverse=True)

                    # 2. Identifier les motifs exclusifs à chaque type de tirage
                    for draw_type in draw_types:
                        if group in results['par_tirage'][draw_type]:
                            type_patterns = set(results['par_tirage'][draw_type][group]["motifs"].keys())
                            other_patterns = set()
                            for other_type in draw_types:
                                if other_type != draw_type and group in results['par_tirage'][other_type]:
                                    other_patterns.update(results['par_tirage'][other_type][group]["motifs"].keys())

                            exclusive = type_patterns - other_patterns
                            for pattern in exclusive:
                                exclusive_patterns[draw_type][group].append({
                                    "motif": pattern,
                                    "occurrences": results['par_tirage'][draw_type][group]["motifs"][pattern]
                                })

                            exclusive_patterns[draw_type][group].sort(key=lambda x: x["occurrences"], reverse=True)

        # 3. Analyser les tendances récentes pour chaque groupe
        for group in groups:
            for draw_type in draw_types:
                if group in results['par_tirage'][draw_type]:
                    played_numbers = results['par_tirage'][draw_type][group]["numeros_joues"]
                    recent_numbers = played_numbers[-min(10, len(played_numbers)):]
                    recent_trends[group][draw_type] = recent_numbers

        # 4. Générer des prédictions basées sur les motifs et tendances
        for group in groups:
            if group in common_patterns and common_patterns[group]:
                top_patterns = common_patterns[group][:3]

                for pattern_info in top_patterns:
                    pattern = pattern_info["motif"]
                    if len(pattern) > 0:
                        possible_continuations = []

                        for draw_type in draw_types:
                            if group in results['par_tirage'][draw_type]:
                                numbers = results['par_tirage'][draw_type][group]["numeros_joues"]
                                for i in range(len(numbers) - len(pattern)):
                                    if tuple(numbers[i:i + len(pattern)]) == pattern and i + len(pattern) < len(
                                            numbers):
                                        possible_continuations.append(numbers[i + len(pattern)])

                        if possible_continuations:
                            counter = Counter(possible_continuations)
                            frequent_continuations = counter.most_common(3)

                            predictions[group][str(pattern)] = [
                                {"numero": num, "frequence": freq}
                                for num, freq in frequent_continuations
                            ]

        # 5. Suggestions de combinaisons prometteuses
        promising_combinations = []

        promising_groups = sorted(common_patterns.keys(),
                                  key=lambda g: sum(m["occurrences_total"] for m in common_patterns[g]) if
                                  common_patterns[g] else 0,
                                  reverse=True)[:3]

        for group in promising_groups:
            if common_patterns[group]:
                top_pattern = common_patterns[group][0]["motif"]
                if len(top_pattern) > 0:
                    if group in predictions and str(top_pattern) in predictions[group]:
                        predicted_continuations = [p["numero"] for p in predictions[group][str(top_pattern)]]
                        if predicted_continuations:
                            promising_combinations.append({
                                "groupe": group,
                                "motif": top_pattern,
                                "numeros_suggeres": predicted_continuations
                            })

        return {
            "motifs_communs": common_patterns,
            "motifs_exclusifs": exclusive_patterns,
            "tendances_recentes": recent_trends,
            "predictions": predictions,
            "suggestions_combinaisons": promising_combinations
        }

    def _save_comparison(self, comparison, filename, mode):
        """
        Enregistre les résultats de la comparaison des motifs dans un fichier texte.
        """
        label = "Terminaison" if mode == "terminaison" else "Commencement"

        with open(f"{filename}.txt", 'w', encoding='utf-8') as f:
            f.write(f"ANALYSE COMPARATIVE DES MOTIFS DE {label.upper()}S ENTRE TYPES DE TIRAGE\n")
            f.write("=" * 80 + "\n\n")

            # 1. Motifs communs
            f.write("MOTIFS COMMUNS ENTRE TYPES DE TIRAGE\n")
            f.write("-" * 50 + "\n\n")

            for group in sorted(comparison["motifs_communs"].keys()):
                patterns = comparison["motifs_communs"][group]
                if patterns:
                    f.write(f"{label} {group} - {len(patterns)} motif(s) commun(s):\n")
                    for i, pattern_info in enumerate(patterns, 1):
                        f.write(
                            f"  {i}. Motif {pattern_info['motif']} - Total: {pattern_info['occurrences_total']} occurrences\n")
                        for draw_type, occurrences in pattern_info["occurrences"].items():
                            f.write(f"     - {draw_type}: {occurrences} occurrences\n")
                    f.write("\n")
                else:
                    f.write(f"{label} {group} - Aucun motif commun trouvé\n\n")

            # 2. Motifs exclusifs
            f.write("\nMOTIFS EXCLUSIFS PAR TYPE DE TIRAGE\n")
            f.write("-" * 50 + "\n\n")

            for draw_type, groups_patterns in comparison["motifs_exclusifs"].items():
                f.write(f"Type de tirage: {draw_type}\n")
                for group in sorted(groups_patterns.keys()):
                    patterns = groups_patterns[group]
                    if patterns:
                        f.write(f"  {label} {group} - {len(patterns)} motif(s) exclusif(s):\n")
                        for i, pattern_info in enumerate(patterns[:5], 1):
                            f.write(
                                f"    {i}. Motif {pattern_info['motif']} - {pattern_info['occurrences']} occurrences\n")
                    else:
                        f.write(f"  {label} {group} - Aucun motif exclusif\n")
                f.write("\n")

            # 3. Tendances récentes
            f.write("\nTENDANCES RÉCENTES PAR GROUPE\n")
            f.write("-" * 50 + "\n\n")

            for group in sorted(comparison["tendances_recentes"].keys()):
                f.write(f"{label} {group}:\n")
                for draw_type, recent_numbers in comparison["tendances_recentes"][group].items():
                    f.write(f"  {draw_type} - Derniers numéros: {recent_numbers}\n")
                f.write("\n")

            # 4. Prédictions
            f.write("\nPRÉDICTIONS BASÉES SUR LES MOTIFS\n")
            f.write("-" * 50 + "\n\n")

            for group in sorted(comparison["predictions"].keys()):
                f.write(f"{label} {group}:\n")
                for pattern, continuations in comparison["predictions"][group].items():
                    f.write(f"  Après le motif {pattern}:\n")
                    for continuation in continuations:
                        f.write(f"    - Numéro {continuation['numero']} (fréquence: {continuation['frequence']})\n")
                f.write("\n")

            # 5. Suggestions de combinaisons
            f.write("\nSUGGESTIONS DE COMBINAISONS PROMETTEUSES\n")
            f.write("-" * 50 + "\n\n")

            for i, suggestion in enumerate(comparison["suggestions_combinaisons"], 1):
                f.write(f"Suggestion {i}: Pour {label} {suggestion['groupe']}\n")
                f.write(f"  Basé sur le motif: {suggestion['motif']}\n")
                f.write(f"  Numéros suggérés: {suggestion['numeros_suggeres']}\n\n")

    def _display_comparison(self, comparison, mode):
        """
        Affiche les résultats de la comparaison des motifs.
        """
        label = "Terminaison" if mode == "terminaison" else "Commencement"

        print(f"\nANALYSE COMPARATIVE DES MOTIFS DE {label.upper()}S ENTRE TYPES DE TIRAGE")
        print("=" * 80 + "\n")

        # Afficher les suggestions de combinaisons prometteuses
        print("SUGGESTIONS DE COMBINAISONS PROMETTEUSES")
        print("-" * 50)

        if comparison["suggestions_combinaisons"]:
            for i, suggestion in enumerate(comparison["suggestions_combinaisons"], 1):
                print(f"Suggestion {i}: Pour {label} {suggestion['groupe']}")
                print(f"  Basé sur le motif: {suggestion['motif']}")
                print(f"  Numéros suggérés: {suggestion['numeros_suggeres']}")
                print()
        else:
            print("Aucune suggestion de combinaison n'a pu être générée.\n")

        # Afficher les prédictions
        print("\nPRÉDICTIONS BASÉES SUR LES MOTIFS COMMUNS")
        print("-" * 50)

        if not comparison["predictions"]:
            print("Aucune prédiction n'a pu être générée.\n")
        else:
            for group in sorted(comparison["predictions"].keys()):
                print(f"{label} {group}:")
                for pattern, continuations in comparison["predictions"][group].items():
                    print(f"  Après le motif {pattern}:")
                    for continuation in continuations:
                        print(f"    - Numéro {continuation['numero']} (fréquence: {continuation['frequence']})")
                print()

        # Afficher les motifs communs (résumé)
        print("\nRÉSUMÉ DES MOTIFS COMMUNS LES PLUS FRÉQUENTS")
        print("-" * 50)

        for group in sorted(comparison["motifs_communs"].keys()):
            patterns = comparison["motifs_communs"][group]

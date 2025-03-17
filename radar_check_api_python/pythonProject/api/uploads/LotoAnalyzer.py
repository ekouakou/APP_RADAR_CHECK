import pandas as pd
from datetime import datetime
import re
from collections import Counter, defaultdict
import itertools
import os


class LotoAnalyzer:
    def __init__(self, csv_file=None, data=None):
        """
        Initialise l'analyseur avec un fichier CSV ou des données directes
        """
        if csv_file and os.path.exists(csv_file):
            self.df = pd.read_csv(csv_file, sep=';')
        elif data:
            # Conversion des données texte en DataFrame
            data_lines = [line.strip() for line in data.strip().split('\n')]
            headers = data_lines[0].split(';')
            rows = [line.split(';') for line in data_lines[1:]]
            self.df = pd.DataFrame(rows, columns=headers)
        else:
            raise ValueError("Aucune donnée fournie")

        # Conversion de la colonne Date en datetime
        self.df['Date'] = pd.to_datetime(self.df['Date'], format='%d/%m/%Y', errors='coerce')

        # Création de colonnes pour les numéros et machines
        self.num_columns = [col for col in self.df.columns if re.match(r'Num\d+', col)]
        self.machine_columns = [col for col in self.df.columns if re.match(r'Machine\d+', col)]

        # Conversion des colonnes numériques en entiers
        for col in self.num_columns + self.machine_columns:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')

    def filter_data(self, start_date=None, end_date=None, tirage_types=None, search_mode='both',
                    respect_positions=True):
        """
        Filtre les données selon les paramètres

        Parameters:
        -----------
        start_date : str, optional
            Date de début au format DD/MM/YYYY
        end_date : str, optional
            Date de fin au format DD/MM/YYYY
        tirage_types : list, optional
            Liste des types de tirage à inclure
        search_mode : str, default='both'
            Mode de recherche ('numbers', 'machines', ou 'both')
        respect_positions : bool, default=True
            Si True, respecte les positions des numéros dans les colonnes
        """
        filtered_df = self.df.copy()

        # Filtrage par date
        if start_date:
            start_date = pd.to_datetime(start_date, format='%d/%m/%Y')
            filtered_df = filtered_df[filtered_df['Date'] >= start_date]
        if end_date:
            end_date = pd.to_datetime(end_date, format='%d/%m/%Y')
            filtered_df = filtered_df[filtered_df['Date'] <= end_date]

        # Filtrage par type de tirage (seulement si tirage_types est fourni et non vide)
        if tirage_types and len(tirage_types) > 0:
            filtered_df = filtered_df[filtered_df['Type de Tirage'].isin(tirage_types)]

        return filtered_df

    def find_patterns_with_context(self, filtered_df=None, top_n=10, search_mode='both', group_sizes=[1, 2, 3, 4, 5],
                                   respect_positions=True):
        """
        Identifie les motifs récurrents dans les tirages avec leur contexte (date et type de tirage)

        Parameters:
        -----------
        filtered_df : DataFrame, optional
            Données filtrées à analyser
        top_n : int, default=10
            Nombre de motifs les plus fréquents à retourner
        search_mode : str, default='both'
            Mode de recherche ('numbers', 'machines', ou 'both')
        group_sizes : list of int, default=[1, 2, 3, 4, 5]
            Tailles des groupes de numéros à analyser (1=numéros individuels, 2=paires, etc.)
        respect_positions : bool, default=True
            Si True, respecte les positions des numéros dans les colonnes
        """
        if filtered_df is None:
            filtered_df = self.df

        patterns = {}

        # Sélection des colonnes selon le mode de recherche
        columns_to_analyze = []
        if search_mode in ['numbers', 'both']:
            columns_to_analyze.extend(self.num_columns)
        if search_mode in ['machines', 'both']:
            columns_to_analyze.extend(self.machine_columns)

        # Dictionnaire pour stocker les contextes pour chaque taille de groupe
        group_contexts = {size: defaultdict(list) for size in group_sizes}

        # Analyse des groupes de numéros avec leur contexte
        for idx, row in filtered_df.iterrows():
            date = row['Date'].strftime('%d/%m/%Y')
            tirage_type = row['Type de Tirage']
            context = {'date': date, 'type': tirage_type}

            if respect_positions:
                # Si nous respectons les positions, nous devons conserver les informations de colonne
                position_nums = [(col, row[col]) for col in columns_to_analyze if pd.notna(row[col])]

                # Pour chaque taille de groupe demandée
                for size in group_sizes:
                    if size <= len(position_nums):  # Vérifier qu'il y a assez de numéros
                        for group_indices in itertools.combinations(range(len(position_nums)), size):
                            # Créer un groupe avec les positions et valeurs
                            group = tuple((position_nums[i][0], int(position_nums[i][1])) for i in group_indices)
                            group_contexts[size][group].append(context)
            else:
                # Si nous ne respectons pas les positions, nous traitons juste les valeurs
                nums = row[columns_to_analyze].dropna().astype(int).tolist()

                # Pour chaque taille de groupe demandée
                for size in group_sizes:
                    if size <= len(nums):  # Vérifier qu'il y a assez de numéros
                        for group in itertools.combinations(sorted(nums), size):
                            group_contexts[size][group].append(context)

        # Construction des résultats avec contexte pour chaque taille de groupe
        for size in group_sizes:
            # Compte des occurrences
            group_counts = {group: len(contexts) for group, contexts in group_contexts[size].items()}

            # Tri par occurrences et récupération des top_n
            top_groups = sorted(group_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]

            # Nom de la clé dans le dictionnaire de résultats
            key_name = f'top_group_{size}'

            # Construction des résultats avec contexte
            patterns[key_name] = {
                'counts': dict(top_groups),
                'context': {group: group_contexts[size][group] for group, _ in top_groups}
            }

        return patterns

    def find_best_combinations(self, filtered_df=None, search_mode='both', respect_positions=True):
        """
        Trouve les meilleures combinaisons et leurs particularités

        Parameters:
        -----------
        filtered_df : DataFrame, optional
            Données filtrées à analyser
        search_mode : str, default='both'
            Mode de recherche ('numbers', 'machines', ou 'both')
        respect_positions : bool, default=True
            Si True, respecte les positions des numéros dans les colonnes
        """
        if filtered_df is None:
            filtered_df = self.df

        # Sélection des colonnes selon le mode de recherche
        columns_to_analyze = []
        if search_mode in ['numbers', 'both']:
            columns_to_analyze.extend(self.num_columns)
        if search_mode in ['machines', 'both']:
            columns_to_analyze.extend(self.machine_columns)

        # Statistiques sur les numéros, en tenant compte du respect des positions
        if respect_positions:
            # Créer un dictionnaire pour enregistrer la fréquence de chaque (position, numéro)
            position_number_counts = Counter()
            for idx, row in filtered_df.iterrows():
                for col in columns_to_analyze:
                    if pd.notna(row[col]):
                        position_number_counts[(col, int(row[col]))] += 1

            # Calcul des poids pour chaque tirage
            filtered_df = filtered_df.copy()
            filtered_df['weight'] = 0
            for idx, row in filtered_df.iterrows():
                row_weight = sum(position_number_counts.get((col, int(row[col])), 0)
                                 for col in columns_to_analyze if pd.notna(row[col]))
                filtered_df.at[idx, 'weight'] = row_weight
        else:
            # Statistiques sur les numéros sans tenir compte des positions
            all_numbers = filtered_df[columns_to_analyze].values.flatten()
            number_counts = Counter(all_numbers[~pd.isna(all_numbers)])

            # Calcul des poids pour chaque tirage
            filtered_df = filtered_df.copy()
            filtered_df['weight'] = 0
            for idx, row in filtered_df.iterrows():
                nums = row[columns_to_analyze].dropna().astype(int).tolist()
                row_weight = sum(number_counts[num] for num in nums)
                filtered_df.at[idx, 'weight'] = row_weight

        # Les meilleures combinaisons sont celles avec le poids le plus élevé
        best_combinations = filtered_df.sort_values('weight', ascending=False).head(10)

        return best_combinations

    def find_similar_draws(self, draw_line, filtered_df=None, search_mode='both', similarity_threshold=0.6,
                           respect_positions=True):
        """
        Trouve tous les tirages similaires à une ligne de résultat donnée

        Parameters:
        -----------
        draw_line : str or dict
            Ligne de tirage de référence
        filtered_df : DataFrame, optional
            Données filtrées à analyser
        search_mode : str, default='both'
            Mode de recherche ('numbers', 'machines', ou 'both')
        similarity_threshold : float, default=0.6
            Seuil de similarité entre 0 et 1
        respect_positions : bool, default=True
            Si True, respecte les positions des numéros dans les colonnes
        """
        if filtered_df is None:
            filtered_df = self.df

        # Traitement de la ligne de résultat fournie
        if isinstance(draw_line, str):
            draw_data = draw_line.split(';')
            draw_dict = {col: val for col, val in zip(self.df.columns, draw_data)}
        else:
            draw_dict = draw_line

        # Sélection des colonnes selon le mode de recherche
        columns_to_analyze = []
        if search_mode in ['numbers', 'both']:
            columns_to_analyze.extend(self.num_columns)
        if search_mode in ['machines', 'both']:
            columns_to_analyze.extend(self.machine_columns)

        # Calcul de la similarité pour chaque tirage
        similarities = []

        if respect_positions:
            # Extraction des numéros de la ligne de référence avec leurs positions
            reference_position_numbers = []
            for col in columns_to_analyze:
                if col in draw_dict and draw_dict[col] and pd.notna(draw_dict[col]):
                    reference_position_numbers.append((col, int(draw_dict[col])))

            # Calcul de la similarité en respectant les positions
            for idx, row in filtered_df.iterrows():
                row_position_numbers = [(col, int(row[col])) for col in columns_to_analyze if pd.notna(row[col])]
                common_position_numbers = set(reference_position_numbers).intersection(set(row_position_numbers))
                similarity = len(common_position_numbers) / max(len(reference_position_numbers),
                                                                len(row_position_numbers))
                similarities.append((idx, similarity))
        else:
            # Extraction des numéros de la ligne de référence sans tenir compte des positions
            reference_numbers = []
            for col in columns_to_analyze:
                if col in draw_dict and draw_dict[col] and pd.notna(draw_dict[col]):
                    reference_numbers.append(int(draw_dict[col]))

            # Calcul de la similarité sans tenir compte des positions
            for idx, row in filtered_df.iterrows():
                row_numbers = row[columns_to_analyze].dropna().astype(int).tolist()
                common_numbers = set(reference_numbers).intersection(set(row_numbers))
                similarity = len(common_numbers) / max(len(reference_numbers), len(row_numbers))
                similarities.append((idx, similarity))

        # Filtrage des tirages avec une similarité suffisante
        similar_draws = [(idx, sim) for idx, sim in similarities if sim >= similarity_threshold]
        similar_draws.sort(key=lambda x: x[1], reverse=True)

        # Ajout de la similarité comme colonne
        result_df = filtered_df.loc[[idx for idx, _ in similar_draws]].copy()
        result_df['similarity'] = [sim for _, sim in similar_draws]

        return result_df

    def paginate_results(self, results, page=1, items_per_page=10):
        """
        Pagine les résultats
        """
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        return results.iloc[start_idx:end_idx]


# Fonction d'affichage formaté pour les motifs avec contexte
def print_patterns_with_context(patterns, respect_positions=True):
    print("Motifs récurrents dans les tirages:")

    # Pour chaque taille de groupe dans les patterns
    for key in sorted(patterns.keys()):
        size = int(key.split('_')[-1])  # Extraction de la taille du groupe à partir de la clé

        if size == 1:
            print(f"\n=== TOP NUMÉROS INDIVIDUELS ===")
        else:
            print(f"\n=== TOP GROUPES DE {size} NUMÉROS ===")

        for group, count in patterns[key]['counts'].items():
            if respect_positions and isinstance(group[0], tuple) if group else False:
                # Format d'affichage pour les groupes avec positions
                group_display = ", ".join([f"{col}:{num}" for col, num in group])
                print(f"Groupe [{group_display}]: {count} occurrence(s)")
            else:
                # Format d'affichage pour les groupes sans positions
                print(f"Groupe {group}: {count} occurrence(s)")

            print("  Contextes:")
            for ctx in patterns[key]['context'][group]:
                print(f"    Date: {ctx['date']}, Type: {ctx['type']}")


# Exemple d'utilisation directe avec paramètres intégrés
def run_analysis():
    # Définition des paramètres d'analyse directement dans le code
    params = {
        # Source des données (choisir l'une des options)
        'csv_file': 'formatted_lottery_results.csv',  # Chemin vers le fichier CSV
        # Filtres
        'start_date': '01/01/2020',  # Format DD/MM/YYYY
        'end_date': '31/12/2020',  # Format DD/MM/YYYY
        'tirage_types': None,  # Liste des types de tirage à analyser ou None pour tous les types
        'search_mode': 'both',  # 'numbers', 'machines', ou 'both'

        # Tailles des groupes à analyser
        'group_sizes': [1, 2, 3, 4, 5,6],  # [1]=numéros individuels, [2]=paires, etc.

        # Paramètres de pagination
        'pagination': True,
        'page': 1,
        'items_per_page': 10,
        'respect_positions': True,  # True pour respecter les positions, False sinon

        # Pour rechercher des tirages similaires
        'draw_line': '05/10/2020;Monday;octobre 2020;Reveil;88;42;76;74;45;49;81;56;16;73',
        'similarity_threshold': 0.6,  # Seuil de similarité entre 0 et 1

        # Action à effectuer
        'action': 'patterns'  # 'patterns', 'best-combinations', ou 'similar-draws'
    }

    # Initialisation de l'analyseur
    # Si vous avez un fichier CSV, utilisez:
    analyzer = LotoAnalyzer(csv_file=params['csv_file'])
    # Sinon, pour les données intégrées:

    # Filtrage des données
    filtered_df = analyzer.filter_data(
        start_date=params['start_date'],
        end_date=params['end_date'],
        tirage_types=params['tirage_types'],
        search_mode=params['search_mode'],
        respect_positions=params['respect_positions']  # Ajout du nouveau paramètre

    )

    # Exécution de l'action demandée
    if params['action'] == 'patterns':
        results = analyzer.find_patterns_with_context(
            filtered_df,
            search_mode=params['search_mode'],
            group_sizes=params['group_sizes'],
            respect_positions=params['respect_positions']  # Ajout du nouveau paramètre

        )
        print_patterns_with_context(results)
        return results

    elif params['action'] == 'best-combinations':
        results = analyzer.find_best_combinations(filtered_df, search_mode=params['search_mode'])
        if params['pagination']:
            results = analyzer.paginate_results(results, params['page'], params['items_per_page'])
        print("Meilleures combinaisons:")
        print(results)
        return results

    elif params['action'] == 'similar-draws':
        results = analyzer.find_similar_draws(
            params['draw_line'],
            filtered_df,
            search_mode=params['search_mode'],
            similarity_threshold=params['similarity_threshold']
        )
        if params['pagination']:
            results = analyzer.paginate_results(results, params['page'], params['items_per_page'])
        print("Tirages similaires:")
        print(results)
        return results


if __name__ == "__main__":
    # Exécution de l'analyse avec les paramètres définis
    results = run_analysis()
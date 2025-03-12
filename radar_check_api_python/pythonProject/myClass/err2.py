import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Dict, Union, Optional
from tqdm import tqdm
from collections import defaultdict


class ProgressRegressConstantesClass:
    """
    Classe d'analyse de séquences constantes dans les résultats de loterie.
    Optimisée pour de meilleures performances.
    """

    def __init__(self):
        self.df = None
        self.num_cols = ['Num1', 'Num2', 'Num3', 'Num4', 'Num5']
        self.machine_cols = ['Machine1', 'Machine2', 'Machine3', 'Machine4', 'Machine5']

    def load_data(self, csv_file: str) -> bool:
        """
        Charge les données à partir d'un fichier CSV.
        Optimisée pour utiliser dtypes dès le chargement.
        """
        try:
            # Définition des types de colonnes pour optimiser le chargement
            dtype_dict = {}
            for col in self.num_cols + self.machine_cols:
                dtype_dict[col] = 'Int64'

            # Utilisation de la fonction read_csv avec les types définis
            self.df = pd.read_csv(
                csv_file,
                sep=';',
                parse_dates=['Date'],
                dayfirst=True,
                dtype=dtype_dict,
                low_memory=False
            )
            return True
        except FileNotFoundError:
            print("Fichier CSV non trouvé.")
            return False
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier CSV: {e}")
            return False

    def _filter_empty_results(self, results: Dict) -> Dict:
        """
        Filtre les résultats pour ne conserver que les données non vides.
        Version optimisée avec moins de récursions.
        """
        if not isinstance(results, dict):
            return results

        filtered_results = {}
        for key, value in results.items():
            if isinstance(value, dict):
                filtered_value = self._filter_empty_results(value)
                if filtered_value:
                    filtered_results[key] = filtered_value
            elif isinstance(value, list) and value:
                filtered_results[key] = value
            elif value or value == 0:  # Garde les valeurs non vides y compris 0
                filtered_results[key] = value

        # Cas spécial pour les dictionnaires contenant "progressions_constantes" et "regressions_constantes"
        if 'progressions_constantes' in results and 'regressions_constantes' in results:
            if not results['progressions_constantes'] and not results['regressions_constantes']:
                return {}

        return filtered_results

    def filter_data(self,
                    date_debut: Optional[str] = None,
                    date_fin: Optional[str] = None,
                    type_tirage: Optional[Union[str, List[str]]] = None,
                    reverse_order: bool = False) -> bool:
        """
        Filtre les données selon les critères spécifiés.
        Optimisée pour utiliser des masques vectorisés.
        """
        if self.df is None:
            print("Aucune donnée chargée. Utilisez load_data() d'abord.")
            return False

        # Création d'une copie optimisée (shallow copy)
        df_filtered = self.df.copy(deep=False)

        # Inversion de l'ordre si nécessaire
        if reverse_order:
            df_filtered = df_filtered.iloc[::-1].reset_index(drop=True)

        # Application des filtres de dates avec des masques
        mask = pd.Series(True, index=df_filtered.index)

        if date_debut:
            try:
                date_debut_dt = datetime.strptime(date_debut, '%d/%m/%Y')
                mask &= df_filtered['Date'] >= date_debut_dt
            except ValueError:
                print("Format de date de début incorrect. Utilisez DD/MM/YYYY.")
                return False

        if date_fin:
            try:
                date_fin_dt = datetime.strptime(date_fin, '%d/%m/%Y')
                mask &= df_filtered['Date'] <= date_fin_dt
            except ValueError:
                print("Format de date de fin incorrect. Utilisez DD/MM/YYYY.")
                return False

        # Application du filtre de type de tirage
        if type_tirage:
            if isinstance(type_tirage, list):
                mask &= df_filtered['Type de Tirage'].isin(type_tirage)
            else:
                mask &= df_filtered['Type de Tirage'] == type_tirage

        # Application du masque final
        df_filtered = df_filtered[mask]

        if df_filtered.empty:
            print("Aucun tirage ne correspond aux critères spécifiés.")
            return False

        self.df = df_filtered
        return True

    def analyser_progression_constante(self,
                                       longueur_min: int = 3,
                                       type_analyse: Optional[str] = None,
                                       respecter_position: bool = True,
                                       analyser_meme_ligne: bool = False,
                                       fusionner_num_machine: bool = False,
                                       utiliser_longueur_min: bool = True,
                                       reverse_order: bool = False) -> Dict:
        """
        Analyse les progressions constantes dans les données.
        Optimisée pour éviter les duplications de code.
        """
        if self.df is None:
            return {"error": "Aucune donnée chargée. Utilisez load_data() d'abord."}

        resultats = {}
        # Extraire seulement les colonnes nécessaires pour optimiser la mémoire
        df_analyse = self.df[['Date', 'Type de Tirage'] + self.num_cols + self.machine_cols].copy()

        # Convertir toutes les colonnes numériques en une seule fois pour éviter les boucles
        cols_to_convert = self.num_cols + self.machine_cols
        for col in cols_to_convert:
            if col in df_analyse.columns:
                df_analyse[col] = pd.to_numeric(df_analyse[col], errors='coerce').astype('Int64')

        # Déterminer les colonnes à analyser
        if fusionner_num_machine:
            colonnes = self.num_cols + self.machine_cols
            analyser_func = self._analyser_sequences_sans_position if not respecter_position else self._analyser_sequences_constantes
            resultats['num_et_machine'] = analyser_func(df_analyse, colonnes, longueur_min, type_analyse,
                                                        analyser_meme_ligne, utiliser_longueur_min, reverse_order)
        else:
            analyser_func = self._analyser_sequences_sans_position if not respecter_position else self._analyser_sequences_constantes
            resultats['num'] = analyser_func(df_analyse, self.num_cols, longueur_min, type_analyse,
                                             analyser_meme_ligne, utiliser_longueur_min, reverse_order)
            resultats['machine'] = analyser_func(df_analyse, self.machine_cols, longueur_min, type_analyse,
                                                 analyser_meme_ligne, utiliser_longueur_min, reverse_order)

        # Filtrer les résultats vides avant de les retourner
        return self._filter_empty_results(resultats)

    def save_results(self, resultats: Dict, output_file: str) -> bool:
        """
        Enregistre les résultats dans un fichier JSON.
        """
        try:
            # Filtrer les résultats vides avant de les enregistrer
            filtered_results = self._filter_empty_results(resultats)

            # Écriture directe pour éviter de charger tout en mémoire
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(filtered_results, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erreur lors de l'enregistrement dans le fichier : {e}")
            return False

    def _analyser_sequences_constantes(self,
                                       df: pd.DataFrame,
                                       colonnes: List[str],
                                       longueur_min: int = 3,
                                       type_analyse: Optional[str] = None,
                                       analyser_meme_ligne: bool = False,
                                       utiliser_longueur_min: bool = True,
                                       reverse_order: bool = False) -> Dict:
        """
        Analyse les séquences constantes par position.
        Version optimisée avec meilleure gestion de mémoire.
        """
        resultats = {}
        all_types_data = {}

        # Analyse sur même ligne si demandé
        if analyser_meme_ligne:
            all_types_data['Même ligne'] = self._analyser_meme_ligne_progressions(df, colonnes, longueur_min,
                                                                                  type_analyse, utiliser_longueur_min)

        # Analyse par position pour tous les types de tirage
        all_types_data = {}
        for position, colonne in enumerate(tqdm(colonnes, desc="Analyse par position")):
            all_types_data[f'Position {position + 1}'] = self._trouver_sequences_constantes(df, colonne,
                                                                                            longueur_min,
                                                                                            type_analyse,
                                                                                            utiliser_longueur_min,
                                                                                            reverse_order)

        resultats['tous_types'] = all_types_data

        # Analyse par type de tirage
        types_tirages = df['Type de Tirage'].unique()
        for type_tirage in types_tirages:
            df_type = df[df['Type de Tirage'] == type_tirage]
            if not utiliser_longueur_min or len(df_type) >= longueur_min:
                type_data = {}

                if analyser_meme_ligne:
                    type_data['Même ligne'] = self._analyser_meme_ligne_progressions(df_type, colonnes, longueur_min,
                                                                                     type_analyse,
                                                                                     utiliser_longueur_min)

                for position, colonne in enumerate(tqdm(colonnes, desc=f"Analyse par position ({type_tirage})")):
                    type_data[f'Position {position + 1}'] = self._trouver_sequences_constantes(df_type, colonne,
                                                                                               longueur_min,
                                                                                               type_analyse,
                                                                                               utiliser_longueur_min,
                                                                                               reverse_order)
                resultats[type_tirage] = type_data

        return resultats

    def _trouver_sequences_constantes(self,
                                      df: pd.DataFrame,
                                      colonne: str,
                                      longueur_min: int = 3,
                                      type_analyse: Optional[str] = None,
                                      utiliser_longueur_min: bool = True,
                                      reverse_order: bool = False) -> Dict:
        """
        Trouve les séquences de progression/régression constante dans une colonne spécifique.
        Version optimisée pour le traitement vectoriel.
        """
        # Tri du DataFrame en fonction de la date
        df = df.sort_values(by='Date', ascending=not reverse_order)

        # Conversion et préparation des données
        # On utilise np.array pour accélérer les calculs
        valeurs = df[colonne].to_numpy()
        dates = df['Date'].to_numpy()
        types_tirages = df['Type de Tirage'].to_numpy()

        # Calcul des différences entre valeurs consécutives
        differences = np.diff(valeurs)

        # Initialisation des listes pour stocker les séquences
        progressions_constantes = []
        regressions_constantes = []

        # Recherche des séquences
        i = 0
        while i < len(valeurs) - 1:
            # Si la différence est nulle, passer à la valeur suivante
            if differences[i] == 0:
                i += 1
                continue

            # Initialiser la séquence courante
            diff_constante = differences[i]
            sequence_courante = [valeurs[i]]
            sequence_dates = [dates[i]]
            sequence_types = [types_tirages[i]]

            # Trouver la longueur de la séquence
            j = i
            while j < len(differences) and differences[j] == diff_constante:
                sequence_courante.append(valeurs[j + 1])
                sequence_dates.append(dates[j + 1])
                sequence_types.append(types_tirages[j + 1])
                j += 1

            # Appliquer le filtre de longueur
            if not utiliser_longueur_min or len(sequence_courante) >= longueur_min:
                sequence_info = {
                    'valeurs': sequence_courante.copy(),
                    'difference': int(diff_constante),  # Convertir en int pour JSON
                    'longueur': len(sequence_courante),
                    'dates': [date.strftime('%d/%m/%Y') for date in sequence_dates],
                    'types': sequence_types.tolist(),  # Convertir numpy array en liste
                    'colonne': colonne
                }

                # Ajouter à la liste appropriée
                if diff_constante > 0:
                    progressions_constantes.append(sequence_info)
                else:
                    regressions_constantes.append(sequence_info)

            # Passer à la prochaine séquence
            i = j

        # Trier les séquences par longueur
        progressions_constantes.sort(key=lambda x: x['longueur'], reverse=True)
        regressions_constantes.sort(key=lambda x: x['longueur'], reverse=True)

        # Retourner les résultats selon le type d'analyse
        if type_analyse == 'progression':
            return {
                'progressions_constantes': progressions_constantes,
                'regressions_constantes': []
            }
        elif type_analyse == 'regression':
            return {
                'progressions_constantes': [],
                'regressions_constantes': regressions_constantes
            }
        else:
            return {
                'progressions_constantes': progressions_constantes,
                'regressions_constantes': regressions_constantes
            }

    def _analyser_meme_ligne_progressions(self,
                                          df: pd.DataFrame,
                                          colonnes: List[str],
                                          longueur_min: int = 3,
                                          type_analyse: Optional[str] = None,
                                          utiliser_longueur_min: bool = True) -> Dict:
        """
        Analyse les progressions sur une même ligne de tirage.
        Version optimisée avec traitement vectoriel.
        """
        progressions_constantes = []
        regressions_constantes = []

        # Convertir toutes les colonnes en une fois
        for col in colonnes:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

        # Utiliser apply au lieu d'itérer sur chaque ligne
        df_values = df[colonnes].values

        for idx, row in tqdm(df.iterrows(), total=len(df), desc="Analyse des lignes"):
            valeurs = row[colonnes].values
            date = row['Date'].strftime('%d/%m/%Y')
            type_tirage = row['Type de Tirage']

            i = 0
            while i < len(valeurs) - 1:
                # Initialiser la séquence
                diff_constante = valeurs[i + 1] - valeurs[i]

                # Ignorer les différences nulles
                if diff_constante == 0:
                    i += 1
                    continue

                # Trouver la longueur de la séquence
                sequence_courante = [valeurs[i]]
                j = i + 1

                while j < len(valeurs) and valeurs[j] - valeurs[j - 1] == diff_constante:
                    sequence_courante.append(valeurs[j])
                    j += 1

                # Appliquer le filtre de longueur
                if not utiliser_longueur_min or len(sequence_courante) >= longueur_min:
                    sequence_info = {
                        'valeurs': sequence_courante,
                        'difference': int(diff_constante),
                        'longueur': len(sequence_courante),
                        'dates': [date] * len(sequence_courante),
                        'types': [type_tirage] * len(sequence_courante),
                        'colonnes': colonnes[i:i + len(sequence_courante)]
                    }

                    if diff_constante > 0:
                        progressions_constantes.append(sequence_info)
                    else:
                        regressions_constantes.append(sequence_info)

                # Passer à la position suivante
                i = j

        # Trier les séquences
        progressions_constantes.sort(key=lambda x: x['longueur'], reverse=True)
        regressions_constantes.sort(key=lambda x: x['longueur'], reverse=True)

        # Retourner les résultats selon le type d'analyse
        if type_analyse == 'progression':
            return {
                'progressions_constantes': progressions_constantes,
                'regressions_constantes': []
            }
        elif type_analyse == 'regression':
            return {
                'progressions_constantes': [],
                'regressions_constantes': regressions_constantes
            }
        else:
            return {
                'progressions_constantes': progressions_constantes,
                'regressions_constantes': regressions_constantes
            }

    def _analyser_sequences_sans_position(self,
                                          df: pd.DataFrame,
                                          colonnes: List[str],
                                          longueur_min: int = 3,
                                          type_analyse: Optional[str] = None,
                                          analyser_meme_ligne: bool = False,
                                          utiliser_longueur_min: bool = True,
                                          reverse_order: bool = False) -> Dict:
        """
        Analyse les séquences sans tenir compte des positions.
        Version optimisée.
        """
        resultats = {}
        all_types_data = {}

        if analyser_meme_ligne:
            all_types_data['Même ligne'] = self._analyser_meme_ligne_progressions(df, colonnes, longueur_min,
                                                                                  type_analyse, utiliser_longueur_min)

        all_types_data['Toutes positions'] = self._trouver_sequences_sans_position(df, colonnes, longueur_min,
                                                                                   type_analyse, utiliser_longueur_min,
                                                                                   reverse_order)

        resultats['tous_types'] = all_types_data

        # Analyse par type de tirage en utilisant un groupby
        types_tirages = df['Type de Tirage'].unique()

        for type_tirage in types_tirages:
            df_type = df[df['Type de Tirage'] == type_tirage]
            if not utiliser_longueur_min or len(df_type) >= longueur_min:
                type_data = {}

                if analyser_meme_ligne:
                    type_data['Même ligne'] = self._analyser_meme_ligne_progressions(df_type, colonnes, longueur_min,
                                                                                     type_analyse,
                                                                                     utiliser_longueur_min)

                type_data['Toutes positions'] = self._trouver_sequences_sans_position(df_type, colonnes, longueur_min,
                                                                                      type_analyse,
                                                                                      utiliser_longueur_min,
                                                                                      reverse_order)

                resultats[type_tirage] = type_data

        return resultats

    def _trouver_sequences_sans_position(self,
                                         df: pd.DataFrame,
                                         colonnes: List[str],
                                         longueur_min: int = 3,
                                         type_analyse: Optional[str] = None,
                                         utiliser_longueur_min: bool = True,
                                         reverse_order: bool = False) -> Dict:
        """
        Trouve les séquences sans tenir compte des positions.
        Version optimisée avec HashMap pour accélérer les recherches.
        """
        # Convertir les colonnes en entiers
        for col in colonnes:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

        # Tri du DataFrame par date
        df = df.sort_values(by='Date', ascending=not reverse_order)

        # Restructuration des données pour un accès plus rapide
        sequence_data = []
        for idx, row in df.iterrows():
            date = row['Date']
            type_tirage = row['Type de Tirage']
            numeros = [{'numero': row[col], 'colonne': col, 'date': date, 'type': type_tirage} for col in colonnes]
            sequence_data.append({'date': date, 'type': type_tirage, 'numeros': numeros})

        # Optimisation: créer un dictionnaire des numéros par valeur
        # Structure: {valeur: [{'numero': val, 'colonne': col, 'date': date, 'type': type}, ...]}
        numero_par_valeur = defaultdict(list)
        for data in sequence_data:
            for num in data['numeros']:
                numero_par_valeur[num['numero']].append(num)

        # Structure de données pour suivre les séquences
        sequences_constantes = []
        sequences_vues = set()

        # Analyse des séquences
        for i, data_i in enumerate(tqdm(sequence_data, desc="Recherche des séquences")):
            for num_i in data_i['numeros']:
                valeur_i = num_i['numero']
                date_i = num_i['date']

                # Trouver toutes les différences potentielles
                for valeur_j in numero_par_valeur.keys():
                    diff = valeur_j - valeur_i
                    if diff == 0:
                        continue

                    # Vérifier s'il existe une séquence avec cette différence
                    sequence_courante = [num_i]
                    valeur_courante = valeur_i
                    date_courante = date_i

                    # Boucle pour trouver les membres suivants de la séquence
                    while True:
                        valeur_suivante = valeur_courante + diff
                        candidats = [n for n in numero_par_valeur.get(valeur_suivante, [])
                                     if (not reverse_order and n['date'] > date_courante) or
                                     (reverse_order and n['date'] < date_courante)]

                        if not candidats:
                            break

                        # Prendre le candidat avec la date la plus proche
                        if reverse_order:
                            candidat = max(candidats, key=lambda x: x['date'])
                        else:
                            candidat = min(candidats, key=lambda x: x['date'])

                        sequence_courante.append(candidat)
                        valeur_courante = valeur_suivante
                        date_courante = candidat['date']

                    # Vérifier si la séquence est assez longue
                    if not utiliser_longueur_min or len(sequence_courante) >= longueur_min:
                        # Créer un identifiant unique pour cette séquence
                        valeurs = tuple(item['numero'] for item in sequence_courante)
                        dates = tuple(item['date'].strftime('%d/%m/%Y') for item in sequence_courante)
                        sequence_id = (valeurs, dates, diff)

                        if sequence_id not in sequences_vues:
                            sequences_vues.add(sequence_id)

                            sequences_constantes.append({
                                'valeurs': list(valeurs),
                                'colonnes': [item['colonne'] for item in sequence_courante],
                                'difference': diff,
                                'longueur': len(sequence_courante),
                                'dates': [item['date'].strftime('%d/%m/%Y') for item in sequence_courante],
                                'types': [item['type'] for item in sequence_courante]
                            })

        # Séparer et trier les séquences
        progressions_constantes = [seq for seq in sequences_constantes if seq['difference'] > 0]
        regressions_constantes = [seq for seq in sequences_constantes if seq['difference'] < 0]

        progressions_constantes.sort(key=lambda x: x['longueur'], reverse=True)
        regressions_constantes.sort(key=lambda x: x['longueur'], reverse=True)

        # Retourner selon le type d'analyse
        if type_analyse == 'progression':
            return {
                'progressions_constantes': progressions_constantes,
                'regressions_constantes': []
            }
        elif type_analyse == 'regression':
            return {
                'progressions_constantes': [],
                'regressions_constantes': regressions_constantes
            }
        else:
            return {
                'progressions_constantes': progressions_constantes,
                'regressions_constantes': regressions_constantes
            }
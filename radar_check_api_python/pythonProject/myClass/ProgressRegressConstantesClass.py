import json
import pandas as pd
from datetime import datetime
import sys
from typing import List, Dict, Union, Optional
from tqdm import tqdm
from collections import defaultdict
import numpy as np


class ProgressRegressConstantesClass:
    """
    Classe d'analyse de séquences constantes dans les résultats de loterie.
    """

    def __init__(self):
        self.df = None
        self.num_cols = ['Num1', 'Num2', 'Num3', 'Num4', 'Num5']
        self.machine_cols = ['Machine1', 'Machine2', 'Machine3', 'Machine4', 'Machine5']

    def load_data(self, csv_file: str) -> bool:
        """
        Charge les données à partir d'un fichier CSV.

        Args:
            csv_file: Chemin vers le fichier CSV des résultats de loterie

        Returns:
            bool: True si le chargement a réussi, False sinon
        """
        try:
            self.df = pd.read_csv(csv_file, sep=';', parse_dates=['Date'], dayfirst=True, low_memory=False)

            # Convertir les colonnes numériques
            colonnes_numeriques = self.num_cols + self.machine_cols
            for col in colonnes_numeriques:
                if col in self.df.columns:
                    try:
                        self.df[col] = pd.to_numeric(self.df[col], errors='raise').astype('Int64')
                    except ValueError as e:
                        print(f"Erreur de conversion de type pour la colonne {col}: {e}")
                        return False
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

        Args:
            results: Dictionnaire des résultats à filtrer

        Returns:
            Dict: Résultats filtrés sans les entrées vides
        """
        if isinstance(results, dict):
            filtered_results = {}
            for key, value in results.items():
                if isinstance(value, dict):
                    # Récursion pour les dictionnaires imbriqués
                    filtered_value = self._filter_empty_results(value)
                    if filtered_value:  # Ne pas ajouter les dictionnaires vides
                        filtered_results[key] = filtered_value
                elif isinstance(value, list):
                    # Pour les listes, vérifie si elles sont non vides
                    if value:
                        filtered_results[key] = value
                else:
                    # Pour les autres types, les ajoute directement
                    filtered_results[key] = value

            # Cas spécial pour les dictionnaires contenant "progressions_constantes" et "regressions_constantes"
            if 'progressions_constantes' in results and 'regressions_constantes' in results:
                if not results['progressions_constantes'] and not results['regressions_constantes']:
                    return {}  # Retourne un dictionnaire vide si les deux listes sont vides

            return filtered_results
        return results

    def filter_data(self,
                    date_debut: Optional[str] = None,
                    date_fin: Optional[str] = None,
                    type_tirage: Optional[Union[str, List[str]]] = None,
                    reverse_order: bool = False) -> bool:
        """
        Filtre les données selon les critères spécifiés.

        Args:
            date_debut: Date de début au format DD/MM/YYYY
            date_fin: Date de fin au format DD/MM/YYYY
            type_tirage: Type de tirage à filtrer, peut être une chaîne ou une liste de chaînes
            reverse_order: Si True, inverse l'ordre des tirages

        Returns:
            bool: True si le filtrage a réussi, False sinon
        """
        if self.df is None:
            print("Aucune donnée chargée. Utilisez load_data() d'abord.")
            return False

        df_filtered = self.df.copy()

        if reverse_order:
            df_filtered = df_filtered.iloc[::-1].copy()

        if date_debut:
            try:
                date_debut_dt = datetime.strptime(date_debut, '%d/%m/%Y')
                df_filtered = df_filtered[df_filtered['Date'] >= date_debut_dt]
            except ValueError:
                print("Format de date de début incorrect. Utilisez DD/MM/YYYY.")
                return False

        if date_fin:
            try:
                date_fin_dt = datetime.strptime(date_fin, '%d/%m/%Y')
                df_filtered = df_filtered[df_filtered['Date'] <= date_fin_dt]
            except ValueError:
                print("Format de date de fin incorrect. Utilisez DD/MM/YYYY.")
                return False

        if type_tirage:
            if isinstance(type_tirage, list):
                # Filtrer par une liste de types de tirage
                df_filtered = df_filtered[df_filtered['Type de Tirage'].isin(type_tirage)]
            else:
                # Filtrer par un seul type de tirage
                df_filtered = df_filtered[df_filtered['Type de Tirage'] == type_tirage]

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

        Args:
            longueur_min: Longueur minimale des séquences à rechercher
            type_analyse: Type d'analyse ('progression', 'regression', ou None pour les deux)
            respecter_position: Si True, analyse par position, sinon sans tenir compte des positions
            analyser_meme_ligne: Si True, analyse les progressions sur une même ligne
            fusionner_num_machine: Si True, analyse les numéros et machines ensemble
            utiliser_longueur_min: Si True, applique le filtre de longueur minimum
            reverse_order: Si True, analyse dans l'ordre inverse

        Returns:
            Dict: Résultats de l'analyse
        """
        if self.df is None:
            return {"error": "Aucune donnée chargée. Utilisez load_data() d'abord."}

        resultats = {}

        df_analyse = self.df[['Date', 'Type de Tirage'] + self.num_cols + self.machine_cols].copy()

        if fusionner_num_machine:
            colonnes = self.num_cols + self.machine_cols
            if respecter_position:
                resultats['num_et_machine'] = self._analyser_sequences_constantes(df_analyse, colonnes, longueur_min,
                                                                                  type_analyse, analyser_meme_ligne,
                                                                                  utiliser_longueur_min, reverse_order)
            else:
                resultats['num_et_machine'] = self._analyser_sequences_sans_position(df_analyse, colonnes, longueur_min,
                                                                                     type_analyse, analyser_meme_ligne,
                                                                                     utiliser_longueur_min,
                                                                                     reverse_order)
        else:
            if respecter_position:
                resultats['num'] = self._analyser_sequences_constantes(df_analyse, self.num_cols, longueur_min,
                                                                       type_analyse,
                                                                       analyser_meme_ligne, utiliser_longueur_min,
                                                                       reverse_order)
                resultats['machine'] = self._analyser_sequences_constantes(df_analyse, self.machine_cols, longueur_min,
                                                                           type_analyse, analyser_meme_ligne,
                                                                           utiliser_longueur_min, reverse_order)
            else:
                resultats['num'] = self._analyser_sequences_sans_position(df_analyse, self.num_cols, longueur_min,
                                                                          type_analyse,
                                                                          analyser_meme_ligne, utiliser_longueur_min,
                                                                          reverse_order)
                resultats['machine'] = self._analyser_sequences_sans_position(df_analyse, self.machine_cols,
                                                                              longueur_min,
                                                                              type_analyse, analyser_meme_ligne,
                                                                              utiliser_longueur_min, reverse_order)

        # Filtrer les résultats vides avant de les retourner
        return self._filter_empty_results(resultats)

    def save_results(self, resultats: Dict, output_file: str) -> bool:
        """
        Enregistre les résultats dans un fichier JSON.

        Args:
            resultats: Dictionnaire des résultats
            output_file: Chemin du fichier de sortie

        Returns:
            bool: True si l'enregistrement a réussi, False sinon
        """
        try:
            # Filtrer les résultats vides avant de les enregistrer
            filtered_results = self._filter_empty_results(resultats)

            json_output = json.dumps(filtered_results, indent=4, ensure_ascii=False)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(json_output)
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
        """
        resultats = {}
        all_types_data = {}

        if analyser_meme_ligne:
            all_types_data['Même ligne'] = self._analyser_meme_ligne_progressions(df, colonnes, longueur_min,
                                                                                  type_analyse, utiliser_longueur_min)

        all_types_data = {}
        with tqdm(colonnes, desc="Analyse par position") as pbar:
            for position, colonne in enumerate(pbar):
                all_types_data[f'Position {position + 1}'] = self._trouver_sequences_constantes(df, colonne,
                                                                                                longueur_min,
                                                                                                type_analyse,
                                                                                                utiliser_longueur_min,
                                                                                                reverse_order)

        resultats['tous_types'] = all_types_data

        types_tirages = df['Type de Tirage'].unique()
        for type_tirage in types_tirages:
            df_type = df[df['Type de Tirage'] == type_tirage]
            if not utiliser_longueur_min or len(df_type) > longueur_min - 1:
                type_data = {}

                if analyser_meme_ligne:
                    type_data['Même ligne'] = self._analyser_meme_ligne_progressions(df_type, colonnes, longueur_min,
                                                                                     type_analyse,
                                                                                     utiliser_longueur_min)

                type_data = {}
                with tqdm(colonnes, desc=f"Analyse par position ({type_tirage})") as pbar:
                    for position, colonne in enumerate(pbar):
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
        Trouve les séquences de progression/régression constante dans une colonne spécifique (vectorisé).
        """
        progressions_constantes = []
        regressions_constantes = []

        # Tri du DataFrame
        df = df.sort_values(by='Date', ascending=reverse_order)

        # Conversion en numérique
        df.loc[:, colonne] = pd.to_numeric(df[colonne], errors='coerce').astype('Int64')
        valeurs = df[colonne].to_numpy()

        # Calcul des différences
        diffs = np.diff(valeurs)

        # Identification des changements
        changements = np.where(np.diff(diffs) != 0)[0] + 1
        changements = np.insert(changements, 0, 0)
        changements = np.append(changements, len(valeurs) - 1)

        # Analyse des séquences
        for i in range(len(changements) - 1):
            start = changements[i]
            end = changements[i + 1]
            longueur = end - start + 1

            if utiliser_longueur_min and longueur < longueur_min:
                continue

            sequence = valeurs[start:end + 1].tolist()
            diff_constante = diffs[start]

            if type_analyse is None or type_analyse == 'progression' and diff_constante > 0 or type_analyse == 'regression' and diff_constante < 0:
                if diff_constante > 0:
                    progressions_constantes.append({
                        'sequence': sequence,
                        'date_debut': str(df['Date'].iloc[start]),
                        'date_fin': str(df['Date'].iloc[end]),
                        'type_tirage': df['Type de Tirage'].iloc[start]
                    })
                elif diff_constante < 0:
                    regressions_constantes.append({
                        'sequence': sequence,
                        'date_debut': str(df['Date'].iloc[start]),
                        'date_fin': str(df['Date'].iloc[end]),
                        'type_tirage': df['Type de Tirage'].iloc[start]
                    })

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
        """
        progressions_constantes = []
        regressions_constantes = []

        for col in colonnes:
            df.loc[:, col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

        for idx, row in df.iterrows():
            valeurs = row[colonnes].tolist()
            date = row['Date'].strftime('%d/%m/%Y')
            type_tirage = row['Type de Tirage']

            i = 0
            while i < len(valeurs) - 1:
                sequence_courante = [valeurs[i]]
                diff_constante = valeurs[i + 1] - valeurs[i]

                if diff_constante == 0:
                    i += 1
                    continue

                j = i + 1
                while j < len(valeurs) and valeurs[j] - valeurs[j - 1] == diff_constante:
                    sequence_courante.append(valeurs[j])
                    j += 1

                if not utiliser_longueur_min or len(sequence_courante) >= longueur_min:
                    sequence_info = {
                        'valeurs': sequence_courante,
                        'difference': diff_constante,
                        'longueur': len(sequence_courante),
                        'dates': [date] * len(sequence_courante),
                        'types': [type_tirage] * len(sequence_courante),
                        'colonnes': colonnes[i:i + len(sequence_courante)]
                    }

                    if diff_constante > 0:
                        progressions_constantes.append(sequence_info)
                    else:
                        regressions_constantes.append(sequence_info)

                i = j

        progressions_constantes.sort(key=lambda x: x['longueur'], reverse=True)
        regressions_constantes.sort(key=lambda x: x['longueur'], reverse=True)

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

        types_tirages = df['Type de Tirage'].unique()
        for type_tirage in types_tirages:
            df_type = df[df['Type de Tirage'] == type_tirage]
            if not utiliser_longueur_min or len(df_type) > longueur_min - 1:
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
        """
        # Convertir les colonnes en type entier
        for col in colonnes:
            df.loc[:, col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

        # Précalculer les données nécessaires
        sequence_data = []
        for idx, row in df.iterrows():
            date = row['Date']
            type_tirage = row['Type de Tirage']
            numeros = [{'numero': row[col], 'colonne': col, 'date': date, 'type': type_tirage} for col in colonnes]
            sequence_data.append({'date': date, 'type': type_tirage, 'numeros': numeros})

        # Précalculer un index des numéros par valeur et date
        numero_par_valeur_date = defaultdict(list)
        for i, data in enumerate(sequence_data):
            for num in data['numeros']:
                numero_par_valeur_date[(num['numero'], num['date'])].append(num)

        sequences_constantes = []
        sequences_vues = set()

        for i in tqdm(range(len(sequence_data)), desc="Analyse des séquences"):
            for num_i in sequence_data[i]['numeros']:
                # Calculer les différences potentielles
                valeurs_possibles = set()
                for data in sequence_data:
                    for num in data['numeros']:
                        if num['numero'] != num_i['numero']:
                            valeurs_possibles.add(num['numero'])

                differences = {val - num_i['numero'] for val in valeurs_possibles if val - num_i['numero'] != 0}

                for diff in differences:
                    sequence_courante = [num_i]
                    valeur_attendue = num_i['numero'] + diff
                    date_prec = num_i['date']
                    j = i + 1

                    while j < len(sequence_data):
                        # Recherche directe dans l'index
                        candidats = numero_par_valeur_date.get((valeur_attendue, sequence_data[j]['date']), [])

                        # Filtrer les candidats en fonction de l'ordre inverse
                        if not reverse_order:
                            candidats = [c for c in candidats if c['date'] > date_prec]
                        else:
                            candidats = [c for c in candidats if c['date'] < date_prec]

                        if candidats:
                            num_j = candidats[0]  # Prendre le premier candidat
                            sequence_courante.append(num_j)
                            valeur_attendue += diff
                            date_prec = num_j['date']
                        else:
                            break
                        j += 1

                    # Appliquer le filtre de longueur si utiliser_longueur_min est True
                    if not utiliser_longueur_min or len(sequence_courante) >= longueur_min:
                        valeurs = tuple(item['numero'] for item in sequence_courante)
                        dates = tuple(item['date'].strftime('%d/%m/%Y') for item in sequence_courante)

                        # Convertir la séquence en un tuple pour la rendre hashable
                        sequence_tuple = (valeurs, dates, diff)

                        # Vérifier si cette séquence a déjà été vue
                        if sequence_tuple not in sequences_vues:
                            sequences_vues.add(sequence_tuple)  # Ajouter la séquence à l'ensemble des séquences vues

                            sequences_constantes.append({
                                'valeurs': list(valeurs),
                                'colonnes': [item['colonne'] for item in sequence_courante],
                                'difference': diff,
                                'longueur': len(sequence_courante),
                                'dates': [item['date'].strftime('%d/%m/%Y') for item in sequence_courante],
                                'types': [item['type'] for item in sequence_courante]
                            })

        # Séparer progressions et régressions
        progressions_constantes = [seq for seq in sequences_constantes if seq['difference'] > 0]
        regressions_constantes = [seq for seq in sequences_constantes if seq['difference'] < 0]

        # Trier par longueur
        progressions_constantes.sort(key=lambda x: x['longueur'], reverse=True)
        regressions_constantes.sort(key=lambda x: x['longueur'], reverse=True)

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
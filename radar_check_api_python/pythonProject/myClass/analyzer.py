import pandas as pd
from datetime import datetime
from typing import List, Dict, Union, Optional
from collections import defaultdict
from tqdm import tqdm


class LotteryAnalyzer:
    def __init__(self):
        self.num_cols = ['Num1', 'Num2', 'Num3', 'Num4', 'Num5']
        self.machine_cols = ['Machine1', 'Machine2', 'Machine3', 'Machine4', 'Machine5']

    def analyser_progression_constante(
            self,
            csv_file: str,
            date_debut: Optional[str] = None,
            date_fin: Optional[str] = None,
            type_tirage: Optional[str] = None,
            longueur_min: int = 3,
            type_analyse: Optional[str] = None,
            respecter_position: bool = True,
            analyser_meme_ligne: bool = False,
            fusionner_num_machine: bool = False,
            utiliser_longueur_min: bool = True,
            reverse_order: bool = False,
    ) -> Union[str, Dict]:
        try:
            df = pd.read_csv(csv_file, sep=';', parse_dates=['Date'], dayfirst=True, low_memory=False)
        except FileNotFoundError:
            return "Fichier CSV non trouvé."
        except Exception as e:
            return f"Erreur lors de la lecture du fichier CSV: {e}"

        # Appliquer les filtres et préparer les données
        df = self._preparer_donnees(df, date_debut, date_fin, type_tirage, reverse_order)

        if df.empty:
            return "Aucun tirage ne correspond aux critères spécifiés."

        # Exécuter l'analyse en fonction des paramètres
        return self._executer_analyse(df, longueur_min, type_analyse, respecter_position,
                                      analyser_meme_ligne, fusionner_num_machine, utiliser_longueur_min, reverse_order)

    def _preparer_donnees(self, df, date_debut, date_fin, type_tirage, reverse_order):
        if reverse_order:
            df = df.iloc[::-1].copy()

        if date_debut:
            try:
                date_debut_dt = datetime.strptime(date_debut, '%d/%m/%Y')
                df = df[df['Date'] >= date_debut_dt]
            except ValueError:
                return "Format de date de début incorrect. Utilisez DD/MM/YYYY."

        if date_fin:
            try:
                date_fin_dt = datetime.strptime(date_fin, '%d/%m/%Y')
                df = df[df['Date'] <= date_fin_dt]
            except ValueError:
                return "Format de date de fin incorrect. Utilisez DD/MM/YYYY."

        if type_tirage:
            df = df[df['Type de Tirage'] == type_tirage]

        # Conversion des colonnes numériques
        colonnes_numeriques = self.num_cols + self.machine_cols
        for col in colonnes_numeriques:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')

        return df

    def _executer_analyse(self, df, longueur_min, type_analyse, respecter_position,
                          analyser_meme_ligne, fusionner_num_machine, utiliser_longueur_min, reverse_order):
        resultats = {}

        colonnes_a_utiliser = self.num_cols + self.machine_cols if fusionner_num_machine else self.num_cols
        df_analyse = df[['Date', 'Type de Tirage'] + colonnes_a_utiliser].copy()

        if fusionner_num_machine:
            colonnes = self.num_cols + self.machine_cols
            method = self.analyser_sequences_constantes if respecter_position else self.analyser_sequences_sans_position
            resultats['num_et_machine'] = method(df_analyse, colonnes, longueur_min,
                                                 type_analyse, analyser_meme_ligne, utiliser_longueur_min,
                                                 reverse_order)
        else:
            method = self.analyser_sequences_constantes if respecter_position else self.analyser_sequences_sans_position
            resultats['num'] = method(df_analyse, self.num_cols, longueur_min, type_analyse,
                                      analyser_meme_ligne, utiliser_longueur_min, reverse_order)
            resultats['machine'] = method(df_analyse, self.machine_cols, longueur_min, type_analyse,
                                          analyser_meme_ligne, utiliser_longueur_min, reverse_order)

        return resultats

    def analyser_sequences_constantes(
            self,
            df: pd.DataFrame,
            colonnes: List[str],
            longueur_min: int = 3,
            type_analyse: Optional[str] = None,
            analyser_meme_ligne: bool = False,
            utiliser_longueur_min: bool = True,
            reverse_order: bool = False,
    ) -> Dict:
        resultats = {}
        all_types_data = {}

        if analyser_meme_ligne:
            all_types_data['Même ligne'] = self.analyser_meme_ligne_progressions(
                df, colonnes, longueur_min, type_analyse, utiliser_longueur_min)

        for position, colonne in enumerate(colonnes):
            all_types_data[f'Position {position + 1}'] = self.trouver_sequences_constantes(
                df, colonne, longueur_min, type_analyse, utiliser_longueur_min, reverse_order)

        resultats['tous_types'] = all_types_data

        # Analyser pour chaque type de tirage
        types_tirages = df['Type de Tirage'].unique()
        for type_tirage in types_tirages:
            df_type = df[df['Type de Tirage'] == type_tirage]
            if not utiliser_longueur_min or len(df_type) > longueur_min - 1:
                type_data = {}

                if analyser_meme_ligne:
                    type_data['Même ligne'] = self.analyser_meme_ligne_progressions(
                        df_type, colonnes, longueur_min, type_analyse, utiliser_longueur_min)

                for position, colonne in enumerate(colonnes):
                    type_data[f'Position {position + 1}'] = self.trouver_sequences_constantes(
                        df_type, colonne, longueur_min, type_analyse, utiliser_longueur_min, reverse_order)

                resultats[type_tirage] = type_data

        return resultats

    def trouver_sequences_constantes(
            self,
            df: pd.DataFrame,
            colonne: str,
            longueur_min: int = 3,
            type_analyse: Optional[str] = None,
            utiliser_longueur_min: bool = True,
            reverse_order: bool = False,
    ) -> Dict:
        progressions_constantes = []
        regressions_constantes = []

        # Tri du DataFrame en fonction de la date
        df = df.sort_values(by='Date', ascending=not reverse_order)

        # Convertir la colonne en type entier et extraire les listes
        valeurs = df[colonne].tolist()
        dates = df['Date'].tolist()
        types_tirages = df['Type de Tirage'].tolist()

        i = 0
        while i < len(valeurs) - 1:
            if pd.isna(valeurs[i]) or pd.isna(valeurs[i + 1]):
                i += 1
                continue

            valeur_initiale = valeurs[i]
            date_initiale = dates[i]
            type_tirage_initial = types_tirages[i]

            diff_constante = valeurs[i + 1] - valeur_initiale

            if diff_constante == 0:
                i += 1
                continue

            sequence_courante = [valeur_initiale]
            sequence_dates = [date_initiale]
            sequence_types = [type_tirage_initial]

            j = i + 1
            while j < len(valeurs) and not pd.isna(valeurs[j]) and valeurs[j] - sequence_courante[-1] == diff_constante:
                sequence_courante.append(valeurs[j])
                sequence_dates.append(dates[j])
                sequence_types.append(types_tirages[j])
                j += 1

            if not utiliser_longueur_min or len(sequence_courante) >= longueur_min:
                sequence_info = {
                    'valeurs': sequence_courante,
                    'difference': diff_constante,
                    'longueur': len(sequence_courante),
                    'dates': [date.strftime('%d/%m/%Y') for date in sequence_dates],
                    'types': sequence_types,
                    'colonne': colonne
                }

                if diff_constante > 0:
                    progressions_constantes.append(sequence_info)
                else:
                    regressions_constantes.append(sequence_info)

            i = j

        # Trier les séquences par longueur
        progressions_constantes.sort(key=lambda x: x['longueur'], reverse=True)
        regressions_constantes.sort(key=lambda x: x['longueur'], reverse=True)

        # Retourner les résultats en fonction du type d'analyse
        return self._filtrer_par_type_analyse(progressions_constantes, regressions_constantes, type_analyse)

    def analyser_meme_ligne_progressions(
            self,
            df: pd.DataFrame,
            colonnes: List[str],
            longueur_min: int = 3,
            type_analyse: Optional[str] = None,
            utiliser_longueur_min: bool = True,
    ) -> Dict:
        progressions_constantes = []
        regressions_constantes = []

        for idx, row in df.iterrows():
            valeurs = row[colonnes].dropna().tolist()
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

        # Trier les séquences par longueur
        progressions_constantes.sort(key=lambda x: x['longueur'], reverse=True)
        regressions_constantes.sort(key=lambda x: x['longueur'], reverse=True)

        return self._filtrer_par_type_analyse(progressions_constantes, regressions_constantes, type_analyse)

    def analyser_sequences_sans_position(
            self,
            df: pd.DataFrame,
            colonnes: List[str],
            longueur_min: int = 3,
            type_analyse: Optional[str] = None,
            analyser_meme_ligne: bool = False,
            utiliser_longueur_min: bool = True,
            reverse_order: bool = False,
    ) -> Dict:
        resultats = {}
        all_types_data = {}

        if analyser_meme_ligne:
            all_types_data['Même ligne'] = self.analyser_meme_ligne_progressions(
                df, colonnes, longueur_min, type_analyse, utiliser_longueur_min)

        all_types_data['Toutes positions'] = self.trouver_sequences_sans_position(
            df, colonnes, longueur_min, type_analyse, utiliser_longueur_min, reverse_order)

        resultats['tous_types'] = all_types_data

        # Analyser pour chaque type de tirage
        types_tirages = df['Type de Tirage'].unique()
        for type_tirage in types_tirages:
            df_type = df[df['Type de Tirage'] == type_tirage]
            if not utiliser_longueur_min or len(df_type) > longueur_min - 1:
                type_data = {}

                if analyser_meme_ligne:
                    type_data['Même ligne'] = self.analyser_meme_ligne_progressions(
                        df_type, colonnes, longueur_min, type_analyse, utiliser_longueur_min)

                type_data['Toutes positions'] = self.trouver_sequences_sans_position(
                    df_type, colonnes, longueur_min, type_analyse, utiliser_longueur_min, reverse_order)

                resultats[type_tirage] = type_data

        return resultats

    def trouver_sequences_sans_position(
            self,
            df: pd.DataFrame,
            colonnes: List[str],
            longueur_min: int = 3,
            type_analyse: Optional[str] = None,
            utiliser_longueur_min: bool = True,
            reverse_order: bool = False,
    ) -> Dict:
        # Préparation des données
        sequence_data = []
        numero_par_valeur_date = defaultdict(list)

        for idx, row in df.iterrows():
            date = row['Date']
            type_tirage = row['Type de Tirage']
            numeros = []

            for col in colonnes:
                val = row[col]
                if not pd.isna(val):
                    num_info = {'numero': val, 'colonne': col, 'date': date, 'type': type_tirage}
                    numeros.append(num_info)
                    numero_par_valeur_date[(val, date)].append(num_info)

            if numeros:
                sequence_data.append({'date': date, 'type': type_tirage, 'numeros': numeros})

        # Optimisation: créer un ensemble de différences possibles
        all_values = set()
        for data in sequence_data:
            for num in data['numeros']:
                all_values.add(num['numero'])

        sequences_constantes = []
        sequences_vues = set()

        for i in range(len(sequence_data)):
            for num_i in sequence_data[i]['numeros']:
                # Calculer les différences possibles de manière optimisée
                valeur_i = num_i['numero']
                differences = {val - valeur_i for val in all_values if val != valeur_i}

                for diff in differences:
                    if diff == 0:
                        continue

                    sequence_courante = [num_i]
                    valeur_attendue = valeur_i + diff
                    date_prec = num_i['date']
                    j = i + 1

                    while j < len(sequence_data):
                        candidats = numero_par_valeur_date.get((valeur_attendue, sequence_data[j]['date']), [])

                        # Filtrer les candidats en fonction de l'ordre
                        candidats_filtres = []
                        for c in candidats:
                            if (not reverse_order and c['date'] > date_prec) or (
                                    reverse_order and c['date'] < date_prec):
                                candidats_filtres.append(c)

                        if candidats_filtres:
                            num_j = candidats_filtres[0]
                            sequence_courante.append(num_j)
                            valeur_attendue += diff
                            date_prec = num_j['date']
                        else:
                            break
                        j += 1

                    # Vérifier si la séquence répond aux critères
                    if not utiliser_longueur_min or len(sequence_courante) >= longueur_min:
                        valeurs = tuple(item['numero'] for item in sequence_courante)
                        dates = tuple(item['date'].strftime('%d/%m/%Y') for item in sequence_courante)

                        # Eviter les doublons
                        sequence_tuple = (valeurs, dates, diff)
                        if sequence_tuple not in sequences_vues:
                            sequences_vues.add(sequence_tuple)

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

        return self._filtrer_par_type_analyse(progressions_constantes, regressions_constantes, type_analyse)

    def _filtrer_par_type_analyse(self, progressions, regressions, type_analyse):
        """Helper method to filter results based on analysis type"""
        if type_analyse == 'progression':
            return {'progressions_constantes': progressions, 'regressions_constantes': []}
        elif type_analyse == 'regression':
            return {'progressions_constantes': [], 'regressions_constantes': regressions}
        else:
            return {'progressions_constantes': progressions, 'regressions_constantes': regressions}
import pandas as pd
from datetime import datetime
import sys
import argparse
import os
from typing import Dict, List, Any, Optional
import numpy as np
from tqdm import tqdm

class LotteryAnalyzer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.num_cols = ['Num1', 'Num2', 'Num3', 'Num4', 'Num5']
        self.machine_cols = ['Machine1', 'Machine2', 'Machine3', 'Machine4', 'Machine5']

    def load_and_filter_data(self, csv_file: str, date_debut: Optional[str] = None,
                             date_fin: Optional[str] = None, type_tirage: Optional[str] = None) -> pd.DataFrame:
        if not os.path.isfile(csv_file):
            raise FileNotFoundError(f"Input file not found: {csv_file}")
        df = pd.read_csv(csv_file, sep=';')
        df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y')

        df = df.sort_values(by='Date', ascending=False)
        if date_debut:
            df = df[df['Date'] >= datetime.strptime(date_debut, '%d/%m/%Y')]
        if date_fin:
            df = df[df['Date'] <= datetime.strptime(date_fin, '%d/%m/%Y')]
        if type_tirage:
            df = df[df['Type de Tirage'] == type_tirage]
        return df

    def find_sequences(self, values: List[int], dates: List[datetime], types: List[str],
                       diff_type: Optional[str] = None) -> List[Dict[str, Any]]:
        seqs = []
        if len(values) < 2:
            return seqs

        diffs = [{'from': values[i - 1], 'to': values[i], 'diff': values[i] - values[i - 1],
                  'prev_date': dates[i - 1].strftime('%d/%m/%Y'), 'curr_date': dates[i].strftime('%d/%m/%Y'),
                  'prev_type': types[i - 1], 'curr_type': types[i]} for i in range(1, len(values))]
        i = 0
        while i < len(diffs):
            curr_seq = [diffs[i]]
            const_diff = diffs[i]['diff']
            j = i + 1
            while j < len(diffs) and diffs[j]['diff'] == const_diff and diffs[j]['prev_date'] < diffs[j - 1]['curr_date']:
                curr_seq.append(diffs[j])
                j += 1

            seqs.append({
                'values': [curr_seq[0]['from']] + [item['to'] for item in curr_seq],
                'diff': const_diff,
                'length': len(curr_seq) + 1,
                'dates': [curr_seq[0]['prev_date']] + [item['curr_date'] for item in curr_seq],
                'types': [curr_seq[0]['prev_type']] + [item['curr_type'] for item in curr_seq]
            })
            i = j

        if diff_type == 'progression':
            seqs = [seq for seq in seqs if seq['diff'] > 0]
        elif diff_type == 'regression':
            seqs = [seq for seq in seqs if seq['diff'] < 0]
        return sorted(seqs, key=lambda x: x['length'], reverse=True)

    def analyze_same_line(self, df: pd.DataFrame, columns: List[str],
                          diff_type: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        progs, regrs = [], []
        for _, row in df.iterrows():
            vals = [int(row[col]) for col in columns]
            date = row['Date'].strftime('%d/%m/%Y')
            t_type = row['Type de Tirage']

            if len(vals) < 2:
                continue

            i = 0
            while i < len(vals) - 1:
                curr_seq = [vals[i]]
                const_diff = vals[i + 1] - vals[i]
                if const_diff == 0:
                    i += 1
                    continue
                j = i + 1
                while j < len(vals) and vals[j] - vals[j - 1] == const_diff:
                    curr_seq.append(vals[j])
                    j += 1

                seq_info = {
                    'values': curr_seq, 'diff': const_diff, 'length': len(curr_seq),
                    'dates': [date] * len(curr_seq), 'types': [t_type] * len(curr_seq),
                    'columns': columns[i:i + len(curr_seq)]
                }
                if const_diff > 0:
                    progs.append(seq_info)
                else:
                    regrs.append(seq_info)
                i = j
        progs.sort(key=lambda x: x['length'], reverse=True)
        regrs.sort(key=lambda x: x['length'], reverse=True)
        if diff_type == 'progression':
            return {'progressions': progs, 'regressions': []}
        elif diff_type == 'regression':
            return {'progressions': [], 'regressions': regrs}
        else:
            return {'progressions': progs, 'regressions': regrs}

    def analyze_by_position(self, df: pd.DataFrame, columns: List[str],
                            diff_type: Optional[str] = None) -> Dict[
        str, Dict[str, List[Dict[str, Any]]]]:
        result = {}
        for pos, col in enumerate(columns):
            nums = df[col].astype(int).tolist()
            dates = df['Date'].tolist()
            types = df['Type de Tirage'].tolist()
            seqs = self.find_sequences(nums, dates, types, diff_type)
            progs = [seq for seq in seqs if seq['diff'] > 0]
            regrs = [seq for seq in seqs if seq['diff'] < 0]
            result[f'Position {pos + 1}'] = {'progressions': progs, 'regressions': regrs}
        return result

    def analyze_across_positions(self, df: pd.DataFrame, columns: List[str],
                                 diff_type: Optional[str] = None) -> Dict[
        str, List[Dict[str, Any]]]:
        # 1. Convertir les colonnes en tableau NumPy
        numbers = df[columns].values.astype(int)
        dates = df['Date'].dt.strftime('%d/%m/%Y').to_numpy()
        types = df['Type de Tirage'].to_numpy()

        # 2. Créer une liste pour stocker les séquences
        sequences = []

        # 3. Itérer sur chaque combinaison possible de nombres, dates et types
        for i in range(numbers.shape[0]):  # Pour chaque ligne
            for col_idx in range(numbers.shape[1]):  # Pour chaque colonne (position)
                num_i = numbers[i, col_idx]
                date_i = dates[i]
                type_i = types[i]

                for diff in range(-5, 6):  # Limiter la plage de différences à +/- 5
                    if diff == 0:
                        continue

                    current_seq = [{'number': num_i, 'column': columns[col_idx], 'date': date_i, 'type': type_i}]
                    expected = num_i + diff
                    j = i + 1
                    while j < numbers.shape[0]:
                        found = False
                        for next_col_idx in range(numbers.shape[1]):  # Recherche dans toutes les positions
                            if numbers[j, next_col_idx] == expected and dates[j] < current_seq[-1]['date']:
                                current_seq.append({
                                    'number': numbers[j, next_col_idx],
                                    'column': columns[next_col_idx],
                                    'date': dates[j],
                                    'type': types[j]
                                })
                                expected += diff
                                found = True
                                break
                        if not found:
                            break
                        j += 1

                    if len(current_seq) > 1:  # Exiger une longueur minimale de 2
                        sequences.append({
                            'values': [item['number'] for item in current_seq],
                            'columns': [item['column'] for item in current_seq],
                            'diff': diff,
                            'length': len(current_seq),
                            'dates': [item['date'] for item in current_seq],
                            'types': [item['type'] for item in current_seq]
                        })

        # 4. Filtrer et trier les séquences
        progressions = [seq for seq in sequences if seq['diff'] > 0]
        regressions = [seq for seq in sequences if seq['diff'] < 0]

        progressions.sort(key=lambda x: x['length'], reverse=True)
        regressions.sort(key=lambda x: x['length'], reverse=True)

        if diff_type == 'progression':
            return {'progressions': progressions, 'regressions': []}
        elif diff_type == 'regression':
            return {'progressions': [], 'regressions': regressions}
        else:
            return {'progressions': progressions, 'regressions': regressions}


    def analyze_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        results = {}
        analyze_cols = {'combined': self.num_cols + self.machine_cols} if self.config['fusionner'] else {
            'numbers': self.num_cols, 'machines': self.machine_cols}
        min_length = 3  # Valeur par défaut pour longueur_min
        for cat, cols in analyze_cols.items():
            cat_results = {'all_types': {}}
            if self.config['analyser_ligne']:
                cat_results['all_types']['Same line'] = self.analyze_same_line(df, cols,
                                                                               self.config['type_analyse'])
            if self.config['respecter_position']:
                cat_results['all_types'].update(self.analyze_by_position(df, cols,
                                                                         self.config['type_analyse']))
            else:
                cat_results['all_types']['All positions'] = self.analyze_across_positions(df, cols,
                                                                                         self.config['type_analyse'])
            for tirage in df['Type de Tirage'].unique():
                df_type = df[df['Type de Tirage'] == tirage]
                if len(df_type) > min_length - 1:
                    cat_results[tirage] = {}
                    if self.config['analyser_ligne']:
                        cat_results[tirage]['Same line'] = self.analyze_same_line(df_type, cols,
                                                                                  self.config['type_analyse'])
                    if self.config['respecter_position']:
                        cat_results[tirage].update(self.analyze_by_position(df_type, cols,
                                                                            self.config['type_analyse']))
                    else:
                        cat_results[tirage]['All positions'] = self.analyze_across_positions(df_type, cols,
                                                                                            self.config['type_analyse'])
            results[cat] = cat_results
        return results

class ResultHandler:
    @staticmethod
    def display_results(results: Dict[str, Any]) -> None:
        for cat, type_data in results.items():
            print(f"\n=== ANALYSIS OF {cat.upper()} ===")
            for tirage, pos_data in type_data.items():
                print(f"\n--- Draw type: {tirage} ---")
                for pos, seqs in pos_data.items():
                    print(f"\n{pos}:")
                    print(f"  Constant progressions found: {len(seqs['progressions'])}")
                    for i, seq in enumerate(seqs['progressions'][:5]):
                        print(f"  Sequence {i + 1} (length: {seq['length']}, difference: +{seq['diff']}):")
                        print(f"    Values: {' ← '.join(map(str, seq['values']))}")
                        print(f"    Dates: {', '.join(seq['dates'])}")
                        print(f"    Types: {', '.join(seq['types'])}")
                        if 'columns' in seq:
                            print(f"    Positions: {', '.join(seq['columns'])}")
                    print(f"\n  Constant regressions found: {len(seqs['regressions'])}")
                    for i, seq in enumerate(seqs['regressions'][:5]):
                        print(f"  Sequence {i + 1} (length: {seq['length']}, difference: {seq['diff']}):")
                        print(f"    Values: {' ← '.join(map(str, seq['values']))}")
                        print(f"    Dates: {', '.join(seq['dates'])}")
                        print(f"    Types: {', '.join(seq['types'])}")
                        if 'columns' in seq:
                            print(f"    Positions: {', '.join(seq['columns'])}")

    @staticmethod
    def export_to_csv(results: Dict[str, Any], output_file: str = 'sequence_results.csv') -> None:
        export_data = []
        for cat, type_data in results.items():
            for tirage, pos_data in type_data.items():
                for pos, seqs in pos_data.items():
                    for seq_type, seq_list in seqs.items():
                        for seq in seq_list:
                            data_row = {
                                'Category': cat, 'Draw type': tirage, 'Position': pos,
                                'Sequence type': seq_type[:-1], 'Difference': seq['diff'], 'Length': seq['length'],
                                'Values': ' ← '.join(map(str, seq['values'])), 'Dates': ', '.join(seq['dates']),
                                'Draw types': ', '.join(seq['types'])
                            }
                            if 'columns' in seq:
                                data_row['Positions used'] = ', '.join(seq['columns'])
                            export_data.append(data_row)
        df_export = pd.DataFrame(export_data)
        df_export.to_csv(output_file, index=False, encoding='utf-8')

def main(config: Dict[str, Any]):
    analyzer = LotteryAnalyzer(config)
    try:
        df = analyzer.load_and_filter_data(
            config['csv_file'], config.get('date_debut'), config.get('date_fin'), config.get('type_tirage'))
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    results = analyzer.analyze_data(df)
    ResultHandler.display_results(results)
    ResultHandler.export_to_csv(results, config.get('output_file', 'sequence_results.csv'))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lottery Analysis Tool")
    parser.add_argument('--csv_file', type=str, default='../formatted_lottery_results.csv',
                        help='Path to CSV file (default: formatted_lottery_results.csv)')
    parser.add_argument('--date_debut', type=str, help='Start date (dd/mm/yyyy)')
    parser.add_argument('--date_fin', type=str, help='End date (dd/mm/yyyy)')
    parser.add_argument('--type_tirage', type=str, help='Type de Tirage')
    parser.add_argument('--fusionner', action='store_true', help='Fusionner les colonnes')
    parser.add_argument('--analyser_ligne', action='store_true', help='Analyser la ligne')
    parser.add_argument('--respecter_position', action='store_true', help='Respecter la position')
    # parser.add_argument('--longueur_min', type=int, default=3, help='Longueur minimale des sequences') # Retiré
    parser.add_argument('--type_analyse', type=str, default=None, help='Type d\'analyse')
    parser.add_argument('--output_file', type=str, default='sequence_results.csv', help='Output CSV file')

    args = parser.parse_args()
    config = {k: getattr(args, k) for k in vars(args)}
    main(config)

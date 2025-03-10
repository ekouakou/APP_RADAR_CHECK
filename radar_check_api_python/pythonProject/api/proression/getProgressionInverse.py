import pandas as pd
from datetime import datetime
import sys
import argparse
import os
from typing import Dict, List, Any, Optional, Tuple


class LotteryAnalyzer:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.num_cols = ['Num1', 'Num2', 'Num3', 'Num4', 'Num5']
        self.machine_cols = ['Machine1', 'Machine2', 'Machine3', 'Machine4', 'Machine5']

    def load_and_filter_data(self, csv_file: str, date_debut: Optional[str] = None,
                             date_fin: Optional[str] = None, type_tirage: Optional[str] = None) -> pd.DataFrame:
        """Load and filter lottery draw data"""
        # Check if file exists
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
                       min_length: int = 3, diff_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Identify sequences with constant differences"""
        sequences = []

        # Calculate differences
        diffs = []
        for i in range(1, len(values)):
            diffs.append({
                'from': values[i - 1],
                'to': values[i],
                'diff': values[i] - values[i - 1],
                'prev_date': dates[i - 1].strftime('%d/%m/%Y'),
                'curr_date': dates[i].strftime('%d/%m/%Y'),
                'prev_type': types[i - 1],
                'curr_type': types[i]
            })

        i = 0
        while i < len(diffs) - 1:
            current_seq = [diffs[i]]
            const_diff = diffs[i]['diff']
            j = i + 1

            while j < len(diffs) and diffs[j]['diff'] == const_diff:
                if diffs[j]['prev_date'] < diffs[j - 1]['curr_date']:
                    current_seq.append(diffs[j])
                    j += 1
                else:
                    break

            if len(current_seq) >= min_length - 1:
                sequences.append({
                    'values': [current_seq[0]['from']] + [item['to'] for item in current_seq],
                    'diff': const_diff,
                    'length': len(current_seq) + 1,
                    'dates': [current_seq[0]['prev_date']] + [item['curr_date'] for item in current_seq],
                    'types': [current_seq[0]['prev_type']] + [item['curr_type'] for item in current_seq]
                })
                i = j
            else:
                i += 1

        # Filter and sort sequences
        if diff_type == 'progression':
            sequences = [seq for seq in sequences if seq['diff'] > 0]
        elif diff_type == 'regression':
            sequences = [seq for seq in sequences if seq['diff'] < 0]

        return sorted(sequences, key=lambda x: x['length'], reverse=True)

    def analyze_same_line(self, df: pd.DataFrame, columns: List[str],
                          min_length: int = 3, diff_type: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Analyze progressions/regressions within the same draw line"""
        progressions = []
        regressions = []

        for _, row in df.iterrows():
            values = [int(row[col]) for col in columns]
            date = row['Date'].strftime('%d/%m/%Y')
            tirage_type = row['Type de Tirage']

            i = 0
            while i < len(values) - 1:
                current_seq = [values[i]]
                const_diff = values[i + 1] - values[i]

                if const_diff == 0:
                    i += 1
                    continue

                j = i + 1
                while j < len(values) and values[j] - values[j - 1] == const_diff:
                    current_seq.append(values[j])
                    j += 1

                if len(current_seq) >= min_length:
                    seq_info = {
                        'values': current_seq,
                        'diff': const_diff,
                        'length': len(current_seq),
                        'dates': [date] * len(current_seq),
                        'types': [tirage_type] * len(current_seq),
                        'columns': columns[i:i + len(current_seq)]
                    }

                    if const_diff > 0:
                        progressions.append(seq_info)
                    else:
                        regressions.append(seq_info)

                i = j

        # Sort by length
        progressions.sort(key=lambda x: x['length'], reverse=True)
        regressions.sort(key=lambda x: x['length'], reverse=True)

        # Filter by analysis type
        if diff_type == 'progression':
            return {'progressions': progressions, 'regressions': []}
        elif diff_type == 'regression':
            return {'progressions': [], 'regressions': regressions}
        else:
            return {'progressions': progressions, 'regressions': regressions}

    def analyze_by_position(self, df: pd.DataFrame, columns: List[str],
                            min_length: int = 3, diff_type: Optional[str] = None) -> Dict[
        str, Dict[str, List[Dict[str, Any]]]]:
        """Analyze constant sequences by position"""
        result = {}

        for position, column in enumerate(columns):
            numbers = df[column].astype(int).tolist()
            dates = df['Date'].tolist()
            types = df['Type de Tirage'].tolist()

            sequences = self.find_sequences(numbers, dates, types, min_length, diff_type)

            progressions = [seq for seq in sequences if seq['diff'] > 0]
            regressions = [seq for seq in sequences if seq['diff'] < 0]

            result[f'Position {position + 1}'] = {
                'progressions': progressions,
                'regressions': regressions
            }

        return result

    def analyze_across_positions(self, df: pd.DataFrame, columns: List[str],
                                 min_length: int = 3, diff_type: Optional[str] = None) -> Dict[
        str, List[Dict[str, Any]]]:
        """Analyze sequences independently of position"""
        seq_data = []

        for _, row in df.iterrows():
            date = row['Date']
            tirage_type = row['Type de Tirage']

            numbers = []
            for col in columns:
                numbers.append({
                    'number': int(row[col]),
                    'column': col,
                    'date': date.strftime('%d/%m/%Y'),
                    'type': tirage_type
                })

            seq_data.append({
                'date': date.strftime('%d/%m/%Y'),
                'type': tirage_type,
                'numbers': numbers
            })

        # Find sequences
        sequences = []

        for i in range(len(seq_data)):
            for num_i in seq_data[i]['numbers']:
                for diff in range(-90, 91):
                    if diff == 0:
                        continue

                    current_seq = [num_i]
                    expected = num_i['number'] + diff
                    prev_date = num_i['date']
                    j = i + 1

                    while j < len(seq_data):
                        found = False
                        for num_j in seq_data[j]['numbers']:
                            if num_j['number'] == expected and seq_data[j]['date'] < prev_date:
                                current_seq.append(num_j)
                                expected += diff
                                prev_date = num_j['date']
                                found = True
                                break

                        if not found:
                            break

                        j += 1

                    if len(current_seq) >= min_length:
                        sequences.append({
                            'values': [item['number'] for item in current_seq],
                            'columns': [item['column'] for item in current_seq],
                            'diff': diff,
                            'length': len(current_seq),
                            'dates': [item['date'] for item in current_seq],
                            'types': [item['type'] for item in current_seq]
                        })

        # Deduplicate
        unique_seqs = []
        for seq in sequences:
            is_duplicate = False
            for unique_seq in unique_seqs:
                if (seq['values'] == unique_seq['values'] and
                        seq['dates'] == unique_seq['dates']):
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_seqs.append(seq)

        # Filter and sort
        progressions = [seq for seq in unique_seqs if seq['diff'] > 0]
        regressions = [seq for seq in unique_seqs if seq['diff'] < 0]

        progressions.sort(key=lambda x: x['length'], reverse=True)
        regressions.sort(key=lambda x: x['length'], reverse=True)

        if diff_type == 'progression':
            return {'progressions': progressions, 'regressions': []}
        elif diff_type == 'regression':
            return {'progressions': [], 'regressions': regressions}
        else:
            return {'progressions': progressions, 'regressions': regressions}

    def analyze_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Main data analysis based on configuration"""
        results = {}

        # Determine columns to analyze
        if self.config['fusionner']:
            all_cols = self.num_cols + self.machine_cols
            analyze_cols = {'combined': all_cols}
        else:
            analyze_cols = {'numbers': self.num_cols, 'machines': self.machine_cols}

        # Analyze by category (numbers/machines/combined)
        for category, cols in analyze_cols.items():
            category_results = {}

            # Analyze all draw types together
            type_results = {}

            if self.config['analyser_ligne']:
                type_results['Same line'] = self.analyze_same_line(
                    df, cols, self.config['longueur_min'], self.config['type_analyse'])

            if self.config['respecter_position']:
                type_results.update(self.analyze_by_position(
                    df, cols, self.config['longueur_min'], self.config['type_analyse']))
            else:
                type_results['All positions'] = self.analyze_across_positions(
                    df, cols, self.config['longueur_min'], self.config['type_analyse'])

            category_results['all_types'] = type_results

            # Analyze by draw type
            for tirage in df['Type de Tirage'].unique():
                df_type = df[df['Type de Tirage'] == tirage]
                if len(df_type) > self.config['longueur_min'] - 1:
                    type_results = {}

                    if self.config['analyser_ligne']:
                        type_results['Same line'] = self.analyze_same_line(
                            df_type, cols, self.config['longueur_min'], self.config['type_analyse'])

                    if self.config['respecter_position']:
                        type_results.update(self.analyze_by_position(
                            df_type, cols, self.config['longueur_min'], self.config['type_analyse']))
                    else:
                        type_results['All positions'] = self.analyze_across_positions(
                            df_type, cols, self.config['longueur_min'], self.config['type_analyse'])

                    category_results[tirage] = type_results

            results[category] = category_results

        return results


class ResultHandler:
    @staticmethod
    def display_results(results: Dict[str, Any]) -> None:
        """Display analysis results in a readable format"""
        for category, type_data in results.items():
            print(f"\n=== ANALYSIS OF {category.upper()} ===")

            for tirage, positions_data in type_data.items():
                print(f"\n--- Draw type: {tirage} ---")

                for position, sequences in positions_data.items():
                    print(f"\n{position}:")

                    # Display progressions
                    print(f"  Constant progressions found: {len(sequences['progressions'])}")
                    for i, seq in enumerate(sequences['progressions'][:5]):
                        print(f"  Sequence {i + 1} (length: {seq['length']}, difference: +{seq['diff']}):")
                        print(f"    Values: {' ← '.join(map(str, seq['values']))}")
                        print(f"    Dates: {', '.join(seq['dates'])}")
                        print(f"    Types: {', '.join(seq['types'])}")
                        if 'columns' in seq:
                            print(f"    Positions: {', '.join(seq['columns'])}")

                    # Display regressions
                    print(f"\n  Constant regressions found: {len(sequences['regressions'])}")
                    for i, seq in enumerate(sequences['regressions'][:5]):
                        print(f"  Sequence {i + 1} (length: {seq['length']}, difference: {seq['diff']}):")
                        print(f"    Values: {' ← '.join(map(str, seq['values']))}")
                        print(f"    Dates: {', '.join(seq['dates'])}")
                        print(f"    Types: {', '.join(seq['types'])}")
                        if 'columns' in seq:
                            print(f"    Positions: {', '.join(seq['columns'])}")

    @staticmethod
    def export_to_csv(results: Dict[str, Any], output_file: str = 'sequence_results.csv') -> None:
        """Export results to a CSV file"""
        export_data = []

        for category, type_data in results.items():
            for tirage, positions_data in type_data.items():
                for position, sequences in positions_data.items():
                    # Process progressions
                    for seq in sequences['progressions']:
                        data_row = {
                            'Category': category,
                            'Draw type': tirage,
                            'Position': position,
                            'Sequence type': 'Constant progression',
                            'Difference': seq['diff'],
                            'Length': seq['length'],
                            'Values': ' ← '.join(map(str, seq['values'])),
                            'Dates': ', '.join(seq['dates']),
                            'Draw types': ', '.join(seq['types'])
                        }
                        if 'columns' in seq:
                            data_row['Positions used'] = ', '.join(seq['columns'])
                        export_data.append(data_row)

                    # Process regressions
                    for seq in sequences['regressions']:
                        data_row = {
                            'Category': category,
                            'Draw type': tirage,
                            'Position': position,
                            'Sequence type': 'Constant regression',
                            'Difference': seq['diff'],
                            'Length': seq['length'],
                            'Values': ' ← '.join(map(str, seq['values'])),
                            'Dates': ', '.join(seq['dates']),
                            'Draw types': ', '.join(seq['types'])
                        }
                        if 'columns' in seq:
                            data_row['Positions used'] = ', '.join(seq['columns'])
                        export_data.append(data_row)

        if export_data:
            df_export = pd.DataFrame(export_data)

            # Ensure the output directory exists
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            df_export.to_csv(output_file, index=False, sep=';')
            print(f"\nResults exported to {output_file}")
        else:
            print("\nNo constant sequences found for export")


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Analyze constant progressions/regressions in lottery data')

    parser.add_argument('csv_file', nargs='?', default='../formatted_lottery_results.csv',
                        help='Path to CSV file (default: formatted_lottery_results.csv)')
    parser.add_argument('--start', dest='date_debut', help='Start date (DD/MM/YYYY)')
    parser.add_argument('--end', dest='date_fin', help='End date (DD/MM/YYYY)')
    parser.add_argument('--type', dest='type_tirage', help='Specific draw type to analyze')
    parser.add_argument('--min-length', dest='longueur_min', type=int, default=3,
                        help='Minimum sequence length (default: 4)')
    parser.add_argument('--analysis', dest='type_analyse', choices=['progression', 'regression'],
                        help='Analysis type (progression or regression)')
    parser.add_argument('--by-position', dest='respecter_position', action='store_true',
                        help='Analyze by position')
    parser.add_argument('--analyze-line', dest='analyser_ligne', action='store_true',
                        help='Analyze progressions within same line')
    parser.add_argument('--combine', dest='fusionner', action='store_true',
                        help='Analyze numbers and machines together')
    parser.add_argument('--output', dest='output_file', default='sequence_results.csv',
                        help='Output CSV file path (default: sequence_results.csv)')

    args = parser.parse_args()

    # Validate input file argument
    if not args.csv_file:
        parser.error("Input CSV file is required")

    return args


def main() -> None:
    """Main execution function"""
    try:
        args = parse_arguments()

        config = {
            'longueur_min': max(2, args.longueur_min),
            'type_analyse': args.type_analyse,
            'respecter_position': args.respecter_position,
            'analyser_ligne': args.analyser_ligne,
            'fusionner': args.fusionner
        }

        print_config_summary(args, config)

        # Initialize analyzer
        analyzer = LotteryAnalyzer(config)

        # Load and filter data
        try:
            df = analyzer.load_and_filter_data(args.csv_file, args.date_debut, args.date_fin, args.type_tirage)
        except FileNotFoundError as e:
            print(f"Error: {e}")
            print(f"Please check if the file '{args.csv_file}' exists and is accessible.")
            sys.exit(1)

        if df.empty:
            print("No draws match the specified criteria.")
            sys.exit(1)

        # Run analysis
        results = analyzer.analyze_data(df)

        # Display and export results
        handler = ResultHandler()
        handler.display_results(results)
        handler.export_to_csv(results, args.output_file)

        print("\nAnalysis completed successfully.")

    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def print_config_summary(args: argparse.Namespace, config: Dict[str, Any]) -> None:
    """Print a summary of the configuration"""
    print(f"Analyzing constant sequences in file {args.csv_file}...")
    print(f"Analysis from most recent to oldest date")
    if args.date_debut:
        print(f"Start date: {args.date_debut}")
    if args.date_fin:
        print(f"End date: {args.date_fin}")
    if args.type_tirage:
        print(f"Draw type: {args.type_tirage}")
    print(f"Minimum sequence length: {config['longueur_min']}")
    print(f"Analysis type: {config['type_analyse'] or 'progression and regression'}")
    print(f"Respect positions: {config['respecter_position']}")
    print(f"Analyze progressions in same line: {config['analyser_ligne']}")
    print(f"Combine numbers and machines: {config['fusionner']}")
    print(f"Output file: {args.output_file}")


if __name__ == "__main__":
    main()
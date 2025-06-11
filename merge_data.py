import pandas as pd
import os

def merge_data_files():
    """
    Merge split data files into a single file.
    Files to merge:
    - data/raw_master_ffa_results_part1.csv
    - data/raw_master_ffa_results_part2.csv
    - data/raw_master_ffa_results_part3.csv
    """
    # List of files to merge
    files = [
        'data/raw_master_ffa_results_part1.csv',
        'data/raw_master_ffa_results_part2.csv',
        'data/raw_master_ffa_results_part3.csv'
    ]

    # Check if all files exist
    missing_files = [f for f in files if not os.path.exists(f)]
    if missing_files:
        print(f"Warning: The following files are missing: {missing_files}")
        return

    # Read and concatenate all files
    dfs = []
    for file in files:
        try:
            df = pd.read_csv(file)
            dfs.append(df)
            print(f"Successfully read {file}")
        except Exception as e:
            print(f"Error reading {file}: {str(e)}")
            return

    # Concatenate all dataframes
    merged_df = pd.concat(dfs, ignore_index=True)

    # Remove duplicates if any
    original_len = len(merged_df)
    merged_df = merged_df.drop_duplicates()
    if len(merged_df) < original_len:
        print(f"Removed {original_len - len(merged_df)} duplicate rows")

    # Save merged file
    output_file = 'data/raw_master_ffa_results.csv'
    merged_df.to_csv(output_file, index=False)
    print(f"Successfully merged data into {output_file}")
    print(f"Total rows: {len(merged_df)}")

    # Create backup
    backup_file = 'data/raw_master_ffa_results_backup.csv'
    merged_df.to_csv(backup_file, index=False)
    print(f"Created backup at {backup_file}")

if __name__ == "__main__":
    merge_data_files()
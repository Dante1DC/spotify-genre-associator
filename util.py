import sys
from pathlib import Path
import pandas as pd

import config

def convert_csv_parquet(input_file, output_file):
    """
    Convert between csv and parquet. If the input file is a csv, then it saves a parquet, if the input file is a parquet, it saves a csv. 
    """
    input_path = Path(input_file)
    output_path = Path(output_file)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file at {input_file} not found.")

    input_suffix = input_path.suffix.lower()
    output_suffix = output_path.suffix.lower()

    if input_suffix == ".csv":
        if output_suffix not in [".parquet", ".parq"]:
            raise ValueError("End the output file path with .parquet or .parq")
        df = pd.read_csv(input_path)
        df.to_parquet(output_path)
    elif input_suffix in [".parquet", ".parq"]:
        if output_suffix != ".csv":
            raise ValueError("End the output file path with .csv")
        df = pd.read_parquet(input_path)
        df.to_csv(output_path, index=False)
    else:
        raise ValueError("Input file should be a .csv or .parquet file.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("--convert_btw_csv_parquet", "-c"):
        if len(sys.argv) != 4:
            print("wdym by that?")
            print("Usage: python app.py --convert_btw_csv_parquet <input_file> <output_file>")
            sys.exit(1)
        
        input_file = sys.argv[2]
        output_file = sys.argv[3]
        
        try:
            convert_csv_parquet(input_file, output_file)
            print(f"Successfully converted {input_file} to {output_file}.")
        except Exception as e:
            print(f"{str(e)}")
            sys.exit(1)

import pandas as pd
import os
import sys

# Force UTF-8 for stdout
sys.stdout.reconfigure(encoding='utf-8')

file_path = r"data/raw/Occupation des locaux_Automne_2025-2026 (1).xlsx"
output_file = "inspection_results.txt"

with open(output_file, "w", encoding="utf-8") as f:
    f.write(f"Inspecting: {file_path}\n")

    try:
        # Load the Excel file to get sheet names
        xl = pd.ExcelFile(file_path)
        f.write(f"Sheet names: {xl.sheet_names}\n")

        # Inspect each sheet
        for sheet in xl.sheet_names:
            f.write(f"\n--- Sheet: {sheet} ---\n")
            df = xl.parse(sheet, nrows=5) # Read only first 5 rows for preview
            f.write(f"Columns: {df.columns.tolist()}\n")
            f.write("First 3 rows:\n")
            f.write(df.head(3).to_string() + "\n")

    except Exception as e:
        f.write(f"Error reading Excel file: {e}\n")

print(f"Inspection complete. Results written to {output_file}")

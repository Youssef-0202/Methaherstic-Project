import pandas as pd
import sys

# Force UTF-8 for stdout
sys.stdout.reconfigure(encoding='utf-8')

file_path = r"data/raw/Occupation des locaux_Automne_2025-2026 (1).xlsx"
output_file = "inspection_results_deep.txt"

with open(output_file, "w", encoding="utf-8") as f:
    try:
        xl = pd.ExcelFile(file_path)
        sheet = xl.sheet_names[0]
        
        # Read rows 5 to 25 to find the structure
        f.write(f"--- Rows 5-25 of {sheet} ---\n")
        df = xl.parse(sheet, header=None, skiprows=5, nrows=20)
        f.write(df.to_string() + "\n")

    except Exception as e:
        f.write(f"Error: {e}\n")

print(f"Deep inspection complete. Results written to {output_file}")

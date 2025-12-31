from src.utils import load_data, save_solution
from src.algorithm import TimetableSolver
import os

DATA_DIR = r"data/processed"

def main():
    rooms, courses, groups, teachers, assignments = load_data(DATA_DIR)
    
    print("\n--- Data Verification ---")
    print(f"Loaded {len(assignments)} assignments.")
    
    # Just show the first few assignments to verify formatting
    print("\nSample Assignments:")
    for a in assignments[:5]:
        print(a)

if __name__ == "__main__":
    main()

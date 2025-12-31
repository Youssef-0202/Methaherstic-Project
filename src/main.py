from src.utils import load_data
from src.algorithm import TimetableSolver
import os

DATA_DIR = r"data/processed"

def main():
    rooms, courses, groups, teachers, assignments = load_data(DATA_DIR)
    
    print("\n--- Data Verification ---")
    print(f"Loaded {len(assignments)} assignments.")
    
    print("Initializing Solver...")
    # Initialize Solver
    solver = TimetableSolver(rooms, courses, groups, teachers, assignments)
    
    # Calculate Initial Cost
    initial_cost = solver.calculate_cost(assignments)
    print(f"\nInitial Solution Cost: {initial_cost}")
    print(f"Hard Violations: {solver.calculate_hard_constraints(assignments)}")

if __name__ == "__main__":
    main()

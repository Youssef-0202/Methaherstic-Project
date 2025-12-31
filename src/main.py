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
    
    print("\nRunning Simulated Annealing...")
    best_solution = solver.solve(max_iterations=5000, initial_temp=5000.0, cooling_rate=0.995)
    
    final_cost = solver.calculate_cost(best_solution)
    print(f"\nFinal Solution Cost: {final_cost}")
    print(f"Final Hard Violations: {solver.calculate_hard_constraints(best_solution)}")
    
    # Save best solution (Optional)
    # ...

if __name__ == "__main__":
    main()

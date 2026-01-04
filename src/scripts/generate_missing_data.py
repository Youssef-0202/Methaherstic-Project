import pandas as pd
import os

# Paths
DATA_DIR = 'data/processed'
GROUPS_FILE = os.path.join(DATA_DIR, 'groups.csv')
ASSIGNMENTS_FILE = os.path.join(DATA_DIR, 'assignments.csv')
TEACHERS_FILE = os.path.join(DATA_DIR, 'teachers.csv')

def generate_data():
    print("Generating missing data...")

    # 1. Update Groups with Sizes
    if os.path.exists(GROUPS_FILE):
        df_groups = pd.read_csv(GROUPS_FILE)
        
        # Define sizes based on section
        size_map = {
            'MST': 30,
            'CI': 45,
            'LST': 70,
            'TC': 180
        }
        
        df_groups['size'] = df_groups['section'].map(size_map).fillna(40).astype(int)
        df_groups.to_csv(GROUPS_FILE, index=False)
        print(f"Updated {GROUPS_FILE} with group sizes.")

    # 2. Assign Teachers to Assignments
    if os.path.exists(ASSIGNMENTS_FILE):
        df_assignments = pd.read_csv(ASSIGNMENTS_FILE)
        
        # --- NEW: Filter out Exams ---
        initial_count = len(df_assignments)
        df_assignments = df_assignments[~df_assignments['session_name'].str.contains('exam', case=False, na=False)]
        removed_count = initial_count - len(df_assignments)
        if removed_count > 0:
            print(f"Removed {removed_count} exam-related sessions.")

        # Get unique session names
        unique_sessions = df_assignments['session_name'].unique()
        
        # Create a mapping: session_name -> teacher_id
        teacher_mapping = {session: f"T_{i+1:03d}" for i, session in enumerate(unique_sessions)}
        
        # Update teacher_id column
        df_assignments['teacher_id'] = df_assignments['session_name'].map(teacher_mapping)
        
        df_assignments.to_csv(ASSIGNMENTS_FILE, index=False)
        print(f"Updated {ASSIGNMENTS_FILE} with generated teacher IDs.")
        
        # 3. Create Teachers Reference File
        teachers_data = []
        for session, t_id in teacher_mapping.items():
            teachers_data.append({
                'teacher_id': t_id,
                'name': f"Professor_{t_id}",
                'specialization': session.split(' ')[0]
            })
        
        df_teachers = pd.DataFrame(teachers_data)
        df_teachers.to_csv(TEACHERS_FILE, index=False)
        print(f"Created {TEACHERS_FILE} with {len(df_teachers)} teachers.")

if __name__ == "__main__":
    generate_data()

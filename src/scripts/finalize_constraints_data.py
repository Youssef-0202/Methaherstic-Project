import pandas as pd
import os

# Paths
DATA_DIR = 'data/processed'
ASSIGNMENTS_FILE = os.path.join(DATA_DIR, 'assignments.csv')
GROUPS_FILE = os.path.join(DATA_DIR, 'groups.csv')
PENALTIES_FILE = os.path.join(DATA_DIR, 'slot_penalties.csv')

def finalize_data_for_constraints():
    print("Finalizing data for constraint analysis...")

    # 1. Load Data
    df_assignments = pd.read_csv(ASSIGNMENTS_FILE)
    df_groups = pd.read_csv(GROUPS_FILE)
    group_list = df_groups['group_name'].tolist()

    # 2. Map Sessions to Groups (for H2: Group Conflict)
    def extract_groups(session_name):
        found = []
        # Special case for TC S1/S2/S3
        if "S1" in session_name and "TC" in session_name: found.append("S1")
        if "S2" in session_name and "TC" in session_name: found.append("S2")
        # General matching
        for g in group_list:
            if g in session_name and g not in found:
                # Avoid matching 'S1' inside 'S19' or 'MST' inside 'MDSIM'
                # But here group names are mostly unique enough
                found.append(g)
        
        # If no group found, assign to a default or keep empty
        return ";".join(found) if found else "Unknown"

    df_assignments['involved_groups'] = df_assignments['session_name'].apply(extract_groups)
    
    # 3. Define Slot Penalties (for S3: Session Timing)
    # We define penalties for each start_time
    # 08:30 -> 10 (Early)
    # 16:30 -> 5 (Late)
    # 18:30 -> 15 (Very Late)
    # Others -> 0
    times = df_assignments['start_time'].unique()
    penalty_map = []
    for t in times:
        p = 0
        if "08:30" in t: p = 10
        elif "16:30" in t: p = 5
        elif "17:30" in t: p = 10
        elif "18:30" in t: p = 15
        penalty_map.append({'start_time': t, 'penalty': p})
    
    df_penalties = pd.DataFrame(penalty_map)
    
    # 4. Save Updated Files
    df_assignments.to_csv(ASSIGNMENTS_FILE, index=False)
    df_penalties.to_csv(PENALTIES_FILE, index=False)
    
    print(f"Updated {ASSIGNMENTS_FILE} with 'involved_groups'.")
    print(f"Created {PENALTIES_FILE} for soft constraint S3.")

if __name__ == "__main__":
    finalize_data_for_constraints()

import pandas as pd
from collections import defaultdict

# Load the processed data
assignments_file = "data/processed/assignments.csv"
groups_file = "data/processed/groups.csv"
teachers_file = "data/processed/teachers.csv"

df_assignments = pd.read_csv(assignments_file)
df_groups = pd.read_csv(groups_file)
df_teachers = pd.read_csv(teachers_file)

print("="*80)
print("DATA VALIDATION REPORT")
print("="*80)

# --- 1. Check for Teacher Conflicts ---
print("\n--- TEACHER CONFLICTS ---")
teacher_conflicts = []
teacher_schedule = defaultdict(list)

for idx, row in df_assignments.iterrows():
    key = (row['teacher_id'], row['day'], row['start_time'])
    teacher_schedule[key].append({
        'session': row['session_name'],
        'room': row['room_id'],
        'groups': row['involved_groups']
    })

conflict_count = 0
for (teacher, day, time), sessions in teacher_schedule.items():
    if len(sessions) > 1:
        conflict_count += 1
        if conflict_count <= 10:  # Show first 10
            print(f"\n{teacher} on {day} at {time}: {len(sessions)} sessions")
            for sess in sessions:
                print(f"  - {sess['session'][:40]:<40} in {sess['room']:<6} (Groups: {sess['groups']})")

total_teacher_conflicts = sum(1 for sessions in teacher_schedule.values() if len(sessions) > 1)
print(f"\nTotal teacher conflicts: {total_teacher_conflicts}")

# --- 2. Check for Group Conflicts ---
print("\n" + "="*80)
print("--- GROUP CONFLICTS ---")
group_conflicts = []
group_schedule = defaultdict(list)

for idx, row in df_assignments.iterrows():
    # Split groups by ';'
    groups = row['involved_groups'].split(';')
    for group in groups:
        group = group.strip()
        key = (group, row['day'], row['start_time'])
        group_schedule[key].append({
            'session': row['session_name'],
            'room': row['room_id'],
            'teacher': row['teacher_id']
        })

conflict_count = 0
for (group, day, time), sessions in group_schedule.items():
    if len(sessions) > 1 and group != "Unknown":
        conflict_count += 1
        if conflict_count <= 10:  # Show first 10
            print(f"\n{group} on {day} at {time}: {len(sessions)} sessions")
            for sess in sessions:
                print(f"  - {sess['session'][:40]:<40} in {sess['room']:<6} by {sess['teacher']}")

total_group_conflicts = sum(1 for (g, _, _), sessions in group_schedule.items()
                             if len(sessions) > 1 and g != "Unknown")
print(f"\nTotal group conflicts: {total_group_conflicts}")

# --- 3. Room Capacity Check ---
print("\n" + "="*80)
print("--- ROOM CAPACITY VALIDATION ---")
df_rooms = pd.read_csv("data/processed/rooms.csv")
room_capacity = dict(zip(df_rooms['room_id'], df_rooms['capacity']))

capacity_violations = []
for idx, row in df_assignments.iterrows():
    groups = row['involved_groups'].split(';')
    total_students = 0

    for group in groups:
        group = group.strip()
        if group in df_groups['group_name'].values:
            group_size = df_groups[df_groups['group_name'] == group]['size'].values[0]
            total_students += group_size

    room_cap = room_capacity.get(row['room_id'], 0)

    if total_students > room_cap:
        capacity_violations.append({
            'session': row['session_name'],
            'room': row['room_id'],
            'room_capacity': room_cap,
            'students': total_students,
            'groups': row['involved_groups']
        })

if capacity_violations:
    print(f"\nFound {len(capacity_violations)} capacity violations:")
    for violation in capacity_violations[:10]:
        print(f"  - {violation['session'][:40]:<40} in {violation['room']:<6}")
        print(f"    Capacity: {violation['room_capacity']}, Students: {violation['students']} (Groups: {violation['groups']})")
else:
    print("\n[OK] No room capacity violations found!")

# --- 4. Summary ---
print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"\nTotal assignments: {len(df_assignments)}")
print(f"Teacher conflicts: {total_teacher_conflicts}")
print(f"Group conflicts: {total_group_conflicts}")
print(f"Room capacity violations: {len(capacity_violations)}")
print(f"Unknown group assignments: {len(df_assignments[df_assignments['involved_groups'].str.contains('Unknown', na=False)])}")

# --- 5. Comparison with Root Cause Analysis ---
print("\n" + "="*80)
print("COMPARISON WITH OLD DATA (from ROOT_CAUSE_ANALYSIS.md)")
print("="*80)
print("\nOLD DATA:")
print("  - 68 Unknown group assignments (37.4%)")
print("  - 54 teacher conflicts")
print("  - 124 group conflicts")
print("\nNEW DATA:")
print(f"  - {len(df_assignments[df_assignments['involved_groups'].str.contains('Unknown', na=False)])} Unknown group assignments ({len(df_assignments[df_assignments['involved_groups'].str.contains('Unknown', na=False)])/len(df_assignments)*100:.1f}%)")
print(f"  - {total_teacher_conflicts} teacher conflicts")
print(f"  - {total_group_conflicts} group conflicts")

improvement_unknown = 68 - len(df_assignments[df_assignments['involved_groups'].str.contains('Unknown', na=False)])
improvement_teacher = 54 - total_teacher_conflicts
improvement_group = 124 - total_group_conflicts

print("\nIMPROVEMENTS:")
print(f"  - Unknown groups reduced by: {improvement_unknown} ({improvement_unknown/68*100:.1f}%)")
print(f"  - Teacher conflicts reduced by: {improvement_teacher} ({improvement_teacher/54*100:.1f}%)")
print(f"  - Group conflicts reduced by: {improvement_group} ({improvement_group/124*100:.1f}%)")

print("\n" + "="*80)
print("DATA QUALITY ASSESSMENT")
print("="*80)

if total_teacher_conflicts == 0 and total_group_conflicts == 0:
    print("\n[EXCELLENT] Data is now CONFLICT-FREE and ready for optimization!")
elif total_teacher_conflicts + total_group_conflicts < 10:
    print("\n[VERY GOOD] Data quality is excellent with minimal conflicts.")
    print("The remaining conflicts can likely be resolved by the optimization algorithm.")
elif total_teacher_conflicts + total_group_conflicts < 50:
    print("\n[GOOD] Data quality significantly improved.")
    print("Remaining conflicts are manageable for the optimization algorithm.")
else:
    print("\n[NEEDS IMPROVEMENT] Some conflicts remain.")
    print("Consider further manual data refinement for better results.")

print("\n" + "="*80)

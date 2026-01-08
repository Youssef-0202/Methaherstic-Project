import pandas as pd
import numpy as np
from collections import defaultdict, Counter

# Load all datasets
assignments_df = pd.read_csv('data/processed/assignments.csv')
groups_df = pd.read_csv('data/processed/groups.csv')
teachers_df = pd.read_csv('data/processed/teachers.csv')
rooms_df = pd.read_csv('data/processed/rooms.csv')

print('='*80)
print('DATA EXTRACTION ROOT CAUSE ANALYSIS')
print('='*80)

# Analysis 1: Check for involved_groups issues
print('\n1. INVOLVED GROUPS ANALYSIS')
print('-'*80)
print(f'Total assignments: {len(assignments_df)}')

# Count Unknown groups
unknown_count = assignments_df['involved_groups'].str.contains('Unknown', na=False).sum()
print(f'Assignments with "Unknown" groups: {unknown_count}')

# Show sample Unknown entries
print('\nSample assignments with Unknown groups:')
unknown_samples = assignments_df[assignments_df['involved_groups'].str.contains('Unknown', na=False)].head(5)
for idx, row in unknown_samples.iterrows():
    print(f'  {row["session_name"]} | {row["session_type"]} | Groups: {row["involved_groups"]}')

# Analysis 2: Check for multi-group sessions that should be split
print('\n2. MULTI-GROUP SESSION ANALYSIS')
print('-'*80)
multi_group = assignments_df[assignments_df['involved_groups'].str.contains(';', na=False)]
print(f'Assignments with multiple groups (using ;): {len(multi_group)}')

# Show examples
print('\nSample multi-group assignments:')
for idx, row in multi_group.head(5).iterrows():
    groups = row['involved_groups'].split(';')
    print(f'  {row["session_name"]} - {len(groups)} groups: {row["involved_groups"]}')

# Analysis 3: Teacher conflict analysis
print('\n3. TEACHER CONFLICTS IN ORIGINAL DATA')
print('-'*80)
teacher_schedule = defaultdict(list)

for idx, row in assignments_df.iterrows():
    key = (row['day'], row['start_time'])
    teacher_id = row['teacher_id']
    teacher_schedule[teacher_id].append(key)

conflicts = 0
conflict_details = []
for teacher, slots in teacher_schedule.items():
    slot_counts = Counter(slots)
    for slot, count in slot_counts.items():
        if count > 1:
            conflicts += (count - 1)
            conflict_details.append((teacher, slot, count))

print(f'Teacher conflicts in original data: {conflicts}')
if conflict_details:
    print('\nSample teacher conflicts:')
    for teacher, slot, count in conflict_details[:10]:
        print(f'  Teacher {teacher} at {slot}: {count} sessions simultaneously')

# Analysis 4: Group size validation
print('\n4. GROUP SIZE VALIDATION')
print('-'*80)
group_size_map = dict(zip(groups_df['group_name'], groups_df['size']))
print(f'Defined groups: {len(group_size_map)}')

# Extract unique groups from assignments
all_groups = set()
for groups_str in assignments_df['involved_groups'].dropna():
    for g in groups_str.split(';'):
        all_groups.add(g.strip())

missing_groups = [g for g in all_groups if g not in group_size_map and g != 'Unknown']
print(f'Groups in assignments but not in groups.csv: {len(missing_groups)}')
if missing_groups:
    print(f'Missing groups: {missing_groups[:10]}')

# Analysis 5: Session extraction and duplication
print('\n5. SESSION EXTRACTION ANALYSIS')
print('-'*80)
session_count = 0
for idx, row in assignments_df.iterrows():
    groups = row['involved_groups'].split(';') if pd.notna(row['involved_groups']) else []
    session_count += len(groups)

print(f'Total sessions after extraction: {session_count}')
print(f'Expected from notebook: 224 sessions')

# Analysis 6: Group conflicts analysis (same group, same slot)
print('\n6. GROUP CONFLICTS IN EXTRACTED SESSIONS')
print('-'*80)
group_schedule = defaultdict(list)
extracted_sessions = []

for idx, row in assignments_df.iterrows():
    groups = row['involved_groups'].split(';') if pd.notna(row['involved_groups']) else []
    for group in groups:
        session_info = {
            'session_name': row['session_name'],
            'session_type': row['session_type'],
            'teacher_id': row['teacher_id'],
            'group_name': group.strip(),
            'day': row['day'],
            'start_time': row['start_time']
        }
        extracted_sessions.append(session_info)
        key = (row['day'], row['start_time'], group.strip())
        group_schedule[key].append(session_info)

group_conflicts = 0
conflict_examples = []
for key, sessions in group_schedule.items():
    if len(sessions) > 1:
        group_conflicts += (len(sessions) - 1)
        conflict_examples.append((key, sessions))

print(f'Group conflicts (same group, same time): {group_conflicts}')
if conflict_examples:
    print('\nSample group conflicts:')
    for key, sessions in conflict_examples[:5]:
        day, time, group = key
        print(f'  {group} at {day} {time}: {len(sessions)} sessions')
        for s in sessions:
            print(f'    - {s["session_name"]} ({s["session_type"]}) by {s["teacher_id"]}')

print('\n' + '='*80)
print('SUMMARY OF ISSUES')
print('='*80)
print(f'1. Assignments with Unknown groups: {unknown_count}')
print(f'2. Teacher conflicts in original data: {conflicts}')
print(f'3. Group conflicts after extraction: {group_conflicts}')
print(f'4. Missing group definitions: {len(missing_groups)}')
print(f'5. Total extracted sessions: {session_count}')
print('='*80)

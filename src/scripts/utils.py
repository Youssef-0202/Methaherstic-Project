import pandas as pd
import os
from typing import List, Dict
from .models import Room, Course, Group, Teacher, Assignment, Slot

def load_data(data_dir: str):
    """
    Load data from CSV files into dictionaries of objects.
    """
    print(f"Loading data from {data_dir}...")
    
    # Load Rooms
    df_rooms = pd.read_csv(os.path.join(data_dir, 'rooms.csv'))
    rooms = {}
    for _, row in df_rooms.iterrows():
        r = Room(
            room_id=str(row['room_id']), 
            capacity=int(row['capacity']), 
            type=row['type']
        )
        rooms[r.room_id] = r
        
    # Load Courses
    df_courses = pd.read_csv(os.path.join(data_dir, 'courses.csv'))
    courses = {}
    for _, row in df_courses.iterrows():
        c_name = str(row['course_name'])
        c = Course(course_name=c_name)
        courses[c_name] = c
        
    # Load Groups
    df_groups = pd.read_csv(os.path.join(data_dir, 'groups.csv'))
    groups = {}
    for _, row in df_groups.iterrows():
        g_id = str(row['group_id'])
        g = Group(group_id=g_id, size=int(row['size']))
        groups[g_id] = g
        
    # Load Teachers
    df_teachers = pd.read_csv(os.path.join(data_dir, 'teachers.csv'))
    teachers = {}
    for _, row in df_teachers.iterrows():
        t_id = str(row['teacher_id'])
        t = Teacher(teacher_id=t_id, name=t_id)
        teachers[t_id] = t
        
    # Load Initial Assignments (The "Solution" from Excel)
    df_assign = pd.read_csv(os.path.join(data_dir, 'assignments.csv'))
    assignments = []
    for _, row in df_assign.iterrows():
        # Parse duration string "4h" -> 4.0
        dur_str = str(row['duration']).replace('h', '')
        duration_val = float(dur_str)
        
        slot = Slot(
            day=row['day'], 
            start_time=row['start_time'], 
            duration=duration_val
        )
        
        a = Assignment(
            course_name=str(row['course_name']),
            group_id=str(row['group_id']),
            teacher_id=str(row['teacher_id']),
            room_id=str(row['room_id']),
            slot=slot,
            type=row['type']
        )
        assignments.append(a)
        
    print(f"Loaded {len(rooms)} rooms, {len(courses)} courses, {len(groups)} groups, {len(teachers)} teachers.")
    print(f"Loaded {len(assignments)} existing assignments.")
    
    return rooms, courses, groups, teachers, assignments

def save_solution(assignments: List[Assignment], output_path: str):
    data = []
    for a in assignments:
        data.append({
            'day': a.slot.day,
            'start_time': a.slot.start_time,
            'duration': a.slot.duration,
            'room_id': a.room_id,
            'course_name': a.course_name,
            'group_id': a.group_id,
            'teacher_id': a.teacher_id,
            'type': a.type
        })
    
    df = pd.DataFrame(data)
    df.to_csv(output_path, index=False)
    print(f"Solution saved to {output_path}")

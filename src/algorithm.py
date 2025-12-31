import random
import math
import copy
from typing import List, Dict
from .models import Assignment, Room, Teacher, Group, Slot

class TimetableSolver:
    def __init__(self, rooms: Dict[str, Room], courses: Dict[str, object], 
                 groups: Dict[str, Group], teachers: Dict[str, Teacher], 
                 initial_solution: List[Assignment]):
        self.rooms = rooms
        self.courses = courses
        self.groups = groups
        self.teachers = teachers
        self.current_solution = copy.deepcopy(initial_solution)
        self.best_solution = copy.deepcopy(initial_solution)
        
        # Weights
        self.w_hard = 1000
        self.w_soft = 1
        
    def calculate_cost(self, solution: List[Assignment]) -> float:
        hard_cost = self.calculate_hard_constraints(solution)
        soft_cost = self.calculate_soft_constraints(solution)
        return (hard_cost * self.w_hard) + (soft_cost * self.w_soft)
    
    def calculate_hard_constraints(self, solution: List[Assignment]) -> int:
        violations = 0
        
        # 1. Teacher Conflict: A teacher cannot be in two places at once
        # Map: teacher_id -> list of (start_time, end_time, day)
        teacher_schedule = {}
        
        # 2. Group Conflict: A group cannot be in two places at once
        group_schedule = {}
        
        # 3. Room Conflict: A room cannot host two courses at once
        room_schedule = {}
        
        for assign in solution:
            # Time range calculation
            # Simplified: Convert time string "HH:MM" to minutes from midnight for comparison
            day = assign.slot.day
            start_min = self._time_to_minutes(assign.slot.start_time)
            end_min = start_min + int(assign.slot.duration * 60)
            
            # Check Teacher
            t_id = assign.teacher_id
            if t_id not in teacher_schedule: teacher_schedule[t_id] = []
            for s, e, d in teacher_schedule[t_id]:
                if d == day and max(start_min, s) < min(end_min, e): # Overlap
                    violations += 1
            teacher_schedule[t_id].append((start_min, end_min, day))
            
            # Check Group
            g_id = assign.group_id
            if g_id not in group_schedule: group_schedule[g_id] = []
            for s, e, d in group_schedule[g_id]:
                if d == day and max(start_min, s) < min(end_min, e):
                    violations += 1
            group_schedule[g_id].append((start_min, end_min, day))
            
            # Check Room
            r_id = assign.room_id
            if r_id not in room_schedule: room_schedule[r_id] = []
            for s, e, d in room_schedule[r_id]:
                if d == day and max(start_min, s) < min(end_min, e):
                    violations += 1
            room_schedule[r_id].append((start_min, end_min, day))
            
            # 4. Room Capacity
            if r_id in self.rooms:
                room_cap = self.rooms[r_id].capacity
                group_size = self.groups[assign.group_id].size if assign.group_id in self.groups else 30
                if group_size > room_cap:
                    violations += 1
            
            # 5. Room Type (Simplified)
            # If course is TP, needs Lab (not Amphitheater)
            # This depends on data quality, skipping for now or adding basic check
            
        return violations

    def calculate_soft_constraints(self, solution: List[Assignment]) -> int:
        # Placeholder for soft constraints (Gaps, etc.)
        return 0

    def _time_to_minutes(self, time_str: str) -> int:
        h, m = map(int, time_str.split(':'))
        return h * 60 + m

    def solve(self, max_iterations=1000, initial_temp=100.0, cooling_rate=0.95):
        current_cost = self.calculate_cost(self.current_solution)
        best_cost = current_cost
        temp = initial_temp
        
        print(f"Initial Cost: {current_cost}")
        
        for i in range(max_iterations):
            # Generate Neighbor (TODO)
            # neighbor = self.get_neighbor(self.current_solution)
            # neighbor_cost = self.calculate_cost(neighbor)
            
            # Acceptance Probability (Metropolis)
            # ...
            
            temp *= cooling_rate
            
        return self.best_solution

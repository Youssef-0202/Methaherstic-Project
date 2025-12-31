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

    def get_neighbor(self, solution: List[Assignment]) -> List[Assignment]:
        neighbor = copy.deepcopy(solution)
        
        # Randomly select a move type: 
        # 1. Move: Change slot/room for one assignment
        # 2. Swap: Swap slots/rooms between two assignments
        move_type = random.choice(['move', 'swap'])
        
        if move_type == 'move' and neighbor:
            # Pick random assignment
            idx = random.randint(0, len(neighbor) - 1)
            assign = neighbor[idx]
            
            # Pick random new slot
            # For simplicity, pick a random day and time (8:30 - 18:30)
            days = ['LUNDI', 'MARDI', 'MERCREDI', 'JEUDI', 'VENDREDI', 'SAMEDI']
            times = ['08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30', 
                     '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', 
                     '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30']
            
            new_day = random.choice(days)
            new_time = random.choice(times)
            
            # Pick random new room
            new_room_id = random.choice(list(self.rooms.keys()))
            
            # Update assignment
            assign.slot.day = new_day
            assign.slot.start_time = new_time
            assign.room_id = new_room_id
            
        elif move_type == 'swap' and len(neighbor) >= 2:
            idx1, idx2 = random.sample(range(len(neighbor)), 2)
            
            # Swap Slot and Room
            neighbor[idx1].slot.day, neighbor[idx2].slot.day = neighbor[idx2].slot.day, neighbor[idx1].slot.day
            neighbor[idx1].slot.start_time, neighbor[idx2].slot.start_time = neighbor[idx2].slot.start_time, neighbor[idx1].slot.start_time
            neighbor[idx1].room_id, neighbor[idx2].room_id = neighbor[idx2].room_id, neighbor[idx1].room_id
            
        return neighbor

    def solve(self, max_iterations=1000, initial_temp=1000.0, cooling_rate=0.99):
        current_cost = self.calculate_cost(self.current_solution)
        self.best_solution = copy.deepcopy(self.current_solution)
        best_cost = current_cost
        
        temp = initial_temp
        
        print(f"Starting SA: Temp={temp}, Cost={current_cost}")
        
        for i in range(max_iterations):
            neighbor = self.get_neighbor(self.current_solution)
            neighbor_cost = self.calculate_cost(neighbor)
            
            delta = neighbor_cost - current_cost
            
            # Acceptance Probability
            if delta < 0 or random.random() < math.exp(-delta / temp):
                self.current_solution = neighbor
                current_cost = neighbor_cost
                
                if current_cost < best_cost:
                    best_cost = current_cost
                    self.best_solution = copy.deepcopy(neighbor)
                    print(f"Iter {i}: New Best Cost = {best_cost}")
            
            temp *= cooling_rate
            
            if i % 100 == 0:
                print(f"Iter {i}: Temp={temp:.2f}, Cost={current_cost}")
                
        return self.best_solution

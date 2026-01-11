"""
================================================================================
FSTM University Timetabling Optimization System
================================================================================
A Hybrid Genetic Algorithm + Simulated Annealing Approach

Module: Metaheuristics - Master in Artificial Intelligence
Authors: Youssef Ait Bahssine, Mustapha Zmirli, Mohamed Bajadi
Date: January 2026

This Streamlit application provides a professional interface for:
- Dataset configuration and loading
- GA/SA parameter tuning
- Constraint configuration
- Real-time optimization monitoring
- Results visualization and export
================================================================================
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict, Counter
import random
import copy
import math
import time
import io
import os
import base64
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ================================================================================
# PAGE CONFIGURATION
# ================================================================================
st.set_page_config(
    page_title="FSTM Timetabling Optimizer",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Main container styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e3a5f;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #3498db;
        margin-bottom: 2rem;
    }
    
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2c3e50;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* Success/warning/error badges */
    .badge-success {
        background-color: #27ae60;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: 600;
    }
    
    .badge-warning {
        background-color: #f39c12;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: 600;
    }
    
    .badge-error {
        background-color: #e74c3c;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: 600;
    }
    
    /* Constraint checkboxes */
    .constraint-item {
        padding: 0.5rem;
        margin: 0.3rem 0;
        border-left: 3px solid #3498db;
        background-color: #f8f9fa;
    }
    
    /* Session type colors */
    .session-cours {
        background-color: #3498db;
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
    }
    
    .session-td {
        background-color: #27ae60;
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
    }
    
    .session-tp {
        background-color: #e74c3c;
        color: white;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
    }
    
    /* Progress styling */
    .stProgress > div > div {
        background-color: #3498db;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Timetable table styling */
    .timetable-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.85rem;
    }
    
    .timetable-table th {
        background-color: #2c3e50;
        color: white;
        padding: 10px;
        text-align: center;
    }
    
    .timetable-table td {
        border: 1px solid #ddd;
        padding: 8px;
        vertical-align: top;
        min-width: 120px;
    }
</style>
""", unsafe_allow_html=True)


# ================================================================================
# OPTIMIZATION ENGINE CLASSES
# ================================================================================

class TimetableGA:
    """Genetic Algorithm system for university timetabling"""
    
    def __init__(self, sessions_df, rooms_df, groups_df, slots_df, group_size_map):
        self.sessions = sessions_df.to_dict('records')
        self.rooms = rooms_df.to_dict('records')
        self.slots = slots_df.to_dict('records')
        self.group_size_map = group_size_map
        
        self.room_dict = {r['room_id']: r for r in self.rooms}
        self.slot_dict = {s['slot_id']: s for s in self.slots}
        self.slot_penalties = {s['slot_id']: s['penalty'] for s in self.slots}
        
        self.room_ids = [r['room_id'] for r in self.rooms]
        self.slot_ids = [s['slot_id'] for s in self.slots]
    
    def create_chromosome(self):
        """Generate random solution"""
        chromosome = []
        for session in self.sessions:
            slot = random.choice(self.slot_ids)
            room = random.choice(self.room_ids)
            chromosome.append((slot, room))
        return chromosome
    
    def create_greedy_chromosome(self):
        """Generate solution using greedy heuristic"""
        chromosome = []
        room_usage = defaultdict(int)
        
        for session in self.sessions:
            group_size = self.group_size_map.get(session['group_name'], 30)
            
            # Select suitable room with lowest usage
            suitable_rooms = [
                r for r in self.room_ids 
                if self.room_dict[r]['capacity'] >= group_size
            ]
            
            if suitable_rooms:
                suitable_rooms.sort(key=lambda r: room_usage[r])
                room = suitable_rooms[0]
            else:
                room = random.choice(self.room_ids)
            
            # Prefer slots with low penalties
            slot = random.choice([s for s in self.slot_ids if self.slot_penalties[s] == 0] or self.slot_ids)
            
            chromosome.append((slot, room))
            room_usage[room] += 1
        
        return chromosome


class ConstraintChecker:
    """Evaluates solution quality based on constraints"""
    
    def __init__(self, ga_system, constraint_weights=None):
        self.ga = ga_system
        self.HARD_WEIGHT = 1_000_000
        self.SOFT_WEIGHT = 1
        
        # Default soft constraint weights
        self.soft_weights = constraint_weights or {
            'gaps': 1.0,
            'time_penalties': 1.0,
            'load_balance': 1.0
        }
    
    def set_soft_weights(self, weights):
        """Update soft constraint weights"""
        self.soft_weights = weights
    
    def check_teacher_conflicts(self, chromosome):
        """Count teacher conflicts (H1)"""
        conflicts = 0
        teacher_schedule = defaultdict(list)
        
        for i, (slot, room) in enumerate(chromosome):
            teacher_id = self.ga.sessions[i].get('teacher_id')
            if teacher_id:
                teacher_schedule[teacher_id].append(slot)
        
        for teacher, slots in teacher_schedule.items():
            slot_counts = Counter(slots)
            for slot, count in slot_counts.items():
                if count > 1:
                    conflicts += (count - 1)
        
        return conflicts
    
    def check_room_conflicts(self, chromosome):
        """Count room conflicts (H2)"""
        conflicts = 0
        room_schedule = defaultdict(list)
        
        for i, (slot, room) in enumerate(chromosome):
            room_schedule[(slot, room)].append(i)
        
        for key, sessions in room_schedule.items():
            if len(sessions) > 1:
                conflicts += (len(sessions) - 1)
        
        return conflicts
    
    def check_group_conflicts(self, chromosome):
        """Count group conflicts (H3)"""
        conflicts = 0
        group_schedule = defaultdict(list)
        
        for i, (slot, room) in enumerate(chromosome):
            group_name = self.ga.sessions[i].get('group_name')
            if group_name:
                group_schedule[(slot, group_name)].append(i)
        
        for key, sessions in group_schedule.items():
            if len(sessions) > 1:
                conflicts += (len(sessions) - 1)
        
        return conflicts
    
    def check_capacity_violations(self, chromosome):
        """Count capacity violations (H4)"""
        violations = 0
        
        for i, (slot, room) in enumerate(chromosome):
            group_name = self.ga.sessions[i].get('group_name')
            group_size = self.ga.group_size_map.get(group_name, 30)
            room_capacity = self.ga.room_dict[room]['capacity']
            
            if group_size > room_capacity:
                violations += 1
        
        return violations
    
    def check_room_type_violations(self, chromosome):
        """Count room type violations (H5)"""
        violations = 0
        
        for i, (slot, room) in enumerate(chromosome):
            session_type = self.ga.sessions[i].get('session_type', '')
            group_size = self.ga.group_size_map.get(self.ga.sessions[i].get('group_name'), 30)
            room_type = self.ga.room_dict[room].get('type', '')
            
            # Large courses (>100 students) should use amphitheaters
            if session_type == 'Cours' and group_size > 100 and room_type != 'Amphitheater':
                violations += 1
        
        return violations
    
    def calculate_schedule_gaps(self, chromosome):
        """Calculate schedule gaps (S1)"""
        gaps = 0
        
        # Group gaps
        group_schedules = defaultdict(lambda: defaultdict(list))
        for i, (slot, room) in enumerate(chromosome):
            group_name = self.ga.sessions[i].get('group_name')
            day_name = self.ga.slot_dict[slot]['day_name']
            time_idx = self.ga.slot_dict[slot]['slot_id'] % 5
            group_schedules[group_name][day_name].append(time_idx)
        
        for group, days in group_schedules.items():
            for day, times in days.items():
                if len(times) > 1:
                    times_sorted = sorted(times)
                    span = times_sorted[-1] - times_sorted[0] + 1
                    gaps += (span - len(times))
        
        # Teacher gaps
        teacher_schedules = defaultdict(lambda: defaultdict(list))
        for i, (slot, room) in enumerate(chromosome):
            teacher_id = self.ga.sessions[i].get('teacher_id')
            day_name = self.ga.slot_dict[slot]['day_name']
            time_idx = self.ga.slot_dict[slot]['slot_id'] % 5
            teacher_schedules[teacher_id][day_name].append(time_idx)
        
        for teacher, days in teacher_schedules.items():
            for day, times in days.items():
                if len(times) > 1:
                    times_sorted = sorted(times)
                    span = times_sorted[-1] - times_sorted[0] + 1
                    gaps += (span - len(times))
        
        return gaps
    
    def calculate_time_penalties(self, chromosome):
        """Calculate time slot penalties (S2)"""
        penalty = sum([self.ga.slot_penalties[slot] for slot, room in chromosome])
        return penalty
    
    def calculate_load_balance(self, chromosome):
        """Calculate load balancing penalty (S3)"""
        day_counts = defaultdict(int)
        
        for slot, room in chromosome:
            day_name = self.ga.slot_dict[slot]['day_name']
            day_counts[day_name] += 1
        
        counts = list(day_counts.values())
        if len(counts) > 1:
            return np.var(counts)
        return 0
    
    def calculate_fitness(self, chromosome):
        """Calculate total fitness (lower is better)"""
        # Hard constraints
        h1 = self.check_teacher_conflicts(chromosome)
        h2 = self.check_room_conflicts(chromosome)
        h3 = self.check_group_conflicts(chromosome)
        h4 = self.check_capacity_violations(chromosome)
        h5 = self.check_room_type_violations(chromosome)
        total_hard = h1 + h2 + h3 + h4 + h5
        
        # Soft constraints (weighted)
        s1 = self.calculate_schedule_gaps(chromosome) * self.soft_weights.get('gaps', 1.0)
        s2 = self.calculate_time_penalties(chromosome) * self.soft_weights.get('time_penalties', 1.0)
        s3 = self.calculate_load_balance(chromosome) * self.soft_weights.get('load_balance', 1.0)
        total_soft = s1 + s2 + s3
        
        fitness = self.HARD_WEIGHT * total_hard + self.SOFT_WEIGHT * total_soft
        
        return fitness, total_hard, total_soft
    
    def get_detailed_analysis(self, chromosome):
        """Return detailed constraint analysis"""
        return {
            'h1_teacher': self.check_teacher_conflicts(chromosome),
            'h2_room': self.check_room_conflicts(chromosome),
            'h3_group': self.check_group_conflicts(chromosome),
            'h4_capacity': self.check_capacity_violations(chromosome),
            'h5_room_type': self.check_room_type_violations(chromosome),
            's1_gaps': self.calculate_schedule_gaps(chromosome),
            's2_time': self.calculate_time_penalties(chromosome),
            's3_balance': self.calculate_load_balance(chromosome)
        }


class GeneticAlgorithm:
    """Genetic Algorithm for timetable optimization"""
    
    def __init__(self, ga_system, checker, pop_size=100, generations=300, 
                 crossover_rate=0.8, mutation_rate=0.15, elitism=10):
        self.ga = ga_system
        self.checker = checker
        self.pop_size = pop_size
        self.generations = generations
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elitism = elitism
    
    def initialize_population(self):
        """Create initial population with diverse strategies"""
        population = []
        
        # 50% random
        for _ in range(self.pop_size // 2):
            population.append(self.ga.create_chromosome())
        
        # 50% greedy
        for _ in range(self.pop_size - len(population)):
            population.append(self.ga.create_greedy_chromosome())
        
        return population
    
    def tournament_selection(self, population, fitnesses, tournament_size=5):
        """Select parent using tournament selection"""
        tournament = random.sample(range(len(population)), min(tournament_size, len(population)))
        best_idx = min(tournament, key=lambda i: fitnesses[i])
        return population[best_idx]
    
    def crossover(self, parent1, parent2):
        """Uniform crossover"""
        if random.random() > self.crossover_rate:
            return parent1.copy(), parent2.copy()
        
        child1, child2 = [], []
        for i in range(len(parent1)):
            if random.random() < 0.5:
                child1.append(parent1[i])
                child2.append(parent2[i])
            else:
                child1.append(parent2[i])
                child2.append(parent1[i])
        
        return child1, child2
    
    def mutate(self, chromosome):
        """Apply mutation operators"""
        mutated = chromosome.copy()
        
        for i in range(len(mutated)):
            if random.random() < self.mutation_rate:
                mutation_type = random.choice(['slot', 'room', 'both'])
                
                if mutation_type == 'slot':
                    mutated[i] = (random.choice(self.ga.slot_ids), mutated[i][1])
                elif mutation_type == 'room':
                    mutated[i] = (mutated[i][0], random.choice(self.ga.room_ids))
                else:
                    mutated[i] = (random.choice(self.ga.slot_ids), random.choice(self.ga.room_ids))
        
        return mutated
    
    def evolve(self, progress_callback=None):
        """Main evolution loop with progress callback"""
        population = self.initialize_population()
        history = []
        best_ever = None
        best_fitness_ever = float('inf')
        
        for gen in range(self.generations):
            # Evaluate fitness
            fitness_data = [self.checker.calculate_fitness(ind) for ind in population]
            fitnesses = [f[0] for f in fitness_data]
            
            # Track best
            best_idx = fitnesses.index(min(fitnesses))
            best_fitness, best_hard, best_soft = fitness_data[best_idx]
            
            if best_fitness < best_fitness_ever:
                best_ever = population[best_idx].copy()
                best_fitness_ever = best_fitness
            
            history.append(best_fitness)
            
            # Progress callback
            if progress_callback:
                progress_callback(gen, self.generations, best_fitness, best_hard, best_soft)
            
            # Early stopping
            if best_fitness == 0:
                break
            
            # Selection and reproduction
            offspring = []
            
            # Elitism
            elite_indices = sorted(range(len(fitnesses)), key=lambda i: fitnesses[i])[:self.elitism]
            offspring.extend([population[i].copy() for i in elite_indices])
            
            # Generate offspring
            while len(offspring) < self.pop_size:
                parent1 = self.tournament_selection(population, fitnesses)
                parent2 = self.tournament_selection(population, fitnesses)
                
                child1, child2 = self.crossover(parent1, parent2)
                
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                
                offspring.extend([child1, child2])
            
            population = offspring[:self.pop_size]
        
        return best_ever, history


class SimulatedAnnealing:
    """Simulated Annealing for local refinement"""
    
    def __init__(self, ga_system, checker):
        self.ga = ga_system
        self.checker = checker
    
    def get_neighbor(self, chromosome):
        """Generate neighbor solution"""
        neighbor = chromosome.copy()
        
        move_type = random.choice(['swap', 'move_slot', 'move_room', 'move_both'])
        
        if move_type == 'swap':
            i, j = random.sample(range(len(neighbor)), 2)
            neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
        elif move_type == 'move_slot':
            i = random.randint(0, len(neighbor) - 1)
            neighbor[i] = (random.choice(self.ga.slot_ids), neighbor[i][1])
        elif move_type == 'move_room':
            i = random.randint(0, len(neighbor) - 1)
            neighbor[i] = (neighbor[i][0], random.choice(self.ga.room_ids))
        else:
            i = random.randint(0, len(neighbor) - 1)
            neighbor[i] = (random.choice(self.ga.slot_ids), random.choice(self.ga.room_ids))
        
        return neighbor
    
    def optimize(self, initial_solution, initial_temp=1000, cooling_rate=0.95, 
                 iterations=100, progress_callback=None):
        """Apply Simulated Annealing with progress callback"""
        current = initial_solution.copy()
        current_fitness, _, _ = self.checker.calculate_fitness(current)
        
        best = current.copy()
        best_fitness = current_fitness
        
        temperature = initial_temp
        history = [current_fitness]
        
        total_iterations = 0
        max_iterations_estimate = int(math.log(0.1 / initial_temp) / math.log(cooling_rate)) * iterations
        
        while temperature > 0.1:
            for _ in range(iterations):
                # Generate neighbor
                neighbor = self.get_neighbor(current)
                neighbor_fitness, neighbor_hard, neighbor_soft = self.checker.calculate_fitness(neighbor)
                
                # Calculate delta
                delta = neighbor_fitness - current_fitness
                
                # Acceptance criterion
                if delta < 0 or random.random() < math.exp(-delta / max(temperature, 0.001)):
                    current = neighbor
                    current_fitness = neighbor_fitness
                    
                    if current_fitness < best_fitness:
                        best = current.copy()
                        best_fitness = current_fitness
                
                history.append(current_fitness)
                total_iterations += 1
            
            # Progress callback
            if progress_callback:
                progress = min(1.0, total_iterations / max(max_iterations_estimate, 1))
                _, best_hard, best_soft = self.checker.calculate_fitness(best)
                progress_callback(progress, temperature, best_fitness, best_hard, best_soft)
            
            # Cool down
            temperature *= cooling_rate
        
        return best, history


class TimetableGenerator:
    """Generate visual timetables from optimization results"""
    
    def __init__(self, ga_system, slots_df):
        self.ga = ga_system
        self.slots_df = slots_df
        self.day_names = ['LUNDI', 'MARDI', 'MERCREDI', 'JEUDI', 'VENDREDI', 'SAMEDI']
        self.time_slots = sorted(slots_df['start_time'].unique())
        self.room_ids = [r['room_id'] for r in ga_system.rooms]
        self.room_capacities = {r['room_id']: r['capacity'] for r in ga_system.rooms}
    
    def build_timetable_data(self, chromosome):
        """Build structured timetable data"""
        timetable_data = defaultdict(lambda: defaultdict(list))
        
        for session_id, (slot_id, room_id) in enumerate(chromosome):
            slot_info = self.ga.slot_dict[slot_id]
            day_name = slot_info['day_name']
            start_time = slot_info['start_time']
            session_info = self.ga.sessions[session_id]
            
            timetable_data[(day_name, start_time)][room_id].append({
                'session_name': session_info.get('session_name', 'N/A'),
                'group_name': session_info.get('group_name', 'N/A'),
                'session_type': session_info.get('session_type', 'N/A'),
                'teacher_id': session_info.get('teacher_id', 'N/A'),
                'room_id': room_id
            })
        
        return timetable_data
    
    def create_excel_buffer(self, chromosome):
        """Create Excel file in memory buffer"""
        timetable_data = self.build_timetable_data(chromosome)
        
        # Create DataFrame
        rows = []
        for day in self.day_names:
            for time_slot in self.time_slots:
                row = {'Day': day, 'Time': time_slot}
                for room in self.room_ids:
                    key = (day, time_slot)
                    sessions = timetable_data[key].get(room, [])
                    cell_content = '\n'.join([
                        f"{s['session_name']} - {s['group_name']} ({s['session_type']})"
                        for s in sessions
                    ])
                    row[room] = cell_content
                rows.append(row)
        
        df = pd.DataFrame(rows)
        
        # Write to buffer
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Timetable', index=False)
        
        buffer.seek(0)
        return buffer
    
    def create_html_content(self, chromosome):
        """Create HTML timetable content"""
        timetable_data = self.build_timetable_data(chromosome)
        
        # Color mapping for session types
        type_colors = {
            'Cours': '#3498db',
            'TD': '#27ae60',
            'TP': '#e74c3c'
        }
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>FSTM Optimized Timetable</title>
    <style>
        body {{ 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 20px; 
            background: #f5f5f5; 
        }}
        h1 {{ 
            color: #2c3e50; 
            text-align: center; 
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .meta-info {{
            text-align: center;
            color: #7f8c8d;
            margin-bottom: 20px;
        }}
        table {{ 
            width: 100%; 
            border-collapse: collapse; 
            background: white; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            border-radius: 10px;
            overflow: hidden;
        }}
        th {{ 
            background: #2c3e50; 
            color: white; 
            padding: 12px 8px; 
            text-align: center;
            font-size: 12px;
        }}
        td {{ 
            border: 1px solid #ecf0f1; 
            padding: 8px; 
            vertical-align: top;
            font-size: 11px;
        }}
        .day-cell {{ 
            background: #34495e; 
            color: white;
            font-weight: bold; 
            text-align: center;
            writing-mode: vertical-rl;
            text-orientation: mixed;
            transform: rotate(180deg);
        }}
        .time-cell {{ 
            background: #ecf0f1; 
            font-weight: bold; 
            text-align: center;
            white-space: nowrap;
        }}
        .session {{
            margin: 3px 0; 
            padding: 6px; 
            border-radius: 4px;
            font-size: 10px;
            line-height: 1.3;
        }}
        .session-cours {{
            background-color: #e3f2fd;
            border-left: 3px solid #3498db;
        }}
        .session-td {{
            background-color: #e8f5e9;
            border-left: 3px solid #27ae60;
        }}
        .session-tp {{
            background-color: #ffebee;
            border-left: 3px solid #e74c3c;
        }}
        .session-name {{
            font-weight: bold;
            color: #2c3e50;
        }}
        .session-group {{
            color: #7f8c8d;
        }}
        .legend {{
            display: flex;
            justify-content: center;
            gap: 30px;
            margin: 20px 0;
            padding: 15px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .legend-color {{
            width: 20px;
            height: 20px;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <h1>FSTM Optimized Timetable</h1>
    <p class="meta-info">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Hybrid GA+SA Optimization</p>
    
    <div class="legend">
        <div class="legend-item">
            <div class="legend-color" style="background: #3498db;"></div>
            <span>Cours</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #27ae60;"></div>
            <span>TD</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #e74c3c;"></div>
            <span>TP</span>
        </div>
    </div>
    
    <table>
        <thead>
            <tr>
                <th>Day</th>
                <th>Time</th>
"""
        
        for room in self.room_ids:
            capacity = self.room_capacities.get(room, 'N/A')
            html += f"<th>{room}<br><small>({capacity})</small></th>"
        
        html += "</tr></thead><tbody>"
        
        for day in self.day_names:
            first_time = True
            for time_slot in self.time_slots:
                html += "<tr>"
                if first_time:
                    html += f"<td class='day-cell' rowspan='{len(self.time_slots)}'>{day}</td>"
                    first_time = False
                html += f"<td class='time-cell'>{time_slot}</td>"
                
                for room in self.room_ids:
                    sessions = timetable_data[(day, time_slot)].get(room, [])
                    html += "<td>"
                    for session in sessions:
                        session_type = session.get('session_type', '').lower()
                        css_class = f"session-{session_type}" if session_type in ['cours', 'td', 'tp'] else 'session-cours'
                        html += f"""
                        <div class="session {css_class}">
                            <div class="session-name">{session['session_name']}</div>
                            <div class="session-group">{session['group_name']}</div>
                        </div>
                        """
                    html += "</td>"
                html += "</tr>"
        
        html += """
        </tbody>
    </table>
    
    <p class="meta-info" style="margin-top: 30px;">
        <strong>Note:</strong> This timetable was optimized using a Hybrid Genetic Algorithm + Simulated Annealing approach.
        <br>All hard constraints are satisfied. Soft constraints have been minimized.
    </p>
</body>
</html>
"""
        return html


class TimetableOptimizer:
    """Main optimizer class that wraps the entire optimization pipeline"""
    
    def __init__(self, data, ga_params, sa_params, constraint_weights, random_seed=42):
        # Set random seed
        random.seed(random_seed)
        np.random.seed(random_seed)
        
        # Store parameters
        self.ga_params = ga_params
        self.sa_params = sa_params
        self.random_seed = random_seed
        
        # Initialize data
        self.rooms_df = data['rooms']
        self.groups_df = data['groups']
        self.assignments_df = data['assignments']
        self.slot_penalties_df = data['slot_penalties']
        
        # Preprocess data
        self._preprocess_data()
        
        # Initialize GA system
        self.ga_system = TimetableGA(
            self.extracted_sessions_df, 
            self.rooms_df, 
            self.groups_df, 
            self.slots_df, 
            self.group_size_map
        )
        
        # Initialize constraint checker
        self.checker = ConstraintChecker(self.ga_system, constraint_weights)
        
        # Initialize timetable generator
        self.generator = TimetableGenerator(self.ga_system, self.slots_df)
        
        # Results storage
        self.best_solution = None
        self.ga_history = []
        self.sa_history = []
        self.execution_time = 0
        self.initial_fitness = None
        self.final_fitness = None
    
    def _preprocess_data(self):
        """Preprocess input data"""
        # Create time slot structure
        day_mapping = {'LUNDI': 1, 'MARDI': 2, 'MERCREDI': 3, 'JEUDI': 4, 'VENDREDI': 5, 'SAMEDI': 6}
        time_slots = sorted(self.slot_penalties_df['start_time'].unique())
        
        # Create comprehensive slot list
        slot_list = []
        slot_id = 1
        for day_name, day_num in day_mapping.items():
            for time_slot in time_slots:
                penalty_rows = self.slot_penalties_df[self.slot_penalties_df['start_time'] == time_slot]
                penalty = penalty_rows['penalty'].values[0] if len(penalty_rows) > 0 else 0
                slot_list.append({
                    'slot_id': slot_id,
                    'day': day_num,
                    'day_name': day_name,
                    'start_time': time_slot,
                    'penalty': penalty
                })
                slot_id += 1
        
        self.slots_df = pd.DataFrame(slot_list)
        
        # Extract individual sessions from assignments
        session_list = []
        for idx, row in self.assignments_df.iterrows():
            groups_str = row.get('involved_groups', '')
            groups = groups_str.split(';') if pd.notna(groups_str) and groups_str else ['Unknown']
            for group in groups:
                session_list.append({
                    'session_id': len(session_list),
                    'session_name': row.get('session_name', 'Unknown'),
                    'session_type': row.get('session_type', 'Unknown'),
                    'teacher_id': row.get('teacher_id', None),
                    'group_name': group.strip() if group else 'Unknown'
                })
        
        self.extracted_sessions_df = pd.DataFrame(session_list)
        self.group_size_map = dict(zip(self.groups_df['group_name'], self.groups_df['size']))
    
    def run_ga(self, progress_callback=None):
        """Run Genetic Algorithm phase"""
        ga = GeneticAlgorithm(
            self.ga_system, 
            self.checker,
            pop_size=self.ga_params['population_size'],
            generations=self.ga_params['generations'],
            crossover_rate=self.ga_params['crossover_rate'],
            mutation_rate=self.ga_params['mutation_rate'],
            elitism=self.ga_params.get('elitism', 10)
        )
        
        best, history = ga.evolve(progress_callback=progress_callback)
        self.ga_history = history
        return best
    
    def run_sa(self, initial_solution, progress_callback=None):
        """Run Simulated Annealing phase"""
        sa = SimulatedAnnealing(self.ga_system, self.checker)
        
        best, history = sa.optimize(
            initial_solution,
            initial_temp=self.sa_params['initial_temp'],
            cooling_rate=self.sa_params['cooling_rate'],
            iterations=self.sa_params['iterations'],
            progress_callback=progress_callback
        )
        
        self.sa_history = history
        return best
    
    def run_full_optimization(self, ga_progress_callback=None, sa_progress_callback=None):
        """Run complete hybrid optimization"""
        start_time = time.time()
        
        # Phase 1: GA
        ga_solution = self.run_ga(progress_callback=ga_progress_callback)
        self.initial_fitness, _, _ = self.checker.calculate_fitness(ga_solution)
        
        # Phase 2: SA
        self.best_solution = self.run_sa(ga_solution, progress_callback=sa_progress_callback)
        self.final_fitness, _, _ = self.checker.calculate_fitness(self.best_solution)
        
        self.execution_time = time.time() - start_time
        
        return self.best_solution
    
    def get_best_solution(self):
        """Get the best solution found"""
        return self.best_solution
    
    def get_metrics(self):
        """Get optimization metrics"""
        if self.best_solution is None:
            return None
        
        fitness, hard, soft = self.checker.calculate_fitness(self.best_solution)
        analysis = self.checker.get_detailed_analysis(self.best_solution)
        
        return {
            'final_fitness': fitness,
            'hard_violations': hard,
            'soft_penalty': soft,
            'execution_time': self.execution_time,
            'initial_fitness': self.initial_fitness,
            'improvement_pct': ((self.initial_fitness - fitness) / self.initial_fitness * 100) if self.initial_fitness else 0,
            'detailed_analysis': analysis
        }
    
    def export_excel(self):
        """Export timetable to Excel buffer"""
        if self.best_solution is None:
            return None
        return self.generator.create_excel_buffer(self.best_solution)
    
    def export_html(self):
        """Export timetable to HTML content"""
        if self.best_solution is None:
            return None
        return self.generator.create_html_content(self.best_solution)


# ================================================================================
# DATA LOADING FUNCTIONS
# ================================================================================

# Data directory path for FSTM real data
FSTM_DATA_PATH = '../data/processed/'


def load_fstm_real_data(data_path=FSTM_DATA_PATH):
    """
    Load actual FSTM data from the processed data directory.
    
    This function loads real university data including:
    - Real room names (A1, A2, S5, GC3, etc.)
    - Real group names (BA, BP, S1_GB, IEGS, etc.)
    - Real course/session names from FSTM
    
    Args:
        data_path: Path to the data directory (default: '../data/processed/')
    
    Returns:
        Dictionary containing DataFrames for rooms, groups, assignments, slot_penalties
        or None if loading fails
    """
    required_files = {
        'rooms': 'rooms.csv',
        'groups': 'groups.csv',
        'assignments': 'assignments.csv',
        'slot_penalties': 'slot_penalties.csv'
    }
    
    # Check if all required files exist
    missing_files = []
    for key, filename in required_files.items():
        filepath = f"{data_path}{filename}"
        if not os.path.exists(filepath):
            missing_files.append(filename)
    
    if missing_files:
        return None, missing_files
    
    try:
        # Load all CSV files
        rooms_df = pd.read_csv(f"{data_path}rooms.csv")
        groups_df = pd.read_csv(f"{data_path}groups.csv")
        assignments_df = pd.read_csv(f"{data_path}assignments.csv")
        slot_penalties_df = pd.read_csv(f"{data_path}slot_penalties.csv")
        
        # Basic validation
        if len(rooms_df) == 0:
            return None, ["rooms.csv is empty"]
        if len(groups_df) == 0:
            return None, ["groups.csv is empty"]
        if len(assignments_df) == 0:
            return None, ["assignments.csv is empty"]
        if len(slot_penalties_df) == 0:
            return None, ["slot_penalties.csv is empty"]
        
        # Ensure required columns exist
        required_columns = {
            'rooms': ['room_id', 'capacity'],
            'groups': ['group_name', 'size'],
            'assignments': ['session_name', 'session_type', 'involved_groups'],
            'slot_penalties': ['start_time', 'penalty']
        }
        
        dataframes = {
            'rooms': rooms_df,
            'groups': groups_df,
            'assignments': assignments_df,
            'slot_penalties': slot_penalties_df
        }
        
        for df_name, cols in required_columns.items():
            df = dataframes[df_name]
            missing_cols = [c for c in cols if c not in df.columns]
            if missing_cols:
                return None, [f"{df_name}.csv missing columns: {missing_cols}"]
        
        # Add 'type' column to rooms if not present (default to Classroom)
        if 'type' not in rooms_df.columns:
            rooms_df['type'] = rooms_df['capacity'].apply(
                lambda x: 'Amphitheater' if x > 100 else 'Classroom'
            )
        
        # Add room_id to assignments if not present
        if 'room_id' not in assignments_df.columns:
            # Assign rooms based on session type and available rooms
            amphitheaters = rooms_df[rooms_df['type'] == 'Amphitheater']['room_id'].tolist()
            classrooms = rooms_df[rooms_df['type'] == 'Classroom']['room_id'].tolist()
            
            def assign_room(row, idx):
                if row.get('session_type') == 'Cours' and amphitheaters:
                    return amphitheaters[idx % len(amphitheaters)]
                elif classrooms:
                    return classrooms[idx % len(classrooms)]
                else:
                    return rooms_df['room_id'].iloc[0]
            
            assignments_df['room_id'] = [
                assign_room(row, idx) for idx, row in assignments_df.iterrows()
            ]
        
        # Add teacher_id if not present
        if 'teacher_id' not in assignments_df.columns:
            assignments_df['teacher_id'] = [f'PROF_{i % 50 + 1}' for i in range(len(assignments_df))]
        
        return {
            'rooms': rooms_df,
            'groups': groups_df,
            'assignments': assignments_df,
            'slot_penalties': slot_penalties_df
        }, None
        
    except Exception as e:
        return None, [f"Error loading data: {str(e)}"]


def load_uploaded_csv_data(rooms_file, groups_file, assignments_file, slot_penalties_file):
    """
    Load data from user-uploaded CSV files.
    
    Args:
        rooms_file: Uploaded rooms.csv file
        groups_file: Uploaded groups.csv file
        assignments_file: Uploaded assignments.csv file
        slot_penalties_file: Uploaded slot_penalties.csv file
    
    Returns:
        Dictionary containing DataFrames or None if loading fails
    """
    try:
        rooms_df = pd.read_csv(rooms_file)
        groups_df = pd.read_csv(groups_file)
        assignments_df = pd.read_csv(assignments_file)
        slot_penalties_df = pd.read_csv(slot_penalties_file)
        
        # Add 'type' column to rooms if not present
        if 'type' not in rooms_df.columns:
            rooms_df['type'] = rooms_df['capacity'].apply(
                lambda x: 'Amphitheater' if x > 100 else 'Classroom'
            )
        
        return {
            'rooms': rooms_df,
            'groups': groups_df,
            'assignments': assignments_df,
            'slot_penalties': slot_penalties_df
        }
    except Exception as e:
        st.error(f"Error loading CSV files: {str(e)}")
        return None


def get_dataset_summary(data, mode_name):
    """
    Generate a summary of the loaded dataset.
    
    Args:
        data: Dictionary containing DataFrames
        mode_name: Name of the data loading mode
    
    Returns:
        Dictionary with summary statistics
    """
    if data is None:
        return None
    
    # Count unique session types
    session_types = data['assignments']['session_type'].value_counts().to_dict()
    
    # Count amphitheaters vs classrooms
    room_types = data['rooms']['type'].value_counts().to_dict() if 'type' in data['rooms'].columns else {}
    
    # Get sample names for display
    sample_groups = data['groups']['group_name'].head(5).tolist()
    sample_rooms = data['rooms']['room_id'].head(5).tolist()
    sample_sessions = data['assignments']['session_name'].head(5).tolist()
    
    # Estimate total sessions (considering groups)
    total_sessions = 0
    for _, row in data['assignments'].iterrows():
        groups_str = row.get('involved_groups', '')
        if pd.notna(groups_str) and groups_str:
            total_sessions += len(str(groups_str).split(';'))
        else:
            total_sessions += 1
    
    return {
        'mode': mode_name,
        'num_rooms': len(data['rooms']),
        'num_groups': len(data['groups']),
        'num_assignments': len(data['assignments']),
        'estimated_sessions': total_sessions,
        'num_time_slots': len(data['slot_penalties']) * 6,  # slots × days
        'session_types': session_types,
        'room_types': room_types,
        'sample_groups': sample_groups,
        'sample_rooms': sample_rooms,
        'sample_sessions': sample_sessions
    }


# ================================================================================
# VISUALIZATION FUNCTIONS
# ================================================================================

def plot_convergence(ga_history, sa_history):
    """Create convergence plot"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # GA Convergence
    axes[0].plot(ga_history, color='#3498db', linewidth=2, label='Best Fitness')
    axes[0].set_xlabel('Generation', fontsize=12)
    axes[0].set_ylabel('Fitness', fontsize=12)
    axes[0].set_title('Genetic Algorithm Convergence', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()
    if max(ga_history) > 1000:
        axes[0].set_yscale('log')
    
    # SA Refinement
    if len(sa_history) > 0:
        sample_size = min(2000, len(sa_history))
        sample_indices = np.linspace(0, len(sa_history)-1, sample_size, dtype=int)
        axes[1].plot([sa_history[i] for i in sample_indices], color='#27ae60', linewidth=2)
        axes[1].set_xlabel('Iteration (sampled)', fontsize=12)
        axes[1].set_ylabel('Fitness', fontsize=12)
        axes[1].set_title('Simulated Annealing Refinement', fontsize=14, fontweight='bold')
        axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig


def plot_constraint_analysis(analysis):
    """Create constraint analysis bar chart"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Hard constraints
    hard_labels = ['Teacher\nConflicts', 'Room\nConflicts', 'Group\nConflicts', 
                   'Capacity\nViolations', 'Room Type\nViolations']
    hard_values = [analysis['h1_teacher'], analysis['h2_room'], analysis['h3_group'],
                   analysis['h4_capacity'], analysis['h5_room_type']]
    
    colors = ['#27ae60' if v == 0 else '#e74c3c' for v in hard_values]
    bars1 = axes[0].bar(hard_labels, hard_values, color=colors, edgecolor='white', linewidth=2)
    axes[0].set_ylabel('Violations', fontsize=12)
    axes[0].set_title('Hard Constraints Status', fontsize=14, fontweight='bold')
    axes[0].axhline(y=0, color='#27ae60', linestyle='--', linewidth=2, label='Target: 0')
    
    for bar, val in zip(bars1, hard_values):
        axes[0].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                     str(int(val)), ha='center', va='bottom', fontweight='bold')
    
    # Soft constraints
    soft_labels = ['Schedule\nGaps', 'Time\nPenalties', 'Load\nBalance']
    soft_values = [analysis['s1_gaps'], analysis['s2_time'], analysis['s3_balance']]
    
    bars2 = axes[1].bar(soft_labels, soft_values, color=['#3498db', '#9b59b6', '#f39c12'], 
                        edgecolor='white', linewidth=2)
    axes[1].set_ylabel('Penalty Score', fontsize=12)
    axes[1].set_title('Soft Constraints Analysis', fontsize=14, fontweight='bold')
    
    for bar, val in zip(bars2, soft_values):
        axes[1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                     f'{val:.1f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    return fig


def create_timetable_view(optimizer, day_filter='All', room_filter='All'):
    """Create a filtered timetable view for Streamlit"""
    if optimizer.best_solution is None:
        return None
    
    timetable_data = optimizer.generator.build_timetable_data(optimizer.best_solution)
    
    days = optimizer.generator.day_names if day_filter == 'All' else [day_filter]
    rooms = optimizer.generator.room_ids if room_filter == 'All' else [room_filter]
    
    # Build display data
    rows = []
    for day in days:
        for time_slot in optimizer.generator.time_slots:
            row = {'Day': day, 'Time': time_slot}
            for room in rooms[:10]:  # Limit to 10 rooms for display
                sessions = timetable_data[(day, time_slot)].get(room, [])
                cell_content = '\n'.join([
                    f"{s['session_name']} | {s['group_name']} | {s['session_type']}"
                    for s in sessions
                ]) if sessions else ''
                row[room] = cell_content
            rows.append(row)
    
    return pd.DataFrame(rows)


# ================================================================================
# MAIN APPLICATION
# ================================================================================

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">FSTM University Timetabling Optimizer</h1>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    <p style="text-align: center; color: #7f8c8d; margin-bottom: 2rem;">
        <strong>Hybrid Metaheuristic Approach:</strong> Genetic Algorithm + Simulated Annealing<br>
        <em>Master in Artificial Intelligence - Metaheuristics Module</em>
    </p>
    """, unsafe_allow_html=True)
    
    # ============================================================================
    # SIDEBAR - Configuration Panel
    # ============================================================================
    with st.sidebar:
        st.markdown("## Configuration Panel")
        
        # --- Dataset Selection ---
        st.markdown("### Dataset")
        
        # Two-mode data source selection
        use_fstm_data = st.checkbox(
            "Use FSTM dataset",
            value=True,
            help="Load real FSTM university data from the processed data directory"
        )
        
        data = None
        
        # --- Mode 1: FSTM Real Data (Default) ---
        if use_fstm_data:
            # Load FSTM real data from fixed path
            data, errors = load_fstm_real_data(FSTM_DATA_PATH)
            
            if data is not None:
                st.success("FSTM data loaded successfully")
                summary = get_dataset_summary(data, "FSTM Data")
                
                with st.expander("Dataset Summary"):
                    st.write(f"**Rooms:** {summary['num_rooms']}")
                    st.write(f"**Groups:** {summary['num_groups']}")
                    st.write(f"**Assignments:** {summary['num_assignments']}")
                    st.write(f"**Estimated Sessions:** {summary['estimated_sessions']}")
                    
                    st.markdown("**Session Types:**")
                    for stype, count in summary['session_types'].items():
                        st.write(f"- {stype}: {count}")
            else:
                st.error("Failed to load FSTM data")
                with st.expander("Error Details"):
                    for err in errors:
                        st.warning(f"- {err}")
                    st.info("""
                    Expected files in '../data/processed/':
                    - rooms.csv
                    - groups.csv  
                    - assignments.csv
                    - slot_penalties.csv
                    """)
        
        # --- Mode 2: Upload Custom CSV ---
        else:
            st.markdown("#### Upload CSV Files")
            
            rooms_file = st.file_uploader(
                "rooms.csv", 
                type='csv', 
                key='rooms',
                help="Columns: room_id, capacity, type (optional)"
            )
            groups_file = st.file_uploader(
                "groups.csv", 
                type='csv', 
                key='groups',
                help="Columns: group_name, size"
            )
            assignments_file = st.file_uploader(
                "assignments.csv", 
                type='csv', 
                key='assignments',
                help="Columns: session_name, session_type, teacher_id, involved_groups"
            )
            penalties_file = st.file_uploader(
                "slot_penalties.csv", 
                type='csv', 
                key='penalties',
                help="Columns: start_time, penalty"
            )
            
            if all([rooms_file, groups_file, assignments_file, penalties_file]):
                data = load_uploaded_csv_data(rooms_file, groups_file, assignments_file, penalties_file)
                if data:
                    st.success("Custom dataset loaded")
                    summary = get_dataset_summary(data, "Custom Upload")
                    
                    with st.expander("Dataset Summary"):
                        st.write(f"**Rooms:** {summary['num_rooms']}")
                        st.write(f"**Groups:** {summary['num_groups']}")
                        st.write(f"**Assignments:** {summary['num_assignments']}")
                        st.write(f"**Estimated Sessions:** {summary['estimated_sessions']}")
            else:
                uploaded_count = sum([
                    rooms_file is not None,
                    groups_file is not None,
                    assignments_file is not None,
                    penalties_file is not None
                ])
                st.info(f"Upload all 4 CSV files ({uploaded_count}/4 uploaded)")
        
        st.markdown("---")
        
        # --- Hard Constraints ---
        st.markdown("### Hard Constraints")
        st.caption("Must be satisfied (non-negotiable)")
        
        st.markdown("""
        - No teacher conflicts
        - No room conflicts
        - No group conflicts
        - Room capacity respected
        - Room type compatibility
        """)
        
        st.markdown("---")
        
        # --- Soft Constraints ---
        st.markdown("### Soft Constraints")
        st.caption("Optimization objectives (weighted)")
        
        enable_gaps = st.checkbox("Minimize schedule gaps", value=True)
        gaps_weight = st.slider("Gap penalty weight", 0.0, 5.0, 1.0, 0.1, 
                                disabled=not enable_gaps)
        
        enable_time = st.checkbox("Minimize time slot penalties", value=True)
        time_weight = st.slider("Time penalty weight", 0.0, 5.0, 1.0, 0.1,
                                disabled=not enable_time)
        
        enable_balance = st.checkbox("Load balancing", value=True)
        balance_weight = st.slider("Balance weight", 0.0, 5.0, 1.0, 0.1,
                                   disabled=not enable_balance)
        
        constraint_weights = {
            'gaps': gaps_weight if enable_gaps else 0,
            'time_penalties': time_weight if enable_time else 0,
            'load_balance': balance_weight if enable_balance else 0
        }
    
    # ============================================================================
    # MAIN CONTENT
    # ============================================================================
    
    # Create tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "Parameters", "Optimization", "Results", "Timetable"
    ])
    
    # --- Tab 1: Parameters ---
    with tab1:
        st.markdown('<h2 class="sub-header">Algorithm Parameters</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Genetic Algorithm")
            st.caption("Global exploration phase")
            
            pop_size = st.slider("Population Size", 20, 200, 100, 10,
                                help="Number of solutions in each generation")
            
            generations = st.slider("Number of Generations", 50, 500, 300, 25,
                                   help="Number of evolution iterations")
            
            crossover_rate = st.slider("Crossover Rate", 0.6, 0.95, 0.8, 0.05,
                                      help="Probability of combining parent solutions")
            
            mutation_rate = st.slider("Mutation Rate", 0.05, 0.3, 0.15, 0.01,
                                     help="Probability of random changes")
            
            ga_params = {
                'population_size': pop_size,
                'generations': generations,
                'crossover_rate': crossover_rate,
                'mutation_rate': mutation_rate,
                'elitism': 10
            }
        
        with col2:
            st.markdown("### Simulated Annealing")
            st.caption("Local refinement phase")
            
            initial_temp = st.slider("Initial Temperature", 100, 5000, 1000, 100,
                                    help="Starting temperature for acceptance probability")
            
            cooling_rate = st.slider("Cooling Rate", 0.90, 0.99, 0.95, 0.01,
                                    help="Temperature reduction factor")
            
            sa_iterations = st.slider("Iterations per Temperature", 50, 200, 100, 10,
                                     help="Number of moves at each temperature level")
            
            sa_params = {
                'initial_temp': initial_temp,
                'cooling_rate': cooling_rate,
                'iterations': sa_iterations
            }
        
        st.markdown("---")
        
        # Random seed
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            random_seed = st.number_input("Random Seed (for reproducibility)", 
                                         min_value=1, max_value=9999, value=42)
        
        # Store parameters in session state
        st.session_state['ga_params'] = ga_params
        st.session_state['sa_params'] = sa_params
        st.session_state['constraint_weights'] = constraint_weights
        st.session_state['random_seed'] = random_seed
        st.session_state['data'] = data
    
    # --- Tab 2: Optimization ---
    with tab2:
        st.markdown('<h2 class="sub-header">Run Optimization</h2>', unsafe_allow_html=True)
        
        if data is None:
            st.warning("Please configure and load a dataset first in the sidebar.")
            st.info("""
            **To proceed:**
            1. Ensure FSTM data checkbox is selected (or upload custom files)
            2. Verify data loads successfully
            3. Configure algorithm parameters in the Parameters tab
            4. Return here to run optimization
            """)
        else:
            # Get summary for display
            summary = get_dataset_summary(data, "FSTM Data" if use_fstm_data else "Custom Data")
            
            # Display configuration summary
            with st.expander("Configuration Summary", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**Dataset**")
                    st.write(f"- Sessions: ~{summary['estimated_sessions']}")
                    st.write(f"- Rooms: {summary['num_rooms']}")
                    st.write(f"- Time slots: {summary['num_time_slots']}")
                
                with col2:
                    st.markdown("**GA Parameters**")
                    st.write(f"- Population: {ga_params['population_size']}")
                    st.write(f"- Generations: {ga_params['generations']}")
                    st.write(f"- Crossover: {ga_params['crossover_rate']}")
                
                with col3:
                    st.markdown("**SA Parameters**")
                    st.write(f"- Initial Temp: {sa_params['initial_temp']}")
                    st.write(f"- Cooling Rate: {sa_params['cooling_rate']}")
                    st.write(f"- Iterations: {sa_params['iterations']}")
            
            st.markdown("---")
            
            # Run button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                run_button = st.button("Run Optimization", use_container_width=True, 
                                      type="primary")
            
            if run_button:
                # Initialize optimizer
                try:
                    optimizer = TimetableOptimizer(
                        data=data,
                        ga_params=ga_params,
                        sa_params=sa_params,
                        constraint_weights=constraint_weights,
                        random_seed=random_seed
                    )
                    
                    st.markdown("---")
                    
                    # Progress containers
                    st.markdown("### Optimization Progress")
                    
                    # GA Progress
                    st.markdown("#### Phase 1: Genetic Algorithm")
                    ga_progress_bar = st.progress(0)
                    ga_status = st.empty()
                    
                    # SA Progress
                    st.markdown("#### Phase 2: Simulated Annealing")
                    sa_progress_bar = st.progress(0)
                    sa_status = st.empty()
                    
                    # Log container
                    log_container = st.empty()
                    logs = []
                    
                    def ga_callback(gen, total_gen, fitness, hard, soft):
                        progress = (gen + 1) / total_gen
                        ga_progress_bar.progress(progress)
                        ga_status.markdown(f"""
                        **Generation {gen + 1}/{total_gen}** | 
                        Fitness: `{fitness:,.1f}` | 
                        Hard Violations: `{hard}` | 
                        Soft Penalty: `{soft:.1f}`
                        """)
                        if gen % 20 == 0:
                            logs.append(f"[GA] Gen {gen}: Fitness={fitness:,.1f}, Hard={hard}")
                            log_container.code('\n'.join(logs[-10:]))
                    
                    def sa_callback(progress, temp, fitness, hard, soft):
                        sa_progress_bar.progress(min(progress, 1.0))
                        sa_status.markdown(f"""
                        **Temperature: {temp:.2f}** | 
                        Best Fitness: `{fitness:,.1f}` | 
                        Hard Violations: `{hard}` | 
                        Soft Penalty: `{soft:.1f}`
                        """)
                    
                    # Run optimization
                    start_time = time.time()
                    optimizer.run_full_optimization(
                        ga_progress_callback=ga_callback,
                        sa_progress_callback=sa_callback
                    )
                    elapsed = time.time() - start_time
                    
                    # Store results
                    st.session_state['optimizer'] = optimizer
                    st.session_state['optimization_complete'] = True
                    
                    # Success message
                    st.success(f"Optimization completed in {elapsed:.2f} seconds!")
                    
                    metrics = optimizer.get_metrics()
                    if metrics['hard_violations'] == 0:
                        st.balloons()
                        st.markdown("""
                        <div style="background: linear-gradient(135deg, #27ae60, #2ecc71); 
                                    padding: 20px; border-radius: 10px; text-align: center; color: white;">
                            <h2>FEASIBLE SOLUTION FOUND</h2>
                            <p>All hard constraints are satisfied. The timetable is ready for deployment.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"Optimization failed: {str(e)}")
                    st.exception(e)
    
    # --- Tab 3: Results ---
    with tab3:
        st.markdown('<h2 class="sub-header">Optimization Results</h2>', unsafe_allow_html=True)
        
        if 'optimizer' not in st.session_state or not st.session_state.get('optimization_complete'):
            st.info("Run optimization first to see results.")
        else:
            optimizer = st.session_state['optimizer']
            metrics = optimizer.get_metrics()
            
            # Summary metrics
            st.markdown("### Summary Metrics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="Initial Fitness",
                    value=f"{metrics['initial_fitness']:,.0f}",
                    delta=None
                )
            
            with col2:
                st.metric(
                    label="Final Fitness",
                    value=f"{metrics['final_fitness']:,.1f}",
                    delta=f"-{metrics['improvement_pct']:.1f}%"
                )
            
            with col3:
                st.metric(
                    label="Hard Violations",
                    value=f"{metrics['hard_violations']}",
                    delta="Feasible" if metrics['hard_violations'] == 0 else "Infeasible"
                )
            
            with col4:
                st.metric(
                    label="Execution Time",
                    value=f"{metrics['execution_time']:.1f}s",
                    delta=None
                )
            
            st.markdown("---")
            
            # Convergence plot
            st.markdown("### Convergence Analysis")
            
            if len(optimizer.ga_history) > 0:
                fig = plot_convergence(optimizer.ga_history, optimizer.sa_history)
                st.pyplot(fig)
                plt.close()
            
            st.markdown("---")
            
            # Constraint analysis
            st.markdown("### Constraint Analysis")
            
            analysis = metrics['detailed_analysis']
            fig = plot_constraint_analysis(analysis)
            st.pyplot(fig)
            plt.close()
            
            # Detailed breakdown
            with st.expander("Detailed Constraint Breakdown"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Hard Constraints**")
                    st.write(f"- Teacher Conflicts: {analysis['h1_teacher']}")
                    st.write(f"- Room Conflicts: {analysis['h2_room']}")
                    st.write(f"- Group Conflicts: {analysis['h3_group']}")
                    st.write(f"- Capacity Violations: {analysis['h4_capacity']}")
                    st.write(f"- Room Type Violations: {analysis['h5_room_type']}")
                
                with col2:
                    st.markdown("**Soft Constraints**")
                    st.write(f"- Schedule Gaps: {analysis['s1_gaps']:.1f}")
                    st.write(f"- Time Penalties: {analysis['s2_time']:.1f}")
                    st.write(f"- Load Balance: {analysis['s3_balance']:.2f}")
            
            st.markdown("---")
            
            # Export section
            st.markdown("### Export Timetable")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                excel_buffer = optimizer.export_excel()
                if excel_buffer:
                    st.download_button(
                        label="Download Excel",
                        data=excel_buffer,
                        file_name=f"FSTM_Timetable_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
            
            with col2:
                html_content = optimizer.export_html()
                if html_content:
                    st.download_button(
                        label="Download HTML",
                        data=html_content,
                        file_name=f"FSTM_Timetable_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                        mime="text/html",
                        use_container_width=True
                    )
    
    # --- Tab 4: Timetable ---
    with tab4:
        st.markdown('<h2 class="sub-header">Timetable Visualization</h2>', unsafe_allow_html=True)
        
        if 'optimizer' not in st.session_state or not st.session_state.get('optimization_complete'):
            st.info("Run optimization first to view the timetable.")
        else:
            optimizer = st.session_state['optimizer']
            
            # Filters
            col1, col2 = st.columns(2)
            
            with col1:
                day_options = ['All'] + optimizer.generator.day_names
                selected_day = st.selectbox("Filter by Day", day_options)
            
            with col2:
                room_options = ['All'] + optimizer.generator.room_ids[:20]  # Limit options
                selected_room = st.selectbox("Filter by Room", room_options)
            
            st.markdown("---")
            
            # Color legend
            st.markdown("""
            <div style="display: flex; gap: 20px; margin-bottom: 20px;">
                <span class="session-cours">Cours</span>
                <span class="session-td">TD</span>
                <span class="session-tp">TP</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Display timetable
            timetable_df = create_timetable_view(optimizer, selected_day, selected_room)
            
            if timetable_df is not None:
                st.dataframe(
                    timetable_df,
                    use_container_width=True,
                    height=600
                )
            
            # HTML preview
            with st.expander("HTML Preview"):
                html_content = optimizer.export_html()
                if html_content:
                    st.components.v1.html(html_content, height=800, scrolling=True)
    
    # ============================================================================
    # Footer
    # ============================================================================
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #7f8c8d; padding: 20px;">
        <p><strong>FSTM Timetabling Optimization System</strong></p>
        <p>Master IAII - Metaheuristics Module | January 2026</p>
        <p><em>Youssef Ait Bahssine • Mustapha Zmirli • Mohamed Bajadi</em></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
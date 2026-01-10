# FSTM University Timetabling Optimization System

## Hybrid Metaheuristic Approach: Genetic Algorithm + Simulated Annealing

**Module:** Metaheuristics - Master in Artificial Intelligence  
**Authors:** Youssef Ait Bahssine, Mustapha Zmirli, Mohamed Bajadi  
**Date:** January 2026

---

## 🎯 Overview

This Streamlit application provides a professional decision-support system for university timetabling optimization. It implements a hybrid metaheuristic approach combining:

- **Genetic Algorithm (GA)** for global exploration
- **Simulated Annealing (SA)** for local refinement

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py
```

### Access
Open your browser at `http://localhost:8501`

---

## 📋 Features

### 1. Dataset Configuration
- **Default FSTM Dataset:** Pre-configured demonstration data
- **Custom Upload:** Support for CSV file uploads
  - `rooms.csv` - Room information (id, capacity, type)
  - `groups.csv` - Student groups (name, size)
  - `assignments.csv` - Course assignments
  - `slot_penalties.csv` - Time slot penalties

### 2. Constraint Configuration

**Hard Constraints (enforced):**
- No teacher conflicts
- No room conflicts  
- No group conflicts
- Room capacity respected
- Room type compatibility

**Soft Constraints (weighted):**
- Minimize schedule gaps
- Minimize time slot penalties
- Load balancing across days

### 3. Algorithm Parameters

**Genetic Algorithm:**
- Population size (20-200)
- Number of generations (50-500)
- Crossover rate (0.6-0.95)
- Mutation rate (0.05-0.3)

**Simulated Annealing:**
- Initial temperature
- Cooling rate (0.90-0.99)
- Iterations per temperature level

### 4. Optimization & Results
- Real-time progress monitoring
- Convergence visualization
- Detailed constraint analysis
- Performance metrics

### 5. Export Options
- Excel (.xlsx) with formatting
- HTML with color-coded sessions

---

## 📊 Expected Outputs

| Metric | Target |
|--------|--------|
| Hard Violations | 0 (feasible solution) |
| Fitness Improvement | >90% |
| Execution Time | <2 minutes |

---

## 📁 CSV File Formats

### rooms.csv
```csv
room_id,capacity,type
AMPHI_A,300,Amphitheater
SALLE_1,40,Classroom
```

### groups.csv
```csv
group_name,size
G1,35
MasterAI_G1,25
```

### assignments.csv
```csv
session_name,session_type,teacher_id,involved_groups,room_id
Algorithmes,Cours,PROF_1,G1;G2;G3,AMPHI_A
```

### slot_penalties.csv
```csv
start_time,penalty
08:30,5
10:30,0
```

---

## 🔧 Technical Architecture

```
app.py
├── TimetableGA           # GA chromosome management
├── ConstraintChecker     # Hard/soft constraint evaluation
├── GeneticAlgorithm      # Evolution operators
├── SimulatedAnnealing    # Local search refinement
├── TimetableGenerator    # Export (Excel/HTML)
└── TimetableOptimizer    # Main orchestration class
```

---

## 📝 License

Academic use - Master IAII Project

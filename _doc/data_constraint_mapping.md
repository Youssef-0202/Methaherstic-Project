# DATA DICTIONARY & CONSTRAINT MAPPING

This document describes the relationship between the processed data files and the mathematical constraints defined in the project report.

## 1. Data Files Overview

| File | Description | Key Columns |
| :--- | :--- | :--- |
| `assignments.csv` | The core schedule of sessions. | `day`, `start_time`, `duration`, `room_id`, `session_name`, `session_type`, `teacher_id`, `involved_groups` |
| `rooms.csv` | Catalog of physical resources. | `room_id`, `capacity`, `type` |
| `groups.csv` | Student cohorts and their sizes. | `group_name`, `section`, `size` |
| `teachers.csv` | Reference list of faculty. | `teacher_id`, `name`, `specialization` |
| `slot_penalties.csv` | Weights for soft constraints. | `start_time`, `penalty` |

---

## 2. Hard Constraints Mapping (Feasibility)

| Constraint | Formula | Data Mapping |
| :--- | :--- | :--- |
| **H1: Teacher Conflict** | $\sum \max(0, \sum x - 1)$ | Uses `teacher_id`, `day`, and `start_time` from `assignments.csv`. |
| **H2: Group Conflict** | $\sum \max(0, \sum x - 1)$ | Uses `involved_groups` (split by `;`), `day`, and `start_time` from `assignments.csv`. |
| **H3: Room Conflict** | $\sum \max(0, \sum x - 1)$ | Uses `room_id`, `day`, and `start_time` from `assignments.csv`. |
| **H4: Room Capacity** | $\sum x \cdot \max(0, size_g - cap_r)$ | Compares `size` (from `groups.csv`) with `capacity` (from `rooms.csv`) for the assigned `room_id`. |
| **H5: Room Type** | $\sum x \cdot |type_c - type_r|$ | Compares `session_type` (Cours/TD/TP) with `type` (Amphitheater/Classroom) from `rooms.csv`. |

---

## 3. Soft Constraints Mapping (Quality)

| Constraint | Formula | Data Mapping |
| :--- | :--- | :--- |
| **S1: Schedule Gaps** | $\sum \text{Gaps}(g, d)$ | Calculated by sorting `assignments.csv` by `day` and `start_time` for each group in `involved_groups`. |
| **S2: Load Balancing** | $\text{Var}(\sum x \text{ per } t)$ | Calculated by summing `duration` (converted to hours) for each `teacher_id` in `assignments.csv`. |
| **S3: Session Timing** | $\sum x \cdot penalty_s$ | Uses `start_time` from `assignments.csv` and maps it to the `penalty` value in `slot_penalties.csv`. |

---

## 4. Key Variables for Algorithm Implementation

*   **$x_{c,t,g,r,s}$**: Represented by each row in `assignments.csv`.
*   **$cap_r$**: Found in `rooms.csv` (column `capacity`).
*   **$size_g$**: Found in `groups.csv` (column `size`).
*   **$type_c$**: Derived from `session_type` in `assignments.csv`.
*   **$type_r$**: Found in `rooms.csv` (column `type`).
*   **$penalty_s$**: Found in `slot_penalties.csv` (column `penalty`).

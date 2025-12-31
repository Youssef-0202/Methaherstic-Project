from dataclasses import dataclass
from typing import List

@dataclass
class Room:
    room_id: str
    capacity: int  # cap_r
    room_type: str # type_r (e.g., 'Amphi', 'Lab', 'Classroom')

@dataclass
class Course:
    course_name: str
    course_type: str # type_c (matches room_type)

@dataclass
class Group:
    group_name: str
    section: str
    size: int # size_g

@dataclass
class Teacher:
    teacher_id: str
    name: str

@dataclass
class Slot:
    day: str
    start_time: str
    duration: float # in hours
    
    def __repr__(self):
        duration_str = f"{int(self.duration)}" if self.duration.is_integer() else f"{self.duration}"
        return f"{self.day} {self.start_time} ({duration_str}h)"

@dataclass
class Assignment:
    course_name: str
    involved_groups: List[str] # Set of groups G
    teacher_id: str           # Teacher T
    room_id: str              # Room R
    slot: Slot                # Slot S
    session_type: str         # Cours, TD, TP

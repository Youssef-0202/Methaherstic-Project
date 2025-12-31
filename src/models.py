from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Room:
    room_id: str
    capacity: int
    type: str # 'Amphitheater' or 'Classroom'

@dataclass
class Course:
    course_id: str
    name: str
    # Add other attributes if needed (e.g., required room type)

@dataclass
class Group:
    group_id: str
    size: int

@dataclass
class Teacher:
    teacher_id: str
    name: str

@dataclass
class Slot:
    day: str
    start_time: str
    duration: int # in minutes
    
    def __repr__(self):
        return f"{self.day} {self.start_time} ({self.duration}m)"

@dataclass
class Assignment:
    course_id: str
    group_id: str
    teacher_id: str
    room_id: str
    slot: Slot
    type: str # 'Cours', 'TD', 'TP'

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Room:
    room_id: str
    capacity: int
    type: str # 'Amphitheater' or 'Classroom'

@dataclass
class Course:
    course_name: str
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
    duration: float # in hours
    
    def __repr__(self):
        duration_str = f"{int(self.duration)}" if self.duration.is_integer() else f"{self.duration}"
        return f"{self.day} {self.start_time} ({duration_str}h)"

@dataclass
class Assignment:
    course_name: str
    group_id: str
    teacher_id: str
    room_id: str
    slot: Slot
    type: str # 'Cours', 'TD', 'TP'

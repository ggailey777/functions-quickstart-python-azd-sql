from dataclasses import dataclass
from typing import Optional
import uuid


@dataclass
class ToDoItem:
    """ToDo item model for Azure SQL Database."""
    id: str
    title: str
    url: str
    order: Optional[int] = None
    completed: Optional[bool] = None
    
    def __init__(self, id: str = None, title: str = "", url: str = "", 
                 order: Optional[int] = None, completed: Optional[bool] = None):
        self.id = id if id is not None else str(uuid.uuid4())
        self.title = title
        self.url = url
        self.order = order
        self.completed = completed
        
    def to_dict(self):
        """Convert to dictionary for SQL binding."""
        return {
            "id": self.id,
            "title": self.title,
            "url": self.url,
            "order": self.order,
            "completed": self.completed
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create ToDoItem from dictionary."""
        return cls(
            id=data.get("id"),
            title=data.get("title", ""),
            url=data.get("url", ""),
            order=data.get("order"),
            completed=data.get("completed")
        )
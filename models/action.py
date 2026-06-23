from dataclasses import dataclass, field
from enum import Enum
import uuid

class ActionType(Enum):
    TAP = 'TAP'
    SWIPE = 'SWIPE'
    TEXT = 'TEXT'
    KEYEVENT = 'KEYEVENT'
    INPUT_CODE = 'INPUT_CODE'
    DELAY = 'DELAY'

@dataclass
class AdbAction:
    action_type: ActionType
    # Dành cho TAP và SWIPE
    x: int = 0
    y: int = 0
    # Dành cho SWIPE
    end_x: int = 0
    end_y: int = 0
    duration_ms: int = 500
    # Dành cho TEXT
    text: str = ''
    # Dành cho KEYEVENT
    keycode: int = 66
    # Dành cho DELAY (nghỉ trước khi thực hiện bước này hoặc dùng như 1 bước độc lập)
    delay_ms: int = 1000

    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self):
        return {
            'action_type': self.action_type.value,
            'x': self.x,
            'y': self.y,
            'end_x': self.end_x,
            'end_y': self.end_y,
            'duration_ms': self.duration_ms,
            'text': self.text,
            'keycode': self.keycode,
            'delay_ms': self.delay_ms,
            'id': self.id
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            action_type=ActionType(data['action_type']),
            x=data.get('x', 0),
            y=data.get('y', 0),
            end_x=data.get('end_x', 0),
            end_y=data.get('end_y', 0),
            duration_ms=data.get('duration_ms', 500),
            text=data.get('text', ''),
            keycode=data.get('keycode', 66),
            delay_ms=data.get('delay_ms', 1000),
            id=data.get('id', str(uuid.uuid4()))
        )

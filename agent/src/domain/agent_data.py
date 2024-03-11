from datetime import datetime
from domain.accelerometer import Accelerometer
from domain.gps import Gps
from dataclasses import dataclass

@dataclass
class AgentData:
    user_id: int
    accelerometer: Accelerometer
    gps: Gps
    timestamp: datetime

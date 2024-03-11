from dataclasses import dataclass
from datetime import datetime
from domain.accelerometer import Accelerometer
from domain.agent_data import AgentData
from domain.parking import Parking


@dataclass
class AggregatedData:
    road_state: str
    agent_data: AgentData
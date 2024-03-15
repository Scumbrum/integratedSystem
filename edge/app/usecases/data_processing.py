from app.entities.agent_data import AgentData
from app.entities.processed_agent_data import ProcessedAgentData


def process_agent_data(
    agent_data: AgentData,
) -> ProcessedAgentData:
    """
    Process agent data and classify the state of the road surface.
    Parameters:
        agent_data (AgentData): Agent data that containing accelerometer, GPS, and timestamp.
    Returns:
        processed_data_batch (ProcessedAgentData): Processed data containing the classified state of the road surface and agent data.
    """
    data = ProcessedAgentData(agent_data=agent_data, road_state='normal')

    if agent_data.accelerometer.y > 5:
        data.road_state = 'pit'
    elif agent_data.accelerometer.z > 5:
        data.road_state = 'waves'
    
    return data
    

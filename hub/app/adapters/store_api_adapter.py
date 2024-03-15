import json
import logging
from typing import List

import pydantic_core
import requests
from fastapi.encoders import jsonable_encoder

from app.entities.processed_agent_data import ProcessedAgentData
from app.interfaces.store_gateway import StoreGateway


class StoreApiAdapter(StoreGateway):
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url

    def save_data(self, processed_agent_data_batch: List[ProcessedAgentData]):
        """
        Save the processed road data to the Store API.
        Parameters:
            processed_agent_data_batch (dict): Processed road data to be saved.
        Returns:
            bool: True if the data is successfully saved, False otherwise.
        """
        headers = {
            'Content-Type': 'application/json',
        }

        json_list = []

        for item in processed_agent_data_batch:
            json_list.append({
                "road_state": item.road_state,
                "agent_data": {
                    "user_id": 12,
                    "timestamp": item.agent_data.timestamp.isoformat(),
                    "accelerometer": {
                        "x": item.agent_data.accelerometer.x,
                        "y": item.agent_data.accelerometer.y,
                        "z": item.agent_data.accelerometer.z
                    },
                    "gps": {
                        "longitude": item.agent_data.gps.longitude,
                        "latitude": item.agent_data.gps.latitude
                    }
                }
            })

        response = requests.post(self.api_base_url + '/processed_agent_data', json=json_list, headers=headers)

        if response.status_code == 200:
            print("POST request was successful!")
            print("Response:")
            print(response.json())  # Print response content as JSON
            return True
        else:
            print("POST request failed with status code:", response.status_code)
            print("Response:")
            print(response.text)
            return False
        

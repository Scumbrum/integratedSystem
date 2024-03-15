from csv import reader
from datetime import datetime
from domain.aggregated_data import AggregatedData
from domain.agent_data import AgentData
from domain.accelerometer import Accelerometer
from domain.parking import Parking
from domain.gps import Gps

class FileDatasource:
    def __init__(self, accelerometer_filename: str, gps_filename: str, parking_filename: str) -> None:
        self.accelerometer_filename = accelerometer_filename
        self.gps_filename = gps_filename
        self.parking_filename= parking_filename
    def read(self) -> AgentData:
        accelerometer_row = self.accelerometer_data[self.accelerometer_index]
        self.accelerometer_index += 1
        if self.accelerometer_index == len(self.accelerometer_data):
            self.accelerometer_index = 1
        gps_row = self.gps_data[self.gps_index]
        self.gps_index += 1
        if self.gps_index == len(self.gps_data):
            self.gps_index = 1
        parking_row = self.parking_data[self.parking_index]
        self.parking_index += 1
        if self.parking_index == len(self.parking_data):
            self.parking_index = 1

        return AgentData(
                accelerometer=Accelerometer(accelerometer_row[0], accelerometer_row[1], accelerometer_row[2]),
                gps=Gps(gps_row[0], gps_row[1]),
                timestamp=datetime.now(),
                user_id=12
            )
        
    def startReading(self, *args, **kwargs):
        self.accelerometer_file = open(self.accelerometer_filename, 'r', newline='')
        preData = reader(self.accelerometer_file);
        self.accelerometer_data = list(preData)
        self.accelerometer_index = 1
        self.gps_file = open(self.gps_filename, 'r', newline='')
        preData = reader(self.gps_file);
        self.gps_data = list(preData)
        self.gps_index = 1
        self.parking_file = open(self.parking_filename, 'r', newline='')
        preData = reader(self.parking_file);
        self.parking_data = list(preData)
        self.parking_index = 1

    def stopReading(self, *args, **kwargs):
        self.accelerometer_file.close()
        self.gps_file.close()
        self.parking_file.close()
       
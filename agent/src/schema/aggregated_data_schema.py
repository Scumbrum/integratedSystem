from marshmallow import Schema, fields
from schema.accelerometer_schema import AccelerometerSchema
from schema.gps_schema import GpsSchema
from schema.parking_schema import ParkingSchema
from domain.aggregated_data import AggregatedData

class AgentDataSchema(Schema):
    user_id = fields.Int()
    accelerometer = fields.Nested(AccelerometerSchema)
    gps = fields.Nested(GpsSchema)
    timestamp = fields.DateTime('iso')

class AggregatedDataSchema(Schema):
    road_state = fields.Str()
    agent_data = fields.Nested(AgentDataSchema)
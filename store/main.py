import asyncio
import json
from typing import Set, Dict, List, Any
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Body
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Float,
    DateTime,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from pydantic import BaseModel, field_validator
from config import (
    POSTGRES_HOST,
    POSTGRES_PORT,
    POSTGRES_DB,
    POSTGRES_USER,
    POSTGRES_PASSWORD,
)

# FastAPI app setup
app = FastAPI()
# SQLAlchemy setup
DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
metadata = MetaData()
# SQLAlchemy model
Base = declarative_base()

# Define SQLAlchemy model
class ProcessedAgentDataRecord(Base):
    __tablename__ = "processed_agent_data"
    id = Column(Integer, primary_key=True, index=True)
    road_state = Column(String)
    user_id = Column(Integer)
    x = Column(Float)
    y = Column(Float)
    z = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    timestamp = Column(DateTime, default=datetime.now)

class ProcessedAgentDataInDB(BaseModel):
    id: int
    road_state: str
    user_id: int
    x: float
    y: float
    z: float
    latitude: float
    longitude: float
    timestamp: datetime


# FastAPI models
class AccelerometerData(BaseModel):
    x: float
    y: float
    z: float


class GpsData(BaseModel):
    latitude: float
    longitude: float


class AgentData(BaseModel):
    user_id: int
    accelerometer: AccelerometerData
    gps: GpsData
    timestamp: datetime

    @classmethod
    @field_validator("timestamp", mode="before")
    def check_timestamp(cls, value):
        if isinstance(value, datetime):
            return value
        try:
            return datetime.fromisoformat(value)
        except (TypeError, ValueError):
            raise ValueError(
                "Invalid timestamp format. Expected ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ)."
            )


class ProcessedAgentData(BaseModel):
    road_state: str
    agent_data: AgentData


# WebSocket subscriptions
subscriptions: Dict[int, Set[WebSocket]] = {}


# FastAPI WebSocket endpoint
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    if user_id not in subscriptions:
        subscriptions[user_id] = set()
    subscriptions[user_id].add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        subscriptions[user_id].remove(websocket)


# Function to send data to subscribed users
async def send_data_to_subscribers(user_id: int, data):
    if user_id in subscriptions:
        for websocket in subscriptions[user_id]:
            await websocket.send_json(json.dumps(data))

metadata.reflect(bind=engine)

if 'processed_agent_data' not in metadata.tables:
    Base.metadata.create_all(bind=engine)


@app.post("/processed_agent_data/")
async def create_processed_agent_data(data: List[ProcessedAgentData]):
    session = SessionLocal()

    for item in data:
        # Create an instance of ProcessedAgentDataInDB
        new_record = ProcessedAgentDataRecord(
            road_state=item.road_state,
            user_id=item.agent_data.user_id,
            x=item.agent_data.accelerometer.x,
            y=item.agent_data.accelerometer.y,
            z=item.agent_data.accelerometer.z,
            latitude=item.agent_data.gps.latitude,
            longitude=item.agent_data.gps.longitude,
            timestamp=item.agent_data.timestamp
        )

        session.add(new_record)

        await send_data_to_subscribers(item.agent_data.user_id, item)

    session.commit()

    session.close()
    return True


@app.get(
    "/processed_agent_data/{processed_agent_data_id}",
    response_model=ProcessedAgentDataInDB,
)
def read_processed_agent_data(processed_agent_data_id: int):
    session = SessionLocal()
    record = session.query(ProcessedAgentDataRecord).filter(ProcessedAgentDataRecord.id == processed_agent_data_id).first()
    session.close()
    data = ProcessedAgentDataInDB(
        id=record.id,
        road_state=record.road_state,
        user_id=record.user_id,
        x=record.x,
        y=record.y,
        z=record.z,
        latitude=record.latitude,
        longitude=record.longitude,
        timestamp=record.timestamp
    )

    return data


@app.get("/processed_agent_data/", response_model=list[ProcessedAgentDataInDB])
def list_processed_agent_data():
    session = SessionLocal()
    records = session.query(ProcessedAgentDataRecord).all()
    session.close()

    list = []

    for record in records:
        data = ProcessedAgentDataInDB(
            id=record.id,
            road_state=record.road_state,
            user_id=record.user_id,
            x=record.x,
            y=record.y,
            z=record.z,
            latitude=record.latitude,
            longitude=record.longitude,
            timestamp=record.timestamp
        )
        list.append(data)

    return list


@app.put(
    "/processed_agent_data/{processed_agent_data_id}",
    response_model=ProcessedAgentDataInDB,
)
def update_processed_agent_data(processed_agent_data_id: int, data: ProcessedAgentData):
    session = SessionLocal()

    record = session.query(ProcessedAgentDataRecord).filter(ProcessedAgentDataRecord.id == processed_agent_data_id).first()

    record.road_state = data.road_state
    record.user_id = data.agent_data.user_id
    record.x=data.agent_data.accelerometer.x,
    record.y=data.agent_data.accelerometer.y,
    record.z=data.agent_data.accelerometer.z,
    record.latitude=data.agent_data.gps.latitude,
    record.longitude=data.agent_data.gps.longitude,
    record.timestamp=data.agent_data.timestamp

    session.commit()

    session.close()

    return ProcessedAgentDataInDB(
        id=processed_agent_data_id,
        road_state=data.road_state,
        user_id=data.agent_data.user_id,
        x=data.agent_data.accelerometer.x,
        y=data.agent_data.accelerometer.y,
        z=data.agent_data.accelerometer.z,
        latitude=data.agent_data.gps.latitude,
        longitude=data.agent_data.gps.longitude,
        timestamp=data.agent_data.timestamp
    )


@app.delete(
    "/processed_agent_data/{processed_agent_data_id}",
    response_model=ProcessedAgentDataInDB,
)
def delete_processed_agent_data(processed_agent_data_id: int):
    session = SessionLocal()

    record = session.query(ProcessedAgentDataRecord).filter(ProcessedAgentDataRecord.id == processed_agent_data_id).first()

    session.delete(record)
    session.commit()

    session.close()

    return ProcessedAgentDataInDB(
        id=record.id,
        road_state=record.road_state,
        user_id=record.user_id,
        x=record.x,
        y=record.y,
        z=record.z,
        latitude=record.latitude,
        longitude=record.longitude,
        timestamp=record.timestamp
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
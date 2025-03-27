import connexion
from connexion import NoContent
from datetime import datetime
import functools
import json
from threading import Thread
from pykafka import KafkaClient
from pykafka.common import OffsetType
import logging
import logging.config
import yaml
from sqlalchemy.orm import Session
from sqlalchemy import select
from database import engine, get_db
from models import Base, TemperatureEvent, TrafficEvent
from flask import jsonify
import os
Base.metadata.create_all(bind=engine)

from dotenv import load_dotenv

load_dotenv()

env = os.getenv("ENV", "dev")
base_config = os.environ.get("APP_CONF_PATH", "/configs")

config_path = os.path.join(base_config, env)
app_conf_file = os.path.join(config_path, "storage/app_conf.yml")

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f)
with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f)
service_name = os.getenv("SERVICE_NAME", "default_service")
log_file_path = f"logs/{service_name}.log"
if "file" in log_config["handlers"]:
    log_config["handlers"]["file"]["filename"] = log_file_path
logging.config.dictConfig(log_config)
logger = logging.getLogger('basicLogger')


# Configurations from app_conf.yml
KAFKA_HOST = app_config['events']['hostname'] + ":" + str(app_config['events']['port'])
KAFKA_TOPIC = app_config['events']['topic']

def parse_timestamp(timestamp_str):
    return datetime.fromisoformat(timestamp_str.replace("Z", ""))  

def use_db_session(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        db = next(get_db())
        try:
            return func(db, *args, **kwargs)
        finally:
            db.close()
    return wrapper

@use_db_session
def report_temperature(db: Session, body):
    """Store a temperature event in the database."""
    logger.info(body)
    event = TemperatureEvent(
        event_id=body.get("eventID"),
        sensor_id=body.get("sensorId"),
        temperature=body.get("temperature"),
        timestamp=parse_timestamp(body.get("timestamp")),
        city_zone=body.get("cityZone"),
        trace_id=body.get("trace_id")
    )
    db.add(event)
    db.commit()
    logger.debug(f"Stored event temperature_condition with a trace id of {event.trace_id}")
    return NoContent, 200

@use_db_session
def report_traffic(db: Session, body):
    """Store a traffic event in the database."""
    logger.info(body)
    event = TrafficEvent(
        event_id=body.get("eventID"),
        sensor_id=body.get("sensorId"),
        traffic_density=body.get("trafficDensity"),
        timestamp=parse_timestamp(body.get("timestamp")),
        incident_report=body.get("incidentReport"),
        trace_id=body.get("trace_id")
    )
    db.add(event)
    db.commit()
    logger.debug(f"Stored event traffic_condition with a trace id of {event.trace_id}")
    return NoContent, 200

# API for querying events
@use_db_session
def get_temperature_events(db: Session, start_timestamp, end_timestamp):
    """Retrieve temperature events within a given time range."""
    start_time = parse_timestamp(start_timestamp)
    end_time = parse_timestamp(end_timestamp)

    logger.debug(f"Querying temperature events from {start_time} to {end_time}")

    statement = select(TemperatureEvent).where(
        TemperatureEvent.date_created >= start_time,
        TemperatureEvent.date_created < end_time
    )

    events = db.execute(statement).scalars().all()
    logger.debug(f"Found {len(events)} temperature events")

    return jsonify([
        {
            "trace_id": event.trace_id,
            "sensorId": event.sensor_id,
            "temperature": event.temperature,
            "timestamp": event.date_created.isoformat(),
            "cityZone": event.city_zone
        }
        for event in events
    ]), 200

@use_db_session
def get_traffic_events(db: Session, start_timestamp, end_timestamp):
    """Retrieve traffic events within a given time range."""
    start_time = parse_timestamp(start_timestamp)
    end_time = parse_timestamp(end_timestamp)

    logger.debug(f"Querying traffic events from {start_time} to {end_time}")

    statement = select(TrafficEvent).where(
        TrafficEvent.date_created >= start_time,
        TrafficEvent.date_created < end_time
    )

    events = db.execute(statement).scalars().all()
    logger.debug(f"Found {len(events)} traffic events")
    return jsonify([
        {
            "trace_id": event.trace_id,
            "sensorId": event.sensor_id,
            "trafficDensity": event.traffic_density,
            "timestamp": event.date_created.isoformat(),
            "incidentReport": event.incident_report
        }
        for event in events
    ]), 200

def process_messages():
    """Process event messages from Kafka"""
    client = KafkaClient(hosts=KAFKA_HOST)
    topic = client.topics[str.encode(KAFKA_TOPIC)]

    consumer = topic.get_simple_consumer(consumer_group=b'event_group',
                                         reset_offset_on_start=False,
                                         auto_offset_reset=OffsetType.LATEST)

    for msg in consumer:
        msg_str = msg.value.decode('utf-8')
        msg = json.loads(msg_str)
        # logger.info(f"Message: {msg}")
        payload = msg["payload"]
        logger.info(f"Payload: {payload}")
        if msg["type"] == "temperature_condition":
            report_temperature(payload)
        elif msg["type"] == "traffic_condition":
            report_traffic(payload)

        # Commit the message as processed
        consumer.commit_offsets()

def setup_kafka_thread():
    """Set up Kafka consumer in a separate thread"""
    t1 = Thread(target=process_messages)
    t1.daemon = True
    t1.start()

app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("AARONDIMA-Smart-City-App-1.0.0.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    setup_kafka_thread()  # Start Kafka consumer in a separate thread
    app.run(port=8090, host="0.0.0.0")

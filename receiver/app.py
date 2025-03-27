import connexion
from connexion import NoContent
import uuid
import yaml
import logging
import logging.config
from pykafka import KafkaClient
import datetime
from datetime import timezone
import json
import os
from dotenv import load_dotenv

load_dotenv()

app_conf_file = os.getenv("APP_CONF_FILE", "/app/app_conf.yml")

with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())
TEMPERATURE_URL = app_config['events']['temperature']['url']
TRAFFIC_URL = app_config['events']['traffic']['url']

log_conf_file = os.getenv("LOG_CONF_FILE", "/app/log_conf.yml")
with open(log_conf_file, "r") as f:
    log_config = yaml.safe_load(f.read())
service_name = os.getenv("SERVICE_NAME", "default_service")
log_file_path = f"logs/{service_name}.log"
if "file" in log_config["handlers"]:
    log_config["handlers"]["file"]["filename"] = log_file_path
logging.config.dictConfig(log_config)
logger = logging.getLogger('basicLogger')

logger = logging.getLogger('basicLogger')
# def report_temperature(body):
#     """Forward temperature event to storage service."""
#     trace_id = str(uuid.uuid4())
#     body["trace_id"] = trace_id
#     logger.info(f"Received event temperature_condition with a trace id of {trace_id}")
#     response = httpx.post(TEMPERATURE_URL, json=body)
#     logger.info(f"Response for event temperature_condition (id: {trace_id}) has status {response.status_code}") 
#     return NoContent, response.status_code 

# def report_traffic(body):
#     """Forward traffic event to storage service."""
#     trace_id = str(uuid.uuid4())
#     body["trace_id"] = trace_id 
#     logger.info(f"Received event traffic_condition with a trace id of {trace_id}")
#     response = httpx.post(TRAFFIC_URL, json=body)
#     logger.info(f"Response for event traffic_condition (id: {trace_id}) has status {response.status_code}")
#     return NoContent, response.status_code 

KAFKA_HOST = app_config['events']['hostname']
KAFKA_PORT = app_config['events']['port']
KAFKA_TOPIC = app_config['events']['topic']
print(KAFKA_HOST, KAFKA_PORT, KAFKA_TOPIC)
client = KafkaClient(hosts=f'{KAFKA_HOST}:{KAFKA_PORT}')
topic = client.topics[str.encode(KAFKA_TOPIC)]
producer = topic.get_sync_producer()

def report_temperature(body):
    """Forward temperature event to Kafka."""
    trace_id = str(uuid.uuid4())
    body["trace_id"] = trace_id
    msg = {
        "type": "temperature_condition",
        "datetime": datetime.datetime.now(timezone.utc).isoformat(),
        "payload": body
    }

    logger.info(f"Received event temperature_condition with a trace id of {trace_id}")
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    
    logger.info(f"Event temperature_condition (id: {trace_id}) sent to Kafka")
    return NoContent, 201  # Return HTTP 201 Created

def report_traffic(body):
    """Forward traffic event to Kafka."""
    trace_id = str(uuid.uuid4())
    body["trace_id"] = trace_id
    msg = {
        "type": "traffic_condition",
        "datetime": datetime.datetime.now(timezone.utc).isoformat(),
        "payload": body
    }

    logger.info(f"Received event temperature_condition with a trace id of {trace_id}")
    msg_str = json.dumps(msg)
    producer.produce(msg_str.encode('utf-8'))
    
    logger.info(f"Event traffic_condition (id: {trace_id}) sent to Kafka")
    return NoContent, 201  # Return HTTP 201 Created

app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("AARONDIMA-Smart-City-App-1.0.0.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080, host="0.0.0.0")

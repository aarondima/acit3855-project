import connexion
import json
from pykafka import KafkaClient
import logging
import logging.config
import yaml
import os

with open('log_conf.yml', 'r') as f:
    log_config = yaml.safe_load(f)
service_name = os.getenv("SERVICE_NAME", "default_service")
log_file_path = f"logs/{service_name}.log"
if "file" in log_config["handlers"]:
    log_config["handlers"]["file"]["filename"] = log_file_path
logging.config.dictConfig(log_config)
logger = logging.getLogger('basicLogger')

logger.info(f"Logging initialized for service: {service_name}")

# Configurations from app_conf.yml
with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())
KAFKA_HOST = app_config['events']['hostname']
KAFKA_PORT = app_config['events']['port']
KAFKA_TOPIC = app_config['events']['topic']

def get_temperature(index):
    index = int(index)  # Ensure index is an integer
    logger.info(f"Fetching temperature event at index {index}")
    client = KafkaClient(hosts=f'{KAFKA_HOST}:{KAFKA_PORT}')
    topic = client.topics[str.encode(KAFKA_TOPIC)]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    counter = 0
    for msg in consumer:
        message = msg.value.decode("utf-8")
        data = json.loads(message)
        payload = data['payload']
        event_type = data.get("type")
        if event_type == 'temperature_condition':
            if counter == index:
                return payload, 200
            counter += 1
    logger.warning(f"No temperature event found at index {index}")
    return {"message": f"No message at index {index}!"}, 404

def get_traffic(index):
    logger.info(f"Fetching traffic event at index {index}")
    client = KafkaClient(hosts=f'{KAFKA_HOST}:{KAFKA_PORT}')
    topic = client.topics[str.encode(KAFKA_TOPIC)]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    counter = 0
    for msg in consumer:
        message = msg.value.decode("utf-8")
        data = json.loads(message)
        payload = data["payload"]
        logger.info(f"Payload: {payload}")
        payload = data['payload']
        event_type = data.get("type")
        if event_type == 'traffic_condition':
            if counter == index:
                return payload, 200
            counter += 1
    logger.warning(f"No traffic event found at index {index}")
    return { "message": f"No message at index {index}!"}, 404

def get_stats():
    logger.info("Fetching statistics of events")
    client = KafkaClient(hosts=f'{KAFKA_HOST}:{KAFKA_PORT}')
    topic = client.topics[str.encode(KAFKA_TOPIC)]
    consumer = topic.get_simple_consumer(reset_offset_on_start=True, consumer_timeout_ms=1000)
    stats = {
        "num_temperature": 0,
        "num_traffic": 0
    }
    
    for msg in consumer:
        message = msg.value.decode("utf-8")
        data = json.loads(message)
        
        event_type = data.get("type")
        if event_type == "temperature_condition":
            stats["num_temperature"] += 1
        elif event_type == "traffic_condition":
            stats["num_traffic"] += 1
    
    logger.info(f"Statistics: {stats}")
    return stats, 200

app = connexion.FlaskApp(__name__, specification_dir="")
app.add_api("AARONDIMA-Smart-City-App-1.0.0.yaml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8110, host="0.0.0.0")
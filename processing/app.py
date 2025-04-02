import connexion
from connexion import NoContent
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
import logging
import logging.config
from flask import Flask
import yaml
import json
import os
import httpx
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

load_dotenv()

app_conf_file = os.getenv("APP_CONF_FILE", "/app/app_conf.yml")
# Load application configuration
with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f)
TEMPERATURE_URL = app_config['eventstores']['temperature']['url']
TRAFFIC_URL = app_config['eventstores']['traffic']['url']
stats_file = app_config['datastore']['filename']
app = Flask(__name__)

log_conf_file = os.getenv("LOG_CONF_FILE", "/app/log_conf.yml")
# Load logging configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f)
service_name = os.getenv("SERVICE_NAME", "default_service")
log_file_path = f"logs/{service_name}.log"
if "file" in log_config["handlers"]:
    log_config["handlers"]["file"]["filename"] = log_file_path
logging.config.dictConfig(log_config)
logger = logging.getLogger('basicLogger')


def populate_stats():
    logger.info("Periodic processing has started")

    stats_file = app_config['datastore']['filename']
    stats_dir = os.path.dirname(stats_file)

    # Ensure the directory exists
    if stats_dir and not os.path.exists(stats_dir):
        os.makedirs(stats_dir)
        logger.info(f"Created missing directory: {stats_dir}")
    
    default_stats = {
        "num_temperature_readings": 0,
        "max_temperature": 0,
        "num_traffic_readings": 0,
        "max_traffic_density": 0,
        "last_updated": (datetime.now(timezone.utc) - timedelta(minutes=5)).isoformat()
    }

    # Check if stats file exists, if not create it with default values
    if os.path.exists(stats_file):
        logger.info(f"Found existing stats file: {stats_file}")
        with open(stats_file, 'r') as f:
            stats = json.load(f)
    else:
        logger.info(f"File not found, creating {stats_file} with default values")
        stats = default_stats
        # Ensure the file gets created
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=4)
        logger.info(f"Created the file: {stats_file}")

    logger.info(f"Last updated timestamp in file: {stats['last_updated']}")
    last_updated = stats["last_updated"]
    current_time = datetime.now(timezone.utc).isoformat()
    logger.debug(f"Current time: {current_time}")
    
    # Ensure 'last_updated' field is being updated
    if last_updated != current_time:
        logger.info(f"Updating 'last_updated' timestamp to {current_time}")
        stats["last_updated"] = current_time
    
    params = {"start_timestamp": last_updated, "end_timestamp": current_time}
    
    temperature_response = httpx.get(TEMPERATURE_URL, params=params)
    traffic_response = httpx.get(TRAFFIC_URL, params=params)
    
    temperature_events = temperature_response.json() if temperature_response.status_code == 200 else []
    traffic_events = traffic_response.json() if traffic_response.status_code == 200 else []
    logger.debug(f"Temperature events received: {temperature_events[:2]}")
    logger.debug(f"Traffic events received: {traffic_events[:2]}")
    
    if not temperature_events and not traffic_events:
        logger.error("Failed to get events or no new events found.")

    
    if temperature_events:
        temperature_values = [event["temperature"] for event in temperature_events]
        stats["num_temperature_readings"] += len(temperature_values)
        stats["max_temperature"] = max(stats["max_temperature"], max(temperature_values))
        
    if traffic_events:
        traffic_values = [event["trafficDensity"] for event in traffic_events]
        stats["num_traffic_readings"] += len(traffic_values)
        stats["max_traffic_density"] = max(stats["max_traffic_density"], max(traffic_values))
    
    # After updating, save stats back to the file
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=4)
    
    logger.info("Periodic processing has ended")

@app.route("/stats", methods=["GET"])
def get_stats():
    logger.info("Request received for event statistics")

    stats_file = app_config['datastore']['filename']

    if not os.path.exists(stats_file):
        logger.error("Statistics do not exist")
        return {"message": "Statistics do not exist"}, 404

    with open(stats_file, 'r') as f:
        stats = json.load(f)

    logger.debug(f"Stats content: {stats}")
    logger.info("Request for event statistics completed")
    return stats, 200

def init_scheduler():
    sched = BackgroundScheduler(daemon=True)
    sched.add_job(populate_stats, 'interval', seconds=app_config['scheduler']['interval'])
    sched.start()

app = connexion.FlaskApp(__name__, specification_dir="")
if "CORS_ALLOW_ALL" in os.environ and os.environ["CORS_ALLOW_ALL"] == "yes":
    app.add_middleware(
        CORSMiddleware,
        position=MiddlewarePosition.BEFORE_EXCEPTION,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
app.add_api(
    "AARONDIMA-Smart-City-App-1.0.0.yaml",
    base_path="/processing",
    strict_validation=True,
    validate_responses=True
)

if __name__ == "__main__":
    init_scheduler()
    app.run(port=8100, host="0.0.0.0")
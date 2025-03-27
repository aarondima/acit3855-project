from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import yaml
from dotenv import load_dotenv
import os
load_dotenv()

# Get the configuration file path (default if APP_CONF_FILE not set)
app_conf_file = os.getenv("APP_CONF_FILE", "/app/app_conf.yml")

# Read the YAML file and replace environment variables
with open(app_conf_file, 'r') as f:
    config_str = os.path.expandvars(f.read())  # Replaces ${VAR} with actual env values
    app_config = yaml.safe_load(config_str)  # Parse YAML content

# Extract datastore configuration
db_config = app_config['datastore']

# Build the database URL using substituted values
DATABASE_URL = (
    f"mysql://{db_config['user']}:{db_config['password']}"
    f"@{db_config['hostname']}:{db_config['port']}/{db_config['db']}"
)

engine = create_engine(DATABASE_URL, echo=True)  
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import yaml
from dotenv import load_dotenv
import os
load_dotenv()
app_conf_file = os.getenv("APP_CONF_FILE", "/app/app_conf.yml")
with open(app_conf_file, 'r') as f:
    # Expand the env variables in the file content
    config_str = os.path.expandvars(f.read())
    app_config = yaml.safe_load(config_str)

db_config = app_config['datastore']
DATABASE_URL = f"mysql://{db_config['user']}:{db_config['password']}@{db_config['hostname']}:{db_config['port']}/{db_config['db']}"

engine = create_engine(DATABASE_URL, echo=True)  
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
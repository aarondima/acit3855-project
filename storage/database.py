from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import yaml
with open('app_conf.yml', 'r') as f:
    app_config = yaml.safe_load(f.read())

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
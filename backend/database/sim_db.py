import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

SIM_DATABASE_URL = os.getenv("SIM_DATABASE_URL")

engine = create_engine(SIM_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_sim_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

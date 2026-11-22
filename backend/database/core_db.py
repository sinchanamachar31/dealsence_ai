import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DEALSENSE_DATABASE_URL = os.getenv(
    "DEALSENSE_DATABASE_URL",
    os.getenv(
        "CORE_DATABASE_URL",
        os.getenv("SIM_DATABASE_URL", "sqlite:///./dealsense_core.db"),
    ),
)

core_engine = create_engine(DEALSENSE_DATABASE_URL)
CoreSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=core_engine)
CoreBase = declarative_base()


def get_core_db():
    db = CoreSessionLocal()
    try:
        yield db
    finally:
        db.close()

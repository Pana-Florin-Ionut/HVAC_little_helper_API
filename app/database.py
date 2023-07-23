from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os

load_dotenv()
password = os.getenv("DBPASS")
user = os.getenv("DBUSER")
host = os.getenv("DBHOST")
name = os.getenv("DBNAME")
port = os.getenv("DBPORT")

SQLALCHEMY_DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{name}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    except:
        db.rollback()
        raise
    finally:
        db.close()

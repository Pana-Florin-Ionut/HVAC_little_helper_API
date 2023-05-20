from datetime import datetime
from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table, Double
from sqlalchemy import MetaData


def create_offer_table(engine, title):
    Table(
        str(title),
        Base.metadata,
        Column("id", Integer, primary_key=True),
        Column("product_name", String, nullable=False),
        Column("ch1", String, nullable=True),
        Column("ch2", String, nullable=True),
        Column("ch3", String, nullable=True),
        Column("ch4", String, nullable=True),
        Column("ch5", String, nullable=True),
        Column("ch6", String, nullable=True),
        Column("ch7", String, nullable=True),
        Column("ch8", String, nullable=True),
        Column("UM", String, nullable=False),
        Column("quantity", Double, nullable=False),
        Column("price", Double, nullable=False),
    )

    Base.metadata.create_all(bind=engine)


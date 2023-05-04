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
        Column("CH1", Double, nullable=False),
        Column("CH2", Double, nullable=True),
        Column("CH3", Double, nullable=True),
        Column("CH4", Double, nullable=True),
        Column("CH5", Double, nullable=True),
        Column("CH6", Double, nullable=True),
        Column("CH7", Double, nullable=True),
        Column("CH8", Double, nullable=True),
        Column("UM", String, nullable=False),
        Column("quantity", Double, nullable=False),
        Column("price", Double, nullable=False),
    )

    Base.metadata.create_all(bind=engine)

def get_table(title):
    return Base.metadata.tables[title]


# def get_offer_table(offer_name, engine):
    # metadata = MetaData().reflect(bind = engine)
    # return metadata.tables[offer_name]
    


# def get_offer2(offer_name):
#     return Base.metadata.tables[offer_name]

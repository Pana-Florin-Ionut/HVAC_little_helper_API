from datetime import datetime
from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text


class Offers(Base):
    __tablename__ = "offers"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    is_finalized = Column(Boolean, server_default="TRUE", nullable=False)
    timestamp = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    # created_by = Column(Integer, ForeignKey("users.id"))


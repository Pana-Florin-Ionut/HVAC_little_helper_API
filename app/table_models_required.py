from datetime import datetime
from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table, Sequence
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy import MetaData

# same function as index=True?
# users_id_seq = Sequence("users_id_seq", metadata=MetaData(), start=1)
# companies_id_seq = Sequence("companies_id_seq", metadata=MetaData(), start=1)
# projects_id_seq = Sequence("projects_id_seq", metadata=MetaData(), start=1)
# offers_id_seq = Sequence("offers_id_seq", metadata=MetaData(), start=1)


class Users(Base):
    __tablename__ = "users"
    #  server_default=users_id_seq.next_value(),
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    company_id = Column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=True
    )
    role = Column(String, nullable=True)
    created = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )


class Companies(Base):
    __tablename__ = "companies"
    # server_default=companies_id_seq.next_value(),
    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )
    company_name = Column(String, nullable=False, unique=True)
    company_key = Column(String, nullable=False, unique=True)
    created = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )


class Projects(Base):
    __tablename__ = "projects"
    # server_default=projects_id_seq.next_value(),
    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )
    company_id = Column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    project_name = Column(String, nullable=False, unique=True)
    project_key = Column(String, nullable=False, unique=True)
    created = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    # created_by = Column(Integer, ForeignKey("users.id"))


class Offers(Base):
    __tablename__ = "offers"
    # server_default=offers_id_seq.next_value(),
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    company_id = Column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    project_id = Column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    offer_name = Column(String, nullable=False, unique=True)
    offer_key = Column(String, nullable=False, unique=True)
    is_finalized = Column(Boolean, server_default="TRUE", nullable=True, default=False)
    timestamp = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)


class Roles(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    can_create_project = Column(Boolean, server_default="FALSE")
    can_create_offer = Column(Boolean, server_default="FALSE")
    can_create_product = Column(Boolean, server_default="FALSE")
    can_view_project = Column(Boolean, server_default="FALSE")
    can_view_offer = Column(Boolean, server_default="FALSE")
    can_view_product = Column(Boolean, server_default="FALSE")
    created = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )

class Products(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, nullable=False, unique=True)
    product_key = Column(String, nullable=False, unique=True)
    ch1 = Column(String, nullable=False)
    ch2 = Column(String, nullable=False)
    ch3 = Column(String, nullable=False)
    ch4 = Column(String, nullable=False)
    ch5 = Column(String, nullable=False)
    ch6 = Column(String, nullable=False)
    ch7 = Column(String, nullable=False)
    ch8 = Column(String, nullable=False)
    created = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
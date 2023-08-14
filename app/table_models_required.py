from datetime import datetime
from .database import Base
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    Double,
    Table,
    Sequence,
    UniqueConstraint,
)
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship

# same function as index=True?
# users_id_seq = Sequence("users_id_seq", metadata=MetaData(), start=1)
# companies_id_seq = Sequence("companies_id_seq", metadata=MetaData(), start=1)
# projects_id_seq = Sequence("projects_id_seq", metadata=MetaData(), start=1)
# offers_id_seq = Sequence("offers_id_seq", metadata=MetaData(), start=1)


class Users(Base):
    __tablename__ = "users"
    #  server_default=users_id_seq.next_value(),
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    company_key = Column(String, ForeignKey("companies.company_key"), nullable=True)
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
    is_verified = Column(Boolean, server_default="FALSE")
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
    company_key = Column(String, ForeignKey("companies.company_key"), nullable=False)
    project_name = Column(String, nullable=False)
    project_key = Column(String, nullable=False)
    created = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    UniqueConstraint(company_key, project_name, name="unique_project_name_for_company")
    UniqueConstraint(company_key, project_key, name="unique_project_key_for_company")
    owner = relationship("Users")
    company = relationship("Companies")


class Offers(Base):
    __tablename__ = "offers"
    # server_default=offers_id_seq.next_value(),
    id = Column(Integer, primary_key=True, index=True)
    client_key = Column(String, ForeignKey("companies.company_key"), nullable=False)
    company_key = Column(
        String, ForeignKey("companies.company_key", ondelete="CASCADE"), nullable=False
    )
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    project_key = Column(String, nullable=False)
    offer_name = Column(String, nullable=False)
    offer_key = Column(String, nullable=False)
    is_finalized = Column(Boolean, server_default="TRUE", nullable=True, default=False)
    created = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    UniqueConstraint(offer_key, project_id, name="unique_offer_key_for_project")
    UniqueConstraint(offer_name, project_id, name="unique_offer_name_for_project")
    owner = relationship("Users")
    company = relationship("Companies", foreign_keys="Offers.company_key")
    client = relationship("Companies", foreign_keys="Offers.client_key")
    project = relationship("Projects", foreign_keys="Offers.project_id")


class Permissions(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    can_create_project = Column(Boolean, server_default="FALSE")
    can_create_offer = Column(Boolean, server_default="FALSE")
    can_create_product = Column(Boolean, server_default="FALSE")
    can_view_project = Column(Boolean, server_default="FALSE")
    can_view_offer = Column(Boolean, server_default="FALSE")
    can_view_product = Column(Boolean, server_default="FALSE")
    can_delete_project = Column(Boolean, server_default="FALSE")
    can_delete_offer = Column(Boolean, server_default="FALSE")
    can_delete_product = Column(Boolean, server_default="FALSE")
    can_view_user = Column(Boolean, server_default="FALSE")
    can_add_user = Column(Boolean, server_default="FALSE")
    can_edit_user = Column(Boolean, server_default="FALSE")
    created = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )


class Products(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String, nullable=False)
    product_key = Column(String, nullable=False, unique=True)
    ch1 = Column(String, nullable=False)
    ch2 = Column(String, nullable=False)
    ch3 = Column(String, nullable=False)
    ch4 = Column(String, nullable=False)
    ch5 = Column(String, nullable=False)
    ch6 = Column(String, nullable=False)
    ch7 = Column(String, nullable=False)
    ch8 = Column(String, nullable=False)
    UM = Column(Double, nullable=False)
    created = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    created_by = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )


class CompanyConnections(Base):
    __tablename__ = "company_connections"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(
        Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    friend_id = Column(Integer, ForeignKey("companies.id"), nullable=False)


class OffersBody(Base):
    __tablename__ = "offers_body"
    id = Column(Integer, primary_key=True, index=True)
    offer_id = Column(Integer, ForeignKey("offers.id"), nullable=False)
    product_name = Column(String, nullable=False)
    product_key = Column(String, nullable=False)
    ch_1 = Column(String, nullable=True)
    ch_2 = Column(String, nullable=True)
    ch_3 = Column(String, nullable=True)
    ch_4 = Column(String, nullable=True)
    ch_5 = Column(String, nullable=True)
    ch_6 = Column(String, nullable=True)
    ch_7 = Column(String, nullable=True)
    ch_8 = Column(String, nullable=True)
    um = Column(String, nullable=False)
    quantity = Column(Double, nullable=False)
    observations = Column(String, nullable=True)

    created = Column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    created_by = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )


class OfferPrices(Base):
    __tablename__ = "offer_prices"

    id = Column(Integer, primary_key=True, index=True)
    offering_company = Column(Integer, ForeignKey("companies.id"), nullable=False)
    offer_product_id = Column(Integer, ForeignKey("offers_body.id"), nullable=False)
    price = Column(Double, nullable=False)

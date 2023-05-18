from psycopg2 import sql
from sqlalchemy import literal_column, text
from .database import get_db as conn


# def create_clients_table():
#     return """CREATE TABLE IF NOT EXISTS clients (
#         id SERIAL PRIMARY KEY,
#         client_name VARCHAR(255)
#         )"""


# def create_projects_table():
#     return """CREATE TABLE IF NOT EXISTS projects (
#         id SERIAL PRIMARY KEY,
#         client_id INT,
#         project_name VARCHAR(255),
#         FOREIGN KEY (client_id) REFERENCES clients(id)
#         )"""


# def create_offers_table():
#     return """CREATE TABLE IF NOT EXISTS offers (
#         id SERIAL PRIMARY KEY,
#         client_id INT,
#         project_id INT,
#         offer_name VARCHAR(255) UNIQUE,
#         FOREIGN KEY (project_id) REFERENCES projects(id),
#         FOREIGN KEY (client_id) REFERENCES clients(id)
#         )"""


def create_offer_table(table_name):
    return sql.SQL(
        """CREATE TABLE {table_name} (
        id SERIAL PRIMARY KEY,
        product_name VARCHAR(255),
        ch1 VARCHAR(255),
        ch2 VARCHAR(255),
        ch3 VARCHAR(255),
        ch4 VARCHAR(255),
        ch5 VARCHAR(255),
        ch6 VARCHAR(255),
        ch7 VARCHAR(255),
        ch8 VARCHAR(255),
        UM VARCHAR(255),
        quantity Decimal)   
    """
    ).format(table_name=sql.Identifier(table_name))


def insert_offer_row(table_name, columns, values):
    print(columns)
    """Insert a row in offer table.
    Required table name, columns, values
    It does not need id
    """
    return sql.SQL("""INSERT INTO {table_name} ({columns}) VALUES ({values})""").format(
        table_name=sql.Identifier(table_name),
        columns=sql.SQL(", ").join(map(sql.Identifier, columns)),
        values=sql.SQL(", ").join(map(sql.Literal, values)),
    )


def get_offer(offer_name):
    # query = sql.SQL("""SELECT * FROM offers WHERE offer_name = {offer_name}""")
    # query = query.format(offer_name=sql.Literal(offer_name))
    # print(f"query: {query.as_string(conn)}")
    # query = f"""SELECT * FROM offers WHERE offer_name = '{offer_name}' """
    query = f"""SELECT * FROM {offer_name} """
    return query
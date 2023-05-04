from contextlib import contextmanager
import psycopg2
from psycopg2.pool import SimpleConnectionPool 
from dotenv import load_dotenv
import os

load_dotenv()

host = os.getenv("DBHOST")
database = os.getenv("DBNAME")
user = os.getenv("DBUSER")
password = os.getenv("DBPASS")

conn = psycopg2.connect(
    host=host,
    database=database,
    user=user,
    password=password,
    port=5432,
)

# pool = SimpleConnectionPool(
#     minconn=1,
#     maxconn=10,
#     host=host,
#     database=database,
#     user=user,
#     password=password,
#     port=5432,
# )
# @contextmanager
# def get_connection():
#     connection = pool.getconn()
#     try:
#         yield connection
#     finally:
#         pool.putconn(connection)

# # @contextmanager
# def get_cursor(connection):
#     with connection.cursor() as cursor:
#         yield cursor
# def connect():
#     conn = None
#     try:
#         psycopg2.connect(
#             host=host,
#             database=database,
#             user=user,
#             password=password,
#             port=5432,
#         )
#     except (Exception, psycopg2.DatabaseError) as error:
#         print(error)
#     finally:
#         if conn is not None:
#             conn.close()

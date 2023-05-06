import psycopg2
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


class Database:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = self.connection.cursor

    def create_table(self, query):
        with self.cursor() as cursor:
            print(query)
            cursor.execute(query)
            self.connection.commit()


def make_table(table_name):
    return f"CREATE TABLE IF NOT EXISTS {table_name} (id INT, name VARCHAR(255), PRIMARY KEY (id))"


# new_db = Database(conn)
# new_db.create_table(make_table("test_table"))

import psycopg2


class Database:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = self.connection.cursor

    def create_table(self, query):
        with self.cursor() as cursor:
            # print(query)
            cursor.execute(query)
            self.connection.commit()

    def get_table(self, query):
        try:
            with self.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()
        except psycopg2.errors.UndefinedTable:
            return {"message": "Table does not exist"}

    def execute(self, query):
        with self.cursor() as cursor:
            print(query)
            cursor.execute(query)
            self.connection.commit()


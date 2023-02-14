import os
from dotenv import load_dotenv
import pymysql.cursors
import sys

load_dotenv()


def createUser(username):
    connection = pymysql.connect(host=os.getenv('db_host'),
                                user=os.getenv('db_user'),
                                password=os.getenv('db_pass'),
                                database=os.getenv('db_schema'),
                                cursorclass=pymysql.cursors.DictCursor)


    with connection:
        with connection.cursor() as cursor:
            sql = f"INSERT INTO users (username) VALUES ('{username}')"
            cursor.execute(sql)
        connection.commit()

if __name__ == "__main__":
    createUser(sys.argv[1])
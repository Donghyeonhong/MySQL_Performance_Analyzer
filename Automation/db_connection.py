import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

# DB 연결 함수
def get_db_connection_analysis():
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password=os.getenv("DB_PASSWORD"),
        database="performance_analysis_db"
    )


def get_db_connection_test():
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password=os.getenv("DB_PASSWORD"),
        database="performance_test_db"
    )
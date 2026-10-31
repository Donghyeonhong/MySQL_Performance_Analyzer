import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

conn = mysql.connector.connect(
    host="localhost",
    port=3306,
    user="root",
    password=os.getenv("DB_PASSWORD"),
    database="performance_test_db"
)

cursor = conn.cursor()

sql = """
UPDATE orders SET total_price = (SELECT SUM(order_detail.quantity * order_detail.unit_price) FROM order_detail WHERE order_detail.order_id = orders.order_id)"""


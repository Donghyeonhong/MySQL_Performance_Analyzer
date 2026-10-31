import mysql.connector
from dotenv import load_dotenv
import os
import random
from datetime import datetime, timedelta

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
INSERT INTO orders(
    customer_id,
    total_price,
    order_date
)
VALUES (%s, %s, %s)"""

time_now = datetime.now()

extract_sql = """select customer_id, signup_date from customer"""

cursor.execute(extract_sql)

customer_information = cursor.fetchall()

order_list = []

for i in customer_information:
    for e in range(random.randint(0, 12)):
        customer_id = i[0]
        total_price = 0
        order_date = i[1] + timedelta(days=random.randint(0, (time_now - i[1]).days))
        vals = (customer_id, total_price, order_date)
        order_list.append(vals)


# print(len(order_list))
# print(order_list[0])
# print(order_list[-1])
# print(order_list[0:10])

# cursor.executemany(sql, order_list)
# conn.commit()
# print('커밋성공')
# cursor.close()
# conn.close()
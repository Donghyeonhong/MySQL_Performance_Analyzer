import mysql.connector
from dotenv import load_dotenv
import os
import random

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
INSERT INTO order_detail(
    order_id,
    option_id,
    quantity,
    unit_price
)
VALUES (%s, %s, %s, %s)"""

extract_order_sql = """SELECT order_id FROM orders"""

cursor.execute(extract_order_sql)

order_inf = cursor.fetchall()

extract_product_sql = """
SELECT product_option.option_id, product.price FROM product_option 
INNER JOIN product ON product_option.product_id = product.product_id"""

cursor.execute(extract_product_sql)
product_inf = cursor.fetchall()

order_detail_list = []

for i in order_inf:
    option_ids = random.sample(product_inf, random.randint(1, 4))
    for e in option_ids:
        order_id = i[0]
        option_id = e[0]
        quantity = random.randint(1, 2)
        unit_price = e[1]

        vals = (order_id, option_id, quantity, unit_price)
        order_detail_list.append(vals)

# print(len(order_detail_list))
# print(order_detail_list[0])
# print(order_detail_list[-1])
# print(order_detail_list[0:10])

# cursor.executemany(sql, order_detail_list)

# conn.commit()
# print("커밋 완료")
# cursor.close()
# conn.close()
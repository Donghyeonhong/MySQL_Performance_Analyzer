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
INSERT INTO product_option(
    product_id,
    size,
    stock_quantity
)
VALUES (%s, %s, %s)"""

sizes = []
sizes = ["S", "M", "L", "XL"]

categories = []
categories = ["상의", "하의", "아우터"]

sub_categories = ["가방", "모자", "액세서리"]

extract_sql = """
SELECT product_id, category, sub_category FROM product"""

cursor.execute(extract_sql)
option = cursor.fetchall()

option_list = []

for i in option:
    if i[1] in categories:
        for e in sizes:
            product_id = i[0]
            size = e
            stock_quantity = random.randint(0, 500)
            vals = (product_id, size, stock_quantity)
            option_list.append(vals)
    elif i[2] in sub_categories:
        product_id = i[0]
        size = "Free"
        stock_quantity = random.randint(0, 100)
        vals = (product_id, size, stock_quantity)
        option_list.append(vals)
    elif i[2] == "신발":
        product_id = i[0]
        size = str(random.choice(range(200, 301, 5))) + "mm"
        stock_quantity = random.randint(0, 200)
        vals = (product_id, size, stock_quantity)
        option_list.append(vals)

# print(len(option_list))
# print(option_list[0:11])
# print(option_list[-1])

# cursor.executemany(sql, option_list)

# conn.commit()
# print('커밋성공')
# cursor.close()
# conn.close()



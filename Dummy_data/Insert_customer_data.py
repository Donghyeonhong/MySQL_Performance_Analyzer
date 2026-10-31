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
INSERT INTO customer(
    customer_name,
    email,
    phone_number,
    login_id,
    signup_date
)
VALUES (%s, %s, %s, %s, %s)"""


surnames = []
given_names = []
names = []

surnames = [
    "김", "이", "박", "최", "정",
    "강", "조", "윤", "장", "임",
    "한", "오", "서", "신", "권",
    "황", "안", "송", "류", "홍"
]

given_names = [
    "민수", "서연", "지훈", "유진", "현우",
    "민지", "서준", "하은", "우진", "수빈"
]

names = [
    surname + given_name
    for surname in surnames
    for given_name in given_names
]

customer_data = []

time_now = datetime.now()

for i in range(1, 50001):
    customer_name = (random.choice(names))
    email = ('user' + str(i) + '@test.com')
    phone_number = (f"010-{str(i).zfill(8)[:4]}-{str(i).zfill(8)[4:]}")
    login_id = ('user' + str(i))
    signup_date = (time_now - timedelta(days=random.randint(0, 730)))

    vals = (customer_name, email, phone_number, login_id, signup_date)

    customer_data.append(vals)

# print(len(customer_data))
# print(customer_data[0])
# print(customer_data[-1])
# cursor.executemany(sql, customer_data)

# conn.commit()

# print('커밋성공')

# cursor.close()
# conn.close()
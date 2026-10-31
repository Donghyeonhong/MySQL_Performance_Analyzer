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
INSERT INTO product(
    product_name,
    category,
    sub_category,
    gender,
    color,
    price,
    release_date
)
VALUES (%s, %s, %s, %s, %s, %s, %s)"""

categories = {}

categories = {
    "상의": ["티셔츠", "셔츠", "니트", "맨투맨", "후드티"],
    "하의": ["청바지", "슬랙스", "면바지", "반바지", "스커트"],
    "아우터": ["코트", "패딩", "재킷", "가디건", "바람막이"],
    "기타": ["가방", "신발", "모자", "액세서리"]
}

count = {}

count = {
    "상의": 20000,
    "하의": 12500,
    "아우터": 12500,
    "기타": 5000
}

product_names = {}

product_names = {
    "티셔츠": ["오버핏", "베이직", "슬림핏", "크롭", "라운드", "레터링", "프린팅", "스트라이프"],
    "셔츠": ["클래식", "베이직", "오버핏", "스트라이프", "체크", "린넨", "캐주얼"],
    "니트": ["소프트", "케이블", "라운드", "브이넥", "오버핏", "골지", "크롭"],
    "맨투맨": ["데일리", "오버핏", "베이직", "프린팅", "레터링", "크롭"],
    "후드티": ["캐주얼", "오버핏", "베이직", "기모", "프린팅", "집업"],

    "청바지": ["슬림핏", "와이드", "스트레이트", "빈티지", "부츠컷", "테이퍼드"],
    "슬랙스": ["모던", "와이드", "슬림핏", "테이퍼드", "세미와이드", "베이직"],
    "면바지": ["베이직", "코튼", "와이드", "슬림핏", "스트레이트", "캐주얼"],
    "반바지": ["캐주얼", "밴딩", "와이드", "데일리", "코튼", "린넨"],
    "스커트": ["플리츠", "미니", "롱", "A라인", "데님", "H라인"],

    "코트": ["클래식", "울", "오버핏", "롱", "더블", "싱글"],
    "패딩": ["데일리", "숏", "롱", "경량", "오버핏", "후드"],
    "재킷": ["모던", "싱글", "오버핏", "크롭", "데님", "트위드"],
    "가디건": ["소프트", "니트", "베이직", "오버핏", "크롭", "브이넥"],
    "바람막이": ["라이트", "후드", "오버핏", "캐주얼", "스포츠", "베이직"],

    "가방": ["데일리", "미니", "클래식", "캐주얼", "모던", "심플"],
    "신발": ["베이직", "캐주얼", "클래식", "데일리", "스포츠", "레트로"],
    "모자": ["캐주얼", "베이직", "데일리", "빈티지", "스포츠", "심플"],
    "액세서리": ["심플", "모던", "클래식", "미니멀", "빈티지", "데일리"]
}

styles = []

styles = [
    "데일리", "캐주얼", "모던", "클래식",
    "빈티지", "미니멀", "스트릿", "베이직",
    "시크", "스포티", "심플", "트렌디"
]

colors = [
    "블랙", "화이트", "네이비", "그레이", "베이지", "브라운",
    "블루", "레드", "그린", "핑크", "옐로우", "퍼플"
]

time_now = datetime.now()

product_data = []

for category, number in count.items():
    for i in range(number):
        sub_category = random.choice(categories[category])
        product_name = random.choice(styles) + " " + random.choice(product_names[sub_category]) + " " + sub_category

        if category == "기타" or sub_category in ["패딩", "바람막이"]:
            gender = "공통"
        elif sub_category == "스커트":
            gender = "여자"
        else:
            gender = random.choice(["남자", "여자", "공통"])

        color = random.choice(colors)

        price = 0
        if category == "상의":
            price = random.randint(15, 60)*1000
        elif category == "하의":
            price = random.randint(25, 70)*1000
        elif category == "아우터" and sub_category in ["패딩", "코트"]:
            price = random.randint(80, 300)*1000
        elif category == "아우터" and sub_category not in ["패딩", "코트"]:
            price = random.randint(50, 150)*1000
        else:
            price = random.randint(15, 150)*1000

        release_date = (time_now - timedelta(days=random.randint(0, 1825)))
        
        vals=(product_name, category, sub_category, gender, color, price, release_date)
        product_data.append(vals)

# cursor.executemany(sql, product_data)

# conn.commit()

# print('커밋성공')

# cursor.close()
# conn.close()
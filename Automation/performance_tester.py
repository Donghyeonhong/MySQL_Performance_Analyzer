import time
import statistics

# 쿼리 실행 시간 측정 함수
def measure_query(cursor, sql_text):
    total_time_list = []

    # 워밍업 1회
    cursor.execute(sql_text)
    cursor.fetchall()

    # 실제 측정 5회
    for t in range(5):
        start_time = time.perf_counter()

        cursor.execute(sql_text)
        cursor.fetchall()

        end_time = time.perf_counter()

        actual_time = (end_time - start_time) * 1000

        total_time_list.append(round(actual_time, 3))

    average_time = statistics.mean(total_time_list)
    median_time = statistics.median(total_time_list)

    return total_time_list, average_time, median_time
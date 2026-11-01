import json

# EXPLAIN 결과 조회 함수
def get_explain_result(cursor, sql_text):
    explain_sql = "EXPLAIN " + sql_text.strip().rstrip(";")

    cursor.execute(explain_sql)
    explain_result = cursor.fetchall()

    return json.dumps(
        [list(row) for row in explain_result],
        ensure_ascii=False,
        default=str
    )

# EXPLAIN ANALYZE 결과 조회 함수
def get_explain_analyze_result(cursor, sql_text):

    explain_sql = "EXPLAIN ANALYZE " + sql_text.strip().rstrip(";")

    cursor.execute(explain_sql)
    explain_analyze_result = cursor.fetchall()

    return json.dumps(
        [list(row) for row in explain_analyze_result],
        ensure_ascii=False,
        default=str
    )
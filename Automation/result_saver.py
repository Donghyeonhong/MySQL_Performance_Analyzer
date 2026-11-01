# 측정 결과 저장 함수
def save_performance_log(
    cursor,
    condition_id,
    total_time_list,
    explain_result,
    explain_analyze_result
):

    insert_sql = """
    INSERT INTO performance_log
    (
        condition_id,
        repeat_number,
        execution_time,
        explain_result,
        explain_analyze_result,
        measured_at
    )
    VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP);
    """

    for t, execution_time in enumerate(total_time_list, start=1):

        values = (
            condition_id,
            t,
            execution_time,
            explain_result,
            explain_analyze_result
        )

        cursor.execute(insert_sql, values)
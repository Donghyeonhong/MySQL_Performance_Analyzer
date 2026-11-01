# 실험 정보
def get_experiment_conditions(cursor, experiment_id):
    select_sql = """
            SELECT
                experiment.experiment_id,
                experiment_name,
                sql_text,
                is_indexed,
                table_name,
                index_name,
                index_columns,
                index_condition.condition_id
            FROM experiment
            INNER JOIN query_history
                ON experiment.experiment_id = query_history.experiment_id
            INNER JOIN index_condition
                ON query_history.query_id = index_condition.query_id
            WHERE experiment.experiment_id = %s
            ORDER BY is_indexed ASC;
            """
    cursor.execute(select_sql, (experiment_id,))
    result_analysis = cursor.fetchall()

    return result_analysis
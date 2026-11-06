from flask import Flask, render_template
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from Automation import db_connection

total_experiments_sql = """select count(*) from experiment;"""
query_conditions_sql = """select count(*) from index_condition;"""
performance_tests_sql = """select count(*) from performance_log;"""
indexed_conditions_sql = """select count(*) from index_condition where is_indexed = %s;"""
experiment_info_sql = """select experiment.experiment_id, experiment_name, created_at, 
count(distinct index_condition.condition_id), count(performance_log.log_id),
case 
	when count(performance_log.log_id) = 0 then 'Not Started'
	when count(performance_log.log_id) = count(distinct index_condition.condition_id) * 5 then 'Completed'
	else 'In Progress'
end as Status
from experiment 
left join query_history on experiment.experiment_id = query_history.experiment_id 
left join index_condition on query_history.query_id = index_condition.query_id 
left join performance_log on index_condition.condition_id = performance_log.condition_id 
group by experiment.experiment_id order by created_at desc limit 5;"""

average_actual_time_sql = """select experiment.experiment_id, query_history.query_id, index_condition.is_indexed, avg(performance_log.execution_time) as avg_execution_time 
from experiment
inner join query_history on experiment.experiment_id = query_history.experiment_id
inner join index_condition on query_history.query_id = index_condition.query_id
inner join performance_log on index_condition.condition_id = performance_log.condition_id
where experiment.experiment_id = %s
group by experiment.experiment_id, query_history.query_id, index_condition.is_indexed; 
""" 

indexed_conditions_vals = 1
experiment_id = 1


app = Flask(__name__)

@app.route("/")
def index():
    conn = None
    cursor = None
    try:
        conn = db_connection.get_db_connection_analysis()
        cursor = conn.cursor()
        print("analysis_db 연결 성공")
        
        cursor.execute(total_experiments_sql)
        total_experiments_count = cursor.fetchone()[0]
        
        cursor.execute(query_conditions_sql)
        total_conditions_count = cursor.fetchone()[0]

        cursor.execute(performance_tests_sql)
        total_performance_tests_count = cursor.fetchone()[0]

        cursor.execute(indexed_conditions_sql, (indexed_conditions_vals,))
        total_indexed_conditions_count = cursor.fetchone()[0]

        cursor.execute(experiment_info_sql)
        experiment_info = cursor.fetchall()

        cursor.execute(average_actual_time_sql, (experiment_id,))
        average_actual_time = cursor.fetchall()

        chart_data = {}
        
        for row in average_actual_time:
            query_id = "Query " + str(row[1])

            if query_id not in chart_data:
                chart_data[query_id] = {
                    "before": None,
                    "after": None
                }
            if row[2] == 0:
                chart_data[query_id]["before"] = row[3]
            else:
                chart_data[query_id]["after"] = row[3]
        labels = list(chart_data.keys())
        before = []
        after = []
        improvement = []
        for data in chart_data.values():
            before.append(float(data['before']))
            after.append(float(data['after']))

        for i in range(len(before)):
            if before[i] != 0:
                rate = ((before[i] - after[i]) / before[i]) * 100
                improvement.append(rate)
            else:
                rate = None
                improvement.append(rate)
        print(chart_data)    
        print(average_actual_time)
        
    finally:
        
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
    return render_template("index.html", total_experiments_count = total_experiments_count, total_conditions_count = total_conditions_count, total_performance_tests_count = total_performance_tests_count, total_indexed_conditions_count = total_indexed_conditions_count, experiment_info=experiment_info, average_actual_time = average_actual_time, labels =labels, before = before, after = after, improvement = improvement)

if __name__ == "__main__":
    app.run(debug=True)

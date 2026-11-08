from flask import Flask, render_template, request
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from Automation import db_connection
import statistics
import json

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

experiment_list_sql = """select experiment_id, experiment_name from experiment order by created_at desc;"""

indexed_conditions_vals = 1

app = Flask(__name__)
@app.route("/")
def index():
    conn = None
    cursor = None
    try:
        experiment_id = request.args.get('experiment_id', type=int)
        if experiment_id is None:
            experiment_id = 1
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

        cursor.execute(experiment_list_sql)
        get_experiment_id_name = cursor.fetchall()

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
    return render_template("index.html", total_experiments_count = total_experiments_count, total_conditions_count = total_conditions_count, total_performance_tests_count = total_performance_tests_count, total_indexed_conditions_count = total_indexed_conditions_count, experiment_info=experiment_info, average_actual_time = average_actual_time, labels =labels, before = before, after = after, improvement = improvement, get_experiment_id_name = get_experiment_id_name, experiment_id = experiment_id)

experiment_detail_info_sql = """select experiment_id, experiment_name, description from experiment where experiment_id = %s;"""

query_info_sql = """select query_id, query_history.experiment_id, sql_text, query_registered_at from query_history where query_history.experiment_id = %s;"""

before_after_index_sql = """select experiment.experiment_id, query_history.query_id, 
index_condition.condition_id, index_condition.is_indexed, 
performance_log.repeat_number, performance_log.execution_time 
from performance_log
inner join index_condition on performance_log.condition_id = index_condition.condition_id
inner join query_history on index_condition.query_id = query_history.query_id
inner join experiment on query_history.experiment_id = experiment.experiment_id
where experiment.experiment_id = %s 
order by query_history.query_id, is_indexed, repeat_number;"""

explain_result_sql = """select experiment.experiment_id, query_history.query_id, 
index_condition.condition_id, index_condition.is_indexed, 
performance_log.explain_result, performance_log.explain_analyze_result
from performance_log
inner join index_condition on performance_log.condition_id = index_condition.condition_id
inner join query_history on index_condition.query_id = query_history.query_id
inner join experiment on query_history.experiment_id = experiment.experiment_id
where experiment.experiment_id = %s and performance_log.repeat_number = 1
order by query_history.query_id, is_indexed;"""

@app.route("/experiment/<int:experiment_id>")
def experiment_detail(experiment_id):
    conn = None
    cursor = None
    try:
        conn = db_connection.get_db_connection_analysis()
        cursor = conn.cursor()
        experiment_detail_info_vals = experiment_id


        cursor.execute(experiment_detail_info_sql, (experiment_detail_info_vals,))
        experiment_detail_info = cursor.fetchone()

        cursor.execute(query_info_sql, (experiment_detail_info_vals,))
        query_info = cursor.fetchall()

        cursor.execute(before_after_index_sql, (experiment_detail_info_vals,))
        before_after_index_info = cursor.fetchall()

        cursor.execute(explain_result_sql, (experiment_detail_info_vals,))
        explain_result_info = cursor.fetchall()

        print(explain_result_info)

        before_after_data = {}
        for i in before_after_index_info:
            query_id = "Query " + str(i[1])
            if query_id not in before_after_data:
                before_after_data[query_id] = {
                    "before": [],
                    "after": []
                }
            if i[3] == 0:
                before_after_data[query_id]["before"].append(i[5])
            else:
                before_after_data[query_id]["after"].append(i[5])

        result_data = {}
        for query_id, data in before_after_data.items():
            before_average_actual_time = statistics.mean(data["before"])
            before_median_actual_time = statistics.median(data["before"])
            after_average_actual_time = statistics.mean(data["after"])
            after_median_actual_time = statistics.median(data["after"])

            if query_id not in result_data:
                result_data[query_id] = {
                    "before": {
                        "times": [],
                        "average": None,
                        "median" : None
                    },
                    "after": {
                        "times": [],
                        "average": None,
                        "median" : None
                    }
                }
            result_data[query_id]["before"]["times"] = data["before"]
            result_data[query_id]["before"]["average"] = before_average_actual_time
            result_data[query_id]["before"]["median"] = before_median_actual_time

            result_data[query_id]["after"]["times"] = data["after"]
            result_data[query_id]["after"]["average"] = after_average_actual_time
            result_data[query_id]["after"]["median"] = after_median_actual_time

        explain_result_data = {}
        explain_columns = [
            "id", "select_type", "table", "partitions",
            "type", "possible_keys", "key", "key_len",
            "ref", "rows", "filtered", "Extra"
        ]
        for t in explain_result_info:
            explain_query_id = "Query " + str(t[1]) 
            if explain_query_id not in explain_result_data:
                explain_result_data[explain_query_id] = {
                    "before": {
                        "explain": None,
                        "explain_analyze": None
                    },
                    "after": {
                        "explain": None,
                        "explain_analyze": None
                    }
                }
            explain_rows = json.loads(t[4])

            explain_data = [
                dict(zip(explain_columns, row))
                for row in explain_rows
            ]
            
            explain_analyze_data = json.loads(t[5])[0][0]

            if t[3] == 0:
                explain_result_data[explain_query_id]["before"]["explain"] = explain_data
                explain_result_data[explain_query_id]["before"]["explain_analyze"] = explain_analyze_data
            else:
                explain_result_data[explain_query_id]["after"]["explain"] = explain_data
                explain_result_data[explain_query_id]["after"]["explain_analyze"] = explain_analyze_data
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
    return render_template("experiment_detail.html", experiment_detail_info = experiment_detail_info, query_info = query_info, result_data = result_data, explain_result_data = explain_result_data)

experiments_info_sql = """select experiment.experiment_id, experiment.experiment_name,
experiment.description, experiment.created_at 
from experiment
order by experiment.created_at desc;"""

@app.route("/experiments")
def experiments():
    conn = None
    cursor = None
    try:
        conn = db_connection.get_db_connection_analysis()
        cursor = conn.cursor()

        cursor.execute(experiments_info_sql)
        experiments_info_data = cursor.fetchall()
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
    return render_template("experiments.html", experiments_info_data = experiments_info_data)

@app.route("/performance-analysis")
def performance_analysis():
    conn = None
    cursor = None
    try:
        conn = db_connection.get_db_connection_analysis()
        cursor = conn.cursor()
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

    return render_template("performance_analysis.html")


if __name__ == "__main__":
    app.run(debug=True)

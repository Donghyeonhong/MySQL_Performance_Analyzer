from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash, session
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from Automation import db_connection
from Automation.main import run_experiment
import statistics
import json
import datetime

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

average_actual_time_sql = """select experiment.experiment_id, query_history.query_id, index_condition.condition_id, index_condition.is_indexed, 
avg(performance_log.execution_time) as avg_execution_time 
from experiment
inner join query_history on experiment.experiment_id = query_history.experiment_id
inner join index_condition on query_history.query_id = index_condition.query_id
inner join performance_log on index_condition.condition_id = performance_log.condition_id
where experiment.experiment_id = %s
group by experiment.experiment_id, query_history.query_id, index_condition.condition_id, index_condition.is_indexed; 
""" 

condition_index_sql = """
select condition_id, 
group_concat(index_name order by index_id SEPARATOR ' + ')
from condition_index
group by condition_id;
"""

experiment_list_sql = """select experiment_id, experiment_name from experiment order by created_at desc;"""

indexed_conditions_vals = 1

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

load_dotenv(os.path.join(BASE_DIR, ".env"))

app.secret_key = os.getenv("FLASK_SECRET_KEY")

@app.context_processor
def current_date():
    current_date = datetime.datetime.now().strftime("%Y. %m. %d.")
    system_ready = check_db_status()

    return {"current_date": current_date, "system_ready": system_ready}

def check_db_status():
    analysis_conn = None
    test_conn = None
    try:
        analysis_conn = db_connection.get_db_connection_analysis()
        test_conn = db_connection.get_db_connection_test()
        return True
    
    except Exception as e:
        print(f"DB 연결 확인 실패: {e}")
        return False

    finally:
        if analysis_conn is not None:
            analysis_conn.close()
        if test_conn is not None:
            test_conn.close()


@app.route("/")
def index():
    conn = None
    cursor = None
    experiment_id = request.args.get('experiment_id', type=int) or 1
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

        cursor.execute(experiment_list_sql)
        get_experiment_id_name = cursor.fetchall()

        cursor.execute(experiment_info_sql)
        experiment_info = cursor.fetchall()

        cursor.execute(average_actual_time_sql, (experiment_id,))
        average_actual_time = cursor.fetchall()

        cursor.execute(condition_index_sql)
        condition_index_data = cursor.fetchall()

        index_names = {}

        for row in condition_index_data:
            index_names[row[0]] = row[1]

        chart_data = {}
        
        for row in average_actual_time:
            query_id = "Query " + str(row[1])
    
            if query_id not in chart_data:
                chart_data[query_id] = {
                    "before": None,
                    "after": []
                }
            
            if row[3] == 0:
                chart_data[query_id]["before"] = row[4]
            else:
                chart_data[query_id]["after"].append({
                    "condition_id": row[2],
                    "execution_time": row[4]
                })
        labels = list(chart_data.keys())
        before = []
        after = {}
        improvement = []

        for query_id, data in chart_data.items():

            before.append(float(data["before"]))

            after[query_id] = []

            for e in data["after"]:
                after[query_id].append({
                    "condition_id": e["condition_id"],
                    "execution_time": float(e["execution_time"]),
                    "index_name": index_names.get(e["condition_id"], "Unknown")
                })

        # for data in chart_data.values():
        #     before.append(float(data['before']))
        #     for e in data['after']:
        #         condition_ids.add(e["condition_id"])
                
        # for condition_id in condition_ids:
        #     after[condition_id] = [None] * len(labels)

        # for query_index, data in enumerate(chart_data.values()):
        #     for e in data["after"]:
        #         after[e["condition_id"]][query_index] = float(e["execution_time"])


        chart_labels = []
        chart_values = []
        chart_types = []


        for query_id, data in chart_data.items():
            # 인덱스 미적용 데이터
            chart_labels.append(query_id + "\n미적용")
            chart_values.append(float(data["before"]))
            chart_types.append("before")

            # 해당 쿼리에 적용된 인덱스 데이터
            for e in after[query_id]:
                chart_labels.append(query_id + "\n" + e["index_name"])
                chart_values.append(e["execution_time"])
                chart_types.append("after")

            before_time = float(data["before"])
            for t in data["after"]:
                condition_id = t["condition_id"]
                execution_time = float(t["execution_time"])
                if before_time != 0:
                    rate = ((before_time - execution_time) / before_time) * 100
                else:
                    rate = None

                improvement.append({
                    "query_id": query_id,
                    "condition_id": condition_id,
                    "rate": rate
                })

    except Exception as e:
        print(f"Dashboard 데이터 조회 실패: {e}")

        flash("데이터베이스 연결에 실패했습니다. 잠시 후 다시 시도해 주세요.", "error")

        total_experiments_count = 0
        total_conditions_count = 0
        total_performance_tests_count = 0
        total_indexed_conditions_count = 0

        get_experiment_id_name = []
        experiment_info = []
        average_actual_time = []

        labels = []
        before = []
        after = {}
        improvement = []

    finally:
        
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
    return render_template("index.html", total_experiments_count = total_experiments_count, total_conditions_count = total_conditions_count, total_performance_tests_count = total_performance_tests_count, total_indexed_conditions_count = total_indexed_conditions_count, experiment_info=experiment_info, average_actual_time = average_actual_time, labels =labels, before = before, after = after, improvement = improvement, get_experiment_id_name = get_experiment_id_name, experiment_id = experiment_id, chart_labels=chart_labels, chart_values=chart_values, chart_types=chart_types)

experiment_detail_info_sql = """select experiment_id, experiment_name, description from experiment where experiment_id = %s;"""

query_info_sql = """select query_id, query_history.experiment_id, sql_text, query_registered_at from query_history where query_history.experiment_id = %s;"""

index_condition_info_sql = """select query_history.query_id, index_condition.condition_id, 
index_condition.is_indexed, condition_index.table_name, condition_index.index_name,
condition_index.index_columns, index_condition.condition_created_at
from query_history
inner join index_condition on query_history.query_id = index_condition.query_id
left join condition_index on index_condition.condition_id = condition_index.condition_id 
where query_history.experiment_id = %s
order by query_history.query_id, index_condition.condition_id;"""

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

insert_query_sql = """
insert into query_history (experiment_id, sql_text, query_registered_at)
values (%s, %s, NOW());"""

insert_index_condition_sql = """
insert into index_condition (query_id, is_indexed, condition_created_at)
values (%s, %s, NOW());"""

insert_condition_index_sql = """
insert into condition_index (condition_id, table_name, index_name, index_columns)
values (%s, %s, %s, %s);"""

@app.route("/experiment/<int:experiment_id>", methods=["GET", "POST"])
def experiment_detail(experiment_id):
    if request.method == "POST":
        form_type = request.form.get("form_type")

        if form_type == "query":
            sql_text = request.form.get("sql_text", "").strip()
        

            if sql_text:
                conn_insert = None
                cursor_insert = None

                try:
                    conn_insert = db_connection.get_db_connection_analysis()
                    cursor_insert = conn_insert.cursor()

                    cursor_insert.execute(insert_query_sql, (experiment_id, sql_text))
                    conn_insert.commit()

                except Exception as e:
                    print(f"쿼리 등록 실패: {e}")
                    flash("데이터베이스 연결에 실패했습니다. 잠시 후 다시 시도해 주세요.", "error")

                finally:
                    if cursor_insert is not None:
                        cursor_insert.close()
                    if conn_insert is not None:
                        conn_insert.close()

        elif form_type == "index_condition":
            query_id = request.form.get("query_id")
            is_indexed = request.form.get("is_indexed")
            table_name = request.form.get("table_name", "").strip()
            index_name = request.form.get("index_name", "").strip()
            index_columns = request.form.get("index_columns", "").strip()

            conn_insert = None
            cursor_insert = None

            try:
                conn_insert = db_connection.get_db_connection_analysis()
                cursor_insert = conn_insert.cursor()

                cursor_insert.execute(insert_index_condition_sql, (int(query_id), int(is_indexed)))

                condition_id = cursor_insert.lastrowid

                if int(is_indexed) == 1:
                    cursor_insert.execute(insert_condition_index_sql, 
                    (condition_id, table_name, index_name, index_columns))

                conn_insert.commit()

            except Exception as e:
                print(f"인덱스 조건 등록 실패: {e}")
                flash("데이터베이스 연결에 실패했습니다. 잠시 후 다시 시도해 주세요.", "error")

            finally:
                if cursor_insert is not None:
                    cursor_insert.close()
                if conn_insert is not None:
                    conn_insert.close()

        elif form_type == "run_experiment":
            result = run_experiment(experiment_id)

            if result:
                flash("실험이 정상적으로 완료되었습니다.", "success")
            else:
                flash("실험 실행 중 오류가 발생했습니다. 터미널 로그를 확인해 주세요.", "error")

        return redirect(url_for("experiment_detail", experiment_id=experiment_id))
    conn = None
    cursor = None

    experiment_detail_info = None
    query_info = []
    index_condition_info = []
    grouped_index_condition_info = {}
    before_after_index_info = []
    explain_result_info = []
    before_after_data = {}
    result_data = {}
    explain_result_data = {}
    try:
        conn = db_connection.get_db_connection_analysis()
        cursor = conn.cursor()
        experiment_detail_info_vals = experiment_id


        cursor.execute(experiment_detail_info_sql, (experiment_detail_info_vals,))
        experiment_detail_info = cursor.fetchone()

        cursor.execute(query_info_sql, (experiment_detail_info_vals,))
        query_info = cursor.fetchall()

        cursor.execute(index_condition_info_sql, (experiment_detail_info_vals,))
        index_condition_info = cursor.fetchall()

        grouped_index_condition_info = {}

        for i in index_condition_info:
            query_id = i[0]
            condition_id = i[1]

            if condition_id not in grouped_index_condition_info:
                grouped_index_condition_info[condition_id] = {
                    "query_id": query_id,
                    "condition_id": condition_id,
                    "is_indexed": i[2],
                    "condition_created_at": i[6],
                    "indexes": []
                }

            if i[2] == 1:
                grouped_index_condition_info[condition_id]["indexes"].append({
                    "table_name": i[3],
                    "index_name": i[4],
                    "index_columns": i[5]
                })

        cursor.execute(before_after_index_sql, (experiment_detail_info_vals,))
        before_after_index_info = cursor.fetchall()

        cursor.execute(explain_result_sql, (experiment_detail_info_vals,))
        explain_result_info = cursor.fetchall()

        before_after_data = {}
        for i in before_after_index_info:
            query_id = "Query " + str(i[1])
            if query_id not in before_after_data:
                before_after_data[query_id] = {
                    "before": [],
                    "after": {}
                }
            if i[3] == 0:
                before_after_data[query_id]["before"].append(i[5])
            else:
                condition_id = i[2]
                if condition_id not in before_after_data[query_id]["after"]:
                    before_after_data[query_id]["after"][condition_id] = []

                before_after_data[query_id]["after"][condition_id].append(i[5])

        result_data = {}
        for query_id, data in before_after_data.items():
            before_average_actual_time = statistics.mean(data["before"])
            before_median_actual_time = statistics.median(data["before"])

            after_result = {}

            for condition_id, times in data["after"].items():
                after_average_actual_time = statistics.mean(times)
                after_median_actual_time = statistics.median(times)

                after_result[condition_id] = {
                    "times": times,
                    "average": after_average_actual_time,
                    "median": after_median_actual_time
                }

            if query_id not in result_data:
                result_data[query_id] = {
                    "before": {
                        "times": [],
                        "average": None,
                        "median" : None
                    },
                    "after": {}
                }

            result_data[query_id]["before"]["times"] = data["before"]
            result_data[query_id]["before"]["average"] = before_average_actual_time
            result_data[query_id]["before"]["median"] = before_median_actual_time
            result_data[query_id]["after"] = after_result
        
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
                    "after": {}
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
                condition_id = t[2]
                if condition_id not in explain_result_data[explain_query_id]["after"]:
                    explain_result_data[explain_query_id]["after"][condition_id] = {
                        "explain": None,
                        "explain_analyze": None
                    }
                explain_result_data[explain_query_id]["after"][condition_id]["explain"] = explain_data
                explain_result_data[explain_query_id]["after"][condition_id]["explain_analyze"] = explain_analyze_data

    except Exception as e:
        print(f"실험 상세 조회 실패: {e}")
        flash("데이터베이스 연결에 실패했습니다. 잠시 후 다시 시도해 주세요.", "error")
            
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
    return render_template("experiment_detail.html", experiment_detail_info = experiment_detail_info, query_info = query_info, result_data = result_data, explain_result_data = explain_result_data,
    grouped_index_condition_info = grouped_index_condition_info)

experiments_info_sql = """select experiment.experiment_id, experiment.experiment_name,
experiment.description, experiment.created_at 
from experiment
order by experiment.created_at desc;"""

@app.route("/experiments")
def experiments():
    conn = None
    cursor = None
    experiments_info_data = []
    try:
        conn = db_connection.get_db_connection_analysis()
        cursor = conn.cursor()

        cursor.execute(experiments_info_sql)
        experiments_info_data = cursor.fetchall()

    except Exception as e:
        print(f"실험 목록 조회 실패: {e}")
        flash("데이터베이스 연결에 실패했습니다. 잠시 후 다시 시도해 주세요.", "error")
    
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()
    return render_template("experiments.html", experiments_info_data = experiments_info_data)

insert_experiment_sql = """
insert into experiment (experiment_name, description)
values (%s, %s)"""

@app.route("/experiments/add", methods=["GET", "POST"])
def add_experiment():
    if request.method == "POST":
        experiment_name = request.form.get("experiment_name")
        description = request.form.get("description")
        vals = (experiment_name, description)

        conn = None
        cursor = None
        try:
            conn = db_connection.get_db_connection_analysis()
            cursor = conn.cursor()
    
            cursor.execute(insert_experiment_sql, vals)
            conn.commit()
            new_experiment_id = cursor.lastrowid

        except Exception as e:
            print(f"실험 추가 실패: {e}")
            flash("데이터베이스 연결에 실패했습니다. 잠시 후 다시 시도해 주세요.", "error")
            return redirect(url_for("add_experiment"))
        
        finally:
            if cursor is not None:
                cursor.close()
            if conn is not None:
                conn.close()
        return redirect(url_for("experiment_detail", experiment_id=new_experiment_id))
    return render_template("add_experiment.html")

cte_sql = """with condition_count as (
	select index_condition.query_id, index_condition.condition_id, index_condition.is_indexed,
	count(performance_log.log_id) as measurement_count, min(performance_log.repeat_number) as min_repeat, 
    max(performance_log.repeat_number) as max_repeat
	from index_condition
	left join performance_log on index_condition.condition_id = performance_log.condition_id
	group by index_condition.query_id, index_condition.condition_id, index_condition.is_indexed
	),
    
	query_count as (
	select query_id, sum(
		case 
			when is_indexed = 1 then 1
			else 0
		end
		) a,
		sum(
		case
			when is_indexed = 0 then 1
			else 0
		end
		) b 
	from condition_count
	group by query_id 
	having min(measurement_count) = 5 and max(measurement_count) = 5 and a >= 1 and b >= 1
    and min(min_repeat) = 1 and max(min_repeat) = 1 and min(max_repeat) = 5 and max(max_repeat) = 5
	)"""

analyzed_queries_count_sql = cte_sql + """ select count(*) from query_count;"""

avg_improvement_sql = cte_sql + """ select query_history.experiment_id, query_history.query_id, index_condition.condition_id, index_condition.is_indexed, 
avg(performance_log.execution_time) as avg_execution_time, experiment.experiment_name
from query_count
inner join query_history on query_count.query_id = query_history.query_id
inner join experiment on query_history.experiment_id = experiment.experiment_id 
inner join index_condition on query_history.query_id = index_condition.query_id
inner join performance_log on index_condition.condition_id = performance_log.condition_id
group by query_history.experiment_id, query_history.query_id, 
index_condition.condition_id, index_condition.is_indexed, experiment.experiment_id; 
""" 

@app.route("/performance-analysis")
def performance_analysis():
    conn = None
    cursor = None
    total_experiments_count = 0
    analyzed_queries_count = 0
    avg_improvement_data = []

    improvement_rates = []
    improvement_data = {}
    summary_data = []

    avg_improvement = 0
    best_improvement = 0

    improved_queries = 0
    regressed_queries = 0
    no_change_queries = 0
    try:
        conn = db_connection.get_db_connection_analysis()
        cursor = conn.cursor()

        cursor.execute(total_experiments_sql)
        total_experiments_count = cursor.fetchone()[0]

        cursor.execute(analyzed_queries_count_sql)
        analyzed_queries_count = cursor.fetchone()[0]

        cursor.execute(avg_improvement_sql)
        avg_improvement_data = cursor.fetchall()

        cursor.execute(condition_index_sql)
        condition_index_data = cursor.fetchall()

        index_names = {}
        for row in condition_index_data:
            index_names[row[0]] = row[1]

        print(index_names)

        improvement_rates = []
        improvement_data = {}

        for row in avg_improvement_data:
            experiment_id = row[0]
            query_id = row[1]
            condition_id = row[2]
            is_indexed = row[3]
            execution_time = float(row[4])
            experiment_name = row[5]

            key = (experiment_id, query_id)

            if key not in improvement_data:
                improvement_data[key] = {
                    "experiment_name": experiment_name,
                    "before": None,
                    "after": []
                }

            if is_indexed == 0:
                improvement_data[key]["before"] = execution_time
            else:
                improvement_data[key]["after"].append({
                    "condition_id": condition_id,
                    "execution_time": execution_time,
                    "index_name": index_names.get(condition_id, "Unknown")
                })

            print(improvement_data)
            # key = (experiment_id, query_id)

            # if key not in improvement_data:
            #     improvement_data[key] = {
            #         "experiment_name": experiment_name,
            #         "before": None,
            #         "after": []
            #     }

            # if is_indexed == 0:
            #     improvement_data[key]["before"] = execution_time
            # else:
            #     improvement_data[key]["after"].append(execution_time)

        summary_data = []

        chart_labels = []
        chart_values = []
        chart_types = []

        for key, data in improvement_data.items():
            before_time = data["before"]

            if before_time is None or before_time == 0:
                continue

            # 인덱스 미적용 데이터
            experiment_name = data["experiment_name"]
            query_id = key[1]

            chart_labels.append(
                experiment_name + "\nQuery " + str(query_id) + "\n미적용"
            )
            chart_values.append(before_time)
            chart_types.append("before")

            # 인덱스 적용 데이터
            for item in data["after"]:
                chart_labels.append(
                    experiment_name + "\nQuery " + str(query_id) + "\n" + item["index_name"]
                )
                chart_values.append(item["execution_time"])
                chart_types.append("after")


            # if data["after"]:
            #     after_data = data["after"]
            #     after_sum = sum(after_data)
            #     after_avg = after_sum / len(after_data)
            #     summary_rate = ((before_time - after_avg) / before_time) * 100
            # else: 
            #     continue
            if data["after"]:
                after_data = data["after"]

                after_sum = sum(
                    item["execution_time"] for item in after_data
                )

                after_avg = after_sum / len(after_data)

                summary_rate = ((before_time - after_avg) / before_time) * 100
            else:
                continue

            summary_data.append({
                "experiment_name": data["experiment_name"],
                "query_id": key[1],
                "before_time": before_time,
                "after_avg": after_avg,
                "improvement": summary_rate
            })

            for after_item in data["after"]:
                after_time = after_item["execution_time"]

                rate = ((before_time - after_time) / before_time) * 100
                improvement_rates.append(rate)

            # for after_time in data["after"]:
            #     rate = ((before_time - after_time) / before_time) * 100
            #     improvement_rates.append(rate)

        print("차트 라벨:", chart_labels)
        print("차트 실행 시간:", chart_values)
        print("차트 조건:", chart_types)

        if improvement_rates:
            avg_improvement = sum(improvement_rates) / len(improvement_rates)
            best_improvement = max(improvement_rates)
        else:
            avg_improvement = 0
            best_improvement = 0

        improved_queries = 0
        regressed_queries = 0
        no_change_queries = 0

        for a in summary_data:
            improvement = round(a["improvement"], 2)
            if improvement > 0:
                improved_queries += 1
            elif improvement == 0:
                no_change_queries += 1
            else:
                regressed_queries += 1

    except Exception as e:
        print(f"성능 분석 데이터 조회 실패: {e}")
        flash("데이터베이스 연결에 실패했습니다. 잠시 후 다시 시도해 주세요.", "error")

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()

    return render_template("performance_analysis.html", 
    total_experiments_count = total_experiments_count, 
    analyzed_queries_count = analyzed_queries_count, 
    avg_improvement = avg_improvement, best_improvement = best_improvement, 
    avg_improvement_data = avg_improvement_data, summary_data = summary_data,
    improved_queries = improved_queries, regressed_queries = regressed_queries, no_change_queries = no_change_queries,
    chart_labels=chart_labels, chart_values=chart_values, chart_types=chart_types)

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "False").lower() == "true")

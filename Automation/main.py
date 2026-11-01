from db_connection import (
    get_db_connection_analysis,
    get_db_connection_test
)

from experiment_manager import get_experiment_conditions

from index_manager import (
    validate_index_info,
    remove_experiment_indexes,
    apply_index_condition
)

from performance_tester import measure_query

from explain_analyzer import (
    get_explain_result,
    get_explain_analyze_result
)

from result_saver import save_performance_log

# 실험 실행 함수
def run_experiment(experiment_id):
    conn_analysis = None
    conn_test = None
    cursor_analysis = None
    cursor_test = None

    indexed_conditions = []
    indexes_validated = False
    indexes_cleaned = False

    try:
        conn_analysis = get_db_connection_analysis()
        cursor_analysis = conn_analysis.cursor()

        conn_test = get_db_connection_test()
        cursor_test = conn_test.cursor()

        result_analysis = get_experiment_conditions(
            cursor_analysis,
            experiment_id
            )

        # 실험 존재 여부 확인
        if not result_analysis:
            raise ValueError("해당 실험 번호가 존재하지 않습니다.")

        # 인덱스 미적용 조건과 적용 조건 분리
        baseline_conditions = [  # 미적용 조건 행 저장
            e for e in result_analysis if e[3] == 0
        ]

        indexed_conditions = [   # 적용 조건 행 저장
            e for e in result_analysis if e[3] == 1
        ]

        if len(baseline_conditions) != 1:
            raise ValueError(
                "인덱스 미적용 조건은 정확히 1개여야 합니다."
            )

        if not indexed_conditions:
            raise ValueError(
                "인덱스 적용 조건이 등록되어 있지 않습니다."
            )

        # 현재는 실험 하나당 SQL문 하나를 사용하는 구조
        sql_text = result_analysis[0][2]
        experiment_name = result_analysis[0][1]

        if any(e[2] != sql_text for e in result_analysis):
            raise ValueError("실험 조건들의 SQL문이 서로 다릅니다.")

        # 모든 인덱스 정보 검증
        for condition in indexed_conditions:

            if not condition[5] or not condition[6]:
                raise ValueError("인덱스 정보가 누락되었습니다.")

            validate_index_info(
                condition[4],
                condition[5],
                condition[6]
            )

        indexes_validated = True

        # 같은 테이블에서 동일한 인덱스 이름이 중복 등록되었는지 확인
        managed_indexes = [
            (e[4], e[5]) for e in indexed_conditions
        ]

        if len(managed_indexes) != len(set(managed_indexes)):
            raise ValueError("동일한 인덱스가 중복 등록되어 있습니다.")

        print("\n실험 이름:", experiment_name)
        print("비교 조건 수:", len(result_analysis))

        # 이전 측정 기록 삭제
        # 현재 구조에서는 재실행 시 이전 기록을 교체함
        condition_ids = [e[7] for e in result_analysis]

        placeholders = ", ".join(["%s"] * len(condition_ids))
        

        delete_sql = """DELETE FROM performance_log WHERE condition_id IN 
        (""" + placeholders + """);"""
        

        cursor_analysis.execute(delete_sql, tuple(condition_ids))

        # 각 조건별 측정
        for condition in result_analysis:

            is_indexed = condition[3]
            condition_id = condition[7]

            print("\n-----------------------------")
            print("인덱스 적용 여부:", is_indexed)

            if is_indexed == 1:
                print("인덱스 이름:", condition[5])
                print("인덱스 컬럼:", condition[6])

            # 이전 실험 조건의 인덱스 전부 제거
            remove_experiment_indexes(
                cursor_test,
                indexed_conditions
            )

            # 현재 조건에 필요한 인덱스만 적용
            apply_index_condition(
                cursor_test,
                condition
            )

            # EXPLAIN 결과 조회
            explain_result = get_explain_result(
                cursor_test,
                sql_text
            )

            # EXPLAIN ANALYZE 결과 조회
            explain_analyze_result = get_explain_analyze_result(
                cursor_test,
                sql_text
            )

            # 실행 시간 측정
            total_time_list, average_time, median_time = measure_query(
                cursor_test,
                sql_text
            )

            # 측정 결과 저장
            save_performance_log(
                cursor_analysis,
                condition_id,
                total_time_list,
                explain_result,
                explain_analyze_result
            )

            print("측정 시간:", total_time_list)
            print("평균:", round(average_time, 3), "ms")
            print("중앙값:", round(median_time, 3), "ms")

        # 모든 측정 결과 저장
        remove_experiment_indexes(
            cursor_test,
            indexed_conditions
        )

        indexes_cleaned = True

        conn_analysis.commit()

        print("\n실험이 정상적으로 완료되었습니다.")

    except Exception as e:

        if conn_analysis:
            conn_analysis.rollback()

        print("\n실험 실행 중 오류가 발생했습니다.")
        print("오류 내용:", e)

    finally:
        if (cursor_test and indexes_validated and not indexes_cleaned):
            try:
                print("\n실험용 인덱스를 정리합니다.")

                remove_experiment_indexes(
                    cursor_test,
                    indexed_conditions
                )

                indexes_cleaned = True

                print("실험용 인덱스 정리가 완료되었습니다.")

            except Exception as cleanup_error:
                print("인덱스 정리 중 오류가 발생했습니다.")
                print("오류 내용:", cleanup_error)
                
        if cursor_analysis:
            cursor_analysis.close()

        if cursor_test:
            cursor_test.close()

        if conn_analysis and conn_analysis.is_connected():
            conn_analysis.close()

        if conn_test and conn_test.is_connected():
            conn_test.close()


# 실험 번호 입력 - 실질적인 실험 시작 단계
if __name__ == "__main__":
    try:
        experiment_id = int(input("실험 번호: "))
        run_experiment(experiment_id)

    except ValueError:
        print("실험 번호는 숫자로 입력해야 합니다.")
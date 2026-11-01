import re

# 인덱스 존재 여부 확인 함수
def check_index(cursor, table_name, index_name):
    show_index_sql = """SHOW INDEX FROM """ + table_name + """;"""
    cursor.execute(show_index_sql)

    show_index_result = cursor.fetchall()

    return any(e[2] == index_name for e in show_index_result)


# 인덱스 이름 및 컬럼 검증 함수
def validate_index_info(table_name, index_name, index_columns):
    pattern = r"^[A-Za-z_][A-Za-z0-9_]*$"

    if not re.fullmatch(pattern, table_name):
        raise ValueError("잘못된 테이블 이름입니다.")

    if not re.fullmatch(pattern, index_name):
        raise ValueError("잘못된 인덱스 이름입니다.")

    column_list = [
        column.strip()
        for column in index_columns.split(",")
    ]

    if not column_list:
        raise ValueError("인덱스 컬럼이 없습니다.")

    for column in column_list:
        if not re.fullmatch(pattern, column):
            raise ValueError("잘못된 인덱스 컬럼입니다.")

    return ", ".join(f"`{column}`" for column in column_list)


# 실험에 등록된 인덱스 전부 제거하는 함수
def remove_experiment_indexes(cursor, indexed_conditions):
    for condition in indexed_conditions:

        table_name = condition[4]
        index_name = condition[5]

        if check_index(cursor, table_name, index_name):

            drop_index_sql = """
            DROP INDEX """ + index_name + """ ON """ + table_name + """;"""
            
            cursor.execute(drop_index_sql)

        # 삭제 후 상태 확인
        if check_index(cursor, table_name, index_name):
            raise RuntimeError(
                index_name + " 인덱스 삭제에 실패했습니다."
            )


# 현재 조건에 해당하는 인덱스 적용하는 함수
def apply_index_condition(cursor, condition):
    is_indexed = condition[3]
    table_name = condition[4]
    index_name = condition[5]
    index_columns = condition[6]

    # 인덱스 미적용 조건
    if is_indexed == 0:
        return

    # 인덱스 적용 조건
    if is_indexed == 1:

        quoted_columns = validate_index_info(
            table_name,
            index_name,
            index_columns
        )

        create_index_sql = """
        CREATE INDEX """ + index_name + """ ON """ + table_name + """
        (""" + quoted_columns + """);"""
        

        if not check_index(cursor, table_name, index_name):
            cursor.execute(create_index_sql)

        # 생성 후 상태 확인
        if not check_index(cursor, table_name, index_name):
            raise RuntimeError(
                index_name + " 인덱스 생성에 실패했습니다."
            )
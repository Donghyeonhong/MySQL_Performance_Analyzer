-- create database performance_test_db;
-- create database performance_analysis_db;

use performance_test_db;
use performance_analysis_db;

# foward engineer 도구 사용

# check 제약조건 추가
-- alter table order_detail add constraint check(quantity >= 1);

-- alter table index_condition add constraint check(is_indexed in (0, 1));
-- alter table index_condition add constraint check(
-- is_indexed = 1 or (index_name is null and index_columns is null)
-- );

-- alter table performance_log add constraint check(repeat_number >= 1);

-- 프로젝트명

-- MySQL Performance Analyzer

-- 프로젝트 목적

-- 대용량 데이터 환경에서 MySQL 데이터베이스의 SQL 실행 성능을 측정하고 분석한다. 
-- 인덱스 적용 및 SQL 구조 변경에 따른 성능 차이를 비교하고, 실행 계획을 분석하여 데이터베이스 성능 개선을 지원하는 시스템을 개발한다.

-- ALTER TABLE product
-- RENAME COLUMN `release` TO release_date;

-- alter table product_option
-- modify column size varchar(10);

-- UPDATE orders SET total_price = 
-- (SELECT SUM(order_detail.quantity * order_detail.unit_price) FROM order_detail 
-- WHERE order_detail.order_id = orders.order_id);

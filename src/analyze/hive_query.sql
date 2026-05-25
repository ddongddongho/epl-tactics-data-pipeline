-- 1. 데이터베이스 사용
USE default;

-- 2. 기존 테이블 초기화
DROP TABLE IF EXISTS epl_event_summary;

-- 3. 이벤트 집계 결과를 담을 외부 테이블 생성
CREATE EXTERNAL TABLE epl_event_summary (
    event_type STRING,
    total_count INT
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t'
LOCATION '/user/maria_dev/epl/mr_output';

-- 4. 발생 횟수 기준 내림차순 정렬 조회
SELECT * FROM epl_event_summary ORDER BY total_count DESC;

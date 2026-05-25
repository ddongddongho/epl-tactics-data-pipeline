-- 1. 데이터 로드 (events.csv)
raw_events = LOAD '/user/maria_dev/epl/raw/events.csv' USING PigStorage(',')
             AS (id_odsp:chararray, id_event:chararray, sort_order:int, time:int, text:chararray, event_type:int, event_team:chararray);

-- 2. 첫 줄(헤더) 및 결측치 제거
filtered_events = FILTER raw_events BY event_type IS NOT NULL AND time IS NOT NULL;

-- 3. 필요한 컬럼만 추출 (팀명, 이벤트 종류, 발생 시간)
cleaned_events = FOREACH filtered_events GENERATE event_team, event_type, time;

-- 4. 결과를 HDFS pig_output 폴더에 저장
STORE cleaned_events INTO '/user/maria_dev/epl/pig_output' USING PigStorage('\t');

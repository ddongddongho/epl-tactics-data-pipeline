# ⚽ EPL 매치 이벤트 대용량 로그 분석 빅데이터 파이프라인

---

## 1. 문제 정의 (Problem Definition)
* **해결하고자 하는 문제:** 현대 축구(EPL) 경기 중 발생하는 수십만 건의 무작위 매치 이벤트 로그(파울, 슛, 교체 등)는 데이터의 부피가 커 단일 PC 환경(Pandas 등)에서는 메모리 초과 및 연산 속도 저하 문제가 발생합니다. 본 프로젝트는 분산 컴퓨팅 프레임워크인 **하둡 생태계(Hadoop Ecosystem)**를 활용하여 대용량 매치 데이터를 안정적으로 적재·정제하고 분산 집계함으로써, 실제 경기에서 가장 빈번하게 발생하는 핵심 전술 이벤트 통계를 추출하고 데이터 웨어하우스를 구축하는 것을 목표로 합니다.
* **분석 데이터셋:** Kaggle 제공 EPL 경기 세부 이벤트 로그 데이터 (`events.csv`, 약 173MB, 총 **705,451건**의 대용량 레코드)

---

## 2. 기술 스택 (Technology Stack)
본 프로젝트는 **HDP Sandbox (Hadoop 3.1.1)** 가상머신 환경 인프라 위에서 구현되었으며, 데이터 수집부터 최종 시각화까지 유기적인 파이프라인 구조를 가집니다.

| 단계 | 사용 도구 | 활용 목적 및 상세 역할 |
| :---: | :--- | :--- |
| **수집 및 적재** | Python 3.6 & HDFS CLI | 로컬 환경의 대용량 원천 CSV 데이터를 HDFS 분산 파일 시스템 내부 지정 디렉토리로 자동 적재 |
| **데이터 전처리** | Apache Pig (v0.17) | `LOAD`, `FILTER`, `FOREACH` 연산자를 사용하여 원천 데이터의 결측치 및 헤더를 제거하고, 분석에 필요한 핵심 칼럼만 추출하여 구조화 |
| **분산 데이터 처리** | Python MapReduce (`mrjob`) | 하둡 스트리밍(Hadoop Streaming) 아키텍처를 활용하여 클러스터 노드들에 연산을 분산시키고, 이벤트 코드별 발생 빈도를 병렬 집계 |
| **데이터 웨어하우스** | Apache Hive (v3.1) | Tez 실행 엔진 기반의 외부 테이블(External Table)을 구성하고 OLAP 연산(`ORDER BY DESC`)을 통해 최종 통계 데이터 정착 |
| **결과 시각화** | Python (Matplotlib, Seaborn) | 데이터 웨어하우스에서 추출된 오프라인 통계치를 바탕으로 프로젝트 보고서용 테마 차트 그래프 제작 |

---

## 3. 디렉토리 구조 (Repository Structure)
기말 프로젝트 가이드라인 요구사항(4.2 항목)을 100% 준수하여 다음과 같이 리포지토리 폴더 구조를 설계하였습니다.

```text
epl-tactics-data-pipeline/
├── README.md                 # 프로젝트 개요 및 재현성 가이드 (본 파일)
├── .gitignore                # 173MB 원본 데이터의 GitHub 업로드 방지 파일 (events.csv 예외 처리)
├── epl_event_chart.png       # 최종 파이썬 결과 시각화 차트 이미지
├── data/
│   └── events_sample.csv     # 코드 검증용 100줄 분량의 샘플 데이터셋
└── src/
    ├── ingest/
    │   └── ingest.py         # HDFS 데이터 수집 자동화 스크립트
    ├── pipeline/
    │   ├── preprocess.pig    # Apache Pig 기반 데이터 정제 스크립트
    │   └── event_count.py    # mrjob 기반 MapReduce 분산 연산 코드
    └── analyze/
        ├── hive_query.sql    # Hive External Table 생성 및 분석 쿼리
        └── visualization.py  # 결과 데이터 시각화 생성 파이썬 코드
```

---

## 4. 파이프라인 실행 가이드 (How to Run)
본 프로젝트의 모든 소스코드는 아래 명령어 순서에 따라 완벽하게 동기화 및 재현(Replication)이 가능합니다.

### Step 1. 데이터 수집 및 HDFS 적재
```bash
python3.6 src/ingest/ingest.py
```

### Step 2. Apache Pig를 통한 결측치 전처리
```bash
pig src/pipeline/preprocess.pig
```

### Step 3. mrjob 기반 분산 MapReduce 연산 실행
하둡 스트리밍 환경에서 워커 노드의 파이썬 호환성을 위해 `--python-bin` 옵션을 명시하여 구동합니다.
```bash
python3.6 src/pipeline/event_count.py -r hadoop hdfs:///user/maria_dev/epl/pig_output/ \
  --output-dir hdfs:///user/maria_dev/epl/mr_output \
  --hadoop-streaming-jar /usr/hdp/current/hadoop-mapreduce-client/hadoop-streaming.jar \
  --python-bin python3.6
```
<img width="572" height="89" alt="1" src="https://github.com/user-attachments/assets/5c1f1605-a975-40fa-a9f2-14d7fe94c1de" />

### Step 4. Hive 웨어하우징 연동 및 SQL 분석
Beeline 또는 Hive CLI 창에 진입하여 아래 스크립트를 수행하여 분산 연산 결과를 연동합니다.
```sql
USE default;
DROP TABLE IF EXISTS epl_event_summary;

CREATE EXTERNAL TABLE epl_event_summary (
    event_type STRING,
    total_count INT
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY '\t'
LOCATION '/user/maria_dev/epl/mr_output';

-- 통계 분석 쿼리 실행
SELECT * FROM epl_event_summary ORDER BY total_count DESC;
```

---

## 5. 분석 결과 및 인사이트 (Analysis Results)
총 **705,451건**의 정제 데이터를 집계한 결과, EPL 경기 중 가장 빈번하게 발생하는 상위 이벤트 트렌드를 도출하였습니다.

<img width="399" height="145" alt="2" src="https://github.com/user-attachments/assets/6231c549-11f8-4460-9f59-7336389e3259" />

### 최종 데이터 웨어하우스 산출물 테이블
| 순위 | 이벤트 타입 및 코드 (event_type) | 총 발생 횟수 (total_count) | 통계적 해석 및 인사이트 |
| :---: | :--- | :--- | :--- |
| **1** | Substitution/Tactics ("8") | 237,932 건 | 경기 중 감독들의 선수 교체 및 치열한 실시간 전술 변화 시도가 가장 빈번함 |
| **2** | Fouls ("3") | 232,907 건 | 현대 축구의 매우 격렬하고 타이트한 압박 및 볼 경합 강도를 증명함 |
| **3** | Shots/Attempts ("1") | 180,006 건 | 경기당 수십 차례 이상 발생하는 공격 시도 및 슈팅 장면의 볼륨 확인 |
| **4** | Others ("4") | 39,911 건 |<img width="572" height="89" alt="1" src="https://github.com/user-attachments/assets/a95ac09d-709e-4589-a26a-48559269ca5b" />
 기타 경기 중단 및 인플레이션 상황 데이터 |
| **5** | Offsides ("10") | 10,730 건 | 수비 라인 브레이킹 및 오프사이드 트랩 작동 빈도 통계 |
| **6** | Cards ("11") | 2,706 건 | 경고 및 퇴장 조치 비율 |
| **7** | Goalkeeper Events ("6") | 1,152 건 | 골키퍼 특수 세이브 및 핸들링 로그 |
| **8** | Defensive Saves ("5") | 100 건 | 수비수의 결정적인 골라인 클리어링 등 희귀 지표 |
| **9** | Penalty Conceded ("2") | 7 건 | 전체 대용량 데이터 중 단 7회만 기록되어 가장 희귀한 이벤트임을 규명 |

> 💡 **시각화 결과 요약:** 상세 시각화 차트 결과물은 상위 레포지토리에 업로드된 `epl_event_chart.png` 파일을 참고하십시오.

---

## 6. AI 도구 활용 명시 (AI Tool Usage Policy)
기말 프로젝트 가이드라인 **'8. AI 도구 사용 정책'** 요구사항에 의거하여 본 프로젝트 수행 중 발생한 오류의 디버깅 및 솔루션 최적화 과정에서 다음과 같이 AI 도구(Gemini)를 정직하게 활용하였음을 명시합니다.

* **YARN MapReduce 컨테이너 경로 에러 디버깅:** `mrjob` 구동 시 발생한 `PipeMapRed.waitOutputThreads() subprocess failed with code 127` 예외에 대하여, 하둡 워커 노드가 로컬 파이썬 실행 바이너리 경로를 참조하지 못하는 인프라 구조적 원인을 파악하고 `--python-bin python3.6` 환경 변수를 주입하는 해결책을 도출하는 데 적극 활용함.
* **Hive 쿼리 권한(Permission) 문제 해결:** Hive 데이터 웨어하우스 외부 테이블 구성 중 발생한 `FAILED: HiveAccessControlException Permission denied: user [hive]` 보안 에러에 대해, 하둡 소유 계정 간의 권한 간섭 문제를 이해하고 HDFS 파일 권한 변경 명령어(`hdfs dfs -chmod -R 777`)를 적용하여 파이프라인을 성공적으로 관통시킴.

import os

def ingest_data():
    current_dir = "/home/maria_dev"
    target_hdfs_dir = "/user/maria_dev/epl/raw/"

    # 다른 csv 제외하고 진짜 축구 데이터만 콕 집어서 타겟팅!
    files = ['events.csv', 'ginf.csv']
    print(f"축구 데이터 수집 및 HDFS 적재 파이프라인을 시작합니다.")

    for file in files:
        if os.path.exists(f"{current_dir}/{file}"):
            print(f"[진행중] {file} 데이터를 HDFS로 이동합니다...")
            os.system(f"hdfs dfs -put -f '{current_dir}/{file}' {target_hdfs_dir}")
        else:
            print(f"[경고] {file} 파일이 없습니다!")

    print("데이터 수집 및 적재 파이프라인 완료")

if __name__ == "__main__":
    ingest_data()

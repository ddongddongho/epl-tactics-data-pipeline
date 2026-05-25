import matplotlib.pyplot as plt
import seaborn as sns

# 1. Hive에서 추출된 실제 최종 데이터 매핑
event_data = {
    "Substitution/Tactics (8)": 237932,
    "Fouls (3)": 232907,
    "Shots/Attempts (1)": 180006,
    "Others (4)": 39911,
    "Offsides (10)": 10730,
    "Cards (11)": 2706,
    "Goalkeeper Events (6)": 1152,
    "Defensive Saves (5)": 100,
    "Penalty Conceded (2)": 7
}

# 데이터 정렬 (내림차순)
sorted_events = sorted(event_data.items(), key=lambda x: x[1], reverse=True)
categories = [item[0] for item in sorted_events]
counts = [item[1] for item in sorted_events]

# 2. 시각화 스타일 설정
plt.figure(figsize=(12, 7))
sns.set_theme(style="whitegrid")
colors = sns.color_palette("Spectral", len(categories))

# 3. 바 차트 생성
barplot = sns.barplot(x=counts, y=categories, palette=colors)

# 그래프 제목 및 축 레이블 설정
plt.title("EPL Total Match Event Count Analysis (Top 9)", fontsize=16, fontweight='bold', pad=20)
plt.xlabel("Total Event Occurrence", fontsize=12, labelpad=10)
plt.ylabel("Event Type (Code)", fontsize=12, labelpad=10)

# 막대 끝에 숫자 레이블 추가
for i, count in enumerate(counts):
    barplot.text(count + 3000, i, f'{count:,}', va='center', fontsize=10, fontweight='bold')

plt.tight_layout()

# 4. 이미지 파일로 저장
plt.savefig("epl_event_chart.png", dpi=300)
print("시각화 차트 저장 완료: epl_event_chart.png")

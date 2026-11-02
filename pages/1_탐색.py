import pandas as pd
import plotly.express as px
import streamlit as st

# ------------------------------
# 페이지 설정 및 데이터 불러오기
# ------------------------------
st.set_page_config(
    page_title="탐색 | 뇌졸중 예측 실습실",
    page_icon="🔎",
    layout="wide",
)

APP_TITLE = "뇌졸중 예측 실습실"
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/stroke.csv"

st.title("🔎 데이터 탐색")
st.caption("나이, 평균 혈당, 질병 여부, 흡연 상태와 뇌졸중의 관계를 데이터로 살펴봅니다.")

@st.cache_data
def load_data():
    return pd.read_csv(DATA_URL, encoding="utf-8")

try:
    df = load_data()
except Exception as error:
    st.error("데이터를 불러오지 못했습니다. 인터넷 연결이나 데이터 주소를 확인해 주세요.")
    st.exception(error)
    st.stop()

required_columns = [
    "age", "avg_glucose_level", "hypertension",
    "heart_disease", "stroke", "bmi", "smoking_status"
]
missing_columns = [column for column in required_columns if column not in df.columns]
if missing_columns:
    st.error(f"데이터에 필요한 열이 없습니다: {', '.join(missing_columns)}")
    st.stop()

# 숫자형 데이터로 분석할 수 있도록 변환
for column in ["age", "avg_glucose_level", "hypertension", "heart_disease", "stroke", "bmi"]:
    df[column] = pd.to_numeric(df[column], errors="coerce")

stroke_labels = {0: "뇌졸중 없음", 1: "뇌졸중 있음"}
df["뇌졸중 여부"] = df["stroke"].map(stroke_labels)

st.info(
    "이 페이지는 데이터의 분포와 그룹별 차이를 살펴보는 탐색 활동입니다. "
    "그래프에서 함께 나타나는 경향만으로 원인과 결과를 단정할 수는 없습니다."
)

# ------------------------------
# 1. 나이와 평균 혈당 분포
# ------------------------------
st.subheader("1. 나이와 평균 혈당의 분포")
left, right = st.columns(2)

with left:
    age_data = df.dropna(subset=["age"])
    fig_age = px.histogram(
        age_data,
        x="age",
        nbins=30,
        title="나이 분포",
        labels={"age": "나이", "count": "사람 수"},
    )
    fig_age.update_layout(yaxis_title="사람 수", bargap=0.08)
    st.plotly_chart(fig_age, use_container_width=True)

with right:
    glucose_data = df.dropna(subset=["avg_glucose_level"])
    fig_glucose = px.histogram(
        glucose_data,
        x="avg_glucose_level",
        nbins=30,
        title="평균 혈당 분포",
        labels={"avg_glucose_level": "평균 혈당", "count": "사람 수"},
    )
    fig_glucose.update_layout(yaxis_title="사람 수", bargap=0.08)
    st.plotly_chart(fig_glucose, use_container_width=True)

st.divider()

# ------------------------------
# 2. 뇌졸중 여부에 따른 나이와 평균 혈당 비교
# ------------------------------
st.subheader("2. 뇌졸중 여부에 따른 나이와 평균 혈당 비교")
box_left, box_right = st.columns(2)

with box_left:
    age_box_data = df.dropna(subset=["age", "뇌졸중 여부"])
    fig_age_box = px.box(
        age_box_data,
        x="뇌졸중 여부",
        y="age",
        color="뇌졸중 여부",
category_orders={"뇌졸중 여부": ["뇌졸중 없음", "뇌졸중 있음"]},
        title="뇌졸중 여부별 나이",
        labels={"뇌졸중 여부": "그룹", "age": "나이"},
    )
    fig_age_box.update_layout(showlegend=False)
    st.plotly_chart(fig_age_box, use_container_width=True)

with box_right:
    glucose_box_data = df.dropna(subset=["avg_glucose_level", "뇌졸중 여부"])
    fig_glucose_box = px.box(
        glucose_box_data,
        x="뇌졸중 여부",
        y="avg_glucose_level",
        color="뇌졸중 여부",
        category_orders={"뇌졸중 여부": ["뇌졸중 없음", "뇌졸중 있음"]},
        title="뇌졸중 여부별 평균 혈당",
        labels={"뇌졸중 여부": "그룹", "avg_glucose_level": "평균 혈당"},
    )
    fig_glucose_box.update_layout(showlegend=False)
    st.plotly_chart(fig_glucose_box, use_container_width=True)

mean_table = (
    df[df["stroke"].isin([0, 1])]
    .groupby("뇌졸중 여부", observed=False)[["age", "avg_glucose_level"]]
    .mean()
    .reindex(["뇌졸중 없음", "뇌졸중 있음"])
    .rename(columns={"age": "평균 나이", "avg_glucose_level": "평균 혈당"})
    .round(2)
)
st.markdown("**그룹별 평균값**")
st.dataframe(mean_table, use_container_width=True)

st.divider()

# ------------------------------
# 3. 고혈압 및 심장병 여부에 따른 뇌졸중 비율
# ------------------------------
st.subheader("3. 고혈압·심장병 여부에 따른 뇌졸중 비율")

def make_rate_table(column, labels):
    valid = df[df[column].isin([0, 1]) & df["stroke"].isin([0, 1])].copy()
    valid["구분"] = valid[column].map(labels)
    result = (
        valid.groupby("구분", observed=False)["stroke"]
        .agg(["mean", "count"])
        .reset_index()
    )
    result["뇌졸중 비율(%)"] = result["mean"] * 100
    return result

risk_left, risk_right = st.columns(2)

with risk_left:
    hypertension_table = make_rate_table(
        "hypertension", {0: "고혈압 없음", 1: "고혈압 있음"}
    )
    fig_hypertension = px.bar(
        hypertension_table,
        x="구분",
        y="뇌졸중 비율(%)",
        text=hypertension_table["뇌졸중 비율(%)"].map(lambda value: f"{value:.2f}%"),
        title="고혈압 여부별 뇌졸중 비율",
        labels={"구분": "고혈압 여부"},
    )
    fig_hypertension.update_layout(yaxis_title="뇌졸중 비율(%)")
    st.plotly_chart(fig_hypertension, use_container_width=True)

with risk_right:
    heart_table = make_rate_table(
        "heart_disease", {0: "심장병 없음", 1: "심장병 있음"}
    )
    fig_heart = px.bar(
        heart_table,
        x="구분",
        y="뇌졸중 비율(%)",
        text=heart_table["뇌졸중 비율(%)"].map(lambda value: f"{value:.2f}%"),
        title="심장병 여부별 뇌졸중 비율",
        labels={"구분": "심장병 여부"},
    )
    fig_heart.update_layout(yaxis_title="뇌졸중 비율(%)")
    st.plotly_chart(fig_heart, use_container_width=True)

st.caption("비율은 각 구분에 속한 사람 중 stroke 값이 1인 사람의 비율입니다.")

st.divider()

# ------------------------------
# 4. BMI 결측 그룹과 전체의 뇌졸중 비율
# ------------------------------
st.subheader("4. BMI가 비어 있는 사람들의 뇌졸중 비율")

missing_bmi = df[df["bmi"].isna()]
valid_all_stroke = df[df["stroke"].isin([0, 1])]
valid_missing_bmi_stroke = missing_bmi[missing_bmi["stroke"].isin([0, 1])]

missing_bmi_rate = (
    valid_missing_bmi_stroke["stroke"].mean() * 100
    if len(valid_missing_bmi_stroke) > 0 else float("nan")
)
overall_rate = (
    valid_all_stroke["stroke"].mean() * 100
    if len(valid_all_stroke) > 0 else float("nan")
)

bmi_comparison = pd.DataFrame([
    {
        "대상": "BMI가 비어 있는 사람",
        "사람 수": len(missing_bmi),
        "뇌졸중 비율(%)": missing_bmi_rate,
    },
    {
        "대상": "전체 사람",
        "사람 수": len(df),
        "뇌졸중 비율(%)": overall_rate,
    },
])
bmi_comparison["뇌졸중 비율(%)"] = bmi_comparison["뇌졸중 비율(%)"].round(2)
st.dataframe(bmi_comparison, hide_index=True, use_container_width=True)
st.caption("BMI 결측 그룹의 비율은 BMI가 비어 있는 사람 중 stroke 값이 확인되는 사람을 기준으로 계산했습니다.")

st.divider()

# ------------------------------
# 5. 흡연 상태별 사람 수
# ------------------------------
st.subheader("5. 흡연 상태별 사람 수")

smoking_counts = (

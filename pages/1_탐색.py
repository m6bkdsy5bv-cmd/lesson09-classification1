import pandas as pd
import plotly.express as px
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="탐색 | 뇌졸중 예측 실습실",
    page_icon="🔎",
    layout="wide",
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/stroke.csv"

st.title("🔎 데이터 탐색")
st.caption("뇌졸중 데이터의 분포와 여러 특성을 비교해 봅니다.")


# 데이터는 첫 화면과 같은 주소에서 UTF-8로 불러옵니다.
@st.cache_data
def load_data():
    data = pd.read_csv(DATA_URL, encoding="utf-8")
    return data


try:
    df = load_data()
except Exception as error:
    st.error("데이터를 불러오지 못했습니다. 인터넷 연결과 데이터 주소를 확인해 주세요.")
    st.exception(error)
    st.stop()


required_columns = [
    "age",
    "avg_glucose_level",
    "hypertension",
    "heart_disease",
    "stroke",
    "bmi",
    "smoking_status",
]

missing_columns = []
for column in required_columns:
    if column not in df.columns:
        missing_columns.append(column)

if missing_columns:
    st.error("필요한 열이 데이터에 없습니다: " + ", ".join(missing_columns))
    st.stop()


# 분석에 사용할 열을 숫자형으로 변환합니다.
numeric_columns = [
    "age",
    "avg_glucose_level",
    "hypertension",
    "heart_disease",
    "stroke",
    "bmi",
]

for column in numeric_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

df["뇌졸중 여부"] = df["stroke"].map({
    0: "뇌졸중 없음",
    1: "뇌졸중 있음",
})

st.info(
    "그래프는 데이터에서 나타나는 경향을 보여 줍니다. "
    "두 변수 사이에 차이가 있다고 해서 한 변수가 다른 변수의 원인이라고 단정할 수는 없습니다."
)


# 1. 나이와 평균 혈당의 분포
st.subheader("1. 나이와 평균 혈당의 분포")

col1, col2 = st.columns(2)

with col1:
    age_data = df.dropna(subset=["age"])
    age_fig = px.histogram(
        age_data,
        x="age",
        nbins=30,
        title="나이 분포",
        labels={"age": "나이", "count": "사람 수"},
    )
    age_fig.update_layout(yaxis_title="사람 수", bargap=0.08)
    st.plotly_chart(age_fig, use_container_width=True)

with col2:
    glucose_data = df.dropna(subset=["avg_glucose_level"])
    glucose_fig = px.histogram(

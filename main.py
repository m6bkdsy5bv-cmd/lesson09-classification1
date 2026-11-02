import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.model_selection import train_test_split  # 이후 예측 모델 실습에 활용 가능

# ------------------------------
# 기본 설정
# ------------------------------
APP_TITLE = "뇌졸중 예측 실습실"
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/stroke.csv"
RECORD_DIR = Path(__file__).parent / "내_기록"
RECORD_FILE = RECORD_DIR / "stroke_data_notes.json"

st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🧠",
    layout="wide",
)

st.title(f"🧠 {APP_TITLE}")
st.caption("뇌졸중 데이터의 구조와 주요 정보를 살펴보는 실습 공간입니다.")

# ------------------------------
# 기록 불러오기 / 저장하기
# ------------------------------
def load_records():
    """저장된 우리말 뜻과 데이터 출처를 불러옵니다."""
    if RECORD_FILE.exists():
        try:
            with RECORD_FILE.open("r", encoding="utf-8") as file:
                data = json.load(file)
            return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, OSError):
            st.warning("기존 기록 파일을 읽지 못해 새 기록으로 시작합니다.")
    return {}


def save_records(meanings, source):
    """우리말 뜻과 데이터 출처를 JSON 파일에 저장합니다."""
    RECORD_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "meanings": meanings,
        "data_source": source,
    }
    with RECORD_FILE.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


saved = load_records()

# ------------------------------
# 데이터 불러오기
# ------------------------------
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
    "id", "gender", "age", "hypertension", "heart_disease",
    "ever_married", "work_type", "Residence_type",
    "avg_glucose_level", "bmi", "smoking_status", "stroke"
]
missing_columns = [column for column in required_columns if column not in df.columns]
if missing_columns:
    st.error(f"데이터에 필요한 열이 없습니다: {', '.join(missing_columns)}")
    st.stop()

# ------------------------------
# 핵심 통계 카드
# ------------------------------
total_people = len(df)
column_count = len(df.columns)
stroke_count = int((df["stroke"] == 1).sum())
stroke_ratio = (stroke_count / total_people * 100) if total_people else 0

st.subheader("📊 데이터 한눈에 보기")
card1, card2, card3, card4 = st.columns(4)
card1.metric("전체 사람 수", f"{total_people:,}명")
card2.metric("열 개수", f"{column_count:,}개")
card3.metric("stroke가 1인 사람 수", f"{stroke_count:,}명")
card4.metric("stroke가 1인 비율", f"{stroke_ratio:.2f}%")

st.divider()

# ------------------------------
# 열 정보 표

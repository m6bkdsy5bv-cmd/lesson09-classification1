
import streamlit as st
import pandas as pd
import json
from pathlib import Path

# ==========================================
# 1. 기본 설정
# ==========================================

st.set_page_config(
    page_title="뇌졸중 예측 실습실",
    page_icon="🧠",
    layout="wide"
)

DATA_URL = (
    "https://raw.githubusercontent.com/"
    "greatsong/modudata/main/data/stroke.csv"
)

RECORD_DIR = Path("내_기록")
RECORD_FILE = RECORD_DIR / "데이터_설명.json"

COLUMNS = [
    "id",
    "gender",
    "age",
    "hypertension",
    "heart_disease",
    "ever_married",
    "work_type",
    "Residence_type",
    "avg_glucose_level",
    "bmi",
    "smoking_status",
    "stroke"
]


# ==========================================
# 2. 기록 파일 불러오기 및 저장하기
# ==========================================

def load_records():
    RECORD_DIR.mkdir(parents=True, exist_ok=True)

    if RECORD_FILE.exists():
        try:
            with open(RECORD_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError):
            pass

    return {
        "column_meanings": {
            column: "" for column in COLUMNS
        },
        "data_source": ""
    }


def save_records(meanings, source):
    RECORD_DIR.mkdir(parents=True, exist_ok=True)

    records = {
        "column_meanings": meanings,
        "data_source": source
    }

    with open(RECORD_FILE, "w", encoding="utf-8") as file:
        json.dump(
            records,
            file,
            ensure_ascii=False,
            indent=4
        )


# ==========================================
# 3. 데이터 불러오기
# ==========================================

@st.cache_data
def load_data():
    return pd.read_csv(
        DATA_URL,
        encoding="utf-8"
    )


try:
    df = load_data()

except Exception as e:
    st.error("데이터를 불러오는 중 오류가 발생했습니다.")
    st.error(str(e))
    st.stop()


records = load_records()


# ==========================================
# 4. 앱 제목
# ==========================================

st.title("🧠 뇌졸중 예측 실습실")

st.markdown(
    """
    ### 데이터 탐색부터 시작하는 뇌졸중 예측 프로젝트

    뇌졸중 관련 데이터를 살펴보고,
    데이터의 특징을 이해하며 머신러닝 예측 모델을
    만들어 보기 위한 실습 공간입니다.
    """
)

st.divider()


# ==========================================
# 5. 데이터 소개
# ==========================================

st.header("📊 1. 데이터 소개")

st.markdown(
    """
    이 데이터는 사람들의 건강 상태와 생활 습관에 관한
    정보를 담고 있으며, 뇌졸중 발생 여부를 나타내는
    `stroke` 열을 포함하고 있습니다.

    데이터를 살펴보면서 각 열의 의미와 데이터의
    전체적인 특징을 알아보겠습니다.
    """
)

total_people = len(df)
total_columns = len(df.columns)
stroke_people = int((df["stroke"] == 1).sum())

stroke_ratio = (
    stroke_people / total_people * 100
    if total_people > 0 else 0
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("👥 전체 사람 수", f"{total_people:,}명")

with col2:
    st.metric("📋 전체 열 개수", f"{total_columns}개")

with col3:
    st.metric("🧠 뇌졸중 발생 인원", f"{stroke_people:,}명")

with col4:
    st.metric("📈 뇌졸중 발생 비율", f"{stroke_ratio:.2f}%")


st.divider()


# ==========================================
# 6. 열 이름과 데이터 특징
# ==========================================

st.header("📝 2. 데이터 열 살펴보기")

st.markdown(
    """
    아래 표에는 데이터의 열 이름과 값의 종류,
    빈 값의 개수가 표시되어 있습니다.

    **우리말 뜻** 칸은 교재를 참고하여 직접 입력해 보세요.
    입력한 내용은 저장 버튼을 누르면 JSON 파일에 저장됩니다.
    """
)

column_info = []

saved_meanings = records.get("column_meanings", {})

for column in df.columns:

    if pd.api.types.is_numeric_dtype(df[column]):
        value_type = "숫자형"
    else:
        value_type = "범주형"

    column_info.append({
        "열 이름": column,
        "우리말 뜻": saved_meanings.get(column, ""),
        "값의 종류": value_type,
        "빈 값 개수": int(df[column].isna().sum())
    })

info_df = pd.DataFrame(column_info)

edited_df = st.data_editor(
    info_df,
    use_container_width=True,
    hide_index=True,
    key="column_editor",
    disabled=[
        "열 이름",
        "값의 종류",
        "빈 값 개수"
    ],
    column_config={
        "열 이름": st.column_config.TextColumn("열 이름"),
        "우리말 뜻": st.column_config.TextColumn(
            "우리말 뜻",
            help="교재를 참고하여 우리말 뜻을 입력하세요.",
            width="large"
        ),
        "값의 종류": st.column_config.TextColumn("값의 종류"),
        "빈 값 개수": st.column_config.NumberColumn(
            "빈 값 개수",
            format="%d"
        )
    }
)

st.divider()


# ==========================================
# 7. 데이터 처음 다섯 줄
# ==========================================

st.header("🔍 3. 데이터 미리 보기")

st.markdown(
    "실제 데이터의 처음 다섯 줄을 확인해 봅시다."
)

st.dataframe(
    df.head(5),
    use_container_width=True,
    hide_index=True
)

st.divider()


# ==========================================
# 8. 데이터 출처 기록
# ==========================================

st.header("📚 4. 데이터 출처")

data_source = st.text_area(
    "데이터 출처 및 참고 자료",
    value=records.get("data_source", ""),
    height=120,
    placeholder="교재에 나온 데이터 출처를 입력하세요.",
    key="data_source_input"
)


# ==========================================
# 9. 저장
# ==========================================

if st.button(
    "💾 입력 내용 저장하기",
    type="primary",
    use_container_width=True
):

    meanings = {}

    for _, row in edited_df.iterrows():
        meanings[row["열 이름"]] = row["우리말 뜻"]

    save_records(meanings, data_source)

    st.success(
        "저장되었습니다! "
        "새로고침해도 입력한 내용을 다시 불러옵니다."
    )

st.caption(
    "저장 위치: 내_기록/데이터_설명.json"
)

st.divider()


# ==========================================
# 10. 마무리
# ==========================================

st.markdown(
    """
    <div style="text-align:center; padding:20px;">
        <h3>🧠 뇌졸중 예측 실습실</h3>
        <p>데이터를 이해하는 것이 예측 모델 만들기의 첫걸음입니다.</p>
    </div>
    """,
    unsafe_allow_html=True
)

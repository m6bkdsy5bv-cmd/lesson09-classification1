
import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. 페이지 설정
# ==========================================

st.set_page_config(
    page_title="탐색 | 뇌졸중 예측 실습실",
    page_icon="🔎",
    layout="wide"
)

DATA_URL = (
    "https://raw.githubusercontent.com/"
    "greatsong/modudata/main/data/stroke.csv"
)


# ==========================================
# 2. 데이터 불러오기
# ==========================================

@st.cache_data
def load_data():

    df = pd.read_csv(
        DATA_URL,
        encoding="utf-8"
    )

    # 숫자형 데이터 변환
    numeric_columns = [
        "age",
        "avg_glucose_level",
        "bmi",
        "hypertension",
        "heart_disease",
        "stroke"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    return df


try:
    df = load_data()

except Exception as e:
    st.error("데이터를 불러오는 중 오류가 발생했습니다.")
    st.error(str(e))
    st.stop()


# ==========================================
# 3. 페이지 제목
# ==========================================

st.title("🔎 데이터 탐색")

st.markdown(
    """
    ### 데이터를 그래프와 표로 자세히 살펴봅시다.

    나이, 평균 혈당, 고혈압, 심장병, BMI, 흡연 상태와
    뇌졸중의 관계를 탐색합니다.
    """
)

st.divider()


# ==========================================
# 4. 나이와 평균 혈당 분포
# ==========================================

st.header("📊 1. 나이와 평균 혈당의 분포")

st.markdown(
    """
    히스토그램은 데이터가 어느 구간에
    많이 분포하는지 알아보는 그래프입니다.
    """
)

col1, col2 = st.columns(2)

with col1:

    st.subheader("나이 분포")

    age_data = df.dropna(subset=["age"])

    fig_age = px.histogram(
        age_data,
        x="age",
        nbins=30,
        title="나이 분포",
        labels={
            "age": "나이",
            "count": "사람 수"
        },
        color_discrete_sequence=["#4C78A8"]
    )

    fig_age.update_layout(
        xaxis_title="나이",
        yaxis_title="사람 수",
        bargap=0.08
    )

    st.plotly_chart(
        fig_age,
        use_container_width=True
    )


with col2:

    st.subheader("평균 혈당 분포")

    glucose_data = df.dropna(
        subset=["avg_glucose_level"]
    )

    fig_glucose = px.histogram(
        glucose_data,
        x="avg_glucose_level",
        nbins=30,
        title="평균 혈당 분포",
        labels={
            "avg_glucose_level": "평균 혈당",
            "count": "사람 수"
        },
        color_discrete_sequence=["#F58518"]
    )

    fig_glucose.update_layout(
        xaxis_title="평균 혈당",
        yaxis_title="사람 수",
        bargap=0.08
    )

    st.plotly_chart(
        fig_glucose,
        use_container_width=True
    )


st.divider()


# ==========================================
# 5. 뇌졸중 유무별 상자그림
# ==========================================

st.header("📦 2. 뇌졸중 유무에 따른 나이와 평균 혈당 비교")

st.markdown(
    """
    상자그림은 중앙값과 데이터의 분포,
    이상치 등을 확인할 수 있는 그래프입니다.

    뇌졸중을 겪은 사람과 겪지 않은 사람의
    나이와 평균 혈당을 비교해 봅시다.
    """
)

df["stroke_group"] = df["stroke"].map({
    0: "뇌졸중 없음",
    1: "뇌졸중 있음"
})

stroke_order = [
    "뇌졸중 없음",
    "뇌졸중 있음"
]

col1, col2 = st.columns(2)

with col1:

    st.subheader("뇌졸중 유무별 나이")

    age_box_data = df.dropna(
        subset=["age", "stroke_group"]
    )

    fig_age_box = px.box(
        age_box_data,
        x="stroke_group",
        y="age",
        color="stroke_group",
        category_orders={
            "stroke_group": stroke_order
        },
        title="뇌졸중 유무별 나이 비교",
        labels={
            "stroke_group": "뇌졸중 여부",
            "age": "나이"
        },
        color_discrete_map={
            "뇌졸중 없음": "#4C78A8",
            "뇌졸중 있음": "#E45756"
        }
    )

    fig_age_box.update_layout(
        showlegend=False,
        xaxis_title="뇌졸중 여부",
        yaxis_title="나이"
    )

    st.plotly_chart(
        fig_age_box,
        use_container_width=True
    )


with col2:

    st.subheader("뇌졸중 유무별 평균 혈당")

    glucose_box_data = df.dropna(
        subset=["avg_glucose_level", "stroke_group"]
    )

    fig_glucose_box = px.box(
        glucose_box_data,
        x="stroke_group",
        y="avg_glucose_level",
        color="stroke_group",
        category_orders={
            "stroke_group": stroke_order
        },
        title="뇌졸중 유무별 평균 혈당 비교",
        labels={
            "stroke_group": "뇌졸중 여부",
            "avg_glucose_level": "평균 혈당"
        },
        color_discrete_map={
            "뇌졸중 없음": "#4C78A8",
            "뇌졸중 있음": "#E45756"
        }
    )

    fig_glucose_box.update_layout(
        showlegend=False,
        xaxis_title="뇌졸중 여부",
        yaxis_title="평균 혈당"
    )

    st.plotly_chart(
        fig_glucose_box,
        use_container_width=True
    )


# 그룹별 평균값 계산
st.subheader("그룹별 평균값 비교")

mean_table = (
    df.groupby("stroke_group", observed=False)
    .agg(
        평균_나이=("age", "mean"),
        평균_혈당=("avg_glucose_level", "mean"),
        사람_수=("stroke", "count")
    )
    .reindex(stroke_order)
    .reset_index()
)

mean_table.columns = [
    "뇌졸중 여부",
    "평균 나이",
    "평균 혈당",
    "사람 수"
]

mean_table["평균 나이"] = mean_table["평균 나이"].round(2)
mean_table["평균 혈당"] = mean_table["평균 혈당"].round(2)

st.dataframe(
    mean_table,
    use_container_width=True,
    hide_index=True
)


st.divider()


# ==========================================
# 6. 고혈압 유무별 뇌졸중 비율
# ==========================================

st.header("❤️ 3. 고혈압 유무별 뇌졸중 비율")

st.markdown(
    """
    고혈압이 있는 사람과 없는 사람의
    뇌졸중 발생 비율을 비교합니다.
    """
)

hypertension_data = (
    df.dropna(
        subset=["hypertension", "stroke"]
    )
    .groupby("hypertension")
    .agg(
        전체_인원=("stroke", "count"),
        뇌졸중_인원=("stroke", "sum")
    )
    .reset_index()
)

hypertension_data["뇌졸중_비율"] = (
    hypertension_data["뇌졸중_인원"]
    / hypertension_data["전체_인원"]
    * 100
)

hypertension_data["고혈압 여부"] = (
    hypertension_data["hypertension"]
    .map({
        0: "고혈압 없음",
        1: "고혈압 있음"
    })
)

fig_hypertension = px.bar(
    hypertension_data,
    x="고혈압 여부",
    y="뇌졸중_비율",
    text=hypertension_data["뇌졸중_비율"].map(
        lambda x: f"{x:.2f}%"
    ),
    title="고혈압 유무별 뇌졸중 발생 비율",
    labels={
        "고혈압 여부": "고혈압 여부",
        "뇌졸중_비율": "뇌졸중 발생 비율 (%)"
    },
    color="고혈압 여부",
    color_discrete_map={
        "고혈압 없음": "#72B7B2",
        "고혈압 있음": "#E45756"
    }
)

fig_hypertension.update_traces(
    textposition="outside"
)

fig_hypertension.update_layout(
    showlegend=False,
    yaxis_title="뇌졸중 발생 비율 (%)"
)

st.plotly_chart(
    fig_hypertension,
    use_container_width=True
)

st.dataframe(
    hypertension_data[
        [
            "고혈압 여부",
            "전체_인원",
            "뇌졸중_인원",
            "뇌졸중_비율"
        ]
    ].rename(columns={
        "전체_인원": "전체 인원",
        "뇌졸중_인원": "뇌졸중 인원",
        "뇌졸중_비율": "뇌졸중 비율(%)"
    }).round(2),
    use_container_width=True,
    hide_index=True
)


st.divider()


# ==========================================
# 7. 심장병 유무별 뇌졸중 비율
# ==========================================

st.header("💗 4. 심장병 유무별 뇌졸중 비율")

st.markdown(
    """
    심장병이 있는 사람과 없는 사람의
    뇌졸중 발생 비율을 비교합니다.
    """
)

heart_data = (
    df.dropna(
        subset=["heart_disease", "stroke"]
    )
    .groupby("heart_disease")
    .agg(
        전체_인원=("stroke", "count"),
        뇌졸중_인원=("stroke", "sum")
    )
    .reset_index()
)

heart_data["뇌졸중_비율"] = (
    heart_data["뇌졸중_인원"]
    / heart_data["전체_인원"]
    * 100
)

heart_data["심장병 여부"] = (
    heart_data["heart_disease"]
    .map({
        0: "심장병 없음",
        1: "심장병 있음"
    })
)

fig_heart = px.bar(
    heart_data,
    x="심장병 여부",
    y="뇌졸중_비율",
    text=heart_data["뇌졸중_비율"].map(
        lambda x: f"{x:.2f}%"
    ),
    title="심장병 유무별 뇌졸중 발생 비율",
    labels={
        "심장병 여부": "심장병 여부",
        "뇌졸중_비율": "뇌졸중 발생 비율 (%)"
    },
    color="심장병 여부",
    color_discrete_map={
        "심장병 없음": "#72B7B2",
        "심장병 있음": "#E45756"
    }
)

fig_heart.update_traces(
    textposition="outside"
)

fig_heart.update_layout(
    showlegend=False,
    yaxis_title="뇌졸중 발생 비율 (%)"
)

st.plotly_chart(
    fig_heart,
    use_container_width=True
)

st.dataframe(
    heart_data[
        [
            "심장병 여부",
            "전체_인원",
            "뇌졸중_인원",
            "뇌졸중_비율"
        ]
    ].rename(columns={
        "전체_인원": "전체 인원",
        "뇌졸중_인원": "뇌졸중 인원",
        "뇌졸중_비율": "뇌졸중 비율(%)"
    }).round(2),
    use_container_width=True,
    hide_index=True
)


st.divider()


# ==========================================
# 8. BMI 결측자와 전체 뇌졸중 비율
# ==========================================

st.header("📋 5. BMI 빈 값과 뇌졸중 발생 비율")

st.markdown(
    """
    BMI(체질량지수)가 비어 있는 사람들을 따로 살펴봅니다.

    BMI가 비어 있는 사람들의 뇌졸중 비율과
    전체 사람들의 뇌졸중 비율을 비교합니다.
    """
)

# BMI 결측자
missing_bmi = df[df["bmi"].isna()]

missing_bmi_count = len(missing_bmi)

missing_bmi_stroke = int(
    (missing_bmi["stroke"] == 1).sum()
)

missing_bmi_ratio = (
    missing_bmi_stroke / missing_bmi_count * 100
    if missing_bmi_count > 0 else 0
)

# 전체 데이터
total_count = len(df)

total_stroke_count = int(
    (df["stroke"] == 1).sum()
)

total_stroke_ratio = (
    total_stroke_count / total_count * 100
    if total_count > 0 else 0
)

bmi_comparison = pd.DataFrame({
    "구분": [
        "BMI 빈 값인 사람",
        "전체 사람"
    ],
    "사람 수": [
        missing_bmi_count,
        total_count
    ],
    "뇌졸중 인원": [
        missing_bmi_stroke,
        total_stroke_count
    ],
    "뇌졸중 비율(%)": [
        round(missing_bmi_ratio, 2),
        round(total_stroke_ratio, 2)
    ]
})

st.dataframe(
    bmi_comparison,
    use_container_width=True,
    hide_index=True
)

st.info(
    f"BMI가 비어 있는 사람은 총 {missing_bmi_count:,}명이며, "
    f"이 중 뇌졸중을 겪은 사람은 {missing_bmi_stroke:,}명입니다."
)


st.divider()


# ==========================================
# 9. 흡연 상태별 사람 수
# ==========================================

st.header("🚬 6. 흡연 상태별 사람 수")

st.markdown(
    """
    흡연 상태에 어떤 값들이 있는지 확인하고,
    각 상태에 해당하는 사람 수를 세어 봅니다.

    빈 값도 별도로 표시합니다.
    """
)

smoking_counts = (
    df["smoking_status"]
    .fillna("빈 값")
    .value_counts()
    .rename_axis("흡연 상태")
    .reset_index(name="사람 수")
)

st.dataframe(
    smoking_counts,
    use_container_width=True,
    hide_index=True
)


st.divider()


# ==========================================
# 10. 마무리
# ==========================================

st.markdown(
    """
    <div style="text-align:center; padding:20px;">
        <h3>🔎 데이터 탐색 완료!</h3>
        <p>데이터의 분포와 변수 사이의 관계를 확인했습니다.</p>
        <p>다음 단계에서는 데이터를 이용하여 예측 모델을 만들어 봅시다.</p>
    </div>
    """,
    unsafe_allow_html=True
)

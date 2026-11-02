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

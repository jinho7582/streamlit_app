import streamlit as st
import pandas as pd
import pydeck as pdk
import math

st.set_page_config(
    page_title="주차장 정보 서비스",
    page_icon="🅿️",
    layout="wide"
)

st.title("🅿️ 주차장 정보 검색 서비스")

uploaded_file = st.file_uploader(
    "CSV 파일 업로드 (CP949)",
    type=["csv"]
)

if uploaded_file:

    df = pd.read_csv(uploaded_file, encoding="cp949")

    # ✅ 숫자 컬럼 정리 (에러 방지 핵심)
    num_cols = ["기본요금", "기본시간", "추가요금", "추가시간"]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["추가시간"] = df["추가시간"].fillna(1)
    df[num_cols] = df[num_cols].fillna(0)

    # 문자열 공백 제거
    df["무료여부"] = df["무료여부"].astype(str).str.strip()

    st.success("파일 업로드 완료!")

    st.subheader("원본 데이터")
    st.dataframe(df)

    # -------------------
    # 사이드바 필터
    # -------------------
    st.sidebar.header("검색 조건")

    gu = st.sidebar.selectbox(
        "자치구 선택",
        ["전체"] + sorted(df["자치구"].dropna().unique().tolist())
    )

    parking_type = st.sidebar.selectbox(
        "주차장 종류",
        ["전체"] + sorted(df["주차장종류"].dropna().unique().tolist())
    )

    fee_type = st.sidebar.radio(
        "요금",
        ["전체", "무료", "유료"]
    )

    parking_time = st.sidebar.number_input(
        "예상 주차시간(분)",
        min_value=10,
        value=60,
        step=10
    )

    result = df.copy()

    # -------------------
    # 필터 적용
    # -------------------
    if gu != "전체":
        result = result[result["자치구"] == gu]

    if parking_type != "전체":
        result = result[result["주차장종류"] == parking_type]

    if fee_type != "전체":
        result = result[result["무료여부"] == fee_type]

    # -------------------
    # 요금 계산 함수
    # -------------------
    def calc_fee(row):

        if row["무료여부"] == "무료":
            return 0

        base_fee = row["기본요금"]
        base_time = row["기본시간"]
        add_fee = row["추가요금"]
        add_time = row["추가시간"]

        if add_time == 0:
            return base_fee

        if parking_time <= base_time:
            return base_fee

        extra = parking_time - base_time
        count = math.ceil(extra / add_time)

        return base_fee + count * add_fee

    result["예상요금"] = result.apply(calc_fee, axis=1)

    # 정렬 (싼 순)
    result = result.sort_values("예상요금")

    st.header("검색 결과")
    st.dataframe(result)

    if len(result) > 0:

        # -------------------
        # 최저가
        # -------------------
        cheapest = result.iloc[0]

        st.success("💰 가장 저렴한 주차장")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("주차장", cheapest["주차장명"])

        with col2:
            st.metric("예상요금", f'{int(cheapest["예상요금"]):,} 원')

        # -------------------
        # TOP 3 추천
        # -------------------
        st.subheader("🏆 추천 TOP 3")
        top3 = result.head(3)
        st.dataframe(top3[["주차장명", "자치구", "예상요금"]])

        # -------------------
        # 지도 표시 (NaN 제거)
        # -------------------
        map_df = result.dropna(subset=["위도", "경도"])

        st.subheader("지도")

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df,
            get_position='[경도, 위도]',
            get_radius=120,
            get_fill_color='[255, 0, 0, 180]',
            pickable=True
        )

        view = pdk.ViewState(
            latitude=map_df["위도"].mean(),
            longitude=map_df["경도"].mean(),
            zoom=11
        )

        st.pydeck_chart(
            pdk.Deck(
                layers=[layer],
                initial_view_state=view,
                tooltip={
                    "text":
                    "주차장명: {주차장명}\n"
                    "자치구: {자치구}\n"
                    "예상요금: {예상요금}원"
                }
            )
        )

    else:
        st.warning("검색 결과가 없습니다.")

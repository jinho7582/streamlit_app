import streamlit as st
import pandas as pd
import pydeck as pdk

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

    st.success("파일 업로드 완료!")

    st.subheader("원본 데이터")
    st.dataframe(df)

    st.sidebar.header("검색 조건")

    gu = st.sidebar.selectbox(
        "자치구 선택",
        ["전체"] + sorted(df["자치구"].unique().tolist())
    )

    parking_type = st.sidebar.selectbox(
        "주차장 종류",
        ["전체"] + sorted(df["주차장종류"].unique().tolist())
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

    if gu != "전체":
        result = result[result["자치구"] == gu]

    if parking_type != "전체":
        result = result[result["주차장종류"] == parking_type]

    if fee_type != "전체":
        result = result[result["무료여부"] == fee_type]

    def calc_fee(row):

        if row["무료여부"] == "무료":
            return 0

        base_fee = row["기본요금"]
        base_time = row["기본시간"]

        add_fee = row["추가요금"]
        add_time = row["추가시간"]

        if parking_time <= base_time:
            return base_fee

        extra = parking_time - base_time

        count = (extra + add_time - 1) // add_time

        return base_fee + count * add_fee

    result["예상요금"] = result.apply(calc_fee, axis=1)

    st.header("검색 결과")

    st.dataframe(result)

    if len(result) > 0:

        cheapest = result.loc[result["예상요금"].idxmin()]

        st.success("💰 가장 저렴한 주차장")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("주차장", cheapest["주차장명"])

        with col2:
            st.metric("예상요금", f'{cheapest["예상요금"]:,} 원')

        st.subheader("지도")

        layer = pdk.Layer(
            "ScatterplotLayer",
            data=result,
            get_position='[경도, 위도]',
            get_radius=120,
            get_fill_color='[255,0,0,180]',
            pickable=True
        )

        view = pdk.ViewState(
            latitude=result["위도"].mean(),
            longitude=result["경도"].mean(),
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

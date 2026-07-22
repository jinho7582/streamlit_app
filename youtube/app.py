import streamlit as st

from utils.youtube_api import get_video_id, YoutubeCommentCollector
from utils.text_processing import extract_keywords
from utils.visualization import (
    keyword_bar_chart,
    comment_length_chart,
    create_wordcloud
)
from utils.gpt_summary import analyze_comments
from utils.github_secret import get_youtube_key, get_openai_key


st.set_page_config(
    page_title="YouTube 댓글 분석기",
    page_icon="📺",
    layout="wide"
)


st.title("📺 YouTube 댓글 분석기")

st.markdown(
    """
    유튜브 댓글을 수집하고  
    AI와 텍스트 분석을 이용해 시청자 의견을 분석합니다.
    """
)


youtube_url = st.text_input(
    "유튜브 영상 링크 입력"
)


comment_count = st.slider(
    "수집할 댓글 수",
    min_value=100,
    max_value=1000,
    value=500
)


if st.button("🔍 댓글 분석 시작"):

    if not youtube_url:
        st.warning("유튜브 링크를 입력하세요.")
        st.stop()


    with st.spinner("댓글 수집 중..."):

        youtube_key = get_youtube_key()

        video_id = get_video_id(
            youtube_url
        )

        collector = YoutubeCommentCollector(
            youtube_key
        )

        comments_df = collector.get_comments(
            video_id,
            comment_count
        )


    if len(comments_df)==0:
        st.error("댓글을 찾을 수 없습니다.")
        st.stop()


    st.success(
        f"{len(comments_df)}개의 댓글 수집 완료"
    )


    comments = (
        comments_df["comment"]
        .tolist()
    )


    # -------------------------
    # 형태소 분석
    # -------------------------

    with st.spinner("텍스트 분석 중..."):

        keywords = extract_keywords(
            comments
        )


    # -------------------------
    # 키워드 분석
    # -------------------------

    st.subheader(
        "🔥 주요 키워드 TOP20"
    )

    fig = keyword_bar_chart(
        keywords
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


    # -------------------------
    # 워드클라우드
    # -------------------------

    st.subheader(
        "☁️ 한글 워드클라우드"
    )

    wc_image = create_wordcloud(
        keywords
    )

    st.image(
        wc_image,
        use_container_width=True
    )


    # -------------------------
    # 댓글 길이
    # -------------------------

    st.subheader(
        "📊 댓글 길이 분석"
    )

    fig2 = comment_length_chart(
        comments_df
    )

    st.plotly_chart(
        fig2,
        use_container_width=True
    )


    # -------------------------
    # GPT 분석
    # -------------------------

    st.subheader(
        "🤖 AI 댓글 분석"
    )


    openai_key = get_openai_key()


    if openai_key:

        with st.spinner(
            "AI 분석 생성 중..."
        ):

            result = analyze_comments(
                comments,
                openai_key
            )

        st.write(
            result
        )

    else:

        st.info(
            "OpenAI API Key가 없어 AI 분석은 건너뜁니다."
        )


    # 원본 댓글 표시

    with st.expander(
        "수집된 댓글 보기"
    ):

        st.dataframe(
            comments_df,
            use_container_width=True
        )

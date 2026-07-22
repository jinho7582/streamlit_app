import streamlit as st
import pandas as pd
import re
import io
from collections import Counter

import plotly.express as px

from googleapiclient.discovery import build

from konlpy.tag import Okt

from wordcloud import WordCloud
import matplotlib.pyplot as plt

from openai import OpenAI



# ==============================
# Streamlit 설정
# ==============================

st.set_page_config(
    page_title="YouTube 댓글 분석기",
    page_icon="📺",
    layout="wide"
)



# ==============================
# API KEY
# ==============================

def get_secret(key):

    try:
        return st.secrets[key]

    except:

        return None



# ==============================
# YouTube URL 처리
# ==============================

def get_video_id(url):

    patterns = [

        r"youtube\.com/watch\?v=([^&]+)",

        r"youtu\.be/([^?]+)",

        r"youtube\.com/embed/([^?]+)"

    ]


    for p in patterns:

        result = re.search(
            p,
            url
        )

        if result:

            return result.group(1)


    return None



# ==============================
# YouTube 댓글 수집
# ==============================

def get_comments(
    api_key,
    video_id,
    limit=500
):


    youtube = build(

        "youtube",
        "v3",
        developerKey=api_key

    )


    comments=[]


    request = youtube.commentThreads().list(

        part="snippet",

        videoId=video_id,

        maxResults=100,

        textFormat="plainText"

    )


    while request and len(comments)<limit:


        response=request.execute()


        for item in response.get(
            "items",
            []
        ):


            data = (

                item["snippet"]
                ["topLevelComment"]
                ["snippet"]

            )


            text=data.get(
                "textDisplay",
                ""
            )


            if text:

                comments.append(text)



            if len(comments)>=limit:

                break



        request = youtube.commentThreads().list_next(

            request,

            response

        )


    return list(
        set(comments)
    )
# ==============================
# 한국어 형태소 분석
# ==============================

okt = Okt()


STOPWORDS = {

    "영상",
    "댓글",
    "진짜",
    "너무",
    "정말",
    "그냥",
    "좋다",
    "좋아요",
    "감사",
    "감사합니다",
    "하다",
    "되다",
    "있다",
    "없다",
    "같다",
    "이번",
    "저",
    "것",
    "수",
    "좀"

}



def clean_text(text):

    text = re.sub(
        r"https?://\S+",
        "",
        text
    )

    text = re.sub(
        r"[^가-힣\s]",
        "",
        text
    )

    return text.strip()




def extract_keywords(
    comments,
    top_n=20
):

    words=[]


    for comment in comments:


        text = clean_text(
            comment
        )


        nouns = okt.nouns(
            text
        )


        for noun in nouns:


            if len(noun)>=2 and noun not in STOPWORDS:

                words.append(
                    noun
                )


    counter = Counter(
        words
    )


    return counter.most_common(
        top_n
    )



# ==============================
# 워드클라우드
# ==============================


def make_wordcloud(
    keywords
):


    data = dict(
        keywords
    )


    wc = WordCloud(

        font_path="assets/NanumGothic.ttf",

        background_color="white",

        width=1000,

        height=600,

        max_words=100

    )


    image = wc.generate_from_frequencies(
        data
    )


    fig = plt.figure(
        figsize=(10,6)
    )


    plt.imshow(
        image,
        interpolation="bilinear"
    )

    plt.axis(
        "off"
    )


    buffer = io.BytesIO()


    plt.savefig(

        buffer,

        format="png",

        bbox_inches="tight"

    )


    plt.close()


    buffer.seek(0)


    return buffer




# ==============================
# 키워드 그래프
# ==============================


def keyword_chart(
    keywords
):


    df=pd.DataFrame(

        keywords,

        columns=[
            "단어",
            "횟수"
        ]

    )


    df=df.sort_values(
        "횟수"
    )


    fig=px.bar(

        df,

        x="횟수",

        y="단어",

        orientation="h",

        color="횟수",

        title="댓글 키워드 TOP20"

    )


    return fig




# ==============================
# 댓글 길이 분석
# ==============================


def length_chart(
    comments
):


    df=pd.DataFrame(
        {
            "길이":[
                len(x)
                for x in comments
            ]
        }
    )


    fig=px.histogram(

        df,

        x="길이",

        title="댓글 길이 분포"

    )


    return fig
# ==============================
# GPT 댓글 분석
# ==============================

def gpt_analysis(
    comments,
    api_key
):

    if not api_key:
        return "OpenAI API Key가 없습니다."


    client = OpenAI(
        api_key=api_key
    )


    sample = comments[:200]


    text="\n".join(
        [
            "- " + c
            for c in sample
        ]
    )


    prompt=f"""
아래는 유튜브 영상 댓글이다.

댓글을 분석해서 한국어로 정리해줘.

분석 항목:

1. 댓글 전체 요약
2. 사람들이 가장 많이 언급한 내용
3. 긍정적인 반응
4. 불만 또는 개선 의견
5. 시청자가 중요하게 보는 요소
6. 영상에 대한 종합 인사이트


댓글:

{text}
"""


    response=client.chat.completions.create(

        model="gpt-4.1-mini",

        messages=[

            {
                "role":"system",
                "content":
                "너는 유튜브 댓글 분석 전문가다."
            },

            {
                "role":"user",
                "content":prompt
            }

        ],

        temperature=0.3

    )


    return (
        response
        .choices[0]
        .message
        .content
    )




# ==============================
# Streamlit UI
# ==============================


st.title(
    "📺 YouTube 댓글 분석기"
)


st.write(
    "유튜브 댓글을 분석하여 키워드, 워드클라우드, AI 인사이트를 제공합니다."
)



url = st.text_input(
    "유튜브 영상 링크"
)



count = st.slider(

    "분석할 댓글 개수",

    100,

    1000,

    500

)



if st.button(
    "🔍 댓글 분석 시작"
):


    youtube_key = get_secret(
        "YOUTUBE_API_KEY"
    )


    if not youtube_key:

        st.error(
            "YouTube API Key를 Streamlit Secrets에 추가하세요."
        )

        st.stop()



    video_id=get_video_id(
        url
    )


    if not video_id:

        st.error(
            "유효한 유튜브 링크가 아닙니다."
        )

        st.stop()



    with st.spinner(
        "댓글 수집 중..."
    ):


        comments=get_comments(

            youtube_key,

            video_id,

            count

        )



    if len(comments)==0:

        st.warning(
            "댓글이 없습니다."
        )

        st.stop()



    st.success(
        f"{len(comments)}개 댓글 분석 완료"
    )



    # ------------------
    # 키워드
    # ------------------

    keywords=extract_keywords(
        comments
    )


    st.subheader(
        "🔥 주요 키워드 TOP20"
    )


    st.plotly_chart(

        keyword_chart(
            keywords
        ),

        use_container_width=True

    )



    # ------------------
    # 워드클라우드
    # ------------------

    st.subheader(
        "☁️ 한글 워드클라우드"
    )


    wc=make_wordcloud(
        keywords
    )


    st.image(
        wc
    )



    # ------------------
    # 댓글 길이
    # ------------------

    st.subheader(
        "📊 댓글 길이 분석"
    )


    st.plotly_chart(

        length_chart(
            comments
        ),

        use_container_width=True

    )



    # ------------------
    # GPT 분석
    # ------------------

    st.subheader(
        "🤖 AI 댓글 분석"
    )


    openai_key=get_secret(
        "OPENAI_API_KEY"
    )


    if openai_key:


        with st.spinner(
            "AI 분석 생성 중..."
        ):


            result=gpt_analysis(

                comments,

                openai_key

            )


        st.write(
            result
        )


    else:

        st.info(
            "OPENAI_API_KEY가 없어 AI 분석을 건너뜁니다."
        )



    # ------------------
    # 댓글 확인
    # ------------------

    with st.expander(
        "원본 댓글 보기"
    ):

        st.dataframe(

            pd.DataFrame(
                {
                    "댓글":comments
                }
            ),

            use_container_width=True

        )

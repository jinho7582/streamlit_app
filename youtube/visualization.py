import plotly.express as px
import pandas as pd

from wordcloud import WordCloud
import matplotlib.pyplot as plt

from PIL import Image
import io



# 한글 폰트 경로
FONT_PATH = "assets/NanumGothic.ttf"




def keyword_bar_chart(
    keywords
):

    """
    키워드 TOP20 막대그래프
    """

    df = pd.DataFrame(
        keywords,
        columns=[
            "keyword",
            "count"
        ]
    )


    df = df.sort_values(
        "count",
        ascending=True
    )


    fig = px.bar(

        df,

        x="count",

        y="keyword",

        orientation="h",

        title="댓글 주요 키워드 TOP20",

        color="count"

    )


    fig.update_layout(

        height=600,

        yaxis_title="",

        xaxis_title="등장 횟수"

    )


    return fig





def comment_length_chart(
    df
):

    """
    댓글 길이 분포
    """


    data = df.copy()


    data["length"] = (
        data["comment"]
        .astype(str)
        .apply(len)
    )


    fig = px.histogram(

        data,

        x="length",

        nbins=30,

        title="댓글 길이 분포"

    )


    fig.update_layout(

        xaxis_title="글자 수",

        yaxis_title="댓글 수"

    )


    return fig





def create_wordcloud(
    keywords
):

    """
    한글 워드클라우드 생성

    keywords:
        [
          ("단어", 빈도),
          ...
        ]

    return:
        이미지 bytes
    """


    word_dict = dict(
        keywords
    )


    wc = WordCloud(

        font_path=FONT_PATH,

        background_color="white",

        width=1200,

        height=700,

        max_words=100,

        colormap="viridis"

    )


    image = wc.generate_from_frequencies(
        word_dict
    )



    fig = plt.figure(
        figsize=(12,7)
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

        bbox_inches="tight",

        dpi=200

    )


    plt.close()



    buffer.seek(0)


    return buffer

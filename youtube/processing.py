from konlpy.tag import Okt
from collections import Counter
import re


okt = Okt()


# 분석에서 제외할 의미 없는 단어
STOPWORDS = {

    "하다",
    "되다",
    "있다",
    "없다",
    "이다",
    "같다",
    "그냥",
    "진짜",
    "너무",
    "정말",
    "영상",
    "댓글",
    "이번",
    "저번",
    "처음",
    "보기",
    "것",
    "수",
    "때",
    "더",
    "좀",
    "잘",
    "많이",
    "감사",
    "감사합니다"

}



def clean_text(text):

    """
    댓글 기본 정제
    """

    if not isinstance(
        text,
        str
    ):
        return ""


    # URL 제거

    text = re.sub(
        r"https?://\S+",
        "",
        text
    )


    # 특수문자 제거

    text = re.sub(
        r"[^가-힣a-zA-Z0-9\s]",
        "",
        text
    )


    # 여러 공백 제거

    text = re.sub(
        r"\s+",
        " ",
        text
    )


    return text.strip()





def extract_nouns(comments):

    """
    댓글 리스트에서
    명사 추출
    """

    nouns=[]


    for comment in comments:


        cleaned = clean_text(
            comment
        )


        if not cleaned:
            continue



        words = okt.nouns(
            cleaned
        )


        for word in words:


            # 두 글자 이상만 사용

            if len(word)>=2:


                if word not in STOPWORDS:

                    nouns.append(
                        word
                    )



    return nouns





def extract_keywords(
    comments,
    top_n=20
):

    """
    키워드 빈도 분석

    return:
        Counter 객체
    """

    nouns = extract_nouns(
        comments
    )


    counter = Counter(
        nouns
    )


    return counter.most_common(
        top_n
    )

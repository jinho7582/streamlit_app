import streamlit as st
import os



def get_youtube_key():

    """
    YouTube Data API Key 가져오기

    우선순위:
    1. Streamlit Cloud Secrets
    2. 환경변수
    """


    try:

        if "YOUTUBE_API_KEY" in st.secrets:

            return st.secrets[
                "YOUTUBE_API_KEY"
            ]

    except Exception:

        pass



    key = os.getenv(
        "YOUTUBE_API_KEY"
    )


    if key:

        return key



    raise Exception(
        """
        YouTube API Key가 없습니다.

        Streamlit Cloud:
        Settings → Secrets

        에 YOUTUBE_API_KEY를 추가하세요.
        """
    )





def get_openai_key():

    """
    OpenAI API Key 가져오기
    """


    try:

        if "OPENAI_API_KEY" in st.secrets:

            return st.secrets[
                "OPENAI_API_KEY"
            ]

    except Exception:

        pass



    key = os.getenv(
        "OPENAI_API_KEY"
    )


    return key

from openai import OpenAI



def analyze_comments(
    comments,
    api_key
):

    """
    댓글 데이터를 GPT에게 전달하여
    요약 및 인사이트 생성
    """

    client = OpenAI(
        api_key=api_key
    )


    # 너무 많은 댓글 입력 방지
    # 최대 200개 사용

    sample_comments = comments[:200]


    joined_comments = "\n".join(
        [
            f"- {c}"
            for c in sample_comments
        ]
    )


    prompt = f"""
아래는 유튜브 영상 댓글 목록이다.

댓글을 분석해서 다음 내용을 한국어로 작성해줘.

1. 댓글 전체 요약
2. 사람들이 가장 많이 언급한 내용
3. 긍정적인 반응 및 칭찬 포인트
4. 개선 요구사항 또는 불만
5. 시청자가 중요하게 생각하는 요소
6. 영상에 대한 종합 인사이트

댓글:

{joined_comments}
"""


    response = client.chat.completions.create(

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

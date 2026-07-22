from googleapiclient.discovery import build
import pandas as pd
import re


def get_video_id(url):

    """
    유튜브 URL에서 영상 ID 추출
    """

    patterns = [
        r"youtube\.com/watch\?v=([^&]+)",
        r"youtu\.be/([^?]+)",
        r"youtube\.com/embed/([^?]+)"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            url
        )

        if match:
            return match.group(1)


    # 이미 ID만 입력한 경우
    if len(url)==11:
        return url


    raise ValueError(
        "유효하지 않은 유튜브 링크입니다."
    )



class YoutubeCommentCollector:


    def __init__(self, api_key):

        self.youtube = build(
            "youtube",
            "v3",
            developerKey=api_key
        )



    def get_comments(
        self,
        video_id,
        max_comments=500
    ):

        """
        유튜브 댓글 수집

        return:
            pandas DataFrame

        columns:
            author
            comment
            likes
            published
        """


        comments=[]


        request = self.youtube.commentThreads().list(

            part="snippet",

            videoId=video_id,

            maxResults=100,

            textFormat="plainText"

        )



        while request and len(comments)<max_comments:


            response = request.execute()



            for item in response.get(
                "items",
                []
            ):


                snippet = (
                    item["snippet"]
                    ["topLevelComment"]
                    ["snippet"]
                )


                comments.append({

                    "author":
                        snippet.get(
                            "authorDisplayName",
                            ""
                        ),


                    "comment":
                        snippet.get(
                            "textDisplay",
                            ""
                        ),


                    "likes":
                        snippet.get(
                            "likeCount",
                            0
                        ),


                    "published":
                        snippet.get(
                            "publishedAt",
                            ""
                        )

                })



                if len(comments)>=max_comments:
                    break



            request = (
                self.youtube
                .commentThreads()
                .list_next(
                    request,
                    response
                )
            )



        df = pd.DataFrame(
            comments
        )


        if len(df)>0:

            # 중복 댓글 제거

            df = df.drop_duplicates(
                subset=[
                    "comment"
                ]
            )


            # 빈 댓글 제거

            df = df[
                df["comment"]
                .str.strip()
                .astype(bool)
            ]


            df = df.reset_index(
                drop=True
            )


        return df

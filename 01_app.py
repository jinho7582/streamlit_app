import streamlit as st
import requests

st.set_page_config(
    page_title="🍽️ 오늘의 날씨 음식 추천",
    page_icon="🍜",
    layout="wide"
)

API_KEY = st.secrets["OPENWEATHER_API_KEY"]


# 음식 데이터
food_data = {
    "hot": {
        "name": "냉면",
        "image": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=800",
        "calories": "520 kcal",
        "nutrition": {
            "탄수화물": "85 g",
            "단백질": "18 g",
            "지방": "7 g"
        }
    },
    "cold": {
        "name": "김치찌개",
        "image": "https://images.unsplash.com/photo-1604908177522-402fe4f68f1b?w=800",
        "calories": "610 kcal",
        "nutrition": {
            "탄수화물": "30 g",
            "단백질": "35 g",
            "지방": "28 g"
        }
    },
    "rain": {
        "name": "파전",
        "image": "https://images.unsplash.com/photo-1604908176997-125f91c8f3d0?w=800",
        "calories": "720 kcal",
        "nutrition": {
            "탄수화물": "62 g",
            "단백질": "18 g",
            "지방": "45 g"
        }
    },
    "snow": {
        "name": "어묵탕",
        "image": "https://images.unsplash.com/photo-1544025162-d76694265947?w=800",
        "calories": "430 kcal",
        "nutrition": {
            "탄수화물": "18 g",
            "단백질": "32 g",
            "지방": "15 g"
        }
    },
    "normal": {
        "name": "비빔밥",
        "image": "https://images.unsplash.com/photo-1512058564366-18510be2db19?w=800",
        "calories": "580 kcal",
        "nutrition": {
            "탄수화물": "74 g",
            "단백질": "22 g",
            "지방": "18 g"
        }
    }
}


def get_weather(city):

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=kr"

    response = requests.get(url)

    if response.status_code != 200:
        return None

    return response.json()


def recommend_food(temp, weather):

    weather = weather.lower()

    if "rain" in weather:
        return food_data["rain"]

    if "snow" in weather:
        return food_data["snow"]

    if temp >= 28:
        return food_data["hot"]

    elif temp <= 10:
        return food_data["cold"]

    else:
        return food_data["normal"]


st.title("🍽️ 오늘의 날씨 음식 추천")

city = st.text_input(
    "도시를 입력하세요",
    value="Seoul"
)

if st.button("추천받기"):

    weather = get_weather(city)

    if weather is None:
        st.error("도시를 찾을 수 없습니다.")
        st.stop()

    temp = weather["main"]["temp"]
    weather_main = weather["weather"][0]["main"]
    weather_desc = weather["weather"][0]["description"]

    food = recommend_food(temp, weather_main)

    st.success(
        f"현재 {city}의 날씨는 **{weather_desc}**, 기온은 **{temp:.1f}℃** 입니다."
    )

    col1, col2 = st.columns([2, 2])

    with col1:

        st.image(food["image"], use_container_width=True)

    with col2:

        st.header(food["name"])

        st.subheader("🔥 칼로리")

        st.write(food["calories"])

        st.subheader("🥗 영양성분")

        st.table(food["nutrition"])

        st.info("오늘의 날씨에 잘 어울리는 음식입니다 😊")

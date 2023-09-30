import streamlit as st
import openai
import os
import ics
from ics import Calendar, Event
from datetime import datetime
import base64
import re
import pandas as pd
import requests


st.set_page_config(
    page_title="Plan the perfect holiday", 
    page_icon=None, 
    layout="centered", 
    initial_sidebar_state="auto"
    
 )


# Title and subtitle in HTML
st.markdown(
  """ 
  <div style ='text-align:center;'>
        <h1>Holiday Planner</h1>
        <h2 style ='font-size:14px;'>Let's plan your perfect holidays</h2>
  </div>
  """,
  unsafe_allow_html = True
)

# Making space
st.write(" ")
st.write(" ")
st.write(" ")


openai.api_key = st.secrets["OPENAI_API_KEY"]
open_weather_api_key = st.secrets["OPENWEATHER_API_KEY"]

@st.cache
def open_ai_plan_initial(city, n_days):
    open_ai_response = openai.Completion.create(
    model="text-davinci-003",
    prompt=f"What should I do on holliday in {city} during {n_days} days. Give me each activity in its on line.And add the lattitude and longitude in brackets, just the numbers.",
    max_tokens=250,
    temperature=0,
    top_p = 0.3
    )

    text_resume = open_ai_response['choices'][0]['text']
    text_resume = text_resume.replace("\n\n","")
    text_resume = text_resume.replace("° N", "").replace("° W", "").replace("° E", "").replace("° S", "").replace("°", "")
    return text_resume


@st.cache
def create_download_link(ics_content, filename):
    b64 = base64.b64encode(ics_content.encode()).decode()  # encode to base64
    href = f'<a href="data:text/calendar;base64,{b64}" download="{filename}">Download your calendar event</a>'
    return href


# Creating columns to have the text input side by side
city_col, n_days_col = st.columns(2)

city = city_col.text_input("Where are you going?")
n_days = n_days_col.text_input("How many days?")

if city != "" and n_days != "":

  #Options to select activities, check the weather or book a hotel.
  if "feature" not in st.session_state:
    st.session_state["feature"] = ""

  #aligning the columns  
  left_spacer, activities, center_spacer, weather, right_spacer, hotels = st.columns([1, 2, 1, 2, 1, 2])
  activities_button = activities.button("Find some cool things to do")
  weather_button = weather.button("Check the weather")
  hotels_button = hotels.button("Find an accomodation")

  
  ##Activities selection feature##
  if activities_button:
    st.session_state["feature"] = "activities"
  if weather_button:
    st.session_state["feature"] = "weather"
  if hotels_button:
    st.session_state["feature"] = "hotels"

  if st.session_state["feature"] == "activities":

    if "First Plan" not in st.session_state:
        st.session_state["First Plan"] = ""
    generate_plan_button = st.button("Generate Plan")
    if generate_plan_button:
        st.session_state["First Plan"] = "Generated"

    if st.session_state["First Plan"] == "Generated":
        st.session_state["reco"] = ""
        last_open_ai_response = open_ai_plan_initial(city,n_days)
        last_reco = re.sub(r'\(.*?\)', '', last_open_ai_response)
        last_reco = re.sub(r'\(.*$', '', last_reco)
        st.session_state["reco"] = last_reco
        st.write(st.session_state["reco"])
        st.write(" ")
        st.write(" ")

        ## View on Maps and Add to calendar##
        st.write(" ")
        st.write(" ")
        st.markdown("<div style ='text-align: center;'>Add a recommended activity to your calendar</div>",unsafe_allow_html=True)
        ###View on maps##
        #creating a dataframe for maps
        dict_coordinates = {}
        last_reco_full = last_open_ai_response.strip().split('\n')
    
        for reco in last_reco_full:
            if reco:
                activity, coordinates = re.findall(r"(.*?)(\(.*|$)", reco)[0]
                # remove leading/trailing whitespaces and digits from the description
                key = re.sub(r'\d+\. ', '', activity).strip()
                # remove brackets from coordinates
                value = coordinates.strip("()")

                dict_coordinates[key] = value
    
        #Getting the list of recommended activities and creating a selectbox
        activities = list(dict_coordinates.keys())
        #Select the activity desired
        selected_recommendation = st.selectbox("Select an activity",activities)

        #Output the selected activity on maps
        maps_data = [{"Activity": key, "latitude": float(value.split(", ")[0]), "longitude": float(value.split(", ")[1])} 
        for key, value in dict_coordinates.items()]
        maps_df_all = pd.DataFrame(maps_data)  
        maps_df_selected = pd.DataFrame(maps_df_all[maps_df_all["Activity"]==selected_recommendation])
        st.map(maps_df_selected)

        ###Add to calendar###      
        selected_date = st.date_input("Select a date for the activity")
        # Create a new .ics calendar events
        if st.button("Add to calendar"):
            c = Calendar()
            e = Event()
            e.name = selected_recommendation
            e.begin = datetime.combine(selected_date, datetime.min.time()) # use selected date with minimum time
            c.events.add(e)

            st.markdown(create_download_link(str(c), "recommendation.ics"), unsafe_allow_html=True)

  elif st.session_state["feature"] == "weather":
    geo_response = requests.get(f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=5&appid={open_weather_api_key}").json()
    for item in geo_response:
        lat = item['lat']
        lon = item['lon']
    weather_response = requests.get(f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=current,minutely,hourly,alerts&appid={open_weather_api_key}").json()
    for day in weather_response["daily"]:
        date = datetime.fromtimestamp(day['dt']).strftime('%Y-%m-%d')
        morning_temp = round(day['temp']['morn'] -273.15)
        day_temp = round(day['temp']['day'] -273.15)
        evening_temp = round(day['temp']['eve'] -273.15)
        main_weather = day['weather'][0]['main']
        weather_emojis = {
                'Rain': ":rain_cloud:",
                'Clouds': "sun_behind_cloud",
                'Sun': ":mostly_sunny:"
                }

        st.write(f"Day: {date}")
        # Display the image and temperatures in columns
        col1, col2 = st.columns([1, 2])
        with col1:
            emoji = (weather_emojis[f"{main_weather}"])
            emoji_size = 50
            st.markdown(
                f'<span style="font-size:{emoji_size}px">{emoji}</span>',
                unsafe_allow_html=True
                )
        with col2:
            st.write(f"Morning Temperature: {morning_temp} °C")
            st.write(f"Day Temperature: {day_temp} °C")
            st.write(f"Evening Temperature: {evening_temp} °C")
        st.write(f"Weather Main: {main_weather}")
        st.write("---")

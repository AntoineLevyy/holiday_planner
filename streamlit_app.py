import streamlit as st
import openai
import os
import ics
from ics import Calendar, Event
from datetime import datetime
import base64
import re



st.set_page_config(
    page_title="Plan the perfect holiday", 
    page_icon=None, 
    layout="centered", 
    initial_sidebar_state="auto"
    
 )

# Setting the page to darkmode
dark = '''
<style>
    .stApp {
    background-color: black;
    }
</style>
'''
st.markdown(dark, unsafe_allow_html=True)

# Title and subtitle in HTML
st.markdown(
  """ 
  <div style ='text-align:center;'>
        <h1>Holiday Planner</h1>
        <h2 style ='font-size:14px;'>Let's plan your perfect holiday activities</h2>
  </div>
  """,
  unsafe_allow_html = True
)

# Making space
st.write(" ")
st.write(" ")
st.write(" ")

# Creating columns to have the text input side by side
city_col, n_days_col = st.columns(2)

city = city_col.text_input("Where are you going?")
n_days = n_days_col.text_input("How many days?")


@st.cache(allow_output_mutation=True)
def open_ai_plan_initial(city, n_days):
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    open_ai_response = openai.Completion.create(
    model="text-davinci-003",
    prompt=f"What should I do on holliday in {city} during {n_days} days. Give me each activity in its on line.",
    max_tokens=250,
    temperature=0,
    top_p = 0.3
    )

    text_resume = open_ai_response['choices'][0]['text']
    text_resume = text_resume.replace("\n\n","")
    return text_resume

@st.cache(allow_output_mutation=True)
def open_ai_plan_edited(city, n_days, last_reco,more,less):
    openai.api_key = st.secrets["OPENAI_API_KEY"]
    open_ai_response = openai.Completion.create(
    model="text-davinci-003",
    prompt=f"Can you edit my  activities for {city} where I am spending {n_days} days. The last time you gave this {last_reco}, but actually I would like a new list with more  {more} and less {less}. Give me each activity in its on line.",
    max_tokens=250,
    temperature=0,
    top_p = 0.3
    )

    recommendations = open_ai_response['choices'][0]['text']
    recommendations = recommendations.replace("\n\n","")
    return recommendations

@st.cache(allow_output_mutation=True)
def create_download_link(ics_content, filename):
    b64 = base64.b64encode(ics_content.encode()).decode()  # encode to base64
    href = f'<a href="data:text/calendar;base64,{b64}" download="{filename}">Download your calendar event</a>'
    return href


activities = ["","museums", "sightseeing", "partying", "restaurants", "shopping"]

if city != "" and n_days != "":
  st.button("Generate Plan")
  if st.button:
    st.session_state["reco"] = ""
    last_reco = open_ai_plan_initial(city,n_days)
    st.session_state["reco"] = last_reco
    st.write(st.session_state["reco"])

    ## Add to calendar##
      # change reco to list without numbers.
    recommendations_1 = last_reco.split(". ")
    recommendations_1 = [re.sub(r'\s\d+$', '', recommendation) for recommendation in recommendations_1 if recommendation]
    st.write(" ")
    st.write(" ")
    st.markdown("<div style ='text-align: center;'>Add a recommended activity to your calendar</div>",unsafe_allow_html=True)
    selected_recommendation = st.selectbox("Select an activity",recommendations_1[1:])
    selected_date = st.date_input("Select a date for the activity")
    # Create a new .ics calendar events
    if st.button("Add to calendar"):
        c = Calendar()
        e = Event()
        e.name = selected_recommendation
        e.begin = datetime.combine(selected_date, datetime.min.time()) # use selected date with minimum time
        c.events.add(e)

        st.markdown(create_download_link(str(c), "recommendation.ics"), unsafe_allow_html=True)



    ## Allowing for a change in recommendation
    st.write(" ")
    st.markdown("<div style='text-align: center;'>Make some changes to the recommendations</div>", unsafe_allow_html=True)
    more_col, less_col = st.columns(2)
    more_col.write(" ") #this allows for the selectbox to show below the col placeholder
    more = more_col.selectbox("More of", activities)
    less_col.write(" ") #this allows for the selectbox to show below the col placeholder
    less = less_col.selectbox("Less of", activities)
    if more != "" and less != "":
        st.button("Edit Plan")
        new_reco = open_ai_plan_edited(city, n_days, last_reco, more, less)
        st.session_state["reco"] = new_reco
        st.write(st.session_state["reco"])
         ## Add to calendar##
         # change reco to list without numbers.
        recommendations_2 = new_reco.split(". ")
        recommendations_2 = [re.sub(r'\s\d+$', '', recommendation) for recommendation in recommendations_2 if recommendation]
        st.write(recommendations_2[2])
        st.write("Add a recommended activity to your calender")
        selected_recommendation_2 = st.selectbox("Select an activity",recommendations_2[1:])
        selected_date_two = st.date_input("Select a date for the new activity")
        # Create a new .ics calendar event
        if st.button("Add new activity to calendar"):
            c = Calendar()
            e = Event()
            e.name = selected_recommendation_2
            e.begin = datetime.combine(selected_date_two, datetime.min.time()) # use selected date with minimum time
            c.events.add(e)

            st.markdown(create_download_link(str(c), "recommendation.ics"), unsafe_allow_html=True)

    



   
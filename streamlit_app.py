import streamlit as st
import openai
import os
import ics
from ics import Calendar, Event
from datetime import datetime
import base64
import re
import pandas as pd


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

openai.api_key = st.secrets["OPENAI_API_KEY"]

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
def open_ai_plan_edited(city, n_days, last_reco,more,less):
    open_ai_response = openai.Completion.create(
    model="text-davinci-003",
    prompt=f"What should I do on holliday in {city} during {n_days} days. The last time you gave this {last_reco}. I want more {more} and less {less} please format your answer exactly as you did here {open_ai_plan_initial} including the latitude and longitude numbers.",
    max_tokens=250,
    temperature=0,
    top_p = 0.3
    )

    recommendations = open_ai_response['choices'][0]['text']
    recommendations = recommendations.replace("\n\n","")
    recommendations = recommendations.replace("° N", "").replace("° W", "").replace("° E", "").replace("° S", "").replace("°", "")
    return recommendations

@st.cache
def create_download_link(ics_content, filename):
    b64 = base64.b64encode(ics_content.encode()).decode()  # encode to base64
    href = f'<a href="data:text/calendar;base64,{b64}" download="{filename}">Download your calendar event</a>'
    return href


activity_types = ["","museums", "sightseeing", "partying", "restaurants", "shopping"]

if city != "" and n_days != "":
  st.button("Generate Plan")
  if st.button:
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



    ## Allowing for a change in recommendation
    st.write(" ")
    st.markdown("<div style='text-align: center;'>Make some changes to the recommendations</div>", unsafe_allow_html=True)
    more_col, less_col = st.columns(2)
    more_col.write(" ") #this allows for the selectbox to show below the col placeholder
    more = more_col.selectbox("More of", activity_types)
    less_col.write(" ") #this allows for the selectbox to show below the col placeholder
    less = less_col.selectbox("Less of", activity_types)
    if more != "" and less != "":
        st.button("Edit Plan")
        new_reco_full = open_ai_plan_edited(city, n_days, last_reco, more, less)
        new_reco = re.sub(r'\(.*?\)', '', new_reco_full)
        new_reco = re.sub(r'\(.*$', '', new_reco)
        st.session_state["reco"] = new_reco
        st.write(st.session_state["reco"])
        st.write(" ")
        st.write(" ")

         ## View on maps and Add to calendar##
         #creating a dataframe for maps
        new_dict_coordinates = {}
        new_reco_full = new_reco_full.strip().split('\n')

        for reco in new_reco_full:
          if reco:
              activity, coordinates = re.findall(r"(.*?)(\(.*|$)", reco)[0]
              # remove leading/trailing whitespaces and digits from the description
              key = re.sub(r'\d+\. ', '', activity).strip()
              # remove brackets from coordinates
              value = coordinates.strip("()")

              new_dict_coordinates[key] = value
        
        #Getting the list of recommended activities and creating a selectbox
        new_activities = list(new_dict_coordinates.keys())
        #Select the activity desired
        new_selected_recommendation = st.selectbox("Select a new activity",new_activities)

        #Output the selected activity on maps
        new_maps_data = [{"Activity": key, "latitude": float(value.split(", ")[0]), "longitude": float(value.split(", ")[1])} 
        for key, value in new_dict_coordinates.items()]
        new_maps_df_all = pd.DataFrame(new_maps_data)  
        new_maps_df_selected = pd.DataFrame(new_maps_df_all[new_maps_df_all["Activity"]==new_selected_recommendation])
        st.map(new_maps_df_selected) 


        ##Add to calendar###      
        new_selected_date = st.date_input("Select a date for the new activity")
        # Create a new .ics calendar event
        if st.button("Add new activity to calendar"):
            c = Calendar()
            e = Event()
            e.name = new_selected_recommendation
            e.begin = datetime.combine(new_selected_date, datetime.min.time()) # use selected date with minimum time
            c.events.add(e)

            st.markdown(create_download_link(str(c), "recommendation.ics"), unsafe_allow_html=True)

    



   
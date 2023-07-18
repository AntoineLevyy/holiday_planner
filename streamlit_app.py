import streamlit as st
import openai
from environ import OPENAI_API_KEY

st.set_page_config('dark')


city = st.text_input("Where are you going?")
n_days = st.text_input("How many days?")




def open_ai_plan_initial(city, n_days):
    openai.api_key = OPENAI_API_KEY
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

def open_ai_plan_edited(city, n_days, last_reco,more,less):
    openai.api_key = OPENAI_API_KEY
    open_ai_response = openai.Completion.create(
    model="text-davinci-003",
    prompt=f"Can you edit my  activities for {city} where I am spending {n_days} days. The last time you gave this {last_reco}, its good but I want more {more} and less {less}. Give me each activity in its on line.",
    max_tokens=250,
    temperature=0,
    top_p = 0.3
    )

    text_resume = open_ai_response['choices'][0]['text']
    text_resume = text_resume.replace("\n\n","")
    return text_resume

activities = ["","museums", "sightseeing", "partying", "restaurants", "shopping"]

if city != "" and n_days != "":
  st.button("Generate Plan")
  if st.button:
    st.session_state["reco"] = ""
    last_reco = open_ai_plan_initial(city,n_days)
    st.session_state["reco"] = last_reco
    st.write(st.session_state["reco"])
    more = st.selectbox("More of", activities)
    less = st.selectbox("Less of", activities)
    if more != "" and less != "":
        st.button("Edit Plan")
        st.session_state["reco"] = open_ai_plan_edited(city, n_days, last_reco, more, less)
        st.write(st.session_state["reco"])

    



   
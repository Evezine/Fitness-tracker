import streamlit as st
import pandas as pd
from pymongo import MongoClient
from datetime import datetime

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")  # Change this to your MongoDB connection string
db = client['fitness_tracker']  # Database name
collection = db['workouts']  # Collection name

# Function to add workout data
def add_workout(date, exercise, duration, calories):
    workout_data = {
        "date": date,
        "exercise": exercise,
        "duration": duration,
        "calories": calories
    }
    collection.insert_one(workout_data)

# Function to get all workout data
def get_workouts():
    return pd.DataFrame(list(collection.find()))

# Streamlit App
st.title("Fitness Tracker")

# Workout Input Form
with st.form("workout_form"):
    st.header("Log Your Workout")
    date = st.date_input("Date", value=datetime.today())
    exercise = st.text_input("Exercise")
    duration = st.number_input("Duration (minutes)", min_value=1)
    calories = st.number_input("Calories Burned", min_value=1)
    
    submitted = st.form_submit_button("Submit")
    if submitted:
        add_workout(date.strftime("%Y-%m-%d"), exercise, duration, calories)
        st.success("Workout logged successfully!")

# Display Logged Workouts
st.header("Your Workout Log")
workouts_df = get_workouts()
if not workouts_df.empty:
    st.dataframe(workouts_df)
else:
    st.write("No workouts logged yet.")

# Optional: Display workout statistics
if not workouts_df.empty:
    st.header("Workout Statistics")
    total_duration = workouts_df['duration'].sum()
    total_calories = workouts_df['calories'].sum()
    st.write(f"Total Workouts: {len(workouts_df)}")
    st.write(f"Total Duration: {total_duration} minutes")
    st.write(f"Total Calories Burned: {total_calories} calories")

# MongoDB Cleanup
def cleanup_db():
    collection.delete_many({})
    st.warning("All workout records have been deleted.")

if st.button("Delete All Workouts"):
    cleanup_db()

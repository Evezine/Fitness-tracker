import streamlit as st
import pandas as pd
from pymongo import MongoClient
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from hashlib import sha256  # For password hashing

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")  # Change this to your MongoDB connection string
db = client['fitness_tracker']  # Database name
collection = db['workouts']  # Collection name
reminder_collection = db['reminders']  # New collection for reminders
user_collection = db['users']  # New collection for user accounts

# Function to add user
def add_user(username, password):
    hashed_password = sha256(password.encode()).hexdigest()  # Hash the password
    user_data = {
        "username": username,
        "password": hashed_password
    }
    user_collection.insert_one(user_data)

# Function to authenticate user
def authenticate_user(username, password):
    hashed_password = sha256(password.encode()).hexdigest()
    user = user_collection.find_one({"username": username, "password": hashed_password})
    return user is not None

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

# Function to add a reminder
def add_reminder(reminder_text, reminder_time):
    reminder_data = {
        "reminder": reminder_text,
        "time": reminder_time
    }
    reminder_collection.insert_one(reminder_data)

# Function to get all reminders
def get_reminders():
    return pd.DataFrame(list(reminder_collection.find()))

# Streamlit App
st.title("Fitness Tracker")

# User Authentication
st.subheader("User Authentication")
auth_option = st.selectbox("Choose an option", ["Sign Up", "Sign In"])

if auth_option == "Sign Up":
    with st.form("signup_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign Up")
        if submitted:
            if user_collection.find_one({"username": username}):
                st.error("Username already exists.")
            else:
                add_user(username, password)
                st.success("Account created successfully! You can now sign in.")
elif auth_option == "Sign In":
    with st.form("signin_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign In")
        if submitted:
            if authenticate_user(username, password):
                st.success("Logged in successfully!")
                
                # Logged in user's workout input form
                with st.form("workout_form"):
                    st.header("Log Your Workout")
                    date = st.date_input("Date", value=datetime.today())
                    exercise = st.text_input("Exercise")
                    duration = st.number_input("Duration (minutes)", min_value=1)
                    calories = st.number_input("Calories Burned", min_value=1)

                    workout_submitted = st.form_submit_button("Submit")
                    if workout_submitted:
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

                    # Visualization
                    st.header("Workout Visualizations")

                    # Convert date column to datetime for plotting
                    workouts_df['date'] = pd.to_datetime(workouts_df['date'])

                    # Group by date for total duration and calories
                    daily_summary = workouts_df.groupby('date').agg({'duration': 'sum', 'calories': 'sum'}).reset_index()

                    # Plotting total duration over time
                    plt.figure(figsize=(10, 5))
                    plt.plot(daily_summary['date'], daily_summary['duration'], marker='o', linestyle='-', color='blue')
                    plt.title('Total Workout Duration Over Time')
                    plt.xlabel('Date')
                    plt.ylabel('Duration (minutes)')
                    plt.xticks(rotation=45)
                    plt.grid()
                    st.pyplot(plt)

                    # Plotting total calories burned over time
                    plt.figure(figsize=(10, 5))
                    plt.plot(daily_summary['date'], daily_summary['calories'], marker='o', linestyle='-', color='orange')
                    plt.title('Total Calories Burned Over Time')
                    plt.xlabel('Date')
                    plt.ylabel('Calories')
                    plt.xticks(rotation=45)
                    plt.grid()
                    st.pyplot(plt)

                    # Export Data as CSV
                    csv = workouts_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download Workouts as CSV",
                        data=csv,
                        file_name='workouts.csv',
                        mime='text/csv'
                    )

                # Reminder Input Form
                with st.form("reminder_form"):
                    st.header("Set a Reminder")
                    reminder_text = st.text_input("Reminder Text")
                    reminder_time = st.time_input("Reminder Time", value=datetime.now().time())

                    reminder_submitted = st.form_submit_button("Add Reminder")
                    if reminder_submitted:
                        reminder_datetime = datetime.combine(datetime.today(), reminder_time)
                        add_reminder(reminder_text, reminder_datetime)
                        st.success("Reminder set successfully!")

                # Display Reminders
                st.header("Your Reminders")
                reminders_df = get_reminders()
                if not reminders_df.empty:
                    st.dataframe(reminders_df)
                else:
                    st.write("No reminders set yet.")

                # MongoDB Cleanup
                def cleanup_db():
                    collection.delete_many({})
                    reminder_collection.delete_many({})
                    st.warning("All workout records and reminders have been deleted.")

                if st.button("Delete All Workouts and Reminders"):
                    cleanup_db()
            else:
                st.error("Invalid username or password.")


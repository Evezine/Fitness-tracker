import streamlit as st
import pandas as pd
from pymongo import MongoClient
from datetime import datetime
import matplotlib.pyplot as plt

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

# User authentication
def authenticate_user(username, password):
    # Check if the user exists in session state
    if username in st.session_state and st.session_state[username]['password'] == password:
        return True
    return False

def signup_user(username, password):
    if username not in st.session_state:
        st.session_state[username] = {'password': password}
        st.success("Signup successful! You can now log in.")
    else:
        st.error("Username already exists. Please choose a different username.")

# Streamlit App
st.title("Fitness Tracker")

# Session state for authentication
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# User authentication interface
if not st.session_state['authenticated']:
    st.subheader("User Authentication")
    option = st.selectbox("Select an option", ["Sign In", "Sign Up"])
    
    if option == "Sign Up":
        username = st.text_input("Choose a Username")
        password = st.text_input("Choose a Password", type='password')
        
        if st.button("Sign Up"):
            if username and password:
                signup_user(username, password)
            else:
                st.error("Please enter both username and password.")
    
    elif option == "Sign In":
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        
        if st.button("Sign In"):
            if authenticate_user(username, password):
                st.session_state['authenticated'] = True
                st.success("Logged in successfully!")
            else:
                st.error("Invalid username or password!")

# After logging in, show the workout input form
if st.session_state['authenticated']:
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

    # MongoDB Cleanup
    def cleanup_db():
        collection.delete_many({})
        st.warning("All workout records have been deleted.")

    if st.button("Delete All Workouts"):
        cleanup_db()
else:
    st.warning("Please log in to access the fitness tracker.")

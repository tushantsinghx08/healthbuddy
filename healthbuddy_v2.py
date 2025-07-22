import streamlit as st
import pandas as pd
import google.generativeai as genai
from datetime import datetime
import numpy as np

# --- Gemini API Setup ---
genai.configure(api_key="AIzaSyDbhlkB2gaFsYU4IneCCfT6Vp-vpsNQtLY")
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_weekly_plan(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Gemini Error: {e}"

# --- Streamlit UI Setup ---
st.set_page_config(page_title="AI Weekly Diet & Exercise", page_icon="🧠", layout="wide")
st.markdown("<h1 style='text-align:center; color:#2E8B57;'>🧠 AI-Powered Indian Weekly Diet & Exercise Planner</h1>", unsafe_allow_html=True)

# --- Sidebar Inputs ---
st.sidebar.header("👤 Your Profile")

age = st.sidebar.number_input("Age", 15, 100, 25)
gender = st.sidebar.selectbox("Gender", ["Male", "Female", "Other"])
height = st.sidebar.number_input("Height (cm)", 100, 250, 170)
weight = st.sidebar.number_input("Weight (kg)", 30, 200, 70)
activity = st.sidebar.selectbox("Activity Level", ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"])
goal = st.sidebar.selectbox("Goal", ["Weight Loss", "Weight Gain", "Muscle Gain", "Maintenance", "Athletic Performance"])
diet = st.sidebar.selectbox("Diet Type", ["Standard", "Vegetarian", "Vegan", "Keto"])
allergies = st.sidebar.multiselect("Allergies", ["Nuts", "Dairy", "Gluten", "Eggs", "None"])

# --- NEW: Current Week Selector ---
current_week = st.sidebar.number_input("📅 Current Week of Program", min_value=1, max_value=52, value=1, step=1)

# --- NEW: Difficulty Selector ---
difficulty = st.sidebar.selectbox("🏋️‍♂️ Difficulty Level", ["Beginner", "Intermediate", "Advanced"])

# --- Health Calcs ---
def calc_bmr(age, gender, height, weight):
    return 88.36 + 13.4 * weight + 4.8 * height - 5.7 * age if gender == "Male" else 447.6 + 9.2 * weight + 3.1 * height - 4.3 * age

def adjust_calories(bmr, level):
    return bmr * {
        "Sedentary": 1.2,
        "Lightly Active": 1.375,
        "Moderately Active": 1.55,
        "Very Active": 1.725
    }.get(level, 1.2)

bmr = calc_bmr(age, gender, height, weight)
base_cals = adjust_calories(bmr, activity)

goal_adjust = {
    "Weight Loss": -500,
    "Weight Gain": +500,
    "Muscle Gain": +300,
    "Maintenance": 0,
    "Athletic Performance": +200
}

target_cals = base_cals + goal_adjust[goal]
bmi = weight / ((height / 100) ** 2)

# --- Summary ---
st.subheader("📊 Your Health Summary")
col1, col2, col3 = st.columns(3)
col1.metric("BMI", f"{bmi:.1f}")
col2.metric("BMR", f"{int(bmr)} cal/day")
col3.metric("Target Calories", f"{int(target_cals)} cal/day")

# --- AI Prompt ---
prompt = f"""
You are a certified Indian dietitian and fitness expert.

This user is on **Week {current_week}** of their fitness journey.

They have already completed all recommendations from week {current_week - 1} and are now progressing to week {current_week}. Generate:
1. A full **7-day Indian diet plan** in table format (breakfast, snack, lunch, dinner) with nutrients.
2. **This week's workout plan** should match their goal: {goal}, difficulty: {difficulty}, activity level: {activity}.
3. Exercises should feel like an upgrade from previous week. Focus on progression (e.g., more reps, new moves, longer time).
4. Include **rest days**, and split workouts between cardio, strength, flexibility, etc.
5. Respect dietary preference: {diet}. Avoid: {', '.join(allergies) if allergies else 'None'}.

Only return **clean markdown tables**, one for diet and one for exercise.
"""

# --- Generate Plan ---
if st.button("🧠 Generate This Week's Plan"):
    with st.spinner(f"Generating week {current_week} plan..."):
        plan = generate_weekly_plan(prompt)
        st.markdown("### 📅 Week " + str(current_week) + " Plan")
        st.markdown(plan, unsafe_allow_html=True)

# --- Footer ---
st.markdown("---")
st.markdown("📝 Tip: You can increase 'week number' to get an advanced workout in future weeks.")

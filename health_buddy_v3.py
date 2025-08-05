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

# --- FitAI Assistant Reply ---
def assistant_reply(user_input, chat_history, user_profile):
    prompt = f"""
You are FitAI — a friendly, expert Indian fitness coach and dietitian. Stay supportive and concise.

User profile:
- Age: {user_profile['age']}, Gender: {user_profile['gender']}, Height: {user_profile['height']} cm, Weight: {user_profile['weight']} kg
- Activity: {user_profile['activity']}, Goal: {user_profile['goal']}, Week: {user_profile['week']}, Difficulty: {user_profile['difficulty']}
- Diet: {user_profile['diet']}, Allergies: {', '.join(user_profile['allergies'])}

Chat history:
{chat_history}

Now answer this message: "{user_input}"

Respond with empathy and step-by-step advice if needed. Include emojis for motivation and clarity.
"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Gemini Error: {e}"

# --- Streamlit UI Setup ---
st.set_page_config(page_title="AI Weekly Diet & Fitness Planner", page_icon="🥗", layout="wide")
st.markdown("<h1 style='text-align:center; color:#2E8B57;'>🥗 AI-Powered Weekly Diet & Workout Planner</h1>", unsafe_allow_html=True)

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
current_week = st.sidebar.number_input("📅 Current Week", min_value=1, max_value=52, value=1)
difficulty = st.sidebar.selectbox("🏋️ Difficulty", ["Beginner", "Intermediate", "Advanced"])

# --- Health Calculation ---
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

# --- Summary Display ---
st.subheader("📊 Your Health Summary")
col1, col2, col3 = st.columns(3)
col1.metric("BMI", f"{bmi:.1f}")
col2.metric("BMR", f"{int(bmr)} cal/day")
col3.metric("Target Calories", f"{int(target_cals)} cal/day")

# --- Gemini Prompt ---
prompt = f"""
You are a certified Indian dietitian and fitness expert.

This user is on **Week {current_week}** of their fitness journey.
They have completed all recommendations from week {current_week - 1} and are progressing.

Generate:
1. A 7-day Indian diet plan (Breakfast, Snack, Lunch, Dinner) — include dishes, calories, macros.
2. Daily workout plan based on: Goal: {goal}, Difficulty: {difficulty}, Activity: {activity}.
3. Ensure it's an upgrade from previous week. Include cardio, strength, rest, flexibility as needed.
4. Respect diet: {diet}, Allergies: {', '.join(allergies) if allergies else 'None'}.

Respond with clean markdown tables only.
"""

if st.button("🧠 Generate My Week Plan"):
    with st.spinner(f"Creating week {current_week} plan..."):
        plan = generate_weekly_plan(prompt)
        st.markdown("### 📅 Week " + str(current_week) + " Plan")
        st.markdown(plan, unsafe_allow_html=True)

# --- Floating Chat Button ---
st.markdown("""
<style>
.floating-chat {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background-color: #2E8B57;
    color: white;
    padding: 10px 18px;
    border-radius: 25px;
    cursor: pointer;
    z-index: 9999;
    font-size: 16px;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.2);
}
</style>
<div class="floating-chat" onclick="window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});">
    💬 Chat with FitAI
</div>
""", unsafe_allow_html=True)

# --- FitAI Chat Assistant ---
st.markdown("## 🧠 FitAI Assistant (Chat)")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = ""

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

user_input = st.chat_input("Ask FitAI anything about your diet, fitness, or routine...")
if user_input:
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    user_profile = {
        "age": age,
        "gender": gender,
        "height": height,
        "weight": weight,
        "activity": activity,
        "goal": goal,
        "diet": diet,
        "allergies": allergies,
        "week": current_week,
        "difficulty": difficulty
    }

    chat_history = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
    ai_reply = assistant_reply(user_input, chat_history, user_profile)
    st.chat_message("assistant").markdown(ai_reply)
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})

# --- Footer ---
st.markdown("---")
st.markdown("📝 Tip: Use the chat to clarify your plan, ask for substitutions, or motivation!")

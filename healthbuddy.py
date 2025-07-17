import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Personalized Diet Planner",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #2E8B57;
    text-align: center;
    margin-bottom: 2rem;
}
.metric-card {
    background-color: #f0f8f0;
    padding: 1rem;
    border-radius: 10px;
    border-left: 5px solid #2E8B57;
}
.food-item {
    background-color: #f9f9f9;
    padding: 0.5rem;
    margin: 0.2rem 0;
    border-radius: 5px;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'user_profile' not in st.session_state:
    st.session_state.user_profile = {}
if 'meal_history' not in st.session_state:
    st.session_state.meal_history = []

# Sidebar - User Profile Input
st.sidebar.header("👤 User Profile")

# Basic Information
st.sidebar.subheader("Basic Information")
age = st.sidebar.number_input("Age", min_value=15, max_value=100, value=25)
gender = st.sidebar.selectbox("Gender", ["Male", "Female", "Other"])
height = st.sidebar.number_input("Height (cm)", min_value=100, max_value=250, value=170)
weight = st.sidebar.number_input("Weight (kg)", min_value=30, max_value=200, value=70)

# Activity Level
activity_level = st.sidebar.selectbox(
    "Activity Level",
    ["Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extra Active"]
)

# Health Goals
goal = st.sidebar.selectbox(
    "Health Goal",
    ["Weight Loss", "Weight Gain", "Muscle Gain", "Maintenance", "Athletic Performance"]
)

# Dietary Preferences
st.sidebar.subheader("Dietary Preferences")
diet_type = st.sidebar.selectbox(
    "Diet Type",
    ["Standard", "Vegetarian", "Vegan", "Keto", "Paleo", "Mediterranean"]
)

# Allergies and Restrictions
allergies = st.sidebar.multiselect(
    "Allergies/Restrictions",
    ["Nuts", "Dairy", "Gluten", "Shellfish", "Eggs", "Soy", "None"]
)

# Calculate BMR and daily calorie needs
def calculate_bmr(age, gender, height, weight):
    if gender == "Male":
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
    else:
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    return bmr

def calculate_daily_calories(bmr, activity_level):
    activity_multipliers = {
        "Sedentary": 1.2,
        "Lightly Active": 1.375,
        "Moderately Active": 1.55,
        "Very Active": 1.725,
        "Extra Active": 1.9
    }
    return bmr * activity_multipliers[activity_level]

# Calculate BMI
bmi = weight / ((height/100) ** 2)
bmr = calculate_bmr(age, gender, height, weight)
daily_calories = calculate_daily_calories(bmr, activity_level)

# Adjust calories based on goal
goal_adjustments = {
    "Weight Loss": -500,
    "Weight Gain": +500,
    "Muscle Gain": +300,
    "Maintenance": 0,
    "Athletic Performance": +200
}
target_calories = daily_calories + goal_adjustments[goal]

# Main Dashboard
st.markdown('<h1 class="main-header">🍎 Personalized Diet Dashboard</h1>', unsafe_allow_html=True)

# User Overview Cards
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("BMI", f"{bmi:.1f}", 
              delta="Normal" if 18.5 <= bmi <= 24.9 else "Check Range")

with col2:
    st.metric("Daily Calories", f"{int(target_calories)}", 
              delta=f"{goal_adjustments[goal]:+d} cal")

with col3:
    st.metric("BMR", f"{int(bmr)}")

with col4:
    st.metric("Activity Level", activity_level)

st.divider()

# Tabs for different sections
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "🍽️ Meal Planner", "📈 Progress", "🥗 Food Database", "⚙️ Settings"])

with tab1:
    st.header("Today's Overview")
    
    # Sample data for demonstration
    today_intake = {
        "Calories": 1456,
        "Protein": 89,
        "Carbs": 145,
        "Fat": 67,
        "Fiber": 23
    }
    
    targets = {
        "Calories": int(target_calories),
        "Protein": int(weight * 1.6),  # 1.6g per kg body weight
        "Carbs": int(target_calories * 0.45 / 4),  # 45% of calories
        "Fat": int(target_calories * 0.25 / 9),  # 25% of calories
        "Fiber": 25
    }
    
    # Progress bars
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Macronutrient Progress")
        for nutrient in ["Calories", "Protein", "Carbs", "Fat"]:
            percentage = (today_intake[nutrient] / targets[nutrient]) * 100
            st.metric(
                nutrient,
                f"{today_intake[nutrient]}/{targets[nutrient]}",
                delta=f"{percentage:.1f}%"
            )
            st.progress(min(percentage/100, 1.0))
    
    with col2:
        # Pie chart for macronutrient distribution
        st.subheader("Macronutrient Distribution")
        
        # Calculate calories from each macro
        protein_cal = today_intake["Protein"] * 4
        carbs_cal = today_intake["Carbs"] * 4
        fat_cal = today_intake["Fat"] * 9
        
        fig_pie = px.pie(
            values=[protein_cal, carbs_cal, fat_cal],
            names=['Protein', 'Carbs', 'Fat'],
            color_discrete_sequence=['#FF9999', '#66B2FF', '#99FF99']
        )
        st.plotly_chart(fig_pie, use_container_width=True)

with tab2:
    st.header("Meal Planner")
    
    # Sample meal suggestions based on diet type
    meal_suggestions = {
        "Standard": {
            "Breakfast": ["Oatmeal with berries", "Greek yogurt with granola", "Scrambled eggs with toast"],
            "Lunch": ["Grilled chicken salad", "Quinoa bowl", "Turkey sandwich"],
            "Dinner": ["Salmon with vegetables", "Lean beef stir-fry", "Pasta with marinara"],
            "Snacks": ["Apple with peanut butter", "Mixed nuts", "Protein smoothie"]
        },
        "Vegetarian": {
            "Breakfast": ["Smoothie bowl", "Avocado toast", "Chia pudding"],
            "Lunch": ["Veggie quinoa salad", "Lentil soup", "Caprese sandwich"],
            "Dinner": ["Vegetable curry", "Stuffed bell peppers", "Eggplant parmesan"],
            "Snacks": ["Hummus with veggies", "Trail mix", "Greek yogurt"]
        }
        # Add more diet types as needed
    }
    
    current_suggestions = meal_suggestions.get(diet_type, meal_suggestions["Standard"])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Today's Meal Plan")
        for meal_type, suggestions in current_suggestions.items():
            st.write(f"**{meal_type}:**")
            selected_meal = st.selectbox(
                f"Choose {meal_type.lower()}",
                suggestions,
                key=f"meal_{meal_type}"
            )
            st.markdown(f'<div class="food-item">{selected_meal}</div>', unsafe_allow_html=True)
    
    with col2:
        st.subheader("Meal History")
        if st.button("Add Current Meals to History"):
            st.session_state.meal_history.append({
                "date": datetime.now().strftime("%Y-%m-%d"),
                "meals": {meal: st.session_state[f"meal_{meal}"] for meal in current_suggestions.keys()}
            })
            st.success("Meals added to history!")
        
        if st.session_state.meal_history:
            for entry in st.session_state.meal_history[-5:]:  # Show last 5 entries
                st.write(f"**{entry['date']}**")
                for meal_type, meal in entry['meals'].items():
                    st.write(f"- {meal_type}: {meal}")
                st.divider()

with tab3:
    st.header("Progress Tracking")
    
    # Sample progress data
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
    weight_data = np.random.normal(weight, 0.5, len(dates))  # Simulate weight fluctuations
    calorie_data = np.random.normal(target_calories, 200, len(dates))
    
    progress_df = pd.DataFrame({
        'Date': dates,
        'Weight': weight_data,
        'Calories': calorie_data
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Weight Progress")
        fig_weight = px.line(progress_df, x='Date', y='Weight', title='Weight Over Time')
        st.plotly_chart(fig_weight, use_container_width=True)
    
    with col2:
        st.subheader("Calorie Intake")
        fig_calories = px.line(progress_df, x='Date', y='Calories', title='Daily Calorie Intake')
        fig_calories.add_hline(y=target_calories, line_dash="dash", line_color="red", 
                              annotation_text="Target Calories")
        st.plotly_chart(fig_calories, use_container_width=True)

with tab4:
    st.header("Food Database")
    
    # Sample food database
    food_db = pd.DataFrame({
        'Food': ['Apple', 'Banana', 'Chicken Breast', 'Rice', 'Broccoli', 'Salmon', 'Oats', 'Almonds'],
        'Calories_per_100g': [52, 89, 165, 130, 34, 208, 389, 579],
        'Protein_g': [0.3, 1.1, 31, 2.7, 2.8, 25.4, 16.9, 21.2],
        'Carbs_g': [14, 23, 0, 28, 7, 0, 66.3, 21.6],
        'Fat_g': [0.2, 0.3, 3.6, 0.3, 0.4, 13.4, 6.9, 49.9],
        'Category': ['Fruit', 'Fruit', 'Protein', 'Grain', 'Vegetable', 'Protein', 'Grain', 'Nuts']
    })
    
    # Search and filter
    search_term = st.text_input("Search food items:")
    category_filter = st.selectbox("Filter by category:", 
                                  ['All'] + list(food_db['Category'].unique()))
    
    # Apply filters
    filtered_db = food_db.copy()
    if search_term:
        filtered_db = filtered_db[filtered_db['Food'].str.contains(search_term, case=False)]
    if category_filter != 'All':
        filtered_db = filtered_db[filtered_db['Category'] == category_filter]
    
    st.dataframe(filtered_db, use_container_width=True)
    
    # Add new food item
    with st.expander("Add New Food Item"):
        col1, col2 = st.columns(2)
        with col1:
            new_food = st.text_input("Food Name")
            new_calories = st.number_input("Calories per 100g", min_value=0)
            new_protein = st.number_input("Protein (g)", min_value=0.0, step=0.1)
        with col2:
            new_carbs = st.number_input("Carbs (g)", min_value=0.0, step=0.1)
            new_fat = st.number_input("Fat (g)", min_value=0.0, step=0.1)
            new_category = st.selectbox("Category", food_db['Category'].unique())
        
        if st.button("Add Food Item"):
            # In a real app, you would save this to a database
            st.success(f"Added {new_food} to database!")

with tab5:
    st.header("Settings & Recommendations")
    
    # Health recommendations based on BMI and goals
    st.subheader("Health Recommendations")
    
    if bmi < 18.5:
        st.warning("⚠️ Your BMI indicates you're underweight. Consider consulting a healthcare provider.")
    elif bmi > 25:
        st.warning("⚠️ Your BMI indicates you're overweight. A balanced diet and exercise can help.")
    else:
        st.success("✅ Your BMI is in the normal range!")
    
    # Water intake recommendation
    water_intake = weight * 35  # ml per kg body weight
    st.info(f"💧 Recommended daily water intake: {water_intake:.0f} ml ({water_intake/1000:.1f} liters)")
    
    # Export settings
    st.subheader("Data Export")
    if st.button("Export Meal History as CSV"):
        if st.session_state.meal_history:
            # In a real app, you would generate and download actual CSV
            st.success("CSV export would be generated here!")
        else:
            st.warning("No meal history to export.")
    
    # Reset data
    st.subheader("Reset Data")
    if st.button("Clear Meal History", type="secondary"):
        st.session_state.meal_history = []
        st.success("Meal history cleared!")

# Footer
st.markdown("---")
st.markdown("*This dashboard is for educational purposes. Consult healthcare professionals for personalized medical advice.*")
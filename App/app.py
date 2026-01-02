"""
CalorieSnap - Professional AI-Powered Nutrition & Fitness Tracker
Complete rebuild with Supabase integration, user authentication, and fitness advisor
"""

import streamlit as st
import anthropic
import json
import base64
from datetime import datetime, timedelta
from PIL import Image
import io
import plotly.graph_objects as go
import plotly.express as px

# Import custom modules
from styles import get_styles
from database import (
    signup_user, login_user, logout_user,
    get_user_profile, update_user_profile,
    save_meal, get_user_meals, get_today_meals, delete_meal,
    calculate_bmr, calculate_tdee, calculate_calorie_goal, get_macro_split,
    get_weekly_stats, get_monthly_stats
)

# Page Configuration
st.set_page_config(
    page_title="CalorieSnap - AI Nutrition Tracker",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply Custom Styles
st.markdown(get_styles(), unsafe_allow_html=True)

# Initialize Session State
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'landing'
if 'anthropic_api_key' not in st.session_state:
    st.session_state.anthropic_api_key = ""


# ==================== AI FOOD ANALYSIS ====================

def analyze_food_image(image_file, api_key):
    """Analyze food image using Claude Vision API"""
    try:
        img_bytes = image_file.getvalue()
        base64_image = base64.b64encode(img_bytes).decode('utf-8')
        image_type = image_file.type

        client = anthropic.Anthropic(api_key=api_key)

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": image_type,
                                "data": base64_image
                            }
                        },
                        {
                            "type": "text",
                            "text": """Analyze this food photo and return ONLY a JSON object (no markdown, no backticks):

{
  "foodName": "food name in English",
  "calories": estimated calories as number,
  "protein": protein in grams as number,
  "carbs": carbohydrates in grams as number,
  "fat": fat in grams as number,
  "portionSize": "portion size description",
  "confidence": "high/medium/low"
}"""
                        }
                    ]
                }
            ]
        )

        response_text = message.content[0].text
        clean_text = response_text.replace('```json', '').replace('```', '').strip()
        food_data = json.loads(clean_text)

        return food_data, None

    except Exception as e:
        return None, str(e)


# ==================== LANDING PAGE ====================

def render_landing_page():
    """Render the landing/marketing page"""

    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <div class="hero-content">
            <div class="hero-text">
                <h1>Food Calorie Tracking</h1>
                <p>Professional nutrition analysis powered by AI. Track your meals effortlessly at your fingertips.</p>
                <div class="hero-buttons">
                    <button class="btn-primary" onclick="return false;">Get Started</button>
                    <button class="btn-secondary" onclick="return false;">Learn More</button>
                </div>
            </div>
            <div class="hero-image">
                <div style="background: rgba(255,255,255,0.1); padding: 40px; border-radius: 20px; backdrop-filter: blur(10px);">
                    <p style="font-size: 1.2rem; text-align: center; color: white;">📸 AI-Powered Food Recognition</p>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Features Section
    st.markdown("""
    <div class="feature-section">
        <div class="section-header">
            <h2>Everything You Need for Fitness Success</h2>
            <p>Comprehensive tools for tracking, analyzing, and optimizing your nutrition and fitness goals</p>
        </div>
        <div class="features-grid">
            <div class="feature-card">
                <div class="feature-icon">📸</div>
                <h3>AI Food Recognition</h3>
                <p>Simply snap a photo of your meal and let AI identify the food and calculate nutrition automatically.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">💪</div>
                <h3>Personalized Goals</h3>
                <p>Get custom calorie and macro targets based on your body stats, activity level, and fitness goals.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <h3>Progress Tracking</h3>
                <p>Visualize your nutrition trends with beautiful charts and detailed analytics over time.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🎯</div>
                <h3>Smart Recommendations</h3>
                <p>Receive intelligent suggestions to optimize your diet and reach your goals faster.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🔒</div>
                <h3>Secure & Private</h3>
                <p>Your data is encrypted and stored securely. Only you have access to your information.</p>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📱</div>
                <h3>Mobile Optimized</h3>
                <p>Works perfectly on any device. Track on-the-go with our mobile-friendly interface.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # CTA Buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("Sign Up Free", type="primary", use_container_width=True):
                st.session_state.current_page = 'signup'
                st.rerun()
        with col_b:
            if st.button("Login", use_container_width=True):
                st.session_state.current_page = 'login'
                st.rerun()


# ==================== AUTH PAGES ====================

def render_login_page():
    """Render login page"""

    st.markdown("""
    <div class="auth-container">
        <div class="auth-header">
            <h2>Welcome Back</h2>
            <p>Sign in to your account to continue</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        col1, col2 = st.columns([1, 1])
        with col1:
            submit = st.form_submit_button("Login", type="primary", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("Back", use_container_width=True)

        if submit:
            if email and password:
                with st.spinner("Logging in..."):
                    success, message, user_data = login_user(email, password)

                    if success:
                        st.session_state.logged_in = True
                        st.session_state.user_data = user_data
                        st.session_state.current_page = 'dashboard'
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
            else:
                st.warning("Please fill in all fields")

        if cancel:
            st.session_state.current_page = 'landing'
            st.rerun()


def render_signup_page():
    """Render signup page"""

    st.markdown("""
    <div class="auth-container">
        <div class="auth-header">
            <h2>Create Account</h2>
            <p>Start your fitness journey today</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    with st.form("signup_form"):
        full_name = st.text_input("Full Name", placeholder="John Doe")
        email = st.text_input("Email", placeholder="you@example.com")
        password = st.text_input("Password", type="password", placeholder="Min. 6 characters")
        password_confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")

        col1, col2 = st.columns([1, 1])
        with col1:
            submit = st.form_submit_button("Create Account", type="primary", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("Back", use_container_width=True)

        if submit:
            if full_name and email and password and password_confirm:
                if password != password_confirm:
                    st.error("Passwords don't match")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    with st.spinner("Creating account..."):
                        success, message, user_data = signup_user(email, password, full_name)

                        if success:
                            st.success(message)
                            st.info("Please login with your new account")
                            st.session_state.current_page = 'login'
                        else:
                            st.error(message)
            else:
                st.warning("Please fill in all fields")

        if cancel:
            st.session_state.current_page = 'landing'
            st.rerun()


# ==================== DASHBOARD ====================

def render_dashboard():
    """Main dashboard - where logged-in users land"""

    user_id = st.session_state.user_data['user_id']
    profile = get_user_profile(user_id)

    if not profile:
        st.error("Failed to load profile")
        return

    # Top Navigation
    col1, col2, col3 = st.columns([2, 6, 2])
    with col1:
        st.markdown("<h2 style='margin: 20px 0;'>CalorieSnap</h2>", unsafe_allow_html=True)
    with col3:
        if st.button("Logout", type="secondary"):
            logout_user()
            st.session_state.logged_in = False
            st.session_state.user_data = None
            st.session_state.current_page = 'landing'
            st.rerun()

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "➕ Add Meal", "📈 Analytics", "⚙️ Settings"])

    # TAB 1: DASHBOARD
    with tab1:
        render_dashboard_tab(user_id, profile)

    # TAB 2: ADD MEAL
    with tab2:
        render_add_meal_tab(user_id)

    # TAB 3: ANALYTICS
    with tab3:
        render_analytics_tab(user_id)

    # TAB 4: SETTINGS
    with tab4:
        render_settings_tab(user_id, profile)


def render_dashboard_tab(user_id, profile):
    """Render main dashboard overview"""

    # Get today's meals
    today_meals = get_today_meals(user_id)

    # Calculate totals
    total_calories = sum(m.get('calories', 0) for m in today_meals)
    total_protein = sum(m.get('protein', 0) for m in today_meals)
    total_carbs = sum(m.get('carbs', 0) for m in today_meals)
    total_fat = sum(m.get('fat', 0) for m in today_meals)

    # Get goals
    calorie_goal = profile.get('daily_calorie_goal', 2000)

    # Calculate macros based on goal
    if profile.get('weight_kg') and profile.get('height_cm') and profile.get('age'):
        bmr = calculate_bmr(
            profile['weight_kg'],
            profile['height_cm'],
            profile['age'],
            profile.get('gender', 'male')
        )
        tdee = calculate_tdee(bmr, profile.get('activity_level', 'moderate'))
        calorie_goal = calculate_calorie_goal(tdee, profile.get('goal', 'maintain'))
        protein_goal, carbs_goal, fat_goal = get_macro_split(calorie_goal, profile.get('goal', 'maintain'))
    else:
        protein_goal, carbs_goal, fat_goal = 150, 200, 65

    # Progress Overview
    st.markdown("### Today's Progress")

    progress_pct = min((total_calories / calorie_goal) * 100, 100)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="stat-card" style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white;">
            <div class="stat-label" style="color: rgba(255,255,255,0.9);">CALORIES</div>
            <div class="stat-value">{total_calories}</div>
            <div class="stat-unit">/ {int(calorie_goal)} kcal</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">PROTEIN</div>
            <div class="stat-value" style="color: #3b82f6;">{total_protein}g</div>
            <div class="stat-unit">/ {protein_goal}g</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">CARBS</div>
            <div class="stat-value" style="color: #10b981;">{total_carbs}g</div>
            <div class="stat-unit">/ {carbs_goal}g</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">FAT</div>
            <div class="stat-value" style="color: #f59e0b;">{total_fat}g</div>
            <div class="stat-unit">/ {fat_goal}g</div>
        </div>
        """, unsafe_allow_html=True)

    # Progress Bar
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-label">
            <span>Daily Goal Progress</span>
            <span><strong>{int(progress_pct)}%</strong></span>
        </div>
        <div class="progress-bar-wrapper">
            <div class="progress-bar" style="width: {progress_pct}%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Today's Meals
    st.markdown("### Today's Meals")

    if not today_meals:
        st.info("No meals logged today. Add your first meal in the 'Add Meal' tab!")
    else:
        for meal in today_meals:
            col1, col2, col3 = st.columns([1, 5, 1])

            with col1:
                if meal.get('image_url'):
                    st.image(meal['image_url'], width=80)
                else:
                    st.markdown("🍽️", unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="meal-item">
                    <div class="meal-name">{meal['food_name']}</div>
                    <div class="meal-calories">{meal['calories']} kcal</div>
                    <div class="meal-macros">P: {meal['protein']}g • C: {meal['carbs']}g • F: {meal['fat']}g</div>
                    <div style="font-size: 0.8rem; color: #9ca3af; margin-top: 4px;">{meal.get('portion_size', 'Standard portion')}</div>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                if st.button("🗑️", key=f"del_{meal['id']}"):
                    delete_meal(meal['id'])
                    st.rerun()


def render_add_meal_tab(user_id):
    """Render add meal interface"""

    st.markdown("### Add New Meal")

    # API Key input if not set
    if not st.session_state.anthropic_api_key:
        with st.expander("⚙️ API Configuration", expanded=True):
            st.info("Enter your Anthropic API key for AI food recognition. Get one at https://console.anthropic.com")
            api_key = st.text_input("Anthropic API Key", type="password")
            if st.button("Save API Key"):
                if api_key:
                    st.session_state.anthropic_api_key = api_key
                    st.success("API Key saved!")
                    st.rerun()

    # Photo Upload
    uploaded_file = st.file_uploader(
        "Upload a photo of your meal",
        type=['jpg', 'jpeg', 'png'],
        help="Take or upload a photo for AI analysis"
    )

    if uploaded_file and st.session_state.anthropic_api_key:
        col1, col2 = st.columns([1, 1])

        with col1:
            st.image(uploaded_file, caption="Your meal", use_container_width=True)

        with col2:
            if st.button("🤖 Analyze with AI", type="primary", use_container_width=True):
                with st.spinner("Analyzing food..."):
                    food_data, error = analyze_food_image(uploaded_file, st.session_state.anthropic_api_key)

                    if food_data:
                        st.success("✅ Food recognized!")

                        st.markdown(f"**{food_data['foodName']}**")
                        st.markdown(f"**{food_data['calories']} kcal**")
                        st.markdown(
                            f"Protein: {food_data['protein']}g • Carbs: {food_data['carbs']}g • Fat: {food_data['fat']}g")
                        st.markdown(f"Portion: {food_data['portionSize']}")

                        # Save button
                        if st.button("💾 Save Meal", use_container_width=True):
                            success, message, _ = save_meal(user_id, food_data)
                            if success:
                                st.success(message)
                                st.balloons()
                            else:
                                st.error(message)
                    else:
                        st.error(f"Analysis failed: {error}")

    elif uploaded_file:
        st.warning("Please enter your API key above to analyze the image")


def render_analytics_tab(user_id):
    """Render analytics and statistics"""

    st.markdown("### Nutrition Analytics")

    # Get weekly data
    weekly_meals = get_weekly_stats(user_id)

    if not weekly_meals:
        st.info("No data yet. Start logging meals to see analytics!")
        return

    # Process data for charts
    from collections import defaultdict
    daily_data = defaultdict(lambda: {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0})

    for meal in weekly_meals:
        date = meal['created_at'][:10]  # Extract date
        daily_data[date]['calories'] += meal.get('calories', 0)
        daily_data[date]['protein'] += meal.get('protein', 0)
        daily_data[date]['carbs'] += meal.get('carbs', 0)
        daily_data[date]['fat'] += meal.get('fat', 0)

    # Sort by date
    sorted_dates = sorted(daily_data.keys())

    # Calories Chart
    fig_cal = go.Figure()
    fig_cal.add_trace(go.Scatter(
        x=sorted_dates,
        y=[daily_data[d]['calories'] for d in sorted_dates],
        mode='lines+markers',
        name='Calories',
        line=dict(color='#10b981', width=3),
        marker=dict(size=8),
        fill='tozeroy',
        fillcolor='rgba(16, 185, 129, 0.1)'
    ))

    fig_cal.update_layout(
        title="Daily Calorie Intake (Last 7 Days)",
        height=300,
        margin=dict(l=0, r=0, t=40, b=0),
        plot_bgcolor='white'
    )

    st.plotly_chart(fig_cal, use_container_width=True)

    # Macros Chart
    total_protein = sum(daily_data[d]['protein'] for d in sorted_dates)
    total_carbs = sum(daily_data[d]['carbs'] for d in sorted_dates)
    total_fat = sum(daily_data[d]['fat'] for d in sorted_dates)

    fig_macros = go.Figure(data=[go.Pie(
        labels=['Protein', 'Carbohydrates', 'Fat'],
        values=[total_protein, total_carbs, total_fat],
        hole=0.4,
        marker=dict(colors=['#3b82f6', '#10b981', '#f59e0b'])
    )])

    fig_macros.update_layout(
        title="Macronutrient Distribution (Weekly)",
        height=300
    )

    st.plotly_chart(fig_macros, use_container_width=True)


def render_settings_tab(user_id, profile):
    """Render settings and profile management"""

    st.markdown("### Profile Settings")

    with st.form("profile_form"):
        st.markdown("#### Personal Information")

        col1, col2 = st.columns(2)
        with col1:
            weight = st.number_input("Weight (kg)", value=profile.get('weight_kg') or 70.0, min_value=30.0,
                                     max_value=200.0)
            height = st.number_input("Height (cm)", value=profile.get('height_cm') or 170.0, min_value=100.0,
                                     max_value=250.0)
            age = st.number_input("Age", value=profile.get('age') or 25, min_value=15, max_value=100)

        with col2:
            gender = st.selectbox("Gender", ["male", "female"], index=0 if profile.get('gender') == 'male' else 1)
            activity = st.selectbox("Activity Level",
                                    ["sedentary", "light", "moderate", "active", "very_active"],
                                    index=["sedentary", "light", "moderate", "active", "very_active"].index(
                                        profile.get('activity_level', 'moderate'))
                                    )
            goal = st.selectbox("Fitness Goal",
                                ["lose", "maintain", "gain"],
                                index=["lose", "maintain", "gain"].index(profile.get('goal', 'maintain')),
                                help="lose = weight loss, maintain = maintain weight, gain = muscle gain"
                                )

        submit = st.form_submit_button("Save Changes", type="primary")

        if submit:
            # Calculate new targets
            bmr = calculate_bmr(weight, height, age, gender)
            tdee = calculate_tdee(bmr, activity)
            new_calorie_goal = calculate_calorie_goal(tdee, goal)

            updates = {
                'weight_kg': weight,
                'height_cm': height,
                'age': age,
                'gender': gender,
                'activity_level': activity,
                'goal': goal,
                'daily_calorie_goal': int(new_calorie_goal)
            }

            success, message = update_user_profile(user_id, updates)

            if success:
                st.success(message)
                st.info(f"Your new daily calorie goal is: **{int(new_calorie_goal)} kcal**")
                st.rerun()
            else:
                st.error(message)

    # Show current calculations
    if profile.get('weight_kg') and profile.get('height_cm') and profile.get('age'):
        st.markdown("---")
        st.markdown("#### Your Metabolic Profile")

        bmr = calculate_bmr(profile['weight_kg'], profile['height_cm'], profile['age'], profile.get('gender', 'male'))
        tdee = calculate_tdee(bmr, profile.get('activity_level', 'moderate'))
        calorie_goal = calculate_calorie_goal(tdee, profile.get('goal', 'maintain'))
        protein, carbs, fat = get_macro_split(calorie_goal, profile.get('goal', 'maintain'))

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("BMR (Basal Metabolic Rate)", f"{bmr} kcal/day")
        with col2:
            st.metric("TDEE (Total Daily Energy)", f"{tdee} kcal/day")
        with col3:
            st.metric("Daily Calorie Goal", f"{int(calorie_goal)} kcal")

        st.markdown("**Recommended Macros:**")
        st.markdown(f"Protein: **{protein}g** • Carbs: **{carbs}g** • Fat: **{fat}g**")


# ==================== MAIN APP ROUTING ====================

def main():
    """Main app router"""

    # Route to correct page
    if not st.session_state.logged_in:
        if st.session_state.current_page == 'login':
            render_login_page()
        elif st.session_state.current_page == 'signup':
            render_signup_page()
        else:  # landing
            render_landing_page()
    else:
        render_dashboard()


if __name__ == "__main__":
    main()
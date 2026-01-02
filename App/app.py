"""
CalorieSnap - AI-Powered Nutrition Tracking
Professional Mobile-Optimized Streamlit App

Installation:
pip install streamlit anthropic pillow plotly

Run:
streamlit run app.py
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

# Page Configuration
st.set_page_config(
    page_title="CalorieSnap",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Professional CSS - No Emoji Style
st.markdown("""
<style>
    /* Clean Professional Design */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main {
        padding: 0.5rem;
        background: #fafafa;
    }
    
    .stButton>button {
        width: 100%;
        height: 56px;
        font-size: 16px;
        font-weight: 600;
        border-radius: 12px;
        border: none;
        background: #10b981;
        color: white;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.2);
        transition: all 0.2s;
    }
    
    .stButton>button:hover {
        background: #059669;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }
    
    /* Clean Headers */
    h1 {
        color: #111827;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
        letter-spacing: -0.025em;
    }
    
    h3 {
        color: #374151;
        font-size: 1.125rem;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
    }
    
    /* Professional Card Styling */
    .metric-card {
        background: white;
        padding: 1.25rem;
        border-radius: 16px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        text-align: center;
        margin: 0.5rem 0;
        border: 1px solid #e5e7eb;
    }
    
    .meal-card {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        margin: 0.75rem 0;
        border: 1px solid #e5e7eb;
        transition: all 0.2s;
    }
    
    .meal-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    
    /* Modern Progress Bar */
    .stProgress > div > div > div {
        background: #10b981;
        height: 8px;
        border-radius: 4px;
    }
    
    /* Clean Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: white;
        padding: 4px;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        border-radius: 8px;
        padding: 0 20px;
        font-weight: 500;
        font-size: 14px;
        color: #6b7280;
        background: transparent;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background: #10b981 !important;
        color: white !important;
    }
    
    /* File Uploader */
    .uploadedFile {
        border-radius: 12px;
        border: 2px dashed #d1d5db;
    }
    
    [data-testid="stFileUploader"] {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        border: 2px dashed #d1d5db;
    }
    
    /* Info/Warning Boxes */
    .stAlert {
        border-radius: 12px;
        border: none;
    }
    
    /* Mobile Optimization */
    @media (max-width: 768px) {
        .stButton>button {
            height: 60px;
            font-size: 16px;
        }
        
        h1 {
            font-size: 1.75rem;
        }
        
        .main {
            padding: 0.25rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize Session State
if 'meals' not in st.session_state:
    st.session_state.meals = []
if 'daily_goal' not in st.session_state:
    st.session_state.daily_goal = 2000
if 'anthropic_api_key' not in st.session_state:
    st.session_state.anthropic_api_key = ""


def analyze_food_image(image_file):
    """Analyze food image using Claude Vision API"""
    try:
        img_bytes = image_file.getvalue()
        base64_image = base64.b64encode(img_bytes).decode('utf-8')
        image_type = image_file.type

        client = anthropic.Anthropic(api_key=st.session_state.anthropic_api_key)

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
                            "text": """Analyze this food photo and return the information in the following JSON format (only JSON, no markdown):

{
  "foodName": "food name in English",
  "calories": estimated calories as number,
  "protein": protein in grams as number,
  "carbs": carbohydrates in grams as number,
  "fat": fat in grams as number,
  "portionSize": "portion size description",
  "confidence": "high/medium/low"
}

Estimate the values as accurately as possible based on the image."""
                        }
                    ]
                }
            ]
        )

        response_text = message.content[0].text
        clean_text = response_text.replace('```json', '').replace('```', '').strip()
        food_data = json.loads(clean_text)

        return food_data

    except Exception as e:
        st.error(f"Analysis error: {str(e)}")
        return None


def add_meal(food_data, image_file):
    """Add meal to list"""
    meal = {
        'id': datetime.now().timestamp(),
        'timestamp': datetime.now().isoformat(),
        'image': image_file,
        **food_data
    }
    st.session_state.meals.insert(0, meal)


def get_today_meals():
    """Get all meals from today"""
    today = datetime.now().date()
    return [m for m in st.session_state.meals if datetime.fromisoformat(m['timestamp']).date() == today]


def get_today_totals():
    """Calculate today's totals"""
    today_meals = get_today_meals()
    return {
        'calories': sum(m['calories'] for m in today_meals),
        'protein': sum(m['protein'] for m in today_meals),
        'carbs': sum(m['carbs'] for m in today_meals),
        'fat': sum(m['fat'] for m in today_meals),
        'count': len(today_meals)
    }


def get_weekly_data():
    """Get data from last 7 days"""
    data = []
    for i in range(6, -1, -1):
        date = datetime.now().date() - timedelta(days=i)
        day_meals = [m for m in st.session_state.meals if datetime.fromisoformat(m['timestamp']).date() == date]
        calories = sum(m['calories'] for m in day_meals)
        data.append({
            'date': date.strftime('%a'),
            'calories': calories
        })
    return data


# ==================== HEADER ====================
st.markdown("<h1>CalorieSnap</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #6b7280; margin-top: -4px; font-size: 0.9rem;'>AI-Powered Nutrition Tracking</p>", unsafe_allow_html=True)

# API Key Configuration
if not st.session_state.anthropic_api_key:
    with st.expander("API Configuration", expanded=True):
        st.info("An Anthropic API key is required for AI food recognition. Get one free at https://console.anthropic.com")
        api_key = st.text_input("Anthropic API Key", type="password")
        if st.button("Save API Key"):
            if api_key:
                st.session_state.anthropic_api_key = api_key
                st.success("API Key saved successfully")
                st.rerun()

# ==================== TABS ====================
tab1, tab2, tab3 = st.tabs(["Overview", "Analytics", "Settings"])

# ==================== OVERVIEW TAB ====================
with tab1:
    # Photo Upload
    st.markdown("### Add Meal")

    uploaded_file = st.file_uploader(
        "Upload photo or use camera",
        type=['jpg', 'jpeg', 'png'],
        label_visibility="collapsed"
    )

    if uploaded_file and st.session_state.anthropic_api_key:
        with st.spinner("Analyzing food..."):
            food_data = analyze_food_image(uploaded_file)

            if food_data:
                st.success("Food recognized successfully")

                # Preview
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(uploaded_file, width=120)
                with col2:
                    st.markdown(f"**{food_data['foodName']}**")
                    st.markdown(f"<span style='color: #10b981; font-weight: 600; font-size: 1.15rem;'>{food_data['calories']} kcal</span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='color: #6b7280; font-size: 0.9rem;'>{food_data['portionSize']}</span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='font-size: 0.9rem;'>P: {food_data['protein']}g • C: {food_data['carbs']}g • F: {food_data['fat']}g</span>", unsafe_allow_html=True)

                if st.button("Add Meal", type="primary"):
                    add_meal(food_data, uploaded_file)
                    st.success("Meal saved successfully")
                    st.rerun()

    elif uploaded_file and not st.session_state.anthropic_api_key:
        st.warning("Please enter your API key in the configuration above")

    st.markdown("---")

    # Daily Goal
    totals = get_today_totals()
    goal = st.session_state.daily_goal
    progress = min((totals['calories'] / goal) * 100, 100)

    st.markdown("### Daily Goal")

    # Modern Progress Card
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #10b981 0%, #059669 100%); 
                padding: 1.75rem; border-radius: 16px; color: white; 
                box-shadow: 0 4px 12px rgba(16, 185, 129, 0.2);'>
        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;'>
            <div>
                <p style='margin: 0; opacity: 0.9; font-size: 0.875rem; font-weight: 500;'>Today's Target</p>
                <h2 style='margin: 0.5rem 0 0 0; font-size: 2.25rem; font-weight: 700;'>
                    {totals['calories']} 
                    <span style='font-size: 1.25rem; opacity: 0.8; font-weight: 500;'>/ {goal}</span>
                </h2>
                <p style='margin: 0.25rem 0 0 0; opacity: 0.9; font-size: 0.875rem;'>kcal</p>
            </div>
            <div style='text-align: right;'>
                <h1 style='margin: 0; font-size: 2.75rem; font-weight: 700;'>{int(progress)}%</h1>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.progress(progress / 100)

    # Macros
    st.markdown("### Macronutrients")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class='metric-card' style='background: #eff6ff; border: 1px solid #dbeafe;'>
            <p style='color: #3b82f6; font-size: 0.75rem; font-weight: 600; margin: 0; text-transform: uppercase; letter-spacing: 0.5px;'>Protein</p>
            <h2 style='color: #1e40af; margin: 0.5rem 0; font-size: 1.75rem; font-weight: 700;'>{totals['protein']}<span style='font-size: 1rem; color: #60a5fa;'>g</span></h2>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='metric-card' style='background: #f0fdf4; border: 1px solid #dcfce7;'>
            <p style='color: #10b981; font-size: 0.75rem; font-weight: 600; margin: 0; text-transform: uppercase; letter-spacing: 0.5px;'>Carbs</p>
            <h2 style='color: #065f46; margin: 0.5rem 0; font-size: 1.75rem; font-weight: 700;'>{totals['carbs']}<span style='font-size: 1rem; color: #34d399;'>g</span></h2>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class='metric-card' style='background: #fffbeb; border: 1px solid #fef3c7;'>
            <p style='color: #f59e0b; font-size: 0.75rem; font-weight: 600; margin: 0; text-transform: uppercase; letter-spacing: 0.5px;'>Fat</p>
            <h2 style='color: #92400e; margin: 0.5rem 0; font-size: 1.75rem; font-weight: 700;'>{totals['fat']}<span style='font-size: 1rem; color: #fbbf24;'>g</span></h2>
        </div>
        """, unsafe_allow_html=True)

    # Today's Meals
    st.markdown("### Today's Meals")

    today_meals = get_today_meals()

    if not today_meals:
        st.markdown("""
        <div style='background: #f9fafb; padding: 2rem; border-radius: 12px; text-align: center; border: 1px dashed #d1d5db;'>
            <p style='color: #9ca3af; margin: 0; font-size: 0.95rem;'>No meals logged today</p>
            <p style='color: #d1d5db; margin: 0.25rem 0 0 0; font-size: 0.85rem;'>Add your first meal above</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        for meal in today_meals:
            col1, col2, col3 = st.columns([1, 3, 1])

            with col1:
                st.image(meal['image'], width=80)

            with col2:
                st.markdown(f"<p style='font-weight: 600; margin: 0; color: #111827;'>{meal['foodName']}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='color: #10b981; font-weight: 600; font-size: 1.05rem; margin: 0.25rem 0;'>{meal['calories']} kcal</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='color: #9ca3af; font-size: 0.85rem; margin: 0;'>{meal['portionSize']}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 0.85rem; color: #6b7280; margin: 0.25rem 0 0 0;'>P: {meal['protein']}g • C: {meal['carbs']}g • F: {meal['fat']}g</p>", unsafe_allow_html=True)

            with col3:
                if st.button("Delete", key=f"del_{meal['id']}", type="secondary"):
                    st.session_state.meals = [m for m in st.session_state.meals if m['id'] != meal['id']]
                    st.rerun()

# ==================== ANALYTICS TAB ====================
with tab2:
    st.markdown("### Weekly Overview")

    weekly_data = get_weekly_data()

    # Line Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[d['date'] for d in weekly_data],
        y=[d['calories'] for d in weekly_data],
        mode='lines+markers',
        line=dict(color='#10b981', width=3),
        marker=dict(size=8, color='#10b981'),
        fill='tozeroy',
        fillcolor='rgba(16, 185, 129, 0.1)'
    ))

    fig.update_layout(
        height=280,
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis_title="",
        yaxis_title="Calories",
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='Inter', size=12)
    )

    st.plotly_chart(fig, use_container_width=True)

    # Macros Distribution
    st.markdown("### Macronutrient Distribution")

    if totals['count'] > 0:
        fig = go.Figure(data=[go.Pie(
            labels=['Protein', 'Carbohydrates', 'Fat'],
            values=[totals['protein'], totals['carbs'], totals['fat']],
            hole=.45,
            marker=dict(colors=['#3b82f6', '#10b981', '#f59e0b']),
            textfont=dict(family='Inter', size=13)
        )])

        fig.update_layout(
            height=280,
            margin=dict(l=0, r=0, t=10, b=0),
            showlegend=True,
            font=dict(family='Inter', size=12)
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for today")

    # Summary Stats
    st.markdown("### Summary")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class='metric-card' style='background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; border: none;'>
            <p style='opacity: 0.9; margin: 0; font-size: 0.875rem; font-weight: 500;'>Total Meals</p>
            <h1 style='margin: 0.5rem 0 0 0; font-size: 2.5rem; font-weight: 700;'>{len(st.session_state.meals)}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='metric-card' style='background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; border: none;'>
            <p style='opacity: 0.9; margin: 0; font-size: 0.875rem; font-weight: 500;'>Today</p>
            <h1 style='margin: 0.5rem 0 0 0; font-size: 2.5rem; font-weight: 700;'>{totals['count']}</h1>
        </div>
        """, unsafe_allow_html=True)

# ==================== SETTINGS TAB ====================
with tab3:
    st.markdown("### Daily Calorie Goal")

    new_goal = st.number_input(
        "Target calories per day",
        min_value=1000,
        max_value=5000,
        value=st.session_state.daily_goal,
        step=100
    )

    if st.button("Save Goal"):
        st.session_state.daily_goal = new_goal
        st.success("Goal saved successfully")

    st.markdown("---")

    st.markdown("### Data Management")
    st.warning("All saved meals will be permanently deleted")

    if st.button("Delete All Data", type="secondary"):
        st.session_state.meals = []
        st.success("Data deleted successfully")
        st.rerun()

    st.markdown("---")

    st.markdown("### About")
    st.markdown("""
    <div style='background: #f9fafb; padding: 1.5rem; border-radius: 12px; border: 1px solid #e5e7eb;'>
        <p style='margin: 0; color: #374151; font-size: 0.95rem; line-height: 1.6;'>
            <strong style='color: #111827;'>CalorieSnap</strong> - AI-powered nutrition tracking app with automatic food recognition.
            Simply take a photo of your meal and let AI estimate the nutritional values.
        </p>
        <p style='margin: 1rem 0 0 0; color: #9ca3af; font-size: 0.85rem;'>Version 1.0</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #9ca3af; font-size: 0.85rem; padding: 1rem 0;'>
    Powered by Streamlit & Claude AI
</div>
""", unsafe_allow_html=True)
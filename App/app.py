"""
CalorieSnap - KI-basierte Kalorienzähl-App
Mobile-optimierte Streamlit Version für PyCharm

Installation:
pip install streamlit anthropic pillow plotly

Starten:
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

# Page Configuration - Mobile optimiert
st.set_page_config(
    page_title="CalorieSnap",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS für Mobile-Optimierung
st.markdown("""
<style>
    /* Mobile-optimiertes Design */
    .main {
        padding: 0.5rem;
    }

    .stButton>button {
        width: 100%;
        height: 60px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 15px;
        border: none;
        background: linear-gradient(135deg, #10b981 0%, #14b8a6 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
    }

    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
    }

    /* Header Styling */
    h1 {
        background: linear-gradient(135deg, #10b981 0%, #14b8a6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        margin-bottom: 0;
    }

    /* Card Styling */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin: 0.5rem 0;
    }

    .meal-card {
        background: white;
        padding: 1rem;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        margin: 0.5rem 0;
        border: 1px solid #e5e7eb;
    }

    /* Progress Bar */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #10b981 0%, #14b8a6 100%);
        height: 12px;
        border-radius: 10px;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        border-radius: 10px;
        padding: 0 24px;
        font-weight: bold;
    }

    /* File Uploader */
    .uploadedFile {
        border-radius: 15px;
    }

    /* Mobile Touch Optimization */
    @media (max-width: 768px) {
        .stButton>button {
            height: 70px;
            font-size: 20px;
        }

        h1 {
            font-size: 2rem;
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
    """Analysiert Essen-Bild mit Claude Vision API"""
    try:
        # Image zu Base64 konvertieren
        img_bytes = image_file.getvalue()
        base64_image = base64.b64encode(img_bytes).decode('utf-8')

        # Determine image type
        image_type = image_file.type

        # Claude API Client
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
                            "text": """Analysiere dieses Essen-Foto und gib mir die Informationen in folgendem JSON-Format zurück (nur JSON, keine Markdown-Backticks):

{
  "foodName": "Name des Essens auf Deutsch",
  "calories": geschätzte Kalorien als Zahl,
  "protein": Protein in Gramm als Zahl,
  "carbs": Kohlenhydrate in Gramm als Zahl,
  "fat": Fett in Gramm als Zahl,
  "portionSize": "Portionsgröße Beschreibung",
  "confidence": "hoch/mittel/niedrig"
}

Schätze die Werte so genau wie möglich basierend auf dem Bild."""
                        }
                    ]
                }
            ]
        )

        # Parse Response
        response_text = message.content[0].text
        clean_text = response_text.replace('```json', '').replace('```', '').strip()
        food_data = json.loads(clean_text)

        return food_data

    except Exception as e:
        st.error(f"Fehler bei der Analyse: {str(e)}")
        return None


def add_meal(food_data, image_file):
    """Fügt Mahlzeit zur Liste hinzu"""
    meal = {
        'id': datetime.now().timestamp(),
        'timestamp': datetime.now().isoformat(),
        'image': image_file,
        **food_data
    }
    st.session_state.meals.insert(0, meal)


def get_today_meals():
    """Holt alle Mahlzeiten von heute"""
    today = datetime.now().date()
    return [m for m in st.session_state.meals if datetime.fromisoformat(m['timestamp']).date() == today]


def get_today_totals():
    """Berechnet heutige Gesamtwerte"""
    today_meals = get_today_meals()
    return {
        'calories': sum(m['calories'] for m in today_meals),
        'protein': sum(m['protein'] for m in today_meals),
        'carbs': sum(m['carbs'] for m in today_meals),
        'fat': sum(m['fat'] for m in today_meals),
        'count': len(today_meals)
    }


def get_weekly_data():
    """Holt Daten der letzten 7 Tage"""
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
st.markdown("<h1>🍽️ CalorieSnap</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #6b7280; margin-top: -10px;'>KI-Powered Food Tracking</p>", unsafe_allow_html=True)

# API Key Input (nur wenn nicht gesetzt)
if not st.session_state.anthropic_api_key:
    with st.expander("⚙️ API Key Konfiguration", expanded=True):
        st.info(
            "Für die KI-Bilderkennung wird ein Anthropic API Key benötigt. Du kannst ihn kostenlos auf https://console.anthropic.com erstellen.")
        api_key = st.text_input("Anthropic API Key", type="password")
        if st.button("API Key speichern"):
            if api_key:
                st.session_state.anthropic_api_key = api_key
                st.success("API Key gespeichert!")
                st.rerun()

# ==================== TABS ====================
tab1, tab2, tab3 = st.tabs(["🏠 Home", "📊 Statistiken", "⚙️ Einstellungen"])

# ==================== HOME TAB ====================
with tab1:
    # Foto Upload / Kamera
    st.markdown("### 📸 Mahlzeit hinzufügen")

    uploaded_file = st.file_uploader(
        "Foto hochladen oder Kamera verwenden",
        type=['jpg', 'jpeg', 'png'],
        label_visibility="collapsed"
    )

    if uploaded_file and st.session_state.anthropic_api_key:
        with st.spinner("🤖 Analysiere Essen..."):
            food_data = analyze_food_image(uploaded_file)

            if food_data:
                st.success("✅ Essen erkannt!")

                # Preview
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.image(uploaded_file, use_container_width=True)
                with col2:
                    st.markdown(f"**{food_data['foodName']}**")
                    st.markdown(f"🔥 **{food_data['calories']} kcal**")
                    st.markdown(f"📏 {food_data['portionSize']}")
                    st.markdown(
                        f"Protein: {food_data['protein']}g • Carbs: {food_data['carbs']}g • Fett: {food_data['fat']}g")

                if st.button("➕ Mahlzeit speichern", type="primary"):
                    add_meal(food_data, uploaded_file)
                    st.success("Mahlzeit gespeichert!")
                    st.rerun()

    elif uploaded_file and not st.session_state.anthropic_api_key:
        st.warning("⚠️ Bitte zuerst API Key eingeben (oben aufklappen)")

    st.markdown("---")

    # Heutiges Ziel
    totals = get_today_totals()
    goal = st.session_state.daily_goal
    progress = min((totals['calories'] / goal) * 100, 100)

    st.markdown("### 🎯 Heutiges Ziel")

    # Progress Card
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #10b981 0%, #14b8a6 100%); 
                padding: 2rem; border-radius: 20px; color: white; box-shadow: 0 8px 20px rgba(16, 185, 129, 0.3);'>
        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;'>
            <div>
                <p style='margin: 0; opacity: 0.9; font-size: 0.9rem;'>Heutiges Ziel</p>
                <h2 style='margin: 0.5rem 0; font-size: 2.5rem;'>{totals['calories']} <span style='font-size: 1.5rem; opacity: 0.8;'>/ {goal}</span></h2>
                <p style='margin: 0; opacity: 0.9;'>kcal</p>
            </div>
            <div style='text-align: right;'>
                <h1 style='margin: 0; font-size: 3rem;'>{int(progress)}%</h1>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.progress(progress / 100)

    # Makros
    st.markdown("### 📊 Makronährstoffe")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class='metric-card' style='background: #eff6ff; border: 2px solid #3b82f6;'>
            <p style='color: #3b82f6; font-size: 0.8rem; font-weight: bold; margin: 0;'>PROTEIN</p>
            <h2 style='color: #1e40af; margin: 0.5rem 0;'>{totals['protein']}g</h2>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='metric-card' style='background: #f0fdf4; border: 2px solid #10b981;'>
            <p style='color: #10b981; font-size: 0.8rem; font-weight: bold; margin: 0;'>CARBS</p>
            <h2 style='color: #065f46; margin: 0.5rem 0;'>{totals['carbs']}g</h2>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class='metric-card' style='background: #fffbeb; border: 2px solid #f59e0b;'>
            <p style='color: #f59e0b; font-size: 0.8rem; font-weight: bold; margin: 0;'>FETT</p>
            <h2 style='color: #92400e; margin: 0.5rem 0;'>{totals['fat']}g</h2>
        </div>
        """, unsafe_allow_html=True)

    # Heutige Mahlzeiten
    st.markdown("### 🍽️ Heutige Mahlzeiten")

    today_meals = get_today_meals()

    if not today_meals:
        st.info("Noch keine Mahlzeiten heute. Füge deine erste Mahlzeit hinzu!")
    else:
        for meal in today_meals:
            col1, col2, col3 = st.columns([1, 3, 1])

            with col1:
                st.image(meal['image'], use_container_width=True)

            with col2:
                st.markdown(f"**{meal['foodName']}**")
                st.markdown(f"🔥 **{meal['calories']} kcal**")
                st.markdown(f"<small>{meal['portionSize']}</small>", unsafe_allow_html=True)
                st.markdown(f"<small>P: {meal['protein']}g • C: {meal['carbs']}g • F: {meal['fat']}g</small>",
                            unsafe_allow_html=True)

            with col3:
                if st.button("🗑️", key=f"del_{meal['id']}"):
                    st.session_state.meals = [m for m in st.session_state.meals if m['id'] != meal['id']]
                    st.rerun()

# ==================== STATISTIKEN TAB ====================
with tab2:
    st.markdown("### 📈 Wöchliche Kalorien")

    weekly_data = get_weekly_data()

    # Line Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[d['date'] for d in weekly_data],
        y=[d['calories'] for d in weekly_data],
        mode='lines+markers',
        line=dict(color='#10b981', width=3),
        marker=dict(size=10, color='#10b981'),
        fill='tozeroy',
        fillcolor='rgba(16, 185, 129, 0.1)'
    ))

    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis_title="",
        yaxis_title="Kalorien",
        plot_bgcolor='white',
        paper_bgcolor='white'
    )

    st.plotly_chart(fig, use_container_width=True)

    # Makronährstoffe Verteilung
    st.markdown("### 🥧 Makronährstoffe Heute")

    if totals['count'] > 0:
        fig = go.Figure(data=[go.Pie(
            labels=['Protein', 'Kohlenhydrate', 'Fett'],
            values=[totals['protein'], totals['carbs'], totals['fat']],
            hole=.4,
            marker=dict(colors=['#3b82f6', '#10b981', '#f59e0b'])
        )])

        fig.update_layout(
            height=300,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Noch keine Daten für heute")

    # Summary Stats
    st.markdown("### 📊 Zusammenfassung")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class='metric-card' style='background: linear-gradient(135deg, #10b981 0%, #14b8a6 100%); color: white;'>
            <p style='opacity: 0.9; margin: 0;'>Gesamt Mahlzeiten</p>
            <h1 style='margin: 0.5rem 0;'>{len(st.session_state.meals)}</h1>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class='metric-card' style='background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%); color: white;'>
            <p style='opacity: 0.9; margin: 0;'>Heute</p>
            <h1 style='margin: 0.5rem 0;'>{totals['count']}</h1>
        </div>
        """, unsafe_allow_html=True)

# ==================== EINSTELLUNGEN TAB ====================
with tab3:
    st.markdown("### ⚙️ Kalorienziel")

    new_goal = st.number_input(
        "Tägliches Kalorienziel",
        min_value=1000,
        max_value=5000,
        value=st.session_state.daily_goal,
        step=100
    )

    if st.button("💾 Ziel speichern"):
        st.session_state.daily_goal = new_goal
        st.success("Ziel gespeichert!")

    st.markdown("---")

    st.markdown("### 🗑️ Daten löschen")
    st.warning("Alle gespeicherten Mahlzeiten werden gelöscht.")

    if st.button("Alle Daten löschen", type="secondary"):
        st.session_state.meals = []
        st.success("Daten gelöscht!")
        st.rerun()

    st.markdown("---")

    st.markdown("### ℹ️ Über die App")
    st.info("""
    **CalorieSnap** - KI-basierte Kalorienzähl-App

    Mache einfach ein Foto von deinem Essen und die App schätzt automatisch die Nährwerte.

    Version 1.0 • Streamlit PWA
    """)

# ==================== FOOTER ====================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #6b7280; font-size: 0.8rem; padding: 1rem;'>
    Made with ❤️ using Streamlit & Claude AI
</div>
""", unsafe_allow_html=True)
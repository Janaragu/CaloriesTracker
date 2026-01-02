"""
admin_launcher.py - Quick launcher for admin panel
Run with: streamlit run admin_launcher.py
"""

import streamlit as st
from admin import admin_main

# Set page config
st.set_page_config(
    page_title="CalorieSnap Admin",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Run admin panel
admin_main()
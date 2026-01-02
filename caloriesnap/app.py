"""
app.py - Main Application File
CalorieSnap - AI-Powered Nutrition Tracking

Modular structure:
- states/ - State management (auth, profile, meals)
- components/ - Reusable UI components
- pages/ - Page components
"""

"""
app.py - Main Application File
CalorieSnap - AI-Powered Nutrition Tracking
"""

import reflex as rx

# Import pages - OHNE "caloriesnap." Prefix
from pages.landing import landing_page
from pages.auth import login_page, signup_page
from pages.dashboard import dashboard_page


# ==================== APP CONFIGURATION ====================

app = rx.App(
    theme=rx.theme(
        appearance="light",
        has_background=True,
        radius="large",
        accent_color="green"
    ),
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap",
    ],
)


# ==================== ROUTES ====================

app.add_page(
    landing_page,
    route="/",
    title="CalorieSnap - AI Nutrition Tracker",
    description="Track your nutrition with AI-powered food recognition"
)

app.add_page(
    login_page,
    route="/login",
    title="Login - CalorieSnap"
)

app.add_page(
    signup_page,
    route="/signup",
    title="Sign Up - CalorieSnap"
)

app.add_page(
    dashboard_page,
    route="/dashboard",
    title="Dashboard - CalorieSnap"
)

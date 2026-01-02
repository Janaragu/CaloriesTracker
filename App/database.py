"""
database.py - Supabase Integration
Handles all database operations and user authentication
"""

from supabase import create_client, Client
import streamlit as st

# Supabase Configuration
SUPABASE_URL = "https://sfvovdpzhyubjctrdpwg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNmdm92ZHB6aHl1YmpjdHJkcHdnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NzM0MjczNCwiZXhwIjoyMDgyOTE4NzM0fQ.dSBya9887OWg8zBU8j_FY4TUQ9AZxMLfSgjyWtdYs4s"


# Initialize Supabase client
@st.cache_resource
def get_supabase_client() -> Client:
    """Create and cache Supabase client"""
    return create_client(SUPABASE_URL, SUPABASE_KEY)


supabase = get_supabase_client()


# ==================== USER AUTHENTICATION ====================

def signup_user(email: str, password: str, full_name: str):
    """
    Register a new user
    Returns: (success: bool, message: str, user_data: dict)
    """
    try:
        # Create auth user
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        if auth_response.user:
            # Create user profile
            profile_data = {
                "user_id": auth_response.user.id,
                "email": email,
                "full_name": full_name,
                "daily_calorie_goal": 2000,
                "weight_kg": None,
                "height_cm": None,
                "age": None,
                "gender": None,
                "activity_level": "moderate",
                "goal": "maintain"  # maintain, lose, gain
            }

            supabase.table("users").insert(profile_data).execute()

            return True, "Account created successfully! Please log in.", auth_response.user
        else:
            return False, "Signup failed. Please try again.", None

    except Exception as e:
        return False, f"Error: {str(e)}", None


def login_user(email: str, password: str):
    """
    Log in existing user
    Returns: (success: bool, message: str, user_data: dict)
    """
    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if auth_response.user:
            # Get user profile
            profile = supabase.table("users").select("*").eq("user_id", auth_response.user.id).execute()

            return True, "Login successful!", {
                "user_id": auth_response.user.id,
                "email": auth_response.user.email,
                "profile": profile.data[0] if profile.data else None
            }
        else:
            return False, "Invalid credentials", None

    except Exception as e:
        return False, f"Error: {str(e)}", None


def logout_user():
    """Log out current user"""
    try:
        supabase.auth.sign_out()
        return True, "Logged out successfully"
    except Exception as e:
        return False, f"Error: {str(e)}"


# ==================== USER PROFILE ====================

def get_user_profile(user_id: str):
    """Get user profile data"""
    try:
        response = supabase.table("users").select("*").eq("user_id", user_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        st.error(f"Error loading profile: {str(e)}")
        return None


def update_user_profile(user_id: str, updates: dict):
    """Update user profile"""
    try:
        response = supabase.table("users").update(updates).eq("user_id", user_id).execute()
        return True, "Profile updated successfully"
    except Exception as e:
        return False, f"Error: {str(e)}"


# ==================== MEALS ====================

def save_meal(user_id: str, meal_data: dict):
    """Save a meal to database"""
    try:
        data = {
            "user_id": user_id,
            "food_name": meal_data["foodName"],
            "calories": meal_data["calories"],
            "protein": meal_data["protein"],
            "carbs": meal_data["carbs"],
            "fat": meal_data["fat"],
            "portion_size": meal_data["portionSize"],
            "confidence": meal_data.get("confidence", "medium"),
            "image_url": meal_data.get("image_url"),
            "meal_time": meal_data.get("meal_time", "lunch")
        }

        response = supabase.table("meals").insert(data).execute()
        return True, "Meal saved successfully", response.data[0] if response.data else None
    except Exception as e:
        return False, f"Error: {str(e)}", None


def get_user_meals(user_id: str, limit: int = 50):
    """Get user's meals"""
    try:
        response = supabase.table("meals").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(
            limit).execute()
        return response.data
    except Exception as e:
        st.error(f"Error loading meals: {str(e)}")
        return []


def get_today_meals(user_id: str):
    """Get meals from today"""
    try:
        from datetime import datetime
        today = datetime.now().date().isoformat()

        response = supabase.table("meals").select("*").eq("user_id", user_id).gte("created_at", today).execute()
        return response.data
    except Exception as e:
        st.error(f"Error loading today's meals: {str(e)}")
        return []


def delete_meal(meal_id: int):
    """Delete a meal"""
    try:
        supabase.table("meals").delete().eq("id", meal_id).execute()
        return True, "Meal deleted"
    except Exception as e:
        return False, f"Error: {str(e)}"


# ==================== FITNESS CALCULATIONS ====================

def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str):
    """
    Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation
    """
    if gender.lower() == "male":
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:  # female
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161

    return round(bmr)


def calculate_tdee(bmr: float, activity_level: str):
    """
    Calculate Total Daily Energy Expenditure
    """
    activity_multipliers = {
        "sedentary": 1.2,  # Little or no exercise
        "light": 1.375,  # Light exercise 1-3 days/week
        "moderate": 1.55,  # Moderate exercise 3-5 days/week
        "active": 1.725,  # Heavy exercise 6-7 days/week
        "very_active": 1.9  # Very heavy exercise, physical job
    }

    multiplier = activity_multipliers.get(activity_level, 1.55)
    return round(bmr * multiplier)


def calculate_calorie_goal(tdee: float, goal: str):
    """
    Calculate daily calorie goal based on fitness goal
    """
    if goal == "lose":
        # 500 kcal deficit for ~0.5kg/week loss
        return tdee - 500
    elif goal == "gain":
        # 300 kcal surplus for lean muscle gain
        return tdee + 300
    else:  # maintain
        return tdee


def get_macro_split(calories: float, goal: str):
    """
    Calculate macronutrient targets
    Returns: (protein_g, carbs_g, fat_g)
    """
    if goal == "lose":
        # High protein for muscle preservation
        protein_ratio = 0.35
        fat_ratio = 0.25
        carbs_ratio = 0.40
    elif goal == "gain":
        # More carbs for energy
        protein_ratio = 0.30
        fat_ratio = 0.25
        carbs_ratio = 0.45
    else:  # maintain
        protein_ratio = 0.30
        fat_ratio = 0.30
        carbs_ratio = 0.40

    protein_g = round((calories * protein_ratio) / 4)  # 4 kcal per gram
    carbs_g = round((calories * carbs_ratio) / 4)
    fat_g = round((calories * fat_ratio) / 9)  # 9 kcal per gram

    return protein_g, carbs_g, fat_g


# ==================== ANALYTICS ====================

def get_weekly_stats(user_id: str):
    """Get nutrition stats for the past 7 days"""
    try:
        from datetime import datetime, timedelta

        week_ago = (datetime.now() - timedelta(days=7)).date().isoformat()

        response = supabase.table("meals").select("*").eq("user_id", user_id).gte("created_at", week_ago).execute()

        return response.data
    except Exception as e:
        st.error(f"Error loading weekly stats: {str(e)}")
        return []


def get_monthly_stats(user_id: str):
    """Get nutrition stats for the past 30 days"""
    try:
        from datetime import datetime, timedelta

        month_ago = (datetime.now() - timedelta(days=30)).date().isoformat()

        response = supabase.table("meals").select("*").eq("user_id", user_id).gte("created_at", month_ago).execute()

        return response.data
    except Exception as e:
        st.error(f"Error loading monthly stats: {str(e)}")
        return []
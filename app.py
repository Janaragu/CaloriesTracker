"""
CalorieSnap - Flask Backend
AI-Powered Nutrition Tracking
"""

import os
import json
import base64
from datetime import datetime, timedelta
from functools import wraps

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from supabase import create_client, Client
import anthropic

# ==================== CONFIG ====================

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "caloriesnap-secret-key-change-in-production")

# Supabase Config
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://sfvovdpzhyubjctrdpwg.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNmdm92ZHB6aHl1YmpjdHJkcHdnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NzM0MjczNCwiZXhwIjoyMDgyOTE4NzM0fQ.dSBya9887OWg8zBU8j_FY4TUQ9AZxMLfSgjyWtdYs4s")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ==================== HELPERS ====================

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def calculate_bmr(weight, height, age, gender):
    """Calculate Basal Metabolic Rate (Mifflin-St Jeor)"""
    if gender == "male":
        return (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        return (10 * weight) + (6.25 * height) - (5 * age) - 161


def calculate_tdee(bmr, activity_level):
    """Calculate Total Daily Energy Expenditure"""
    multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9
    }
    return bmr * multipliers.get(activity_level, 1.55)


def calculate_calorie_goal(tdee, goal):
    """Calculate daily calorie goal"""
    if goal == "lose":
        return int(tdee - 500)
    elif goal == "gain":
        return int(tdee + 300)
    return int(tdee)


# ==================== PAGE ROUTES ====================

@app.route("/")
def landing():
    """Landing page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template("landing.html")


@app.route("/login")
def login():
    """Login page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template("login.html")


@app.route("/signup")
def signup():
    """Signup page"""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template("signup.html")


@app.route("/dashboard")
@login_required
def dashboard():
    """Dashboard page"""
    return render_template("dashboard.html", user_email=session.get('user_email', ''))


@app.route("/logout")
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('landing'))


# ==================== AUTH API ====================

@app.route("/api/signup", methods=["POST"])
def api_signup():
    """API: Sign up new user"""
    try:
        data = request.json
        email = data.get("email", "").strip()
        password = data.get("password", "")
        full_name = data.get("full_name", "User")
        
        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400
        
        if len(password) < 6:
            return jsonify({"error": "Password must be at least 6 characters"}), 400
        
        # Create auth user
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        if auth_response.user:
            # Create user profile
            supabase.table("users").insert({
                "user_id": auth_response.user.id,
                "email": email,
                "full_name": full_name,
                "weight_kg": 70,
                "height_cm": 170,
                "age": 25,
                "gender": "male",
                "activity_level": "moderate",
                "goal": "maintain",
                "daily_calorie_goal": 2000
            }).execute()
            
            return jsonify({"success": True, "message": "Account created! Please login."})
        else:
            return jsonify({"error": "Signup failed"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/login", methods=["POST"])
def api_login():
    """API: Login user"""
    try:
        data = request.json
        email = data.get("email", "").strip()
        password = data.get("password", "")
        
        if not email or not password:
            return jsonify({"error": "Email and password required"}), 400
        
        # Login with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        if auth_response.user and auth_response.session:
            # Set session
            session['user_id'] = auth_response.user.id
            session['user_email'] = auth_response.user.email
            session['access_token'] = auth_response.session.access_token
            
            return jsonify({"success": True, "redirect": "/dashboard"})
        else:
            return jsonify({"error": "Invalid credentials"}), 401
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== PROFILE API ====================

@app.route("/api/profile", methods=["GET"])
@login_required
def api_get_profile():
    """API: Get user profile"""
    try:
        response = supabase.table("users").select("*").eq("user_id", session['user_id']).execute()
        
        if response.data:
            profile = response.data[0]
            # Calculate BMR and TDEE
            bmr = calculate_bmr(
                profile.get("weight_kg", 70),
                profile.get("height_cm", 170),
                profile.get("age", 25),
                profile.get("gender", "male")
            )
            tdee = calculate_tdee(bmr, profile.get("activity_level", "moderate"))
            
            return jsonify({
                "success": True,
                "profile": profile,
                "bmr": int(bmr),
                "tdee": int(tdee)
            })
        else:
            return jsonify({"error": "Profile not found"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/profile", methods=["POST"])
@login_required
def api_update_profile():
    """API: Update user profile"""
    try:
        data = request.json
        
        weight = float(data.get("weight_kg", 70))
        height = float(data.get("height_cm", 170))
        age = int(data.get("age", 25))
        gender = data.get("gender", "male")
        activity = data.get("activity_level", "moderate")
        goal = data.get("goal", "maintain")
        
        # Calculate new calorie goal
        bmr = calculate_bmr(weight, height, age, gender)
        tdee = calculate_tdee(bmr, activity)
        calorie_goal = calculate_calorie_goal(tdee, goal)
        
        # Update database
        supabase.table("users").update({
            "weight_kg": weight,
            "height_cm": height,
            "age": age,
            "gender": gender,
            "activity_level": activity,
            "goal": goal,
            "daily_calorie_goal": calorie_goal
        }).eq("user_id", session['user_id']).execute()
        
        return jsonify({
            "success": True,
            "calorie_goal": calorie_goal,
            "bmr": int(bmr),
            "tdee": int(tdee)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== MEALS API ====================

@app.route("/api/meals", methods=["GET"])
@login_required
def api_get_meals():
    """API: Get user's meals"""
    try:
        # Get today's date
        today = datetime.now().date().isoformat()
        
        # Get today's meals
        today_response = supabase.table("meals").select("*").eq(
            "user_id", session['user_id']
        ).gte("created_at", today).order("created_at", desc=True).execute()
        
        # Get all recent meals
        all_response = supabase.table("meals").select("*").eq(
            "user_id", session['user_id']
        ).order("created_at", desc=True).limit(50).execute()
        
        today_meals = today_response.data if today_response.data else []
        all_meals = all_response.data if all_response.data else []
        
        # Calculate totals
        total_calories = sum(m.get("calories", 0) for m in today_meals)
        total_protein = sum(m.get("protein", 0) for m in today_meals)
        total_carbs = sum(m.get("carbs", 0) for m in today_meals)
        total_fat = sum(m.get("fat", 0) for m in today_meals)
        
        return jsonify({
            "success": True,
            "today_meals": today_meals,
            "all_meals": all_meals,
            "totals": {
                "calories": total_calories,
                "protein": round(total_protein, 1),
                "carbs": round(total_carbs, 1),
                "fat": round(total_fat, 1)
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/meals", methods=["POST"])
@login_required
def api_add_meal():
    """API: Add a meal"""
    try:
        data = request.json
        
        supabase.table("meals").insert({
            "user_id": session['user_id'],
            "food_name": data.get("food_name", "Unknown"),
            "calories": int(data.get("calories", 0)),
            "protein": float(data.get("protein", 0)),
            "carbs": float(data.get("carbs", 0)),
            "fat": float(data.get("fat", 0)),
            "portion_size": data.get("portion_size", "1 serving"),
            "confidence": data.get("confidence", "medium"),
            "meal_time": data.get("meal_time", "lunch")
        }).execute()
        
        return jsonify({"success": True, "message": "Meal saved!"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/meals/<int:meal_id>", methods=["DELETE"])
@login_required
def api_delete_meal(meal_id):
    """API: Delete a meal"""
    try:
        supabase.table("meals").delete().eq("id", meal_id).eq("user_id", session['user_id']).execute()
        return jsonify({"success": True, "message": "Meal deleted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== AI ANALYSIS API ====================

@app.route("/api/analyze", methods=["POST"])
@login_required
def api_analyze_food():
    """API: Analyze food image with Claude Vision"""
    try:
        api_key = request.form.get("api_key", "").strip()
        
        if not api_key:
            return jsonify({"error": "Please enter your Anthropic API key"}), 400
        
        if 'image' not in request.files:
            return jsonify({"error": "No image uploaded"}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({"error": "No image selected"}), 400
        
        # Read and encode image
        image_data = file.read()
        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        # Determine media type
        filename = file.filename.lower()
        if filename.endswith('.png'):
            media_type = "image/png"
        elif filename.endswith('.gif'):
            media_type = "image/gif"
        elif filename.endswith('.webp'):
            media_type = "image/webp"
        else:
            media_type = "image/jpeg"
        
        # Call Claude Vision API
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
                                "media_type": media_type,
                                "data": base64_image
                            }
                        },
                        {
                            "type": "text",
                            "text": """Analyze this food photo and return ONLY a JSON object (no markdown, no backticks):

{
  "foodName": "food name in English",
  "calories": estimated calories as integer,
  "protein": protein in grams as float,
  "carbs": carbohydrates in grams as float,
  "fat": fat in grams as float,
  "portionSize": "portion size description",
  "confidence": "high/medium/low"
}

Estimate values as accurately as possible based on the image."""
                        }
                    ]
                }
            ]
        )
        
        # Parse response
        response_text = message.content[0].text
        clean_text = response_text.replace('```json', '').replace('```', '').strip()
        food_data = json.loads(clean_text)
        
        return jsonify({"success": True, "food": food_data})
        
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to parse AI response"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==================== RUN ====================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

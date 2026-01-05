"""
CalorieSnap v4.0 - Flask Backend
AI-Powered Nutrition Tracking with Cuisine Preferences & Smart Recommendations
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

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://sfvovdpzhyubjctrdpwg.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNmdm92ZHB6aHl1YmpjdHJkcHdnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NzM0MjczNCwiZXhwIjoyMDgyOTE4NzM0fQ.dSBya9887OWg8zBU8j_FY4TUQ9AZxMLfSgjyWtdYs4s")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Available cuisines
CUISINES = [
    {"code": "indian", "name": "Indian / South Asian", "emoji": "🇮🇳"},
    {"code": "tamil", "name": "Tamil / Sri Lankan", "emoji": "🇱🇰"},
    {"code": "chinese", "name": "Chinese", "emoji": "🇨🇳"},
    {"code": "japanese", "name": "Japanese", "emoji": "🇯🇵"},
    {"code": "korean", "name": "Korean", "emoji": "🇰🇷"},
    {"code": "thai", "name": "Thai", "emoji": "🇹🇭"},
    {"code": "vietnamese", "name": "Vietnamese", "emoji": "🇻🇳"},
    {"code": "mexican", "name": "Mexican", "emoji": "🇲🇽"},
    {"code": "italian", "name": "Italian", "emoji": "🇮🇹"},
    {"code": "mediterranean", "name": "Mediterranean", "emoji": "🇬🇷"},
    {"code": "middle_eastern", "name": "Middle Eastern", "emoji": "🇱🇧"},
    {"code": "african", "name": "African", "emoji": "🌍"},
    {"code": "american", "name": "American", "emoji": "🇺🇸"},
    {"code": "german", "name": "German / Swiss", "emoji": "🇩🇪"},
    {"code": "french", "name": "French", "emoji": "🇫🇷"},
    {"code": "other", "name": "Other / Mixed", "emoji": "🌐"}
]


# ==================== HELPERS ====================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def calculate_bmr(weight, height, age, gender):
    if gender == "male":
        return (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        return (10 * weight) + (6.25 * height) - (5 * age) - 161


def calculate_tdee(bmr, activity_level):
    multipliers = {"sedentary": 1.2, "light": 1.375, "moderate": 1.55, "active": 1.725, "very_active": 1.9}
    return bmr * multipliers.get(activity_level, 1.55)


def calculate_calorie_goal(tdee, goal):
    if goal == "lose": return int(tdee - 500)
    elif goal == "gain": return int(tdee + 300)
    return int(tdee)


def get_streak(user_id):
    try:
        today = datetime.now().date()
        streak = 0
        for i in range(365):
            check_date = (today - timedelta(days=i)).isoformat()
            next_date = (today - timedelta(days=i-1)).isoformat() if i > 0 else (today + timedelta(days=1)).isoformat()
            response = supabase.table("meals").select("id").eq("user_id", user_id).gte("created_at", check_date).lt("created_at", next_date).limit(1).execute()
            if response.data: streak += 1
            else: break
        return streak
    except: return 0


def get_achievements(user_id, streak, total_meals):
    achievements = []
    if streak >= 1: achievements.append({"icon": "🔥", "name": "First Log", "desc": "Logged your first meal"})
    if streak >= 7: achievements.append({"icon": "⭐", "name": "Week Warrior", "desc": "7 day streak"})
    if streak >= 30: achievements.append({"icon": "🏆", "name": "Monthly Master", "desc": "30 day streak"})
    if total_meals >= 10: achievements.append({"icon": "🍽️", "name": "Getting Started", "desc": "10 meals logged"})
    if total_meals >= 50: achievements.append({"icon": "🥗", "name": "Nutrition Tracker", "desc": "50 meals logged"})
    if total_meals >= 100: achievements.append({"icon": "🎯", "name": "Dedicated", "desc": "100 meals logged"})
    return achievements


def get_user_preferences(user_id):
    try:
        response = supabase.table("users").select("*").eq("user_id", user_id).execute()
        if response.data:
            user = response.data[0]
            return {"cuisines": user.get("preferred_cuisines", []), "goal": user.get("goal", "maintain")}
    except: pass
    return {"cuisines": [], "goal": "maintain"}


# ==================== PAGE ROUTES ====================

@app.route("/")
def landing():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    return render_template("landing.html")

@app.route("/login")
def login():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    return render_template("login.html")

@app.route("/signup")
def signup():
    if 'user_id' in session: return redirect(url_for('dashboard'))
    return render_template("signup.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user_email=session.get('user_email', ''), cuisines=CUISINES)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('landing'))


# ==================== AUTH API ====================

@app.route("/api/signup", methods=["POST"])
def api_signup():
    try:
        data = request.json
        email = data.get("email", "").strip()
        password = data.get("password", "")
        full_name = data.get("full_name", "User")
        
        if not email or not password: return jsonify({"error": "Email and password required"}), 400
        if len(password) < 6: return jsonify({"error": "Password must be at least 6 characters"}), 400
        
        auth_response = supabase.auth.sign_up({"email": email, "password": password})
        
        if auth_response.user:
            supabase.table("users").insert({
                "user_id": auth_response.user.id, "email": email, "full_name": full_name,
                "weight_kg": 70, "height_cm": 170, "age": 25, "gender": "male",
                "activity_level": "moderate", "goal": "maintain", "daily_calorie_goal": 2000,
                "preferred_cuisines": []
            }).execute()
            return jsonify({"success": True, "message": "Account created! Please login."})
        return jsonify({"error": "Signup failed"}), 400
    except Exception as e: return jsonify({"error": str(e)}), 500


@app.route("/api/login", methods=["POST"])
def api_login():
    try:
        data = request.json
        email = data.get("email", "").strip()
        password = data.get("password", "")
        
        if not email or not password: return jsonify({"error": "Email and password required"}), 400
        
        auth_response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        
        if auth_response.user and auth_response.session:
            session['user_id'] = auth_response.user.id
            session['user_email'] = auth_response.user.email
            return jsonify({"success": True, "redirect": "/dashboard"})
        return jsonify({"error": "Invalid credentials"}), 401
    except Exception as e: return jsonify({"error": str(e)}), 500


# ==================== PROFILE API ====================

@app.route("/api/profile", methods=["GET"])
@login_required
def api_get_profile():
    try:
        response = supabase.table("users").select("*").eq("user_id", session['user_id']).execute()
        if response.data:
            profile = response.data[0]
            bmr = calculate_bmr(profile.get("weight_kg", 70), profile.get("height_cm", 170), profile.get("age", 25), profile.get("gender", "male"))
            tdee = calculate_tdee(bmr, profile.get("activity_level", "moderate"))
            return jsonify({"success": True, "profile": profile, "bmr": int(bmr), "tdee": int(tdee), "cuisines": CUISINES})
        return jsonify({"error": "Profile not found"}), 404
    except Exception as e: return jsonify({"error": str(e)}), 500


@app.route("/api/profile", methods=["POST"])
@login_required
def api_update_profile():
    try:
        data = request.json
        weight = float(data.get("weight_kg", 70))
        height = float(data.get("height_cm", 170))
        age = int(data.get("age", 25))
        gender = data.get("gender", "male")
        activity = data.get("activity_level", "moderate")
        goal = data.get("goal", "maintain")
        preferred_cuisines = data.get("preferred_cuisines", [])
        
        bmr = calculate_bmr(weight, height, age, gender)
        tdee = calculate_tdee(bmr, activity)
        calorie_goal = calculate_calorie_goal(tdee, goal)
        
        supabase.table("users").update({
            "weight_kg": weight, "height_cm": height, "age": age, "gender": gender,
            "activity_level": activity, "goal": goal, "daily_calorie_goal": calorie_goal,
            "preferred_cuisines": preferred_cuisines
        }).eq("user_id", session['user_id']).execute()
        
        return jsonify({"success": True, "calorie_goal": calorie_goal, "bmr": int(bmr), "tdee": int(tdee)})
    except Exception as e: return jsonify({"error": str(e)}), 500


# ==================== MEALS API ====================

@app.route("/api/meals", methods=["GET"])
@login_required
def api_get_meals():
    try:
        today = datetime.now().date().isoformat()
        today_response = supabase.table("meals").select("*").eq("user_id", session['user_id']).gte("created_at", today).order("created_at", desc=True).execute()
        all_response = supabase.table("meals").select("*").eq("user_id", session['user_id']).order("created_at", desc=True).limit(100).execute()
        
        today_meals = today_response.data or []
        all_meals = all_response.data or []
        
        totals = {
            "calories": sum(m.get("calories", 0) for m in today_meals),
            "protein": round(sum(m.get("protein", 0) for m in today_meals), 1),
            "carbs": round(sum(m.get("carbs", 0) for m in today_meals), 1),
            "fat": round(sum(m.get("fat", 0) for m in today_meals), 1)
        }
        
        profile_response = supabase.table("users").select("daily_calorie_goal").eq("user_id", session['user_id']).execute()
        calorie_goal = profile_response.data[0].get("daily_calorie_goal", 2000) if profile_response.data else 2000
        
        return jsonify({
            "success": True, "today_meals": today_meals, "all_meals": all_meals, "totals": totals,
            "calorie_goal": calorie_goal, "streak": get_streak(session['user_id']),
            "achievements": get_achievements(session['user_id'], get_streak(session['user_id']), len(all_meals)),
            "total_meals": len(all_meals)
        })
    except Exception as e: return jsonify({"error": str(e)}), 500


@app.route("/api/meals", methods=["POST"])
@login_required
def api_add_meal():
    try:
        data = request.json
        supabase.table("meals").insert({
            "user_id": session['user_id'], "food_name": data.get("food_name", "Unknown"),
            "calories": int(data.get("calories", 0)), "protein": float(data.get("protein", 0)),
            "carbs": float(data.get("carbs", 0)), "fat": float(data.get("fat", 0)),
            "portion_size": data.get("portion_size", "1 serving"), "cuisine": data.get("cuisine", ""),
            "local_name": data.get("local_name", "")
        }).execute()
        return jsonify({"success": True, "message": "Meal saved!"})
    except Exception as e: return jsonify({"error": str(e)}), 500


@app.route("/api/meals/<int:meal_id>", methods=["DELETE"])
@login_required
def api_delete_meal(meal_id):
    try:
        supabase.table("meals").delete().eq("id", meal_id).eq("user_id", session['user_id']).execute()
        return jsonify({"success": True})
    except Exception as e: return jsonify({"error": str(e)}), 500


# ==================== STATS API ====================

@app.route("/api/stats/weekly", methods=["GET"])
@login_required
def api_weekly_stats():
    try:
        stats = []
        today = datetime.now().date()
        for i in range(7):
            day = today - timedelta(days=6-i)
            response = supabase.table("meals").select("calories").eq("user_id", session['user_id']).gte("created_at", day.isoformat()).lt("created_at", (day + timedelta(days=1)).isoformat()).execute()
            stats.append({"date": day.strftime("%a"), "calories": sum(m.get("calories", 0) for m in (response.data or []))})
        return jsonify({"success": True, "stats": stats})
    except Exception as e: return jsonify({"error": str(e)}), 500


@app.route("/api/stats/monthly", methods=["GET"])
@login_required
def api_monthly_stats():
    try:
        stats = []
        today = datetime.now().date()
        for i in range(30):
            day = today - timedelta(days=29-i)
            response = supabase.table("meals").select("calories").eq("user_id", session['user_id']).gte("created_at", day.isoformat()).lt("created_at", (day + timedelta(days=1)).isoformat()).execute()
            stats.append({"date": day.strftime("%d"), "calories": sum(m.get("calories", 0) for m in (response.data or []))})
        return jsonify({"success": True, "stats": stats})
    except Exception as e: return jsonify({"error": str(e)}), 500


# ==================== AI ANALYZE (IMPROVED) ====================

@app.route("/api/analyze", methods=["POST"])
@login_required
def api_analyze_food():
    try:
        if not ANTHROPIC_API_KEY: return jsonify({"error": "AI not configured"}), 500
        if 'image' not in request.files: return jsonify({"error": "No image"}), 400
        
        file = request.files['image']
        if file.filename == '': return jsonify({"error": "No image selected"}), 400
        
        prefs = get_user_preferences(session['user_id'])
        cuisine_hint = ""
        if prefs["cuisines"]:
            names = [c["name"] for c in CUISINES if c["code"] in prefs["cuisines"]]
            cuisine_hint = f"User typically eats: {', '.join(names)}. Prioritize these cuisines."
        
        base64_image = base64.b64encode(file.read()).decode('utf-8')
        ext = file.filename.lower().split('.')[-1]
        media_type = {"png": "image/png", "gif": "image/gif", "webp": "image/webp"}.get(ext, "image/jpeg")
        
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        prompt = f"""Analyze this food photo. {cuisine_hint}

IMPORTANT: Regional dishes have different nutritional values:
- Tamil Upma ≠ Couscous (Upma has more oil, spices, sometimes vegetables)
- Indian dishes often have ghee/oil that adds calories
- Consider authentic preparation methods

Return ONLY JSON (no markdown):
{{
  "foodName": "accurate English name",
  "localName": "local name (e.g., Upma, Idli, Dosa, Biryani)",
  "cuisine": "specific cuisine (e.g., Tamil, North Indian, Italian)",
  "calories": accurate integer,
  "protein": grams,
  "carbs": grams,
  "fat": grams (include cooking oil!),
  "fiber": grams,
  "portionSize": "description",
  "confidence": "high/medium/low",
  "ingredients": ["main ingredients"],
  "healthTip": "one sentence tip"
}}"""

        message = client.messages.create(
            model="claude-sonnet-4-20250514", max_tokens=1000,
            messages=[{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": base64_image}},
                {"type": "text", "text": prompt}
            ]}]
        )
        
        food_data = json.loads(message.content[0].text.replace('```json', '').replace('```', '').strip())
        return jsonify({"success": True, "food": food_data})
    except json.JSONDecodeError: return jsonify({"error": "Failed to parse AI response"}), 500
    except Exception as e: return jsonify({"error": str(e)}), 500


# ==================== CORRECT FOOD ====================

@app.route("/api/correct", methods=["POST"])
@login_required
def api_correct_food():
    try:
        if not ANTHROPIC_API_KEY: return jsonify({"error": "AI not configured"}), 500
        
        data = request.json
        correct_name = data.get("correct_name", "")
        cuisine = data.get("cuisine", "")
        
        if not correct_name: return jsonify({"error": "Please provide food name"}), 400
        
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        prompt = f"""Provide accurate nutritional info for "{correct_name}" from {cuisine} cuisine.
Consider authentic preparation with typical oil/ghee amounts.

Return ONLY JSON:
{{
  "foodName": "{correct_name}",
  "localName": "local name",
  "cuisine": "{cuisine}",
  "calories": accurate integer,
  "protein": grams,
  "carbs": grams,
  "fat": grams,
  "fiber": grams,
  "portionSize": "typical serving",
  "confidence": "high",
  "ingredients": ["ingredients"],
  "healthTip": "tip"
}}"""

        message = client.messages.create(model="claude-sonnet-4-20250514", max_tokens=1000, messages=[{"role": "user", "content": prompt}])
        food_data = json.loads(message.content[0].text.replace('```json', '').replace('```', '').strip())
        return jsonify({"success": True, "food": food_data})
    except Exception as e: return jsonify({"error": str(e)}), 500


# ==================== AI RECOMMENDATIONS ====================

@app.route("/api/recommend", methods=["POST"])
@login_required
def api_recommend_food():
    try:
        if not ANTHROPIC_API_KEY: return jsonify({"error": "AI not configured"}), 500
        
        data = request.json
        current_food = data.get("current_food", {})
        prefs = get_user_preferences(session['user_id'])
        
        goal_text = {"lose": "LOWER calorie, higher protein alternatives", "gain": "HIGHER calorie, protein-rich alternatives"}.get(prefs["goal"], "balanced alternatives")
        cuisine_names = [c["name"] for c in CUISINES if c["code"] in prefs["cuisines"]] or ["any"]
        
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        prompt = f"""User ate: {current_food.get('foodName', 'meal')} ({current_food.get('calories', 0)} kcal, {current_food.get('cuisine', 'unknown')} cuisine)
User goal: {prefs['goal']} weight
Preferred cuisines: {', '.join(cuisine_names)}

Suggest 3 {goal_text} from similar cuisines.

Return ONLY JSON array:
[{{"name": "dish", "localName": "local name", "cuisine": "type", "calories": int, "protein": g, "carbs": g, "fat": g, "reason": "why better for goal", "recipe_tip": "quick healthy tip"}}]"""

        message = client.messages.create(model="claude-sonnet-4-20250514", max_tokens=1500, messages=[{"role": "user", "content": prompt}])
        recommendations = json.loads(message.content[0].text.replace('```json', '').replace('```', '').strip())
        return jsonify({"success": True, "recommendations": recommendations, "goal": prefs["goal"]})
    except Exception as e: return jsonify({"error": str(e)}), 500


# ==================== RECIPES ====================

@app.route("/api/recipes", methods=["POST"])
@login_required
def api_get_recipes():
    try:
        if not ANTHROPIC_API_KEY: return jsonify({"error": "AI not configured"}), 500
        
        data = request.json
        meal_type = data.get("meal_type", "any")
        prefs = get_user_preferences(session['user_id'])
        cuisine_names = [c["name"] for c in CUISINES if c["code"] in prefs["cuisines"]] or ["various"]
        
        cal_range = {"lose": "under 400", "gain": "500+"}.get(prefs["goal"], "400-500")
        
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        prompt = f"""Create 3 {meal_type} recipes.
Cuisines: {', '.join(cuisine_names)}
Goal: {prefs['goal']} weight ({cal_range} kcal/serving)

Return ONLY JSON array:
[{{
  "name": "recipe name",
  "localName": "traditional name",
  "cuisine": "type",
  "prepTime": "time",
  "calories": int,
  "protein": g,
  "carbs": g,
  "fat": g,
  "ingredients": ["ingredient with amount"],
  "steps": ["step 1", "step 2"],
  "healthyTip": "substitution or tip"
}}]"""

        message = client.messages.create(model="claude-sonnet-4-20250514", max_tokens=2000, messages=[{"role": "user", "content": prompt}])
        recipes = json.loads(message.content[0].text.replace('```json', '').replace('```', '').strip())
        return jsonify({"success": True, "recipes": recipes})
    except Exception as e: return jsonify({"error": str(e)}), 500


# ==================== SUGGESTIONS ====================

@app.route("/api/suggest", methods=["POST"])
@login_required
def api_suggest_meals():
    try:
        if not ANTHROPIC_API_KEY: return jsonify({"error": "AI not configured"}), 500
        
        data = request.json
        remaining = data.get("remaining_calories", 500)
        prefs = get_user_preferences(session['user_id'])
        cuisine_names = [c["name"] for c in CUISINES if c["code"] in prefs["cuisines"]] or ["any"]
        
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        prompt = f"""Suggest 3 meals for {remaining} remaining calories.
Cuisines: {', '.join(cuisine_names)}

Return ONLY JSON array:
[{{"name": "meal", "localName": "local", "cuisine": "type", "calories": int, "protein": g, "description": "brief"}}]"""

        message = client.messages.create(model="claude-sonnet-4-20250514", max_tokens=1000, messages=[{"role": "user", "content": prompt}])
        suggestions = json.loads(message.content[0].text.replace('```json', '').replace('```', '').strip())
        return jsonify({"success": True, "suggestions": suggestions})
    except Exception as e: return jsonify({"error": str(e)}), 500


# ==================== EXPORT ====================

@app.route("/api/export/csv", methods=["GET"])
@login_required
def api_export_csv():
    try:
        response = supabase.table("meals").select("*").eq("user_id", session['user_id']).order("created_at", desc=True).execute()
        lines = ["Date,Food,LocalName,Cuisine,Calories,Protein,Carbs,Fat,Portion"]
        for m in (response.data or []):
            lines.append(f'{m.get("created_at","")[:10]},{m.get("food_name","")},{m.get("local_name","")},{m.get("cuisine","")},{m.get("calories",0)},{m.get("protein",0)},{m.get("carbs",0)},{m.get("fat",0)},{m.get("portion_size","")}')
        return jsonify({"success": True, "csv": "\n".join(lines), "filename": f"caloriesnap_{datetime.now().strftime('%Y%m%d')}.csv"})
    except Exception as e: return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=False)

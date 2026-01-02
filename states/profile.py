"""
states/profile.py - Profile State
Handles user profile data and fitness calculations
"""

import reflex as rx
from .auth import supabase, AuthState


class ProfileState(rx.State):
    """User profile state management"""
    
    # Profile data
    weight_kg: float = 70.0
    height_cm: float = 170.0
    age: int = 25
    gender: str = "male"
    activity_level: str = "moderate"
    goal: str = "maintain"
    daily_calorie_goal: int = 2000
    
    def load_profile(self):
        """Load user profile from database"""
        if not AuthState.user_id:
            return
        
        try:
            response = supabase.table("users").select("*").eq("user_id", AuthState.user_id).execute()
            
            if response.data:
                profile = response.data[0]
                self.weight_kg = profile.get("weight_kg") or 70.0
                self.height_cm = profile.get("height_cm") or 170.0
                self.age = profile.get("age") or 25
                self.gender = profile.get("gender", "male")
                self.activity_level = profile.get("activity_level", "moderate")
                self.goal = profile.get("goal", "maintain")
                self.daily_calorie_goal = profile.get("daily_calorie_goal", 2000)
                
        except Exception as e:
            print(f"Error loading profile: {e}")
    
    def calculate_bmr(self, weight: float, height: float, age: int, gender: str) -> float:
        """Calculate Basal Metabolic Rate (Mifflin-St Jeor)"""
        if gender == "male":
            bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
        else:
            bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
        return bmr
    
    def calculate_tdee(self, bmr: float, activity_level: str) -> float:
        """Calculate Total Daily Energy Expenditure"""
        activity_multipliers = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725,
            "very_active": 1.9
        }
        return bmr * activity_multipliers.get(activity_level, 1.55)
    
    def calculate_calorie_goal(self, tdee: float, goal: str) -> int:
        """Calculate daily calorie goal based on fitness goal"""
        if goal == "lose":
            return int(tdee - 500)  # 500 kcal deficit
        elif goal == "gain":
            return int(tdee + 300)  # 300 kcal surplus
        else:
            return int(tdee)  # Maintain
    
    def update_profile(self, form_data: dict):
        """Update user profile"""
        try:
            # Parse form data
            weight = float(form_data.get("weight_kg", self.weight_kg))
            height = float(form_data.get("height_cm", self.height_cm))
            age = int(form_data.get("age", self.age))
            gender = form_data.get("gender", self.gender)
            activity = form_data.get("activity_level", self.activity_level)
            goal = form_data.get("goal", self.goal)
            
            # Calculate new calorie goal
            bmr = self.calculate_bmr(weight, height, age, gender)
            tdee = self.calculate_tdee(bmr, activity)
            new_calorie_goal = self.calculate_calorie_goal(tdee, goal)
            
            # Update database
            supabase.table("users").update({
                "weight_kg": weight,
                "height_cm": height,
                "age": age,
                "gender": gender,
                "activity_level": activity,
                "goal": goal,
                "daily_calorie_goal": new_calorie_goal
            }).eq("user_id", AuthState.user_id).execute()
            
            # Update local state
            self.weight_kg = weight
            self.height_cm = height
            self.age = age
            self.gender = gender
            self.activity_level = activity
            self.goal = goal
            self.daily_calorie_goal = new_calorie_goal
            
            return rx.window_alert(f"Profile updated! Your new calorie goal is {new_calorie_goal} kcal/day")
            
        except Exception as e:
            return rx.window_alert(f"Update failed: {str(e)}")
    
    @rx.var
    def bmr(self) -> int:
        """Current BMR"""
        return int(self.calculate_bmr(self.weight_kg, self.height_cm, self.age, self.gender))
    
    @rx.var
    def tdee(self) -> int:
        """Current TDEE"""
        return int(self.calculate_tdee(self.bmr, self.activity_level))

"""
states/meals.py - Meals State
Handles meal tracking, AI food analysis, and meal CRUD
"""

import reflex as rx
from typing import List, Dict, Optional
import anthropic
import base64
import json
from datetime import datetime
from .auth import supabase, AuthState


class MealState(rx.State):
    """Meals state management"""
    
    # Meals data
    meals: List[Dict] = []
    today_meals: List[Dict] = []
    
    # AI Analysis
    analyzing: bool = False
    analyzed_food: Optional[Dict] = None
    anthropic_api_key: str = ""
    
    def load_meals(self):
        """Load user's meals from database"""
        if not AuthState.user_id:
            return
        
        try:
            # All meals (last 50)
            response = supabase.table("meals").select("*").eq(
                "user_id", AuthState.user_id
            ).order("created_at", desc=True).limit(50).execute()
            
            self.meals = response.data if response.data else []
            
            # Today's meals
            today = datetime.now().date().isoformat()
            today_response = supabase.table("meals").select("*").eq(
                "user_id", AuthState.user_id
            ).gte("created_at", today).execute()
            
            self.today_meals = today_response.data if today_response.data else []
            
        except Exception as e:
            print(f"Error loading meals: {e}")
            self.meals = []
            self.today_meals = []
    
    async def analyze_food(self, files: List[rx.UploadFile]):
        """Analyze food image with Claude Vision API"""
        
        # Validation
        if not files:
            return rx.window_alert("Please upload an image")
        
        if not self.anthropic_api_key:
            return rx.window_alert("Please enter your Anthropic API key first")
        
        self.analyzing = True
        yield
        
        try:
            # Read image file
            file = files[0]
            image_data = await file.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Call Claude Vision API
            client = anthropic.Anthropic(api_key=self.anthropic_api_key)
            
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
                                    "media_type": "image/jpeg",
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
            
            # Save to state
            self.analyzed_food = food_data
            self.analyzing = False
            
            yield rx.window_alert("Food analyzed successfully!")
            
        except Exception as e:
            self.analyzing = False
            yield rx.window_alert(f"Analysis failed: {str(e)}")
    
    def save_meal(self):
        """Save analyzed meal to database"""
        if not self.analyzed_food:
            return rx.window_alert("No food data to save")
        
        if not AuthState.user_id:
            return rx.window_alert("Please login first")
        
        try:
            # Insert into database
            supabase.table("meals").insert({
                "user_id": AuthState.user_id,
                "food_name": self.analyzed_food["foodName"],
                "calories": int(self.analyzed_food["calories"]),
                "protein": float(self.analyzed_food["protein"]),
                "carbs": float(self.analyzed_food["carbs"]),
                "fat": float(self.analyzed_food["fat"]),
                "portion_size": self.analyzed_food["portionSize"],
                "confidence": self.analyzed_food.get("confidence", "medium"),
                "meal_time": "lunch"
            }).execute()
            
            # Clear analyzed food
            self.analyzed_food = None
            
            # Reload meals
            self.load_meals()
            
            return rx.window_alert("Meal saved successfully!")
            
        except Exception as e:
            return rx.window_alert(f"Save failed: {str(e)}")
    
    def delete_meal(self, meal_id: int):
        """Delete a meal"""
        try:
            supabase.table("meals").delete().eq("id", meal_id).execute()
            self.load_meals()
            return rx.window_alert("Meal deleted")
        except Exception as e:
            return rx.window_alert(f"Delete failed: {str(e)}")
    
    def clear_analyzed_food(self):
        """Clear the analyzed food data"""
        self.analyzed_food = None
    
    # Computed properties
    @rx.var
    def today_calories(self) -> int:
        """Total calories today"""
        return sum(meal.get("calories", 0) for meal in self.today_meals)
    
    @rx.var
    def today_protein(self) -> float:
        """Total protein today"""
        return round(sum(meal.get("protein", 0) for meal in self.today_meals), 1)
    
    @rx.var
    def today_carbs(self) -> float:
        """Total carbs today"""
        return round(sum(meal.get("carbs", 0) for meal in self.today_meals), 1)
    
    @rx.var
    def today_fat(self) -> float:
        """Total fat today"""
        return round(sum(meal.get("fat", 0) for meal in self.today_meals), 1)
    
    @rx.var
    def today_meal_count(self) -> int:
        """Number of meals today"""
        return len(self.today_meals)
    
    @rx.var
    def total_meal_count(self) -> int:
        """Total number of meals"""
        return len(self.meals)

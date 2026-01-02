"""
states/auth.py - Authentication State
Handles user login, signup, and logout
"""

import reflex as rx
from supabase import create_client, Client

# Supabase Config
SUPABASE_URL = "https://sfvovdpzhyubjctrdpwg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InNmdm92ZHB6aHl1YmpjdHJkcHdnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NzM0MjczNCwiZXhwIjoyMDgyOTE4NzM0fQ.dSBya9887OWg8zBU8j_FY4TUQ9AZxMLfSgjyWtdYs4s"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class AuthState(rx.State):
    """Authentication state management"""
    
    # User data
    is_logged_in: bool = False
    user_id: str = ""
    user_email: str = ""
    access_token: str = ""
    
    def signup(self, form_data: dict):
        """Sign up new user"""
        try:
            # Validate
            if not form_data.get("email") or not form_data.get("password"):
                return rx.window_alert("Please fill all fields")
            
            if len(form_data.get("password", "")) < 6:
                return rx.window_alert("Password must be at least 6 characters")
            
            # Create auth user
            auth_response = supabase.auth.sign_up({
                "email": form_data["email"],
                "password": form_data["password"]
            })
            
            if auth_response.user:
                # Create profile
                supabase.table("users").insert({
                    "user_id": auth_response.user.id,
                    "email": form_data["email"],
                    "full_name": form_data.get("full_name", "User"),
                    "daily_calorie_goal": 2000,
                    "activity_level": "moderate",
                    "goal": "maintain"
                }).execute()
                
                return rx.window_alert("Account created successfully! Please login.")
            else:
                return rx.window_alert("Signup failed. Please try again.")
            
        except Exception as e:
            return rx.window_alert(f"Error: {str(e)}")
    
    def login(self, form_data: dict):
        """Login user"""
        try:
            # Validate
            if not form_data.get("email") or not form_data.get("password"):
                return rx.window_alert("Please fill all fields")
            
            # Login
            auth_response = supabase.auth.sign_in_with_password({
                "email": form_data["email"],
                "password": form_data["password"]
            })
            
            if auth_response.user and auth_response.session:
                self.is_logged_in = True
                self.user_id = auth_response.user.id
                self.user_email = auth_response.user.email
                self.access_token = auth_response.session.access_token
                
                return rx.redirect("/dashboard")
            else:
                return rx.window_alert("Invalid credentials")
            
        except Exception as e:
            return rx.window_alert(f"Login failed: {str(e)}")
    
    def logout(self):
        """Logout user"""
        try:
            supabase.auth.sign_out()
        except:
            pass
        
        self.is_logged_in = False
        self.user_id = ""
        self.user_email = ""
        self.access_token = ""
        
        return rx.redirect("/")

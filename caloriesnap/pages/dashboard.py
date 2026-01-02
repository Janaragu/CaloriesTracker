"""
pages/dashboard.py - Main Dashboard
Complete dashboard with Overview, Add Meal, and Settings tabs
"""

import reflex as rx
from ..components.navbar import navbar
from ..components.cards import stat_card, meal_card, info_card
from ..states.auth import AuthState
from ..states.profile import ProfileState
from ..states.meals import MealState


def overview_tab() -> rx.Component:
    """Overview tab - Today's progress and meals"""
    return rx.vstack(
        # Header
        rx.heading("Today's Progress", size="7", font_weight="700", margin_bottom="6"),
        
        # Stats Grid
        rx.grid(
            stat_card("Calories", f"{MealState.today_calories} / {ProfileState.daily_calorie_goal}", "green"),
            stat_card("Protein", f"{MealState.today_protein}g", "blue"),
            stat_card("Carbs", f"{MealState.today_carbs}g", "purple"),
            stat_card("Fat", f"{MealState.today_fat}g", "orange"),
            columns=rx.breakpoints(initial="1", sm="2", lg="4"),
            spacing="4",
            margin_bottom="8",
            width="100%"
        ),
        
        # Today's Meals
        rx.heading("Today's Meals", size="6", font_weight="600", margin_bottom="4"),
        
        rx.cond(
            MealState.today_meals,
            rx.vstack(
                rx.foreach(MealState.today_meals, meal_card),
                spacing="2",
                width="100%"
            ),
            rx.card(
                rx.text(
                    "No meals logged today. Add your first meal in the 'Add Meal' tab!",
                    color="gray.500",
                    text_align="center"
                ),
                padding="8"
            )
        ),
        
        spacing="6",
        width="100%"
    )


def add_meal_tab() -> rx.Component:
    """Add Meal tab - Photo upload and AI analysis"""
    return rx.vstack(
        rx.heading("Add New Meal", size="7", font_weight="700", margin_bottom="6"),
        
        # API Key Input
        rx.cond(
            MealState.anthropic_api_key == "",
            rx.card(
                rx.vstack(
                    rx.text("Enter your Anthropic API Key:", font_weight="600", size="3"),
                    rx.input(
                        placeholder="sk-ant-...",
                        on_change=MealState.set_anthropic_api_key,
                        size="3",
                        width="100%",
                        type="password"
                    ),
                    rx.link(
                        "Get API key at console.anthropic.com →",
                        href="https://console.anthropic.com",
                        color="green.600",
                        size="2"
                    ),
                    spacing="3",
                    width="100%"
                ),
                padding="6",
                margin_bottom="6",
                bg="blue.50"
            )
        ),
        
        # Upload Section
        rx.card(
            rx.vstack(
                rx.upload(
                    rx.vstack(
                        rx.icon("camera", size=48, color="green.500"),
                        rx.text("Upload Food Photo", font_weight="600", size="4"),
                        rx.text(
                            "Click to upload or drag and drop",
                            color="gray.500",
                            size="2"
                        ),
                        spacing="2",
                        align_items="center"
                    ),
                    id="upload_food",
                    accept={"image/*": [".jpg", ".jpeg", ".png"]},
                    max_files=1,
                    disabled=MealState.analyzing,
                    border="2px dashed",
                    border_color="gray.300",
                    padding="12",
                    border_radius="lg",
                    _hover={"border_color": "green.500", "bg": "green.50"}
                ),
                
                rx.button(
                    rx.cond(
                        MealState.analyzing,
                        rx.hstack(
                            rx.spinner(size="3"),
                            rx.text("Analyzing..."),
                            spacing="2"
                        ),
                        rx.hstack(
                            rx.icon("sparkles", size=20),
                            rx.text("Analyze with AI"),
                            spacing="2"
                        )
                    ),
                    on_click=MealState.analyze_food(rx.upload_files(upload_id="upload_food")),
                    size="4",
                    color_scheme="green",
                    width="100%",
                    disabled=MealState.analyzing
                ),
                
                spacing="6",
                width="100%"
            ),
            padding="8"
        ),
        
        # Analysis Results
        rx.cond(
            MealState.analyzed_food,
            rx.card(
                rx.vstack(
                    rx.heading("Analysis Results", size="5", font_weight="600", color="green.600"),
                    
                    rx.divider(),
                    
                    rx.vstack(
                        rx.heading(MealState.analyzed_food["foodName"], size="7", font_weight="700"),
                        rx.heading(
                            f"{MealState.analyzed_food['calories']} kcal",
                            size="8",
                            color="green.600",
                            font_weight="700"
                        ),
                        rx.text(
                            f"Portion: {MealState.analyzed_food['portionSize']}",
                            color="gray.600",
                            size="3"
                        ),
                        rx.hstack(
                            rx.badge(f"P: {MealState.analyzed_food['protein']}g", color_scheme="blue"),
                            rx.badge(f"C: {MealState.analyzed_food['carbs']}g", color_scheme="purple"),
                            rx.badge(f"F: {MealState.analyzed_food['fat']}g", color_scheme="orange"),
                            spacing="2"
                        ),
                        spacing="3",
                        align_items="center"
                    ),
                    
                    rx.hstack(
                        rx.button(
                            "Save Meal",
                            on_click=MealState.save_meal,
                            size="3",
                            color_scheme="green",
                            flex="1"
                        ),
                        rx.button(
                            "Cancel",
                            on_click=MealState.clear_analyzed_food,
                            size="3",
                            variant="outline",
                            color_scheme="gray",
                            flex="1"
                        ),
                        spacing="3",
                        width="100%"
                    ),
                    
                    spacing="6",
                    width="100%"
                ),
                padding="8",
                bg="green.50",
                border="2px solid",
                border_color="green.200"
            )
        ),
        
        spacing="6",
        width="100%"
    )


def settings_tab() -> rx.Component:
    """Settings tab - Profile management"""
    return rx.vstack(
        rx.heading("Profile Settings", size="7", font_weight="700", margin_bottom="6"),
        
        # Profile Form
        rx.card(
            rx.form(
                rx.vstack(
                    # Body Metrics
                    rx.text("Body Metrics", font_weight="600", size="4"),
                    rx.grid(
                        rx.vstack(
                            rx.text("Weight (kg)", size="2", color="gray.600"),
                            rx.input(
                                placeholder="70",
                                name="weight_kg",
                                type="number",
                                default_value=ProfileState.weight_kg,
                                size="3"
                            ),
                            spacing="1",
                            align_items="start",
                            width="100%"
                        ),
                        rx.vstack(
                            rx.text("Height (cm)", size="2", color="gray.600"),
                            rx.input(
                                placeholder="170",
                                name="height_cm",
                                type="number",
                                default_value=ProfileState.height_cm,
                                size="3"
                            ),
                            spacing="1",
                            align_items="start",
                            width="100%"
                        ),
                        rx.vstack(
                            rx.text("Age", size="2", color="gray.600"),
                            rx.input(
                                placeholder="25",
                                name="age",
                                type="number",
                                default_value=ProfileState.age,
                                size="3"
                            ),
                            spacing="1",
                            align_items="start",
                            width="100%"
                        ),
                        columns=rx.breakpoints(initial="1", sm="3"),
                        spacing="4",
                        width="100%"
                    ),
                    
                    rx.divider(),
                    
                    # Fitness Settings
                    rx.text("Fitness Settings", font_weight="600", size="4"),
                    rx.grid(
                        rx.vstack(
                            rx.text("Gender", size="2", color="gray.600"),
                            rx.select(
                                ["male", "female"],
                                name="gender",
                                default_value=ProfileState.gender,
                                size="3"
                            ),
                            spacing="1",
                            align_items="start",
                            width="100%"
                        ),
                        rx.vstack(
                            rx.text("Activity Level", size="2", color="gray.600"),
                            rx.select(
                                ["sedentary", "light", "moderate", "active", "very_active"],
                                name="activity_level",
                                default_value=ProfileState.activity_level,
                                size="3"
                            ),
                            spacing="1",
                            align_items="start",
                            width="100%"
                        ),
                        rx.vstack(
                            rx.text("Goal", size="2", color="gray.600"),
                            rx.select(
                                ["lose", "maintain", "gain"],
                                name="goal",
                                default_value=ProfileState.goal,
                                size="3"
                            ),
                            spacing="1",
                            align_items="start",
                            width="100%"
                        ),
                        columns=rx.breakpoints(initial="1", sm="3"),
                        spacing="4",
                        width="100%"
                    ),
                    
                    # Submit Button
                    rx.button(
                        "Save Profile",
                        type="submit",
                        size="4",
                        color_scheme="green",
                        width="100%"
                    ),
                    
                    spacing="6",
                    width="100%"
                ),
                on_submit=ProfileState.update_profile
            ),
            padding="8"
        ),
        
        # Current Goals Display
        rx.grid(
            info_card("Daily Calorie Goal", f"{ProfileState.daily_calorie_goal} kcal", "Automatically calculated"),
            info_card("BMR", f"{ProfileState.bmr} kcal", "Basal Metabolic Rate"),
            info_card("TDEE", f"{ProfileState.tdee} kcal", "Total Daily Energy"),
            columns=rx.breakpoints(initial="1", sm="3"),
            spacing="4",
            width="100%",
            margin_top="6"
        ),
        
        spacing="6",
        width="100%"
    )


def dashboard_page() -> rx.Component:
    """Main dashboard page with tabs"""
    return rx.box(
        navbar(),
        
        rx.container(
            rx.tabs(
                rx.tab_list(
                    rx.tab("Overview", value="overview"),
                    rx.tab("Add Meal", value="add_meal"),
                    rx.tab("Settings", value="settings"),
                ),
                
                rx.tab_panels(
                    rx.tab_panel(overview_tab(), value="overview"),
                    rx.tab_panel(add_meal_tab(), value="add_meal"),
                    rx.tab_panel(settings_tab(), value="settings"),
                ),
                
                default_value="overview",
                margin_top="6"
            ),
            
            max_width="1200px",
            padding="4"
        ),
        
        min_height="100vh",
        bg="gray.50",
        on_mount=[ProfileState.load_profile, MealState.load_meals]
    )

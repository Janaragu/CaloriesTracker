"""
components/cards.py - Reusable Card Components
"""

import reflex as rx
from typing import Dict


def stat_card(label: str, value: str, color: str = "green") -> rx.Component:
    """Statistics card component"""
    return rx.card(
        rx.vstack(
            rx.text(
                label,
                size="2",
                color="gray.500",
                font_weight="600",
                text_transform="uppercase",
                letter_spacing="wider"
            ),
            rx.heading(
                value,
                size="8",
                color=f"{color}.600",
                font_weight="700"
            ),
            spacing="2",
            align_items="center"
        ),
        padding="6",
        _hover={"transform": "translateY(-2px)", "box_shadow": "lg"},
        transition="all 0.2s"
    )


def meal_card(meal: Dict) -> rx.Component:
    """Meal card component"""
    from ..states.meals import MealState
    
    return rx.card(
        rx.hstack(
            # Meal info
            rx.vstack(
                rx.heading(
                    meal.get("food_name", "Unknown"),
                    size="5",
                    font_weight="600"
                ),
                rx.text(
                    f"{meal.get('calories', 0)} kcal",
                    color="green.600",
                    font_weight="600",
                    size="4"
                ),
                rx.text(
                    meal.get("portion_size", ""),
                    color="gray.500",
                    size="2"
                ),
                rx.text(
                    f"P: {meal.get('protein', 0)}g • C: {meal.get('carbs', 0)}g • F: {meal.get('fat', 0)}g",
                    color="gray.600",
                    size="2"
                ),
                align_items="start",
                spacing="1",
                flex="1"
            ),
            
            rx.spacer(),
            
            # Delete button
            rx.button(
                rx.icon("trash-2", size=16),
                on_click=lambda: MealState.delete_meal(meal["id"]),
                color_scheme="red",
                variant="soft",
                size="2"
            ),
            
            width="100%",
            align_items="start"
        ),
        padding="4",
        margin_y="2",
        _hover={"box_shadow": "md"},
        transition="all 0.2s"
    )


def feature_card(icon: str, title: str, description: str) -> rx.Component:
    """Feature card for landing page"""
    return rx.card(
        rx.vstack(
            # Icon
            rx.box(
                rx.icon(icon, size=32, color="white"),
                bg="linear-gradient(135deg, #10b981 0%, #059669 100%)",
                padding="4",
                border_radius="xl"
            ),
            
            # Title
            rx.heading(
                title,
                size="5",
                font_weight="600"
            ),
            
            # Description
            rx.text(
                description,
                color="gray.600",
                text_align="center",
                line_height="1.6"
            ),
            
            spacing="4",
            align_items="center"
        ),
        padding="8",
        _hover={"transform": "translateY(-4px)", "box_shadow": "xl"},
        transition="all 0.3s"
    )


def info_card(title: str, value: str, description: str = "") -> rx.Component:
    """Information card component"""
    return rx.card(
        rx.vstack(
            rx.heading(title, size="4", font_weight="600"),
            rx.heading(value, size="8", color="green.600", font_weight="700"),
            rx.cond(
                description != "",
                rx.text(description, color="gray.500", size="2"),
                rx.box()
            ),
            spacing="2"
        ),
        padding="6"
    )

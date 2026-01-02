"""
components/navbar.py - Navigation Bar Component
"""

import reflex as rx
from ..states.auth import AuthState


def navbar() -> rx.Component:
    """Main navigation bar"""
    return rx.box(
        rx.hstack(
            # Logo
            rx.link(
                rx.heading(
                    "CalorieSnap",
                    size="7",
                    color="green.600",
                    _hover={"color": "green.700"}
                ),
                href="/"
            ),
            
            rx.spacer(),
            
            # Navigation links
            rx.cond(
                AuthState.is_logged_in,
                # Logged in - show user email and logout
                rx.hstack(
                    rx.text(
                        f"👋 {AuthState.user_email}",
                        color="gray.700",
                        font_weight="500"
                    ),
                    rx.button(
                        "Logout",
                        on_click=AuthState.logout,
                        color_scheme="red",
                        variant="outline",
                        size="2"
                    ),
                    spacing="4"
                ),
                # Not logged in - show login/signup
                rx.hstack(
                    rx.link(
                        rx.button(
                            "Login",
                            variant="outline",
                            size="2"
                        ),
                        href="/login"
                    ),
                    rx.link(
                        rx.button(
                            "Sign Up",
                            color_scheme="green",
                            size="2"
                        ),
                        href="/signup"
                    ),
                    spacing="3"
                )
            ),
            
            width="100%",
            padding="4",
            align_items="center"
        ),
        bg="white",
        box_shadow="sm",
        position="sticky",
        top="0",
        z_index="1000",
        width="100%"
    )

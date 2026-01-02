"""
pages/auth.py - Authentication Pages (Login & Signup)
"""

import reflex as rx
from components import navbar
from states.auth import AuthState


def login_page() -> rx.Component:
    """Login page"""
    return rx.box(
        navbar(),
        
        rx.center(
            rx.card(
                rx.vstack(
                    # Header
                    rx.vstack(
                        rx.heading("Welcome Back", size="8", font_weight="700"),
                        rx.text(
                            "Sign in to your account to continue",
                            color="gray.600",
                            size="3"
                        ),
                        spacing="2",
                        align_items="center",
                        margin_bottom="6"
                    ),
                    
                    # Login Form
                    rx.form(
                        rx.vstack(
                            rx.input(
                                placeholder="Email",
                                name="email",
                                type="email",
                                size="3",
                                width="100%"
                            ),
                            rx.input(
                                placeholder="Password",
                                name="password",
                                type="password",
                                size="3",
                                width="100%"
                            ),
                            rx.button(
                                "Login",
                                type="submit",
                                size="3",
                                width="100%",
                                color_scheme="green"
                            ),
                            spacing="4",
                            width="100%"
                        ),
                        on_submit=AuthState.login,
                        width="100%"
                    ),
                    
                    # Sign up link
                    rx.hstack(
                        rx.text("Don't have an account?", color="gray.600", size="2"),
                        rx.link(
                            "Sign up",
                            href="/signup",
                            color="green.600",
                            font_weight="600",
                            size="2"
                        ),
                        spacing="2"
                    ),
                    
                    spacing="6",
                    width="100%"
                ),
                padding="8",
                max_width="420px",
                box_shadow="xl"
            ),
            padding_y="20",
            min_height="80vh"
        )
    )


def signup_page() -> rx.Component:
    """Signup page"""
    return rx.box(
        navbar(),
        
        rx.center(
            rx.card(
                rx.vstack(
                    # Header
                    rx.vstack(
                        rx.heading("Create Account", size="8", font_weight="700"),
                        rx.text(
                            "Start your fitness journey today",
                            color="gray.600",
                            size="3"
                        ),
                        spacing="2",
                        align_items="center",
                        margin_bottom="6"
                    ),
                    
                    # Signup Form
                    rx.form(
                        rx.vstack(
                            rx.input(
                                placeholder="Full Name",
                                name="full_name",
                                size="3",
                                width="100%"
                            ),
                            rx.input(
                                placeholder="Email",
                                name="email",
                                type="email",
                                size="3",
                                width="100%"
                            ),
                            rx.input(
                                placeholder="Password (min 6 characters)",
                                name="password",
                                type="password",
                                size="3",
                                width="100%"
                            ),
                            rx.button(
                                "Create Account",
                                type="submit",
                                size="3",
                                width="100%",
                                color_scheme="green"
                            ),
                            spacing="4",
                            width="100%"
                        ),
                        on_submit=AuthState.signup,
                        width="100%"
                    ),
                    
                    # Login link
                    rx.hstack(
                        rx.text("Already have an account?", color="gray.600", size="2"),
                        rx.link(
                            "Login",
                            href="/login",
                            color="green.600",
                            font_weight="600",
                            size="2"
                        ),
                        spacing="2"
                    ),
                    
                    spacing="6",
                    width="100%"
                ),
                padding="8",
                max_width="420px",
                box_shadow="xl"
            ),
            padding_y="20",
            min_height="80vh"
        )
    )

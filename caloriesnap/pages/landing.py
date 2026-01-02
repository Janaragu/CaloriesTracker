"""
pages/landing.py - Landing Page
"""

import reflex as rx
from caloriesnap.components.navbar import navbar
from caloriesnap.components.cards import feature_card


def landing_page() -> rx.Component:
    """Main landing page"""
    return rx.box(
        navbar(),
        
        rx.container(
            # Hero Section
            rx.center(
                rx.vstack(
                    rx.heading(
                        "Food Calorie Tracking",
                        size="9",
                        text_align="center",
                        font_weight="800",
                        background="linear-gradient(135deg, #10b981 0%, #059669 100%)",
                        background_clip="text",
                        color="transparent"
                    ),
                    
                    rx.text(
                        "Professional nutrition analysis powered by AI. Track your meals effortlessly at your fingertips.",
                        size="5",
                        color="gray.600",
                        text_align="center",
                        max_width="700px",
                        line_height="1.6"
                    ),
                    
                    rx.hstack(
                        rx.link(
                            rx.button(
                                "Get Started",
                                size="4",
                                color_scheme="green",
                                _hover={"transform": "translateY(-2px)", "box_shadow": "xl"}
                            ),
                            href="/signup"
                        ),
                        rx.link(
                            rx.button(
                                "Learn More",
                                size="4",
                                variant="outline",
                                color_scheme="gray"
                            ),
                            href="#features"
                        ),
                        spacing="4"
                    ),
                    
                    spacing="6",
                    padding_y="20",
                    align_items="center"
                )
            ),
            
            # Features Section
            rx.box(
                rx.vstack(
                    rx.heading(
                        "Everything You Need for Fitness Success",
                        size="8",
                        text_align="center",
                        font_weight="700"
                    ),
                    rx.text(
                        "Comprehensive tools for tracking, analyzing, and optimizing your nutrition",
                        size="4",
                        color="gray.600",
                        text_align="center",
                        max_width="600px"
                    ),
                    spacing="4",
                    margin_bottom="12"
                ),
                
                rx.grid(
                    feature_card(
                        "camera",
                        "AI Food Recognition",
                        "Simply snap a photo of your meal and let AI identify the food automatically."
                    ),
                    feature_card(
                        "trending-up",
                        "Track Progress",
                        "Visualize your nutrition trends with beautiful charts over time."
                    ),
                    feature_card(
                        "target",
                        "Personalized Goals",
                        "Get custom calorie targets based on your body stats and goals."
                    ),
                    feature_card(
                        "zap",
                        "Smart Recommendations",
                        "Receive intelligent suggestions to optimize your diet."
                    ),
                    feature_card(
                        "shield",
                        "Secure & Private",
                        "Your data is encrypted and stored securely."
                    ),
                    feature_card(
                        "smartphone",
                        "Mobile Optimized",
                        "Works perfectly on any device, track on-the-go."
                    ),
                    
                    columns=rx.breakpoints(initial="1", sm="2", lg="3"),
                    spacing="6",
                    padding_y="12"
                ),
                
                id="features"
            ),
            
            # CTA Section
            rx.center(
                rx.card(
                    rx.vstack(
                        rx.heading(
                            "Ready to Transform Your Health?",
                            size="7",
                            text_align="center",
                            color="white"
                        ),
                        rx.text(
                            "Join thousands of users tracking their nutrition with AI",
                            size="4",
                            color="green.100",
                            text_align="center"
                        ),
                        rx.link(
                            rx.button(
                                "Start Free Today",
                                size="4",
                                variant="solid",
                                bg="white",
                                color="green.600",
                                _hover={"bg": "gray.50"}
                            ),
                            href="/signup"
                        ),
                        spacing="6",
                        align_items="center"
                    ),
                    padding="12",
                    bg="linear-gradient(135deg, #10b981 0%, #059669 100%)",
                    box_shadow="xl",
                    margin_y="12"
                ),
                padding_y="12"
            ),
            
            max_width="1200px",
            padding="4"
        ),
        
        # Footer
        rx.box(
            rx.center(
                rx.text(
                    "© 2026 CalorieSnap. All rights reserved.",
                    color="gray.500",
                    size="2"
                ),
                padding="8"
            ),
            bg="gray.50",
            border_top="1px solid",
            border_color="gray.200",
            width="100%"
        ),
        
        min_height="100vh",
        bg="white"
    )

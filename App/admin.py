"""
admin.py - Admin Panel for CalorieSnap
Complete admin interface for managing users, content, and analytics
"""

import streamlit as st
from database import get_supabase_client
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px

supabase = get_supabase_client()

# Admin credentials (change these!)
ADMIN_EMAIL = "admin@caloriesnap.com"
ADMIN_PASSWORD = "admin123"  # CHANGE THIS!


# ==================== ADMIN AUTHENTICATION ====================

def check_admin_login(email, password):
    """Check if admin credentials are correct"""
    return email == ADMIN_EMAIL and password == ADMIN_PASSWORD


def admin_login_page():
    """Render admin login page"""
    st.markdown("""
    <div style='max-width: 400px; margin: 100px auto; padding: 40px; background: white; border-radius: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.12);'>
        <h2 style='text-align: center; margin-bottom: 30px;'>🔐 Admin Login</h2>
    </div>
    """, unsafe_allow_html=True)

    with st.form("admin_login"):
        email = st.text_input("Admin Email", placeholder="admin@caloriesnap.com")
        password = st.text_input("Admin Password", type="password")

        submit = st.form_submit_button("Login as Admin", type="primary", use_container_width=True)

        if submit:
            if check_admin_login(email, password):
                st.session_state.admin_logged_in = True
                st.success("Admin login successful!")
                st.rerun()
            else:
                st.error("Invalid admin credentials")


# ==================== USER MANAGEMENT ====================

def get_all_users():
    """Get all users from database"""
    try:
        response = supabase.table("users").select("*").order("created_at", desc=True).execute()
        return response.data
    except Exception as e:
        st.error(f"Error loading users: {str(e)}")
        return []


def delete_user(user_id):
    """Delete a user and all their data"""
    try:
        # Supabase will cascade delete meals automatically
        supabase.table("users").delete().eq("user_id", user_id).execute()
        return True, "User deleted successfully"
    except Exception as e:
        return False, f"Error: {str(e)}"


def get_user_stats(user_id):
    """Get statistics for a specific user"""
    try:
        meals = supabase.table("meals").select("*").eq("user_id", user_id).execute()

        total_meals = len(meals.data)
        total_calories = sum(m.get('calories', 0) for m in meals.data)
        avg_calories = total_calories / total_meals if total_meals > 0 else 0

        return {
            'total_meals': total_meals,
            'total_calories': total_calories,
            'avg_calories': round(avg_calories)
        }
    except Exception as e:
        return {'total_meals': 0, 'total_calories': 0, 'avg_calories': 0}


def render_user_management():
    """Render user management interface"""
    st.markdown("### 👥 User Management")

    users = get_all_users()

    if not users:
        st.info("No users registered yet")
        return

    # Overview stats
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Users", len(users))

    with col2:
        active_today = len([u for u in users if u.get('updated_at', '').startswith(datetime.now().date().isoformat())])
        st.metric("Active Today", active_today)

    with col3:
        avg_weight = sum(u.get('weight_kg', 0) for u in users if u.get('weight_kg')) / len(
            [u for u in users if u.get('weight_kg')]) if any(u.get('weight_kg') for u in users) else 0
        st.metric("Avg Weight", f"{avg_weight:.1f} kg")

    with col4:
        goals = [u.get('goal') for u in users if u.get('goal')]
        most_common_goal = max(set(goals), key=goals.count) if goals else "N/A"
        st.metric("Popular Goal", most_common_goal.title())

    st.markdown("---")

    # User table
    st.markdown("#### All Users")

    # Convert to DataFrame for better display
    user_data = []
    for user in users:
        stats = get_user_stats(user['user_id'])
        user_data.append({
            'Email': user['email'],
            'Name': user['full_name'],
            'Goal': user.get('goal', 'N/A').title(),
            'Weight': f"{user.get('weight_kg', 0)} kg" if user.get('weight_kg') else 'N/A',
            'Meals': stats['total_meals'],
            'Avg Cal': stats['avg_calories'],
            'Joined': user['created_at'][:10],
            'User ID': user['user_id']
        })

    df = pd.DataFrame(user_data)

    # Search/Filter
    search = st.text_input("🔍 Search users (email or name)", "")
    if search:
        df = df[df['Email'].str.contains(search, case=False) | df['Name'].str.contains(search, case=False)]

    st.dataframe(df, use_container_width=True, hide_index=True)

    # Delete user
    st.markdown("#### Delete User")
    user_emails = [u['email'] for u in users]
    selected_user = st.selectbox("Select user to delete", ["Select..."] + user_emails)

    if selected_user != "Select...":
        st.warning(f"⚠️ This will permanently delete {selected_user} and all their data!")

        if st.button("🗑️ Delete User", type="secondary"):
            user_id = next(u['user_id'] for u in users if u['email'] == selected_user)
            success, message = delete_user(user_id)

            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)


# ==================== CONTENT MANAGEMENT ====================

def render_content_editor():
    """Edit landing page content"""
    st.markdown("### 📝 Content Editor")

    st.info("Edit the landing page content (Hero section, features, etc.)")

    # Hero Section
    with st.expander("🎯 Hero Section", expanded=True):
        st.markdown("#### Main Headline")
        hero_title = st.text_input("Title", value="Food Calorie Tracking", key="hero_title")

        st.markdown("#### Subtitle")
        hero_subtitle = st.text_area(
            "Subtitle",
            value="Professional nutrition analysis powered by AI. Track your meals effortlessly at your fingertips.",
            key="hero_subtitle"
        )

        if st.button("Save Hero Content"):
            st.success("Hero content saved! (Note: Implement persistence in app_new.py)")

    # Features Section
    with st.expander("✨ Features Section"):
        st.markdown("#### Feature Cards")

        default_features = [
            {"icon": "📸", "title": "AI Food Recognition",
             "desc": "Simply snap a photo of your meal and let AI identify the food and calculate nutrition automatically."},
            {"icon": "💪", "title": "Personalized Goals",
             "desc": "Get custom calorie and macro targets based on your body stats, activity level, and fitness goals."},
            {"icon": "📊", "title": "Progress Tracking",
             "desc": "Visualize your nutrition trends with beautiful charts and detailed analytics over time."},
        ]

        for i, feature in enumerate(default_features):
            col1, col2, col3 = st.columns([1, 2, 5])
            with col1:
                st.text_input(f"Icon {i + 1}", value=feature['icon'], key=f"icon_{i}")
            with col2:
                st.text_input(f"Title {i + 1}", value=feature['title'], key=f"title_{i}")
            with col3:
                st.text_area(f"Description {i + 1}", value=feature['desc'], key=f"desc_{i}", height=100)

        if st.button("Save Features"):
            st.success("Features saved! (Note: Implement persistence)")

    # Color Theme
    with st.expander("🎨 Color Theme"):
        col1, col2, col3 = st.columns(3)

        with col1:
            primary_color = st.color_picker("Primary Color", "#10b981")
        with col2:
            secondary_color = st.color_picker("Secondary Color", "#059669")
        with col3:
            accent_color = st.color_picker("Accent Color", "#3b82f6")

        if st.button("Update Theme"):
            st.success("Theme updated! (Note: Update styles.py)")
            st.code(f"""
# Add to styles.py:
PRIMARY_COLOR = "{primary_color}"
SECONDARY_COLOR = "{secondary_color}"
ACCENT_COLOR = "{accent_color}"
            """)


# ==================== ANALYTICS ====================

def get_platform_stats():
    """Get overall platform statistics"""
    try:
        # Users
        users = supabase.table("users").select("*").execute()
        total_users = len(users.data)

        # Meals
        meals = supabase.table("meals").select("*").execute()
        total_meals = len(meals.data)

        # Today's meals
        today = datetime.now().date().isoformat()
        today_meals = [m for m in meals.data if m['created_at'].startswith(today)]

        # Total calories tracked
        total_calories = sum(m.get('calories', 0) for m in meals.data)

        return {
            'total_users': total_users,
            'total_meals': total_meals,
            'today_meals': len(today_meals),
            'total_calories': total_calories
        }
    except Exception as e:
        st.error(f"Error loading stats: {str(e)}")
        return {'total_users': 0, 'total_meals': 0, 'today_meals': 0, 'total_calories': 0}


def render_analytics_dashboard():
    """Render analytics dashboard"""
    st.markdown("### 📊 Platform Analytics")

    stats = get_platform_stats()

    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 24px; border-radius: 16px; color: white; text-align: center;'>
            <div style='font-size: 0.9rem; opacity: 0.9;'>Total Users</div>
            <div style='font-size: 2.5rem; font-weight: 700; margin: 8px 0;'>{stats['total_users']}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); padding: 24px; border-radius: 16px; color: white; text-align: center;'>
            <div style='font-size: 0.9rem; opacity: 0.9;'>Total Meals</div>
            <div style='font-size: 2.5rem; font-weight: 700; margin: 8px 0;'>{stats['total_meals']}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); padding: 24px; border-radius: 16px; color: white; text-align: center;'>
            <div style='font-size: 0.9rem; opacity: 0.9;'>Today's Meals</div>
            <div style='font-size: 2.5rem; font-weight: 700; margin: 8px 0;'>{stats['today_meals']}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); padding: 24px; border-radius: 16px; color: white; text-align: center;'>
            <div style='font-size: 0.9rem; opacity: 0.9;'>Total Calories</div>
            <div style='font-size: 2.5rem; font-weight: 700; margin: 8px 0;'>{stats['total_calories']:,}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # User Growth Chart
    try:
        users = supabase.table("users").select("created_at").execute()

        # Process data by date
        from collections import defaultdict
        daily_signups = defaultdict(int)

        for user in users.data:
            date = user['created_at'][:10]
            daily_signups[date] += 1

        # Sort by date
        sorted_dates = sorted(daily_signups.keys())
        cumulative = []
        total = 0

        for date in sorted_dates:
            total += daily_signups[date]
            cumulative.append(total)

        # Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=sorted_dates,
            y=cumulative,
            mode='lines+markers',
            name='Total Users',
            line=dict(color='#10b981', width=3),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor='rgba(16, 185, 129, 0.1)'
        ))

        fig.update_layout(
            title="User Growth Over Time",
            height=350,
            margin=dict(l=0, r=0, t=40, b=0),
            plot_bgcolor='white'
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error creating chart: {str(e)}")

    # Goal Distribution
    try:
        users = supabase.table("users").select("goal").execute()
        goals = [u.get('goal', 'maintain') for u in users.data if u.get('goal')]

        goal_counts = {}
        for goal in set(goals):
            goal_counts[goal.title()] = goals.count(goal)

        fig2 = go.Figure(data=[go.Pie(
            labels=list(goal_counts.keys()),
            values=list(goal_counts.values()),
            hole=0.4,
            marker=dict(colors=['#10b981', '#3b82f6', '#f59e0b'])
        )])

        fig2.update_layout(
            title="User Fitness Goals Distribution",
            height=350
        )

        st.plotly_chart(fig2, use_container_width=True)

    except Exception as e:
        st.error(f"Error creating pie chart: {str(e)}")


# ==================== DATABASE MANAGEMENT ====================

def render_database_management():
    """Database management tools"""
    st.markdown("### 🗄️ Database Management")

    st.warning("⚠️ Dangerous operations - use with caution!")

    # View raw data
    with st.expander("👁️ View Raw Data"):
        table = st.selectbox("Select table", ["users", "meals"])

        if st.button("Load Data"):
            try:
                data = supabase.table(table).select("*").limit(100).execute()
                df = pd.DataFrame(data.data)
                st.dataframe(df, use_container_width=True)

                # Export option
                csv = df.to_csv(index=False)
                st.download_button(
                    "📥 Download as CSV",
                    csv,
                    f"{table}_export.csv",
                    "text/csv"
                )
            except Exception as e:
                st.error(f"Error: {str(e)}")

    # Bulk operations
    with st.expander("⚡ Bulk Operations"):
        st.markdown("#### Delete Old Data")

        days = st.number_input("Delete meals older than (days)", min_value=7, value=30)

        if st.button("🗑️ Delete Old Meals", type="secondary"):
            try:
                cutoff_date = (datetime.now() - timedelta(days=days)).date().isoformat()
                result = supabase.table("meals").delete().lt("created_at", cutoff_date).execute()
                st.success(f"Deleted meals older than {days} days")
            except Exception as e:
                st.error(f"Error: {str(e)}")

    # Backup
    with st.expander("💾 Backup & Restore"):
        st.markdown("#### Export Full Backup")

        if st.button("📦 Create Backup"):
            try:
                users = supabase.table("users").select("*").execute()
                meals = supabase.table("meals").select("*").execute()

                backup_data = {
                    'users': users.data,
                    'meals': meals.data,
                    'timestamp': datetime.now().isoformat()
                }

                import json
                json_str = json.dumps(backup_data, indent=2)

                st.download_button(
                    "📥 Download Backup (JSON)",
                    json_str,
                    f"caloriesnap_backup_{datetime.now().strftime('%Y%m%d')}.json",
                    "application/json"
                )

                st.success("Backup created successfully!")

            except Exception as e:
                st.error(f"Error: {str(e)}")


# ==================== MAIN ADMIN PANEL ====================

def render_admin_panel():
    """Main admin panel interface"""

    # Top bar
    col1, col2 = st.columns([6, 1])
    with col1:
        st.markdown("# 🔧 CalorieSnap Admin Panel")
    with col2:
        if st.button("Logout"):
            st.session_state.admin_logged_in = False
            st.rerun()

    st.markdown("---")

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Analytics", "👥 Users", "📝 Content", "🗄️ Database"])

    with tab1:
        render_analytics_dashboard()

    with tab2:
        render_user_management()

    with tab3:
        render_content_editor()

    with tab4:
        render_database_management()


# ==================== MAIN FUNCTION ====================

def admin_main():
    """Main entry point for admin panel"""

    # Initialize session state
    if 'admin_logged_in' not in st.session_state:
        st.session_state.admin_logged_in = False

    # Check if logged in
    if not st.session_state.admin_logged_in:
        admin_login_page()
    else:
        render_admin_panel()


if __name__ == "__main__":
    # Page config
    st.set_page_config(
        page_title="CalorieSnap Admin",
        page_icon="🔧",
        layout="wide"
    )

    admin_main()
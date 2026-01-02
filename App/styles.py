"""
styles.py - All CSS styling for CalorieSnap
Separated from main app for better organization
"""


def get_styles():
    """Returns all CSS styles as a string"""
    return """
    <style>
        /* Import Professional Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        /* Global Resets & Base */
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* Hide Streamlit Branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Main Container */
        .main {
            padding: 0;
            background: #f8f9fa;
        }

        .block-container {
            padding: 0 !important;
            max-width: 100% !important;
        }

        /* ==================== HERO SECTION ==================== */
        .hero-section {
            background: linear-gradient(135deg, #1e3a5f 0%, #2d5a7b 100%);
            padding: 80px 40px;
            color: white;
            position: relative;
            overflow: hidden;
        }

        .hero-content {
            max-width: 1200px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 60px;
            align-items: center;
        }

        .hero-text h1 {
            font-size: 3.5rem;
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 20px;
            letter-spacing: -1px;
        }

        .hero-text p {
            font-size: 1.1rem;
            opacity: 0.9;
            margin-bottom: 30px;
            line-height: 1.6;
        }

        .hero-buttons {
            display: flex;
            gap: 15px;
        }

        .btn-primary {
            background: #10b981;
            color: white;
            padding: 14px 32px;
            border-radius: 12px;
            font-weight: 600;
            border: none;
            cursor: pointer;
            font-size: 1rem;
            transition: all 0.3s;
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
        }

        .btn-primary:hover {
            background: #059669;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
        }

        .btn-secondary {
            background: transparent;
            color: white;
            padding: 14px 32px;
            border-radius: 12px;
            font-weight: 600;
            border: 2px solid rgba(255,255,255,0.3);
            cursor: pointer;
            font-size: 1rem;
            transition: all 0.3s;
        }

        .btn-secondary:hover {
            background: rgba(255,255,255,0.1);
            border-color: rgba(255,255,255,0.5);
        }

        .hero-image {
            position: relative;
        }

        /* ==================== STATS CARDS ==================== */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 40px;
        }

        .stat-card {
            background: white;
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            transition: all 0.3s;
        }

        .stat-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.12);
        }

        .stat-label {
            font-size: 0.875rem;
            color: #6b7280;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }

        .stat-value {
            font-size: 2.5rem;
            font-weight: 700;
            color: #111827;
        }

        .stat-unit {
            font-size: 1rem;
            color: #9ca3af;
            font-weight: 500;
        }

        /* ==================== FEATURE SECTION ==================== */
        .feature-section {
            padding: 80px 40px;
            background: white;
        }

        .section-header {
            text-align: center;
            max-width: 700px;
            margin: 0 auto 60px;
        }

        .section-header h2 {
            font-size: 2.5rem;
            font-weight: 700;
            color: #111827;
            margin-bottom: 16px;
        }

        .section-header p {
            font-size: 1.1rem;
            color: #6b7280;
            line-height: 1.6;
        }

        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            max-width: 1200px;
            margin: 0 auto;
        }

        .feature-card {
            background: #f9fafb;
            padding: 32px;
            border-radius: 20px;
            transition: all 0.3s;
            border: 1px solid #e5e7eb;
        }

        .feature-card:hover {
            background: white;
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        }

        .feature-icon {
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 20px;
            font-size: 28px;
        }

        .feature-card h3 {
            font-size: 1.4rem;
            font-weight: 600;
            color: #111827;
            margin-bottom: 12px;
        }

        .feature-card p {
            color: #6b7280;
            line-height: 1.6;
        }

        /* ==================== DASHBOARD LAYOUT ==================== */
        .dashboard-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 40px;
        }

        .dashboard-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 30px;
        }

        .main-content {
            background: white;
            border-radius: 20px;
            padding: 32px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }

        .sidebar-content {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        /* ==================== CARDS ==================== */
        .card {
            background: white;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            border: 1px solid #e5e7eb;
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }

        .card-title {
            font-size: 1.25rem;
            font-weight: 600;
            color: #111827;
        }

        /* ==================== PROGRESS BARS ==================== */
        .progress-container {
            margin: 20px 0;
        }

        .progress-label {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 0.9rem;
            color: #6b7280;
        }

        .progress-bar-wrapper {
            height: 12px;
            background: #e5e7eb;
            border-radius: 6px;
            overflow: hidden;
        }

        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #10b981 0%, #059669 100%);
            border-radius: 6px;
            transition: width 0.5s ease;
        }

        /* ==================== MEAL CARDS ==================== */
        .meal-item {
            display: flex;
            gap: 16px;
            padding: 16px;
            background: #f9fafb;
            border-radius: 12px;
            margin-bottom: 12px;
            transition: all 0.3s;
            border: 1px solid #e5e7eb;
        }

        .meal-item:hover {
            background: white;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        }

        .meal-image {
            width: 80px;
            height: 80px;
            border-radius: 12px;
            object-fit: cover;
        }

        .meal-info {
            flex: 1;
        }

        .meal-name {
            font-weight: 600;
            color: #111827;
            margin-bottom: 4px;
        }

        .meal-calories {
            color: #10b981;
            font-weight: 600;
            font-size: 1.1rem;
        }

        .meal-macros {
            font-size: 0.85rem;
            color: #6b7280;
            margin-top: 8px;
        }

        /* ==================== LOGIN/SIGNUP FORMS ==================== */
        .auth-container {
            max-width: 450px;
            margin: 80px auto;
            padding: 40px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.12);
        }

        .auth-header {
            text-align: center;
            margin-bottom: 32px;
        }

        .auth-header h2 {
            font-size: 2rem;
            font-weight: 700;
            color: #111827;
            margin-bottom: 8px;
        }

        .auth-header p {
            color: #6b7280;
        }

        .form-group {
            margin-bottom: 20px;
        }

        .form-label {
            display: block;
            font-weight: 500;
            color: #374151;
            margin-bottom: 8px;
            font-size: 0.9rem;
        }

        .form-input {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e5e7eb;
            border-radius: 10px;
            font-size: 1rem;
            transition: all 0.3s;
        }

        .form-input:focus {
            outline: none;
            border-color: #10b981;
            box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
        }

        /* ==================== BUTTONS ==================== */
        .stButton>button {
            width: 100%;
            padding: 14px 24px;
            background: #10b981;
            color: white;
            border: none;
            border-radius: 12px;
            font-weight: 600;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s;
        }

        .stButton>button:hover {
            background: #059669;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        }

        /* ==================== TABS ==================== */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: white;
            padding: 6px;
            border-radius: 12px;
            border: 1px solid #e5e7eb;
        }

        .stTabs [data-baseweb="tab"] {
            height: 48px;
            border-radius: 10px;
            padding: 0 24px;
            font-weight: 500;
            font-size: 0.95rem;
            color: #6b7280;
            background: transparent;
            border: none;
        }

        .stTabs [aria-selected="true"] {
            background: #10b981 !important;
            color: white !important;
        }

        /* ==================== MOBILE RESPONSIVE ==================== */
        @media (max-width: 768px) {
            .hero-content {
                grid-template-columns: 1fr;
                gap: 40px;
            }

            .hero-text h1 {
                font-size: 2.5rem;
            }

            .dashboard-grid {
                grid-template-columns: 1fr;
            }

            .features-grid {
                grid-template-columns: 1fr;
            }

            .dashboard-container {
                padding: 20px;
            }

            .section-header h2 {
                font-size: 2rem;
            }
        }

        /* ==================== LOADING OPTIMIZATION ==================== */
        .stSpinner > div {
            border-color: #10b981 transparent transparent transparent;
        }

        /* ==================== CUSTOM SCROLLBAR ==================== */
        ::-webkit-scrollbar {
            width: 10px;
        }

        ::-webkit-scrollbar-track {
            background: #f1f1f1;
        }

        ::-webkit-scrollbar-thumb {
            background: #10b981;
            border-radius: 5px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #059669;
        }
    </style>
    """
import streamlit as st

def apply_custom_styles():
    st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        :root {
            --bg-color: #020617; /* Slate 950 */
            --sidebar-bg: #0f172a; /* Slate 900 */
            --card-bg: rgba(30, 41, 59, 0.4); /* Slate 800 with opacity */
            --border-color: rgba(255, 255, 255, 0.08);
            --primary-gradient: linear-gradient(135deg, #6366f1 0%, #a855f7 100%); /* Indigo to Purple */
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-color: #818cf8;
        }
        
        /* HIDE SIDEBAR & TOGGLE */
        [data-testid="stSidebar"] { display: none; }
        [data-testid="collapsedControl"] { display: none; }

        /* Global Reset & Font */
        .stApp {
            background-color: var(--bg-color);
            font-family: 'Inter', sans-serif;
        }
        
        .block-container {
            padding-bottom: 70px;
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: var(--text-primary) !important;
            font-family: 'Inter', sans-serif;
            font-weight: 800;
            letter-spacing: -0.025em;
        }
        
        p, span, div, label {
            color: var(--text-secondary);
            font-family: 'Inter', sans-serif;
            font-weight: 400;
        }

        /* Modern Glass Cards */
        .glass-card {
            background: var(--card-bg);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 24px;
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
        }
        
        .glass-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.4);
            border-color: rgba(168, 85, 247, 0.3);
        }

        /* Metric Boxes */
        .metric-box {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            transition: all 0.3s ease;
            height: 100%;
        }
        
        .metric-box:hover {
            border-color: var(--accent-color);
            background: rgba(255, 255, 255, 0.05);
            transform: translateY(-2px);
        }
        
        .metric-icon {
            font-size: 1.8rem;
            margin-bottom: 16px;
            color: var(--accent-color);
            background: rgba(129, 140, 248, 0.15);
            width: 50px;
            height: 50px;
            border-radius: 14px;
            display: flex; align-items: center; justify-content: center;
        }
        
        .metric-value {
            font-size: 2.2rem;
            font-weight: 800;
            color: var(--text-primary);
            line-height: 1.1;
            margin-bottom: 4px;
        }
        
        .metric-label {
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* Profile Hero Section */
        .profile-hero {
            background: var(--primary-gradient);
            border-radius: 20px;
            padding: 30px;
            display: flex;
            align-items: center;
            gap: 25px;
            color: white;
            box-shadow: 0 20px 40px -10px rgba(99, 102, 241, 0.4);
            margin-bottom: 40px;
            position: relative;
            overflow: hidden;
        }
        
        .profile-hero::after {
            content: '';
            position: absolute;
            top: 0; right: 0; bottom: 0; left: 0;
            background: url('https://www.transparenttextures.com/patterns/cubes.png');
            opacity: 0.1;
            pointer-events: none;
        }
        
        .profile-avatar {
            width: 80px;
            height: 80px;
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(8px);
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            color: white;
            border: 2px solid rgba(255, 255, 255, 0.3);
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        }
        
        .profile-info h2 {
            color: white !important;
            margin: 0 0 4px 0;
            font-size: 1.6rem;
        }
        
        .profile-info p {
            color: rgba(255, 255, 255, 0.9) !important;
            font-size: 0.9rem;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        /* Custom Header */
        .app-header {
            text-align: center;
            padding: 60px 0;
            background: radial-gradient(circle at center, rgba(99, 102, 241, 0.15) 0%, transparent 70%);
            margin-bottom: 50px;
        }
        
        .app-header h1 {
            font-size: 3.5rem;
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }

        /* Streamlit Component Overrides */
        .stButton button {
            background: #ffffff !important;
            color: #000000 !important;
            border: none !important;
            padding: 0.75rem 1.5rem !important;
            border-radius: 12px !important;
            font-weight: 600 !important;
            letter-spacing: 0.5px !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3) !important;
            width: 100%;
        }
        
        .stButton button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 20px rgba(99, 102, 241, 0.5) !important;
        }
        
        .stTextInput input, .stSelectbox div[data-baseweb="select"] {
            background-color: rgba(255, 255, 255, 0.03) !important;
            border: 1px solid var(--border-color) !important;
            border-radius: 12px !important;
            color: white !important;
            padding: 0.5rem !important;
        }

        /* DYNAMIC ISLAND NAVBAR */
        [data-testid="stRadio"] {
            position: sticky;
            top: 20px;
            z-index: 1000;
            display: flex;
            justify-content: center;
            margin-top: 0px;
            margin-bottom: 20px;
        }

        [data-testid="stRadio"] > div[role="radiogroup"] {
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(20px);
            padding: 8px;
            border-radius: 36px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            display: inline-flex;
            justify-content: center;
            gap: 8px;
            box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.5);
            width: auto !important;
        }
        
        /* Hide circular radio button */
        [data-testid="stRadio"] > div[role="radiogroup"] > label > div:first-child {
            display: none !important;
        }
        
        [data-testid="stRadio"] > div[role="radiogroup"] > label {
            background: transparent;
            border: none;
            border-radius: 28px;
            padding: 12px 28px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            flex: 0 1 auto;
            text-align: center;
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 0;
        }
        
        [data-testid="stRadio"] > div[role="radiogroup"] > label:hover {
            background: rgba(255, 255, 255, 0.05);
            color: white;
            transform: scale(1.02);
        }
        
        [data-testid="stRadio"] > div[role="radiogroup"] > label[data-checked="true"] {
            background: var(--primary-gradient);
            color: white !important;
            box-shadow: 0 2px 10px rgba(99, 102, 241, 0.3);
            transform: scale(1.05);
        }
        
        [data-testid="stRadio"] > div[role="radiogroup"] > label p {
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            margin: 0 !important;
            line-height: 1 !important;
        }

        [data-testid="stRadio"] > div[role="radiogroup"] > label[data-checked="true"] p {
            color: white !important;
            font-weight: 700 !important;
        }

        /* SMALLER FOOTER */
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            padding: 8px;
            font-size: 0.75rem;
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(10px);
            text-align: center;
            z-index: 9999;
            border-top: 1px solid var(--border-color);
        }
        
        .footer p {
            margin: 0;
        }

        /* Style for st.container(border=True) to match glass-card */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background-color: var(--card-bg) !important;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--border-color) !important;
            border-radius: 20px !important;
            padding: 20px !important;
            box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.3);
        }
    </style>
    """, unsafe_allow_html=True)
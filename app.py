import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import importlib
import database as db
importlib.reload(db)
import auth
importlib.reload(auth)
import ml_utils
importlib.reload(ml_utils)

# Initialize database schema
db.init_db()

# Set page configuration
st.set_page_config(
    page_title="WealthFlow | Personal Finance Board",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session States
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None
if "active_users" not in st.session_state:
    st.session_state.active_users = {}
if "show_add_account" not in st.session_state:
    st.session_state.show_add_account = False
if "success_toast" not in st.session_state:
    st.session_state.success_toast = None
if "chat_started" not in st.session_state:
    st.session_state.chat_started = False

# Dynamic Auth-State CSS Injection
if not st.session_state.logged_in:
    # ---------------- LOGIN PAGE STYLING (Fullscreen Center, Hide Sidebar/Header) ----------------
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

        /* Global Typography */
        html, body, [class*="css"], .stMarkdown, .stText, .stButton, .stTextInput, .stNumberInput, .stSelectbox {
            font-family: 'Outfit', sans-serif !important;
        }

        /* Hide standard Streamlit header, footer and empty sidebar arrow */
        [data-testid="stHeader"], footer, [data-testid="stSidebar"], section[data-testid="stSidebar"] {
            display: none !important;
            visibility: hidden !important;
        }

        /* Set page background gradient on main container */
        .stApp, .stMain, .main {
            background: radial-gradient(circle at 10% 20%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
                        radial-gradient(circle at 90% 80%, rgba(6, 182, 212, 0.15) 0%, transparent 50%),
                        radial-gradient(circle at 50% 50%, rgba(236, 72, 153, 0.05) 0%, transparent 60%),
                        #070a13 !important;
        }

        /* Force Main Canvas to occupy exactly 100vh, center contents and constrain width */
        .stMain .block-container, .main .block-container {
            padding: 40px 20px !important;
            margin: 0 auto !important;
            min-height: 100vh !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
            background: transparent !important;
        }

        /* Landing page custom features list styles */
        .landing-feature-card {
            background: rgba(255, 255, 255, 0.02) !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            border-radius: 16px !important;
            padding: 16px 20px !important;
            margin-bottom: 12px !important;
            display: flex !important;
            align-items: center !important;
            min-height: 95px !important; /* Make all boxes of uniform height */
            box-sizing: border-box !important;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
        }
        .landing-feature-card:hover {
            background: rgba(255, 255, 255, 0.04) !important;
            border-color: rgba(0, 230, 118, 0.2) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 30px rgba(0, 230, 118, 0.05) !important;
        }
        .landing-feature-card > div:last-child {
            min-width: 0 !important;
            flex: 1 1 0% !important;
        }
        
        /* Styled custom instruction callouts */
        .guide-box {
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.03) 0%, rgba(255, 255, 255, 0.01) 100%) !important;
            border: 1px dashed rgba(255, 255, 255, 0.1) !important;
            border-radius: 14px !important;
            padding: 15px !important;
            margin-top: 15px !important;
        }

        /* Prevent columns, forms, and tabs from stretching vertically on the login page */
        div[data-testid="column"], div[data-testid="stForm"], div[role="tabpanel"] {
            height: auto !important;
            min-height: unset !important;
        }

        /* Hide default Streamlit input helper text ("Press Enter to submit") that overlaps with custom styles */
        div[data-testid="InputInstructions"] {
            display: none !important;
        }

        /* Set a clean spacing gap inside form blocks */
        div[data-testid="stForm"] div[data-testid="stVerticalBlock"] {
            gap: 16px !important;
        }

        /* Glassmorphic card styling for forms */
        div[data-testid="stForm"] {
            background: linear-gradient(135deg, rgba(21, 27, 38, 0.85) 0%, rgba(15, 23, 42, 0.75) 100%) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 24px !important;
            padding: 35px !important;
            box-shadow: 0 30px 60px rgba(0, 0, 0, 0.6), 
                        0 0 50px rgba(0, 230, 118, 0.02) !important;
            backdrop-filter: blur(20px) saturate(180%) !important;
            -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
        }

        /* Style form titles */
        div[data-testid="stForm"] h3 {
            font-family: 'Outfit', sans-serif !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            text-align: center !important;
            margin-bottom: 25px !important;
            font-size: 1.6rem !important;
            letter-spacing: -0.5px !important;
        }

        /* Input Labels */
        div[data-testid="stForm"] label {
            font-size: 0.8rem !important;
            font-weight: 600 !important;
            color: #8892b0 !important;
            margin-bottom: 8px !important;
            text-transform: uppercase !important;
            letter-spacing: 1.5px !important;
        }

        /* Custom Input Fields */
        div[data-baseweb="input"] {
            background-color: rgba(255, 255, 255, 0.02) !important;
            border: 1.5px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 12px !important;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        }
        div[data-baseweb="input"]:focus-within {
            border-color: #00e676 !important;
            box-shadow: 0 0 15px rgba(0, 230, 118, 0.25) !important;
            background-color: rgba(255, 255, 255, 0.04) !important;
        }
        div[data-baseweb="input"] input {
            color: #ffffff !important;
            font-size: 1rem !important;
        }

        /* Tabs selection switches - styled as an elegant segmented control */
        div[role="tablist"] {
            background-color: rgba(255, 255, 255, 0.03) !important;
            border-radius: 30px !important;
            padding: 6px !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            display: flex !important;
            justify-content: space-between !important;
            margin-bottom: 25px !important;
            gap: 5px !important;
        }
        button[data-baseweb="tab"] {
            color: #8892b0 !important;
            font-size: 0.95rem !important;
            font-weight: 600 !important;
            background: transparent !important;
            border: none !important;
            border-radius: 24px !important;
            padding: 8px 16px !important;
            flex-grow: 1 !important;
            text-align: center !important;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        }
        button[data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(90deg, #00e676 0%, #00b0ff 100%) !important;
            color: #0b0c10 !important;
            box-shadow: 0 4px 15px rgba(0, 230, 118, 0.3) !important;
        }
        button[data-baseweb="tab"]:hover {
            color: #ffffff !important;
        }
        /* Hide default BaseWeb tabs underline indicator */
        div[role="tablist"] > div:not(button) {
            display: none !important;
        }

        /* Full width login button */
        div[data-testid="stFormSubmitButton"],
        div[data-testid="stFormSubmitButton"] button {
            width: 100% !important;
        }
        div[data-testid="stFormSubmitButton"] button {
            background: linear-gradient(90deg, #00e676 0%, #00b0ff 100%) !important;
            color: #0b0c10 !important;
            font-weight: 700 !important;
            font-size: 1.05rem !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 12px 30px !important;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
            margin-top: 15px !important;
            box-shadow: 0 4px 15px rgba(0, 230, 118, 0.2) !important;
        }
        div[data-testid="stFormSubmitButton"] button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(0, 230, 118, 0.4) !important;
            color: #0b0c10 !important;
        }
        
        .text-center {
            text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)
else:
    # ---------------- DASHBOARD & UTILITIES STYLING (Standard Grid + Sidebar) ----------------
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

        /* Global Typography */
        html, body, [class*="css"], .stMarkdown, .stText, .stButton, .stTextInput, .stNumberInput, .stSelectbox {
            font-family: 'Outfit', sans-serif !important;
        }

        /* Set page background gradient on main container */
        .stApp, .stMain, .main {
            background: radial-gradient(circle at 10% 20%, rgba(99, 102, 241, 0.15) 0%, transparent 50%),
                        radial-gradient(circle at 90% 80%, rgba(6, 182, 212, 0.15) 0%, transparent 50%),
                        radial-gradient(circle at 50% 50%, rgba(236, 72, 153, 0.05) 0%, transparent 60%),
                        #070a13 !important;
        }

        /* Standard top headers and footers for active dashboards */
        [data-testid="stHeader"], footer {
            display: block !important;
            visibility: visible !important;
        }

        /* Premium glassmorphic metric cards */
        .kpi-card {
            background: linear-gradient(135deg, rgba(21, 27, 38, 0.85) 0%, rgba(30, 41, 59, 0.6) 100%);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border-top: 4px solid #00e676;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        }
        .kpi-card:hover {
            background: linear-gradient(135deg, rgba(21, 27, 38, 0.95) 0%, rgba(30, 41, 59, 0.7) 100%);
            border-color: rgba(0, 230, 118, 0.4);
            transform: translateY(-4px);
            box-shadow: 0 12px 40px 0 rgba(0, 230, 118, 0.2);
        }
        .kpi-label {
            font-size: 0.85rem;
            color: #8892b0;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .kpi-value {
            font-size: 2.2rem;
            font-weight: 800;
            color: #ffffff;
            margin-top: 8px;
            letter-spacing: -0.5px;
        }
        .kpi-trend-up {
            color: #00e676;
            font-size: 0.85rem;
            font-weight: 500;
            margin-top: 8px;
            background: rgba(0, 230, 118, 0.1);
            padding: 2px 8px;
            border-radius: 20px;
            display: inline-block;
        }
        .kpi-trend-down {
            color: #ff1744;
            font-size: 0.85rem;
            font-weight: 500;
            margin-top: 8px;
            background: rgba(255, 23, 68, 0.1);
            padding: 2px 8px;
            border-radius: 20px;
            display: inline-block;
        }
        
        /* Clean glassmorphic form overlays */
        div[data-testid="stForm"] {
            background: linear-gradient(135deg, rgba(21, 27, 38, 0.5) 0%, rgba(15, 23, 42, 0.4) 100%) !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            border-radius: 16px !important;
            padding: 30px !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
            backdrop-filter: blur(6px) !important;
            -webkit-backdrop-filter: blur(6px) !important;
        }
        
        /* Sidebar container custom styling */
        section[data-testid="stSidebar"] {
            background-color: #0c1017 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.04) !important;
        }
        
        .text-center-sidebar {
            text-align: center !important;
            margin-bottom: 10px !important;
            width: 100% !important;
        }
        .text-center-sidebar h2 {
            font-weight: 800 !important;
            font-size: 1.8rem !important;
            letter-spacing: -0.5px !important;
        }

        /* Style the Sidebar Radio options as full-width menu buttons */
        div[data-testid="stRadio"] {
            width: 100% !important;
        }
        /* Hide the default "Navigate Menu" label at the top of the radio group */
        div[data-testid="stRadio"] > label {
            display: none !important;
        }
        /* Hide the radio input circles */
        div[data-testid="stRadio"] div[data-testid="stMarker"] {
            display: none !important;
            visibility: hidden !important;
        }
        /* Style the radio option labels */
        div[data-testid="stRadio"] label {
            background-color: rgba(255, 255, 255, 0.02) !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            border-radius: 12px !important;
            padding: 12px 18px !important;
            margin-bottom: 10px !important;
            display: flex !important;
            align-items: center !important;
            width: 100% !important;
            cursor: pointer !important;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.15) !important;
        }
        /* Hover state */
        div[data-testid="stRadio"] label:hover {
            background-color: rgba(255, 255, 255, 0.04) !important;
            border-color: rgba(0, 230, 118, 0.2) !important;
            transform: translateX(4px) !important;
        }
        /* Selected/Active state */
        div[data-testid="stRadio"] label:has(input:checked) {
            background: linear-gradient(90deg, rgba(0, 230, 118, 0.1) 0%, rgba(0, 176, 255, 0.1) 100%) !important;
            border-color: #00e676 !important;
            color: #00e676 !important;
            font-weight: 700 !important;
            box-shadow: 0 0 15px rgba(0, 230, 118, 0.15) !important;
        }
        /* Reset label indentation */
        div[data-testid="stRadio"] label [data-testid="stMarkdownContainer"] {
            margin-left: 0 !important;
            font-size: 0.95rem !important;
        }
        
        /* Glowing Neon Progress Bars override */
        div[data-testid="stProgress"] > div > div > div {
            background-image: linear-gradient(90deg, #00e676 0%, #00b0ff 100%) !important;
            border-radius: 10px;
        }
        
        /* Styled Submit Buttons */
        div[data-testid="stFormSubmitButton"] button {
            background: linear-gradient(90deg, #00e676 0%, #00b0ff 100%) !important;
            color: #0b0c10 !important;
            font-weight: 700 !important;
            font-size: 1.05rem !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 12px 30px !important;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        }
        div[data-testid="stFormSubmitButton"] button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(0, 230, 118, 0.45) !important;
            color: #0b0c10 !important;
        }
        
        .text-center {
            text-align: center;
        }
    </style>
    """, unsafe_allow_html=True)

# Category definitions
CATEGORIES = ["Food", "Entertainment", "Education", "Shopping", "Bills & Utilities", "Other"]

# --- AUTHENTICATION FLOW ---

def show_auth_page():
    is_compact = (st.session_state.logged_in and st.session_state.show_add_account)
    max_width = "460px" if is_compact else "940px"
    
    # Inject dynamic max-width override
    st.markdown(f"""
    <style>
        .stMain .block-container, .main .block-container {{
            max-width: {max_width} !important;
        }}
    </style>
    """, unsafe_allow_html=True)

    # Helper function to render form block to avoid copy-pasting forms
    def render_forms():
        tab1, tab2 = st.tabs(["🔑 Log In", "📝 Create Account"])
        
        with tab1:
            with st.form("login_form"):
                st.markdown("<h3 style='color: #ffffff; font-weight: 700; text-align: center; margin-bottom: 25px; font-size: 1.6rem;'>🔑 Sign In</h3>", unsafe_allow_html=True)
                username = st.text_input("Username", placeholder="Enter username").strip()
                password = st.text_input("Password", type="password", placeholder="Enter password")
                submitted = st.form_submit_button("Sign In", use_container_width=True)
                
                if submitted:
                    if not username or not password:
                        st.error("Please fill in all fields.")
                    else:
                        user = db.get_user_by_username(username)
                        if user and auth.check_password(password, user["password_hash"]):
                            st.session_state.active_users[user["id"]] = user["username"]
                            st.session_state.logged_in = True
                            st.session_state.user_id = user["id"]
                            st.session_state.username = user["username"]
                            st.session_state.show_add_account = False
                            st.success(f"Welcome back, {user['username']}!")
                            st.rerun()
                        else:
                            st.error("Invalid username or password.")
                            
        with tab2:
            with st.form("register_form"):
                st.markdown("<h3 style='color: #ffffff; font-weight: 700; text-align: center; margin-bottom: 25px; font-size: 1.6rem;'>📝 Register</h3>", unsafe_allow_html=True)
                new_username = st.text_input("Choose Username", placeholder="e.g. johndoe").strip()
                new_password = st.text_input("Choose Password", type="password", placeholder="Min. 8 characters (A-Z, 0-9, !@#)")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
                submitted_reg = st.form_submit_button("Sign Up & Setup", use_container_width=True)
                
                if submitted_reg:
                    if not new_username or not new_password or not confirm_password:
                        st.error("Please fill in all fields.")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match.")
                    else:
                        is_strong, strength_msg = auth.validate_password_strength(new_password)
                        if not is_strong:
                            st.error(f"⚠️ **Too Weak Password**: {strength_msg}")
                        else:
                            existing = db.get_user_by_username(new_username)
                            if existing:
                                st.error("Username is already taken. Please choose another.")
                            else:
                                pwd_hash = auth.hash_password(new_password)
                                user_id = db.add_user(new_username, pwd_hash)
                                if user_id:
                                    for cat in CATEGORIES:
                                        db.set_budget(user_id, cat, 300.0)
                                    
                                    st.session_state.active_users[user_id] = new_username
                                    st.session_state.logged_in = True
                                    st.session_state.user_id = user_id
                                    st.session_state.username = new_username
                                    st.session_state.show_add_account = False
                                    st.success("Account successfully created and logged in!")
                                    st.rerun()
                                else:
                                    st.error("An error occurred during registration. Please try again.")

    # Spacing
    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    if is_compact:
        # Abort button if logging in to another account while already authenticated
        if st.button("🔙 Back to Dashboard", use_container_width=True):
            st.session_state.show_add_account = False
            st.rerun()
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        st.markdown("<h1 class='text-center' style='color: #00e676; margin-bottom: 5px; font-weight: 800; font-size: 2.5rem;'>💰 WealthFlow</h1>", unsafe_allow_html=True)
        st.markdown("<p class='text-center' style='color: #8892b0; font-size: 0.95rem; margin-bottom: 25px;'>Add Another Account Session</p>", unsafe_allow_html=True)
        render_forms()
    else:
        # Landing style with branding left and login forms right
        st.markdown("<h1 class='text-center' style='color: #00e676; margin-bottom: 5px; font-weight: 800; font-size: 2.8rem;'>💰 WealthFlow</h1>", unsafe_allow_html=True)
        st.markdown("<p class='text-center' style='color: #8892b0; font-size: 1.05rem; margin-bottom: 35px;'>Your Smart Personal Finance & ML Forecasting Companion</p>", unsafe_allow_html=True)
        
        col_left, col_right = st.columns([1.1, 0.9])
        
        with col_left:
            st.markdown("""
            <h3 style='color: #ffffff; margin-bottom: 15px; font-weight: 700; font-size: 1.4rem;'>🚀 Welcome to WealthFlow</h3>
            <p style='color: #8892b0; line-height: 1.6; margin-bottom: 25px; font-size: 0.92rem;'>
                Take control of your financial destiny with our automated analytics dashboard. WealthFlow combines day-to-day logging with machine learning forecasting and real-time AI guidance.
            </p>
            
            <div class="landing-feature-card">
                <div style="font-size: 1.8rem; margin-right: 15px; filter: drop-shadow(0 0 10px rgba(0, 230, 118, 0.3));">📊</div>
                <div>
                    <h4 style="margin: 0; color: #ffffff; font-weight: 600; font-size: 1.05rem;">Real-Time Financial Dashboard</h4>
                    <p style="margin: 4px 0 0 0; color: #8892b0; font-size: 0.85rem; line-height: 1.4;">Track monthly net savings, savings rate, and category budgets with interactive Plotly visualizers.</p>
                </div>
            </div>
            
            <div class="landing-feature-card">
                <div style="font-size: 1.8rem; margin-right: 15px; filter: drop-shadow(0 0 10px rgba(255, 152, 0, 0.3));">🔮</div>
                <div>
                    <h4 style="margin: 0; color: #ffffff; font-weight: 600; font-size: 1.05rem;">ML Expense Forecasting</h4>
                    <p style="margin: 4px 0 0 0; color: #8892b0; font-size: 0.85rem; line-height: 1.4;">Generate automated 3-month expense projections using Scikit-Learn regression models.</p>
                </div>
            </div>
            
            <div class="landing-feature-card">
                <div style="font-size: 1.8rem; margin-right: 15px; filter: drop-shadow(0 0 10px rgba(0, 176, 255, 0.3));">🧠</div>
                <div>
                    <h4 style="margin: 0; color: #ffffff; font-weight: 600; font-size: 1.05rem;">Gemini AI Financial Coach</h4>
                    <p style="margin: 4px 0 0 0; color: #8892b0; font-size: 0.85rem; line-height: 1.4;">Synthesize budget alerts and transaction trends into custom coaching reports powered by Gemini.</p>
                </div>
            </div>

            <div class="landing-feature-card">
                <div style="font-size: 1.8rem; margin-right: 15px; filter: drop-shadow(0 0 10px rgba(138, 43, 226, 0.3));">👥</div>
                <div>
                    <h4 style="margin: 0; color: #ffffff; font-weight: 600; font-size: 1.05rem;">Concurrent Multi-Accounts</h4>
                    <p style="margin: 4px 0 0 0; color: #8892b0; font-size: 0.85rem; line-height: 1.4;">Log into multiple user profiles simultaneously in one browser tab and switch on the fly.</p>
                </div>
            </div>
            
            <div class="guide-box">
                <p style="margin: 0 0 8px 0; color: #ffffff; font-weight: 600; font-size: 0.9rem;">📝 Quick Start Guide:</p>
                <ol style="margin: 0; padding-left: 20px; color: #8892b0; font-size: 0.82rem; line-height: 1.5;">
                    <li>Switch to the <b>Create Account</b> tab to register a profile.</li>
                    <li>Record transactions in <b>Transactions</b> to train your ML model.</li>
                    <li>Establish spending caps and goals in <b>Budgets & Goals</b>.</li>
                </ol>
            </div>
            """, unsafe_allow_html=True)
        
        with col_right:
            render_forms()

# --- HELPERS ---

def format_currency(val):
    return f"₹{val:,.2f}"

def render_kpi(label, val, trend_text="", trend_dir=""):
    trend_html = ""
    if trend_dir == "up":
        trend_html = f"<div class='kpi-trend-up'>▲ {trend_text}</div>"
    elif trend_dir == "down":
        trend_html = f"<div class='kpi-trend-down'>▼ {trend_text}</div>"
        
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{format_currency(val)}</div>
        {trend_html}
    </div>
    """, unsafe_allow_html=True)

# --- PAGES ---

def show_dashboard(user_id):
    st.title("📊 Financial Dashboard")
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(0, 230, 118, 0.08) 0%, rgba(0, 176, 255, 0.08) 100%); padding: 22px; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 25px;">
        <h3 style="margin: 0; color: #ffffff; font-weight: 700; font-size: 1.4rem;">👋 Welcome back, {st.session_state.username}!</h3>
        <p style="margin: 6px 0 0 0; color: #8892b0; font-size: 0.92rem; line-height: 1.5;">
            Here is your live financial snapshot. Use the sidebar menu to log transaction entries under <b>Transactions</b>, set up category budgets under <b>Budgets & Goals</b>, or consult your ML forecasting engine and Google Gemini AI coach under <b>Predictions & Advice</b>.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load Incomes & Expenses
    df_inc = db.get_incomes(user_id)
    df_exp = db.get_expenses(user_id)
    
    if df_inc.empty and df_exp.empty:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(0, 230, 118, 0.05) 0%, rgba(0, 176, 255, 0.05) 100%); padding: 30px; border-radius: 16px; border: 1.5px dashed rgba(0, 230, 118, 0.3); margin-bottom: 25px; text-align: center; box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);">
            <div style="font-size: 3rem; margin-bottom: 15px; filter: drop-shadow(0 0 10px rgba(0, 230, 118, 0.4));">🚀</div>
            <h3 style="margin: 0; color: #ffffff; font-weight: 700; font-size: 1.4rem;">Get Started with WealthFlow Demo Data</h3>
            <p style="margin: 8px auto 20px auto; color: #8892b0; font-size: 0.95rem; line-height: 1.6; max-width: 600px;">
                It looks like this profile doesn't have any transaction history yet! To immediately see the dynamic <b>Plotly graphs</b>, <b>Machine Learning forecasting models</b>, and <b>Gemini AI coaching reports</b> in action, click the button below to seed 6 months of mock transactions, budgets, and savings goals.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✨ Seed 6 Months of Financial Demo Data", key="seed_empty_dashboard", use_container_width=True, type="primary"):
            with st.spinner("Seeding database with mock transactions, budgets, and goals..."):
                db.generate_mock_data(user_id)
            st.toast("🎉 Database successfully seeded with 6 months of historical transactions!", icon="🚀")
            st.rerun()
            
    # Current month metrics
    current_month_str = datetime.now().strftime("%Y-%m")
    
    # Calculating stats
    # Income
    if not df_inc.empty:
        df_inc['date'] = pd.to_datetime(df_inc['date'])
        month_inc = df_inc[df_inc['date'].dt.strftime('%Y-%m') == current_month_str]['amount'].sum()
        total_inc = df_inc['amount'].sum()
    else:
        month_inc = 0.0
        total_inc = 0.0
        
    # Expenses
    if not df_exp.empty:
        df_exp['date'] = pd.to_datetime(df_exp['date'])
        month_exp = df_exp[df_exp['date'].dt.strftime('%Y-%m') == current_month_str]['amount'].sum()
        total_exp = df_exp['amount'].sum()
    else:
        month_exp = 0.0
        total_exp = 0.0
        
    net_savings = month_inc - month_exp
    savings_rate = (net_savings / month_inc * 100) if month_inc > 0 else 0.0
    
    # Render KPI Cards in columns
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi("Monthly Income", month_inc, "Current Month", "up" if month_inc > 0 else "")
    with col2:
        render_kpi("Monthly Expenses", month_exp, "Current Month", "down" if month_exp > 0 else "")
    with col3:
        trend_dir = "up" if net_savings >= 0 else "down"
        trend_lbl = "Net Positive" if net_savings >= 0 else "Net Deficit"
        render_kpi("Monthly Net Savings", net_savings, trend_lbl, trend_dir)
    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Savings Rate</div>
            <div class="kpi-value">{savings_rate:.1f}%</div>
            <div class="kpi-trend-up" style="color: {'#00e676' if savings_rate >= 20 else ('#ffeb3b' if savings_rate >= 0 else '#ff1744')}">
                {'Healthy (>=20%)' if savings_rate >= 20 else ('Moderate' if savings_rate >= 0 else 'Deficit alert')}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    # Warning for Overspending
    df_bud = db.get_expenses_vs_budget(user_id)
    if not df_bud.empty:
        overspent = df_bud[df_bud['spent_amount'] > df_bud['budget_amount']]
        if not overspent.empty:
            for idx, r in overspent.iterrows():
                excess = r['spent_amount'] - r['budget_amount']
                st.warning(f"⚠️ **Budget Overspent Warning**: You have exceeded your budget for **{r['category']}** by **{format_currency(excess)}** this month! (Spent: {format_currency(r['spent_amount'])} / Budget: {format_currency(r['budget_amount'])})")
                
    st.markdown("---")
    
    # Visualizations Section
    col_left, col_right = st.columns([3, 2])
    
    with col_left:
        st.subheader("Income vs Expenses Monthly Trend")
        if df_inc.empty and df_exp.empty:
            st.info("No transaction data available yet to build trend charts.")
        else:
            # Combine monthly data
            df_inc_m = df_inc.copy() if not df_inc.empty else pd.DataFrame(columns=['amount', 'date'])
            df_exp_m = df_exp.copy() if not df_exp.empty else pd.DataFrame(columns=['amount', 'date'])
            
            # Aggregate Incomes
            if not df_inc_m.empty:
                df_inc_m['Month'] = df_inc_m['date'].dt.strftime('%Y-%m')
                monthly_inc = df_inc_m.groupby('Month')['amount'].sum().reset_index().rename(columns={'amount': 'Income'})
            else:
                monthly_inc = pd.DataFrame(columns=['Month', 'Income'])
                
            # Aggregate Expenses
            if not df_exp_m.empty:
                df_exp_m['Month'] = df_exp_m['date'].dt.strftime('%Y-%m')
                monthly_exp = df_exp_m.groupby('Month')['amount'].sum().reset_index().rename(columns={'amount': 'Expenses'})
            else:
                monthly_exp = pd.DataFrame(columns=['Month', 'Expenses'])
                
            # Merge
            trend_df = pd.merge(monthly_inc, monthly_exp, on='Month', how='outer').fillna(0.0)
            trend_df = trend_df.sort_values('Month')
            
            if not trend_df.empty:
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=trend_df['Month'],
                    y=trend_df['Income'],
                    name='Income',
                    marker_color='#00e676',
                    hovertemplate='Income: ₹%{y:,.2f}<extra></extra>'
                ))
                fig.add_trace(go.Bar(
                    x=trend_df['Month'],
                    y=trend_df['Expenses'],
                    name='Expenses',
                    marker_color='#ff1744',
                    hovertemplate='Expenses: ₹%{y:,.2f}<extra></extra>'
                ))
                fig.update_layout(
                    barmode='group',
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='#ffffff',
                    xaxis=dict(showgrid=False, tickfont=dict(family='Outfit', size=11)),
                    yaxis=dict(gridcolor='rgba(255,255,255,0.06)', tickfont=dict(family='Outfit', size=11)),
                    margin=dict(l=20, r=20, t=20, b=20),
                    height=300,
                    legend=dict(font=dict(family='Outfit', size=11), orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Insufficient data to display bar charts.")
                
    with col_right:
        st.subheader("Expense Breakdown (This Month)")
        if df_exp.empty or month_exp == 0.0:
            st.info("No expense data recorded for this month.")
        else:
            # Filter current month expenses
            curr_month_exp = df_exp[df_exp['date'].dt.strftime('%Y-%m') == current_month_str]
            if curr_month_exp.empty:
                st.info("No expense data recorded for this specific month.")
            else:
                cat_exp = curr_month_exp.groupby('category')['amount'].sum().reset_index()
                fig = px.pie(
                    cat_exp, 
                    values='amount', 
                    names='category',
                    color_discrete_sequence=['#00e676', '#00b0ff', '#ff9800', '#8a2bbe', '#ff1744', '#e91e63'],
                    hole=0.55
                )
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    font_color='#ffffff',
                    margin=dict(l=10, r=10, t=10, b=10),
                    legend=dict(font=dict(family='Outfit', size=11), orientation="h", yanchor="bottom", y=-0.28, xanchor="center", x=0.5),
                    height=300
                )
                fig.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    hovertemplate='<b>%{label}</b><br>Spent: ₹%{value:,.2f}<br>Percentage: %{percent:.1%}<extra></extra>',
                    marker=dict(line=dict(color='#0b0c10', width=2))
                )
                st.plotly_chart(fig, use_container_width=True)
                
    st.markdown("---")
    
    # Bottom Layout: Recent Transactions vs Savings Goals progress
    col_bottom_left, col_bottom_right = st.columns([1, 1])
    
    with col_bottom_left:
        st.subheader("Recent Transactions")
        
        # Combine income and expenses
        hist_records = []
        if not df_inc.empty:
            for idx, r in df_inc.head(5).iterrows():
                hist_records.append({
                    "Date": r['date'].strftime('%Y-%m-%d'),
                    "Type": "Income 🟢",
                    "Category/Source": r['source'],
                    "Amount": format_currency(r['amount'])
                })
        if not df_exp.empty:
            for idx, r in df_exp.head(5).iterrows():
                hist_records.append({
                    "Date": r['date'].strftime('%Y-%m-%d'),
                    "Type": "Expense 🔴",
                    "Category/Source": r['category'],
                    "Amount": format_currency(r['amount'])
                })
                
        if hist_records:
            df_hist = pd.DataFrame(hist_records)
            df_hist = df_hist.sort_values(by="Date", ascending=False).head(5)
            
            for item in df_hist.to_dict(orient="records"):
                color = "#00e676" if "Income" in item["Type"] else "#ff1744"
                icon = "🟢" if "Income" in item["Type"] else "🔴"
                st.markdown(f"""
                <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 12px 16px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <span style="font-size: 1.2rem;">{icon}</span>
                        <div>
                            <div style="color: #ffffff; font-weight: 600; font-size: 0.95rem;">{item['Category/Source']}</div>
                            <div style="color: #8892b0; font-size: 0.75rem;">{item['Date']}</div>
                        </div>
                    </div>
                    <div style="color: {color}; font-weight: 700; font-size: 1.05rem;">{item['Amount']}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No transaction history available yet.")
            
    with col_bottom_right:
        st.subheader("Savings Goals Progress")
        df_goals = db.get_savings_goals(user_id)
        
        if df_goals.empty:
            st.info("No savings goals added yet. Navigate to 'Budgets & Goals' to set them!")
        else:
            for idx, row in df_goals.iterrows():
                progress = (row['current_amount'] / row['target_amount'])
                progress = min(1.0, max(0.0, progress)) # clamp between 0 and 1
                
                col_g1, col_g2 = st.columns([3, 1])
                with col_g1:
                    st.write(f"🎯 **{row['goal_name']}**")
                    st.progress(progress)
                with col_g2:
                    st.write(f"**{row['current_amount']:.0f}** / **{row['target_amount']:.0f}**")
                    st.caption(f"Target: {row['target_date']}")

def show_transactions(user_id):
    st.title("🔀 Transactions")
    st.info("💡 **Transactions Guide**: Log your income sources and expense records here. A detailed transaction history is required to compile your budgets and train the Machine Learning forecasting engine.")
    
    tab1, tab2 = st.tabs(["💵 Income Tracker", "💸 Expense Tracker"])
    
    with tab1:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Add Income Source")
            with st.form("income_form", clear_on_submit=True):
                amount = st.number_input("Amount (₹)", min_value=0.01, step=50.0, format="%.2f")
                source = st.selectbox("Source", ["Salary", "Freelance", "Investments", "Gifts", "Rental Income", "Other"])
                # Fallback text input if source is other
                other_source = st.text_input("If 'Other', specify source description:").strip()
                income_date = st.date_input("Date Received", value=date.today())
                
                submitted = st.form_submit_button("Record Income", use_container_width=True)
                if submitted:
                    final_source = other_source if (source == "Other" and other_source) else source
                    db.add_income(user_id, amount, final_source, income_date.strftime("%Y-%m-%d"))
                    st.session_state.success_toast = f"Successfully recorded income of {format_currency(amount)} from {final_source}!"
                    st.rerun()
                    
        with col2:
            st.subheader("Income Records")
            df = db.get_incomes(user_id)
            if df.empty:
                st.info("No income records found. Add one on the left!")
            else:
                # Filter and Pagination Controls
                col_ctrl1, col_ctrl2 = st.columns([2, 1])
                with col_ctrl1:
                    search_source = st.text_input("🔍 Search Source", key="search_inc_src").strip()
                with col_ctrl2:
                    limit_inc = st.number_input("Show Limit", min_value=5, max_value=100, value=10, step=5, key="limit_inc_val")
                
                # Apply filter
                display_df = df.copy()
                if search_source:
                    display_df = display_df[display_df['source'].str.contains(search_source, case=False)]
                
                display_df = display_df.sort_values(by='date', ascending=False)
                total_records = len(display_df)
                records_to_show = display_df.head(limit_inc)
                
                if records_to_show.empty:
                    st.warning("No records match your search query.")
                else:
                    st.caption(f"Showing {len(records_to_show)} of {total_records} records (Sorted by Date Newest-First)")
                    
                    # Custom interactive table header
                    col_h1, col_h2, col_h3, col_h4 = st.columns([1.5, 2, 1.5, 0.8])
                    with col_h1:
                        st.markdown("**Date**")
                    with col_h2:
                        st.markdown("**Source**")
                    with col_h3:
                        st.markdown("**Amount**")
                    with col_h4:
                        st.markdown("**Action**")
                    st.markdown("<hr style='margin: 4px 0 10px 0; border: none; border-top: 1px solid rgba(255,255,255,0.15);'/>", unsafe_allow_html=True)
                    
                    # Custom interactive table rows
                    for idx, row in records_to_show.iterrows():
                        rec_id = row['id']
                        c1, c2, c3, c4 = st.columns([1.5, 2, 1.5, 0.8])
                        with c1:
                            st.write(row['date'].strftime('%Y-%m-%d') if hasattr(row['date'], 'strftime') else str(row['date']))
                        with c2:
                            st.write(row['source'])
                        with c3:
                            st.write(format_currency(row['amount']))
                        with c4:
                            with st.popover("🗑️", help="Delete this income record"):
                                st.write("Confirm delete?")
                                if st.button("Yes, Delete", key=f"del_inc_{rec_id}", type="primary", use_container_width=True):
                                    db.delete_income(rec_id, user_id)
                                    st.toast("Income record deleted!", icon="🗑️")
                                    st.rerun()
                    
    with tab2:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Record New Expense")
            
            # Sub-navigation for manual vs scan
            expense_mode = st.radio("Expense Input Method", ["📝 Enter Manually", "📷 Scan Bill with AI"], label_visibility="collapsed", horizontal=True)
            
            if expense_mode == "📝 Enter Manually":
                with st.form("expense_form", clear_on_submit=True):
                    amount = st.number_input("Amount (₹)", min_value=0.01, step=10.0, format="%.2f")
                    category = st.selectbox("Category", CATEGORIES)
                    description = st.text_input("Description / Notes").strip()
                    expense_date = st.date_input("Transaction Date", value=date.today())
                    
                    submitted = st.form_submit_button("Record Expense", use_container_width=True)
                    if submitted:
                        db.add_expense(user_id, amount, category, description, expense_date.strftime("%Y-%m-%d"))
                        st.session_state.success_toast = f"Recorded expense of {format_currency(amount)} in category {category}!"
                        st.rerun()
            else:
                # Receipt Scanning flow
                if "scan_result" not in st.session_state:
                    st.session_state.scan_result = None
                
                if st.session_state.scan_result is None:
                    uploaded_file = st.file_uploader("Upload Bill/Receipt Image", type=["png", "jpg", "jpeg"])
                    if uploaded_file is not None:
                        st.image(uploaded_file, caption="Uploaded Bill", use_container_width=True)
                    
                    api_key_override = st.text_input("Gemini API Key (Optional Override)", type="password", help="Leave blank to use the configured system key.")
                    
                    if st.button("Scan Receipt", use_container_width=True, type="primary"):
                        if uploaded_file is None:
                            st.error("Please upload an image file first.")
                        else:
                            with st.spinner("Analyzing receipt with Gemini AI..."):
                                image_bytes = uploaded_file.read()
                                mime_type = uploaded_file.type
                                result = ml_utils.parse_receipt_image(image_bytes, mime_type, api_key_override.strip() or None)
                                
                                if result["status"] == "success":
                                    st.session_state.scan_result = result["data"]
                                    st.rerun()
                                else:
                                    st.error(f"Failed to scan receipt: {result['message']}")
                else:
                    st.markdown("<h4 style='color: #00e676; margin-top: 15px; margin-bottom: 10px;'>🔍 Review Scanned Bill</h4>", unsafe_allow_html=True)
                    
                    parsed_amt = float(st.session_state.scan_result.get("amount", 0.0))
                    parsed_cat = st.session_state.scan_result.get("category", "Other")
                    if parsed_cat not in CATEGORIES:
                        parsed_cat = "Other"
                    parsed_desc = st.session_state.scan_result.get("description", "")
                    parsed_date_str = st.session_state.scan_result.get("date", date.today().strftime("%Y-%m-%d"))
                    try:
                        parsed_date = datetime.strptime(parsed_date_str, "%Y-%m-%d").date()
                    except ValueError:
                        parsed_date = date.today()
                    
                    with st.form("confirm_scan_form"):
                        amount = st.number_input("Amount (₹)", min_value=0.01, step=10.0, format="%.2f", value=parsed_amt)
                        category = st.selectbox("Category", CATEGORIES, index=CATEGORIES.index(parsed_cat))
                        description = st.text_input("Description / Notes", value=parsed_desc).strip()
                        expense_date = st.date_input("Transaction Date", value=parsed_date)
                        
                        confirm_btn = st.form_submit_button("Confirm & Save", use_container_width=True)
                        
                    if st.button("Cancel & Scan Again", use_container_width=True):
                        st.session_state.scan_result = None
                        st.rerun()
                        
                    if confirm_btn:
                        db.add_expense(user_id, amount, category, description, expense_date.strftime("%Y-%m-%d"))
                        st.session_state.success_toast = f"Recorded scanned expense of {format_currency(amount)} in category {category}!"
                        st.session_state.scan_result = None
                        st.rerun()

                    
        with col2:
            st.subheader("Expense History")
            df = db.get_expenses(user_id)
            if df.empty:
                st.info("No expenses found. Record your first expense on the left!")
            else:
                # Filter and Pagination Controls
                col_ctrl1, col_ctrl2 = st.columns([2, 1])
                with col_ctrl1:
                    search_exp = st.text_input("🔍 Search Description/Category", key="search_exp_val").strip()
                with col_ctrl2:
                    limit_exp = st.number_input("Show Limit", min_value=5, max_value=100, value=10, step=5, key="limit_exp_val")
                
                # Apply filter
                display_df = df.copy()
                if search_exp:
                    # Filter by category or description
                    display_df = display_df[
                        display_df['category'].str.contains(search_exp, case=False) | 
                        display_df['description'].str.contains(search_exp, case=False)
                    ]
                
                display_df = display_df.sort_values(by='date', ascending=False)
                total_records = len(display_df)
                records_to_show = display_df.head(limit_exp)
                
                if records_to_show.empty:
                    st.warning("No records match your search query.")
                else:
                    st.caption(f"Showing {len(records_to_show)} of {total_records} records (Sorted by Date Newest-First)")
                    
                    # Custom interactive table header
                    col_h1, col_h2, col_h3, col_h4, col_h5 = st.columns([1.2, 1.6, 2.2, 1.2, 0.6])
                    with col_h1:
                        st.markdown("**Date**")
                    with col_h2:
                        st.markdown("**Category**")
                    with col_h3:
                        st.markdown("**Description**")
                    with col_h4:
                        st.markdown("**Amount**")
                    with col_h5:
                        st.markdown("**Action**")
                    st.markdown("<hr style='margin: 4px 0 10px 0; border: none; border-top: 1px solid rgba(255,255,255,0.15);'/>", unsafe_allow_html=True)
                    
                    # Custom interactive table rows
                    for idx, row in records_to_show.iterrows():
                        rec_id = row['id']
                        c1, c2, c3, c4, c5 = st.columns([1.2, 1.6, 2.2, 1.2, 0.6])
                        with c1:
                            st.write(row['date'].strftime('%Y-%m-%d') if hasattr(row['date'], 'strftime') else str(row['date']))
                        with c2:
                            st.write(row['category'])
                        with c3:
                            st.write(row['description'] or "-")
                        with c4:
                            st.write(format_currency(row['amount']))
                        with c5:
                            with st.popover("🗑️", help="Delete this expense record"):
                                st.write("Confirm delete?")
                                if st.button("Yes, Delete", key=f"del_exp_{rec_id}", type="primary", use_container_width=True):
                                    db.delete_expense(rec_id, user_id)
                                    st.toast("Expense record deleted!", icon="🗑️")
                                    st.rerun()

def show_budgets_goals(user_id):
    st.title("🎯 Budgets & Savings Goals")
    st.info("💡 **Budgets & Goals Guide**: Establish spending limits per category under **Category Budgets** to track real-time overspending alerts. Define target sums and dates under **Saving Target Goals** to track progress on your savings milestones.")
    
    tab1, tab2 = st.tabs(["📊 Set Category Budgets", "🎯 Saving Target Goals"])
    
    with tab1:
        st.subheader("Manage Monthly Budgets")
        col_set, col_status = st.columns([1, 2])
        
        with col_set:
            st.markdown("#### Adjust Limits")
            with st.form("budget_form"):
                cat = st.selectbox("Category", CATEGORIES)
                budget_amt = st.number_input("Monthly Limit (₹)", min_value=0.0, step=50.0, format="%.2f")
                submitted = st.form_submit_button("Set Budget", use_container_width=True)
                if submitted:
                    db.set_budget(user_id, cat, budget_amt)
                    st.session_state.success_toast = f"Set budget limit of {format_currency(budget_amt)} for {cat}!"
                    st.rerun()
                    
        with col_status:
            st.markdown("#### Budget Utilization (This Month)")
            df_bud = db.get_expenses_vs_budget(user_id)
            
            if df_bud.empty:
                st.info("No budgets configured yet. Create a budget on the left!")
            else:
                for idx, row in df_bud.iterrows():
                    budget_val = row['budget_amount']
                    spent_val = row['spent_amount']
                    pct = (spent_val / budget_val) if budget_val > 0 else 0.0
                    
                    # Colors: Red if overspending, Orange if nearing (>85%), otherwise Green
                    if pct > 1.0:
                        color = "#ff1744"
                        label_suffix = f"🚨 (Overspent by {format_currency(spent_val - budget_val)})"
                    elif pct > 0.85:
                        color = "#ffeb3b"
                        label_suffix = "⚠️ (Nearing budget)"
                    else:
                        color = "#00e676"
                        label_suffix = "✅ (Under limit)"
                        
                    st.write(f"**{row['category']}** Budget: **{format_currency(budget_val)}** | Spent: **{format_currency(spent_val)}** {label_suffix}")
                    
                    # Progress bar
                    pct_clamped = min(1.0, max(0.0, pct))
                    st.progress(pct_clamped)
                    
    with tab2:
        col_g1, col_g2 = st.columns([1, 2])
        
        with col_g1:
            st.subheader("Create a Goal")
            with st.form("goal_form"):
                g_name = st.text_input("Goal Name (e.g., Emergency Fund)").strip()
                g_target = st.number_input("Target Amount (₹)", min_value=1.0, step=100.0, format="%.2f")
                g_current = st.number_input("Initial Saved (₹)", min_value=0.0, step=50.0, format="%.2f")
                g_date = st.date_input("Target Date", value=date.today())
                submitted = st.form_submit_button("Add Goal", use_container_width=True)
                if submitted:
                    if not g_name:
                        st.error("Goal name is required.")
                    else:
                        db.add_savings_goal(user_id, g_name, g_target, g_current, g_date.strftime("%Y-%m-%d"))
                        st.session_state.success_toast = f"Added goal: '{g_name}' with a target of {format_currency(g_target)}!"
                        st.rerun()
                        
        with col_g2:
            st.subheader("Active Savings Goals")
            df_g = db.get_savings_goals(user_id)
            if df_g.empty:
                st.info("No savings targets set yet. Use the form on the left to add one.")
            else:
                for idx, row in df_g.iterrows():
                    goal_id = row['id']
                    curr = row['current_amount']
                    targ = row['target_amount']
                    pct = curr / targ
                    pct_clamped = min(1.0, max(0.0, pct))
                    
                    st.markdown(f"#### 🎯 {row['goal_name']}")
                    st.write(f"Progress: **{format_currency(curr)}** of **{format_currency(targ)}** ({pct * 100:.1f}%) | Target Date: **{row['target_date']}**")
                    st.progress(pct_clamped)
                    
                    # Quick contribute form
                    contribute_val = st.number_input(f"Contribute to {row['goal_name']} (₹)", min_value=0.0, step=50.0, key=f"contrib_{goal_id}")
                    col_b1, col_b2 = st.columns([1, 1])
                    with col_b1:
                        if st.button("Add Contribution", key=f"btn_add_{goal_id}"):
                            if contribute_val > 0:
                                db.update_savings_goal(goal_id, user_id, curr + contribute_val)
                                st.session_state.success_toast = f"Recorded contribution of {format_currency(contribute_val)} to '{row['goal_name']}'!"
                                st.rerun()
                    with col_b2:
                        with st.popover("Delete Goal", use_container_width=True):
                            st.write("Confirm goal deletion?")
                            if st.button("Yes, Delete", key=f"btn_del_{goal_id}", type="primary", use_container_width=True):
                                db.delete_savings_goal(goal_id, user_id)
                                st.toast("Savings goal deleted.", icon="🎯")
                                st.rerun()
                    st.markdown("---")

def show_predictions_advice(user_id):
    st.title("🔮 AI Forecasting & Financial Advisory")
    st.info("💡 **ML Forecasting & AI Coaching Guide**: Select your forecast horizon below to view spending projections. We use a Linear Regression model trained on your historical transaction intervals to estimate daily or monthly aggregates.")
    
    df_exp = db.get_expenses(user_id)
    df_inc = db.get_incomes(user_id)
    
    # Selection Selector
    st.write("---")
    horizon = st.radio(
        "Select Forecast Horizon",
        ["📅 Next 10 Days", "📅 Next Month", "📅 Next Year"],
        horizontal=True
    )
    
    # Run ML Model based on selection
    if horizon == "📅 Next 10 Days":
        forecast_results = ml_utils.forecast_expenses_daily(df_exp, days_to_predict=10)
    elif horizon == "📅 Next Month":
        forecast_results = ml_utils.forecast_expenses(df_exp, months_to_predict=1)
    else:
        forecast_results = ml_utils.forecast_expenses(df_exp, months_to_predict=12)
        
    if forecast_results["status"] != "success":
        st.warning(f"⚠️ **ML Forecasting Temporarily Unavailable**: {forecast_results['message']}")
        st.info("💡 **Tip**: Please log transaction records covering at least 7 distinct days (for daily predictions) or 3 distinct calendar months (for monthly predictions).")
    else:
        # Horizon header
        if horizon == "📅 Next 10 Days":
            st.subheader("Daily Expenses Forecasting (10-Day Future Predictor)")
        elif horizon == "📅 Next Month":
            st.subheader("Monthly Expenses Forecasting (Upcoming Month Predictor)")
        else:
            st.subheader("Monthly Expenses Forecasting (12-Month/Next Year Predictor)")
            
        df_hist = forecast_results["historical"]
        df_pred = forecast_results["predictions"]
        metrics = forecast_results["metrics"]
        
        # Plotting Plotly chart
        fig = go.Figure()
        
        if horizon == "📅 Next 10 Days":
            # Only plot last 30 daily data points to keep the chart readable
            df_hist_plot = df_hist.tail(30)
            
            # Historical Daily
            fig.add_trace(go.Scatter(
                x=df_hist_plot["Date"],
                y=df_hist_plot["Actual Expense"],
                mode="lines+markers",
                name="Historical Daily Spending",
                line=dict(color="#00b0ff", width=3),
                marker=dict(size=6, symbol="circle", line=dict(color="#070a13", width=1)),
                hovertemplate='Date: %{x}<br>Spent: ₹%{y:,.2f}<extra></extra>'
            ))
            # Predicted Daily
            fig.add_trace(go.Scatter(
                x=df_pred["Date"],
                y=df_pred["Predicted Expense"],
                mode="lines+markers",
                name="ML Daily Prediction",
                line=dict(color="#ff9800", width=3, dash="dash"),
                marker=dict(size=6, symbol="diamond", line=dict(color="#070a13", width=1)),
                hovertemplate='Date: %{x}<br>Predicted: ₹%{y:,.2f}<extra></extra>'
            ))
            # Confidence interval Upper bound
            fig.add_trace(go.Scatter(
                x=df_pred["Date"],
                y=df_pred["Upper Bound"],
                mode="lines",
                name="Upper Range",
                line=dict(width=0),
                showlegend=False,
                hoverinfo="skip"
            ))
            # Confidence interval Lower bound
            fig.add_trace(go.Scatter(
                x=df_pred["Date"],
                y=df_pred["Lower Bound"],
                mode="lines",
                name="95% Confidence Range",
                fill="tonexty",
                fillcolor="rgba(255, 152, 0, 0.08)",
                line=dict(width=0),
                hoverinfo="skip"
            ))
        else:
            # Historical Monthly
            fig.add_trace(go.Scatter(
                x=df_hist["Month"],
                y=df_hist["Actual Expense"],
                mode="lines+markers",
                name="Historical Expenses",
                line=dict(color="#00b0ff", width=3, shape="spline"),
                marker=dict(size=8, symbol="circle", line=dict(color="#070a13", width=1.5)),
                hovertemplate='Spent: ₹%{y:,.2f}<extra></extra>'
            ))
            # Predicted Monthly
            fig.add_trace(go.Scatter(
                x=df_pred["Month"],
                y=df_pred["Predicted Expense"],
                mode="lines+markers",
                name="ML Prediction",
                line=dict(color="#ff9800", width=3, dash="dash", shape="spline"),
                marker=dict(size=8, symbol="diamond", line=dict(color="#070a13", width=1.5)),
                hovertemplate='Predicted: ₹%{y:,.2f}<extra></extra>'
            ))
            # Confidence interval Upper bound
            fig.add_trace(go.Scatter(
                x=df_pred["Month"],
                y=df_pred["Upper Bound"],
                mode="lines",
                name="Upper Forecast Range",
                line=dict(width=0),
                showlegend=False,
                hoverinfo="skip"
            ))
            # Confidence interval Lower bound
            fig.add_trace(go.Scatter(
                x=df_pred["Month"],
                y=df_pred["Lower Bound"],
                mode="lines",
                name="95% Confidence Range",
                fill="tonexty",
                fillcolor="rgba(255, 152, 0, 0.08)",
                line=dict(width=0),
                hoverinfo="skip"
            ))
            
        fig.update_layout(
            title=dict(
                text="Daily Expense Projection" if horizon == "📅 Next 10 Days" else "Linear Regression Monthly Forecast",
                font=dict(family='Outfit', size=14, color='#ffffff')
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#ffffff',
            xaxis=dict(showgrid=False, tickfont=dict(family='Outfit', size=11)),
            yaxis=dict(gridcolor='rgba(255,255,255,0.06)', tickfont=dict(family='Outfit', size=11)),
            margin=dict(l=20, r=20, t=50, b=20),
            height=350,
            legend=dict(font=dict(family='Outfit', size=11), orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Display Metrics cards
        col1, col2, col3 = st.columns(3)
        unit = "day" if horizon == "📅 Next 10 Days" else "month"
        with col1:
            st.metric(f"Average Spending (per {unit})", format_currency(metrics["average_expense"]))
        with col2:
            st.metric(f"Linear Spending Trend (slope)", f"{format_currency(metrics['slope'])} / {unit}", 
                      delta=f"Increasing" if metrics["slope"] > 0 else "Decreasing", 
                      delta_color="inverse")
        with col3:
            st.metric("Model Strength (R²)", f"{metrics['r_squared'] * 100:.2f}%")
            
        st.markdown("---")
        
        # 2. Financial Advisory Engine (Always calculate monthly metrics to ensure stable advice context)
        st.subheader("💡 Dynamic Financial Advice")
        
        # Calculate monthly summary for Gemini
        monthly_advice_results = ml_utils.forecast_expenses(df_exp, months_to_predict=3)
        monthly_metrics = monthly_advice_results.get("metrics", metrics)
        monthly_df_pred = monthly_advice_results.get("predictions", df_pred)
        
        # Calculate recent parameters
        avg_monthly_inc = 0.0
        if not df_inc.empty:
            df_inc['date'] = pd.to_datetime(df_inc['date'])
            monthly_inc = df_inc.groupby(df_inc['date'].dt.to_period('M'))['amount'].sum()
            avg_monthly_inc = monthly_inc.mean()
            
        df_bud = db.get_expenses_vs_budget(user_id)
        
        # Prepare context data for Gemini Advisor
        category_summary_text = ""
        overspent_summary_text = ""
        if not df_bud.empty:
            for idx, r in df_bud.iterrows():
                category_summary_text += f"- {r['category']}: Spent ₹{r['spent_amount']:,.2f} / Budget ₹{r['budget_amount']:,.2f}\n"
                if r['spent_amount'] > r['budget_amount']:
                    overspent_summary_text += f"- {r['category']}: Overspent by ₹{r['spent_amount'] - r['budget_amount']:,.2f} (Spent: ₹{r['spent_amount']:,.2f} / Budget: ₹{r['budget_amount']:,.2f})\n"
        if not category_summary_text:
            category_summary_text = "No category budgets or transactions recorded."
        if not overspent_summary_text:
            overspent_summary_text = "No categories overspent. Excellent job!"
            
        financial_data = {
            "avg_income": avg_monthly_inc,
            "avg_expenses": monthly_metrics["average_expense"],
            "net_savings": avg_monthly_inc - monthly_metrics["average_expense"],
            "savings_rate": ((avg_monthly_inc - monthly_metrics["average_expense"]) / avg_monthly_inc) * 100 if avg_monthly_inc > 0 else 0.0,
            "slope": monthly_metrics["slope"],
            "forecast_next_month": monthly_df_pred["Predicted Expense"].iloc[0] if not monthly_df_pred.empty else 0.0,
            "category_summary_text": category_summary_text,
            "overspent_summary_text": overspent_summary_text
        }
        
        # Create standard and Gemini tab options
        tab_static, tab_ai = st.tabs(["📋 Standard Insights", "🧠 Gemini AI Coaching"])
        
        with tab_static:
            advice_list = []
            
            # Trend advice
            if monthly_metrics["slope"] > 20.0:
                advice_list.append({
                    "icon": "⚠️",
                    "title": "Rising Spending Trend Detected",
                    "desc": f"Your monthly expenses are trending upwards by {format_currency(monthly_metrics['slope'])} per month. We advise auditing your discretionary categories (like Shopping or Entertainment) to stabilize this trend."
                })
            elif monthly_metrics["slope"] < -20.0:
                advice_list.append({
                    "icon": "🎉",
                    "title": "Healthy Spending Trend Decreasing",
                    "desc": "Great job! Your overall spending is decreasing month-over-month. Keep doing what you are doing, and allocate the surplus to your savings goals."
                })
                
            # Savings Rate advice
            if avg_monthly_inc > 0:
                savings_rate = ((avg_monthly_inc - monthly_metrics["average_expense"]) / avg_monthly_inc) * 100
                if savings_rate < 10.0:
                    advice_list.append({
                        "icon": "🚨",
                        "title": "Low Savings Rate",
                        "desc": f"Your average savings rate is {savings_rate:.1f}%, which is below the recommended 20%. Consider adopting the **50/30/20 budgeting rule** (50% Needs, 30% Wants, 20% Savings)."
                    })
                elif savings_rate >= 25.0:
                    advice_list.append({
                        "icon": "🌟",
                        "title": "Exceptional Savings Performance",
                        "desc": f"You are saving an average of {savings_rate:.1f}% of your monthly income. This puts you in a strong position. Think about indexing these savings in diversified investments."
                    })
                    
            # Category advice
            if not df_bud.empty:
                overspent = df_bud[df_bud['spent_amount'] > df_bud['budget_amount']]
                for idx, r in overspent.iterrows():
                    advice_list.append({
                        "icon": "📌",
                        "title": f"Review {r['category']} Budget",
                        "desc": f"You have overspent in {r['category']} this month. Check if this is a one-time outlier. If it's a regular occurrence, adjust the budget limit to reflect reality, or enforce stricter caps."
                    })
                    
            # Defaults if empty
            if not advice_list:
                advice_list.append({
                    "icon": "ℹ️",
                    "title": "Financial Health Stable",
                    "desc": "No warning triggers hit. Continue logging your details daily to get further personalized insights."
                })
                
            # Display advice list
            for item in advice_list:
                st.markdown(f"#### {item['icon']} {item['title']}")
                st.write(item['desc'])
                st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                
        with tab_ai:
            st.markdown("<p style='color: #8892b0; font-size: 0.95rem; margin-bottom: 20px;'>Consult your personal AI Coach powered by <b>Gemini 2.5 Flash</b> for advanced, context-aware analysis of your spending habits, saving strategies, and forecasts.</p>", unsafe_allow_html=True)
            
            if "ai_coaching_report" not in st.session_state:
                st.session_state.ai_coaching_report = None
                
            if st.button("🤖 Generate AI Coaching Report", type="primary", use_container_width=True):
                with st.spinner("Connecting to Gemini AI Coach..."):
                    report = ml_utils.generate_gemini_financial_advice(financial_data)
                    st.session_state.ai_coaching_report = report
                    
            if st.session_state.ai_coaching_report:
                st.markdown("---")
                st.markdown("<h4 style='color: #00e676; margin-bottom: 15px;'>🧠 Gemini Financial Coach Report</h4>", unsafe_allow_html=True)
                st.markdown(st.session_state.ai_coaching_report)
                
                # Option to clear/refresh
                if st.button("🔄 Refresh Report", key="btn_refresh_ai_report", use_container_width=True):
                    st.session_state.ai_coaching_report = None
                    st.rerun()

def show_ai_coach(user_id):
    st.title("🧠 AI Financial Assistant")
    
    # 1. Check data availability
    df_exp = db.get_expenses(user_id)
    df_inc = db.get_incomes(user_id)
    budgets = db.get_budgets(user_id)
    
    if df_exp.empty and df_inc.empty:
        st.warning("⚠️ **Insufficient Data**: Please log some transactions (income or expenses) to consult the AI Financial Coach.")
        return
        
    # Get multi-month historical summary
    summary = ml_utils.get_historical_financial_summary(df_exp, df_inc, budgets)
    
    if summary["status"] == "no_data":
        st.warning("⚠️ **Insufficient Data**: No historical transaction logs detected.")
        return
        
    num_months = len(summary["months_data"])
    st.info(f"📊 **Context Loaded**: Found **{num_months} month(s)** of financial history to analyze. Categories evaluated: {', '.join(summary['category_averages'].keys())}")
    
    if not st.session_state.chat_started:
        # Welcome Gate Page
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(138, 43, 226, 0.08) 0%, rgba(99, 102, 241, 0.08) 100%); padding: 25px; border-radius: 16px; border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 25px; margin-top: 15px;">
            <h3 style="margin: 0; color: #ffffff; font-weight: 700; font-size: 1.4rem;">👋 Meet Your Wealth Advisor</h3>
            <p style="margin: 8px 0 20px 0; color: #8892b0; font-size: 0.95rem; line-height: 1.6;">
                WealthFlow AI Advisor is ready to analyze your multi-month income, expense records, and budget targets to offer personalized, real-time guidance. 
                Click the button below to start a secure, one-on-one chat session where you can ask custom questions or request complete audits.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("💬 Ask Advisor", type="primary", use_container_width=True):
            st.session_state.chat_started = True
            st.session_state.ai_chat_history = [
                {
                    "role": "assistant",
                    "content": "👋 **Welcome to your AI Financial Coach!**\n\nI have loaded your active financial logs, current budgets, and savings goals. You can ask me any custom question about your spending habits, or choose one of the quick actions below to begin."
                }
            ]
            st.rerun()
    else:
        # Active Chat Room Screen
        col_hdr1, col_hdr2 = st.columns([3.2, 0.8])
        with col_hdr1:
            st.subheader("💬 Advisor Chat Session")
        with col_hdr2:
            if st.button("🔙 Exit & Reset Chat", use_container_width=True):
                st.session_state.chat_started = False
                st.session_state.ai_chat_history = []
                st.rerun()
                
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        
        # Render scrollable history
        for msg in st.session_state.ai_chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
        st.markdown("---")
        
        # Quick Actions
        st.write("✨ **Quick Actions:**")
        col_s1, col_s2, col_s3 = st.columns(3)
        preset_query = None
        with col_s1:
            if st.button("📊 Run Full Audit", use_container_width=True, help="Analyze full history and provide an overall grade."):
                preset_query = "Please run a full financial history audit and provide a budget optimization report with grade."
        with col_s2:
            if st.button("💡 Optimize Budgets", use_container_width=True, help="Get category budget recommendations based on averages."):
                preset_query = "Suggest concrete budget optimizations based on my average monthly spending."
        with col_s3:
            if st.button("🔮 Spending Forecasts", use_container_width=True, help="Analyze spending trends and budget overflow risks."):
                preset_query = "Analyze my current spending trends and predict any future budget overflow risks."
                
        # st.chat_input automatically clears itself on submit
        prompt = st.chat_input("Ask a question about your finances...")
        
        if preset_query or prompt:
            query_text = preset_query or prompt
            st.session_state.ai_chat_history.append({"role": "user", "content": query_text})
            
            with st.spinner("Thinking..."):
                answer = ml_utils.ask_gemini_custom_question(summary, query_text, st.session_state.ai_chat_history[:-1])
                st.session_state.ai_chat_history.append({"role": "assistant", "content": answer})
                st.rerun()


def show_settings(user_id):
    st.title("🛠 Settings")
    st.info("💡 **Settings Guide**: Manage your active user sessions here. You can sign out of your current account session individually or sign out of all active concurrent profiles at once.")
    
    st.subheader("User Information")
    st.info(f"Logged in as: **{st.session_state.username}** (User ID: {user_id})")
    
    st.markdown("---")
    st.subheader("🚪 Session Management")
    
    col_out1, col_out2 = st.columns(2)
    with col_out1:
        if st.button("Sign Out of Current Account", use_container_width=True):
            curr_id = st.session_state.user_id
            if curr_id in st.session_state.active_users:
                del st.session_state.active_users[curr_id]
                
            if st.session_state.active_users:
                next_id = list(st.session_state.active_users.keys())[0]
                st.session_state.user_id = next_id
                st.session_state.username = st.session_state.active_users[next_id]
                st.session_state.ai_coaching_report = None
            else:
                st.session_state.logged_in = False
                st.session_state.user_id = None
                st.session_state.username = None
                st.session_state.ai_coaching_report = None
                st.session_state.show_add_account = False
            st.success("Successfully signed out of the current account.")
            st.rerun()
            
    with col_out2:
        if st.button("Sign Out of All Accounts", type="primary", use_container_width=True):
            st.session_state.active_users = {}
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.ai_coaching_report = None
            st.session_state.show_add_account = False
            st.success("Successfully signed out of all accounts.")
            st.rerun()

    st.markdown("---")
    st.subheader("⚙️ Data Tools")
    st.markdown("""
    <p style='color: #8892b0; font-size: 0.92rem; margin-bottom: 15px; line-height: 1.5;'>
        Need to test the ML forecasting models and Gemini AI coach with rich, multi-month trends? 
        Use the button below to seed 6 months of mock transactions, category budgets, and savings goals. 
        <br/><strong style='color: #ff9800;'>⚠️ Warning:</strong> This will overwrite all existing transaction records for the current profile.
    </p>
    """, unsafe_allow_html=True)
    if st.button("🚀 Regenerate & Seed 6-Month Demo Data", key="seed_settings_data", use_container_width=True):
        with st.spinner("Clearing old records and seeding new mock data..."):
            db.generate_mock_data(user_id)
        st.toast("🎉 Account successfully populated with mock financial history!", icon="🚀")
        st.rerun()

# --- MAIN APP ROUTING ---

def main():
    if "success_toast" in st.session_state and st.session_state.success_toast:
        st.toast(st.session_state.success_toast, icon="✅")
        st.session_state.success_toast = None
        
    if not st.session_state.logged_in or st.session_state.show_add_account:
        show_auth_page()
    else:
        # Sidebar layout
        with st.sidebar:
            st.markdown(f"""
                <div class="text-center-sidebar">
                    <h2 style='color: #00e676; margin-bottom: 0px;'>💰 WealthFlow</h2>
                    <p style='color: #8892b0; margin-bottom: 25px;'>Welcome, <b>{st.session_state.username}</b></p>
                </div>
            """, unsafe_allow_html=True)
            
            # Account Switcher
            st.markdown("<p style='color: #8892b0; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;'>👥 Accounts</p>", unsafe_allow_html=True)
            user_options = {uname: uid for uid, uname in st.session_state.active_users.items()}
            current_uname = st.session_state.username
            
            try:
                index = list(user_options.keys()).index(current_uname)
            except ValueError:
                index = 0
                
            selected_uname = st.selectbox(
                "Switch Active Account",
                options=list(user_options.keys()),
                index=index,
                label_visibility="collapsed",
                key="account_switcher"
            )
            
            if selected_uname != current_uname:
                st.session_state.user_id = user_options[selected_uname]
                st.session_state.username = selected_uname
                st.session_state.ai_coaching_report = None
                st.rerun()
                
            if st.button("➕ Add Account", use_container_width=True):
                st.session_state.show_add_account = True
                st.rerun()
                
            st.markdown("<hr style='margin: 15px 0; border: none; border-top: 1px solid rgba(255,255,255,0.08);'/>", unsafe_allow_html=True)
            
            page = st.radio(
                "Navigate Menu",
                ["🏠 Dashboard Overview", "🔀 Transactions", "🎯 Budgets & Goals", "🔮 Predictions & Advice", "🧠 AI Financial Coach", "🛠 Settings"]
            )
            
        # Display selected page
        if page == "🏠 Dashboard Overview":
            show_dashboard(st.session_state.user_id)
        elif page == "🔀 Transactions":
            show_transactions(st.session_state.user_id)
        elif page == "🎯 Budgets & Goals":
            show_budgets_goals(st.session_state.user_id)
        elif page == "🔮 Predictions & Advice":
            show_predictions_advice(st.session_state.user_id)
        elif page == "🧠 AI Financial Coach":
            show_ai_coach(st.session_state.user_id)
        elif page == "🛠 Settings":
            show_settings(st.session_state.user_id)


if __name__ == "__main__":
    main()

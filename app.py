import streamlit as st
from streamlit_option_menu import option_menu

from database import init_db
from styles import load_css
from auth import render_auth_page
from home import render_home_page
from dashboard import render_dashboard_page
from stock_market import render_stock_page
from prediction import render_prediction_page
from about import render_about_page
from contact import render_contact_page
from ai_assistant import render_floating_chatbot
from user_profile import render_user_profile
from adminpanel import render_admin_page

# Page Configuration
st.set_page_config(
    page_title="Visionary Analytics",
    page_icon="🤖",
    layout="wide"
)

# Initialize Database & Custom CSS
init_db()
load_css("Style.css")

# Session State Setup
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = "user"
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

# Authentication Check
if not st.session_state.logged_in:
    render_auth_page()
    st.stop()


# ---------------- 📑 MODAL DIALOGS ----------------
@st.dialog("👤 User Profile & Settings", width="large")
def show_profile_modal():
    render_user_profile()


@st.dialog("❓ How Visionary Analytics Works", width="large")
def show_help_modal():
    st.markdown("### 🚀 Welcome to Visionary Analytics!")
    st.write("Yeh platform aapke business & dataset ko analyze karke AI-powered insights provide karta hai. Niche dekhiye poora project kaise kaam karta hai:")

    st.divider()

    # SECTION 1: END-TO-END WORKFLOW
    st.markdown("### 🔄 1. Complete Workflow")
    st.markdown("""
    1. **🔑 Authentication & Account Security**
       * User Login & Registration System (SQLite Backend).
       * **Security:** Failed attempts par account auto-lock hota hai aur Forgot Password par OTP email send hota hai.

    2. **📊 Data Analysis & Visualization (`Dashboard`)**
       * Sales Excel file (`.xlsx`) upload karein.
       * Instant KPIs, Interactive Plotly Visual Charts, Correlation Heatmaps dekhein aur PDF Report download karein.

    3. **📈 Sales Prediction (`Prediction`)**
       * Machine Learning (`scikit-learn` Linear Regression) ke sath numerical variables choose karke future values forecast karein.

    4. **💹 Live Financial Intelligence (`Stock Market`)**
       * Yahoo Finance (`yfinance`) se live stocks ka data aur Google Gemini AI se auto-generated financial summaries payein.

    5. **👤 User Profile & History (`Profile`)**
       * Profile details dekhein, Password change karein aur apni Upload History manage/clear karein.

    6. **🛡️ Admin Dashboard (`Admin Panel`)**
       * Admin roles platform-wide users aur unki file upload history ko track & audit kar sakte hain.
    """)

    st.divider()

    # SECTION 2: MODULE EXPANDERS
    st.markdown("### 🧩 2. Project Modules Overview")

    with st.expander("🔐 Authentication & Security", expanded=False):
        st.write("""
        * **Login/Signup:** Passwords SHA-256 hash format me securely store hote hain.
        * **Account Recovery:** 6-digit OTP mail par receive hota hai password reset ke liye.
        """)

    with st.expander("📊 Dashboard & PDF Report Generation", expanded=False):
        st.write("""
        * **Data Processing:** Excel sheet se total sales, average, and row counts calculate hote hain.
        * **PDF Export:** `fpdf` library se dynamically summary report download hoti hai.
        """)

    with st.expander("🔮 ML Predictions & AI Stock Analysis", expanded=False):
        st.write("""
        * **ML Model:** Linear Regression engine independent ($X$) aur dependent ($Y$) variables par fit hota hai.
        * **Gemini AI:** Live stock graphs ke trend ko natural language summary me translate karta hai.
        """)

    st.divider()

    # SECTION 3: QUICK FAQ
    st.markdown("### ❓ Quick FAQ")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Q: Konsi files supported hain?**\n*Ans: Abhi Dashboard me `.xlsx` (Excel) files supported hain.*")
    with col2:
        st.markdown("**Q: Data kaha save hota hai?**\n*Ans: User data aur upload logs SQLite (`users.db`) database me local database me store hote hain.*")


# ---------------- 👤 PROFILE POPOVER ----------------
def render_profile_popover():
    username = st.session_state.get("username", "User")
    role_label = "🛡️ Admin" if st.session_state.get("role") == "admin" else "User"

    with st.popover(f"🟡 **{username}**  \n:grey[{role_label}]", use_container_width=True):
        st.markdown(f"### 🟡 {username}")
        st.caption(role_label + " Account")
        st.divider()

        if st.button("👤 Profile", use_container_width=True, key="pop_profile"):
            show_profile_modal()

        if st.button("❓ Help", use_container_width=True, key="pop_help"):
            show_help_modal()

        st.divider()

        if st.button("🚪 Log out", use_container_width=True, key="pop_logout"):
            st.toast("✅ Logged Out Successfully!")
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.role = "user"
            st.session_state.current_page = "Home"
            st.rerun()


# ---------------- 📍 SIDEBAR NAVIGATION ----------------
with st.sidebar:
    st.title("📊 Visionary Analytics")

    # Base pages array for normal users
    pages = ["Home", "Dashboard", "Stock Market", "Prediction", "About", "Contact"]
    icons = ["house-fill", "bar-chart-fill", "currency-exchange", "graph-up", "info-circle-fill", "telephone-fill"]

    # SIRF ADMIN USERS KE LIYE ADMIN PANEL SIDEBAR ME SHOW HOGA
    if st.session_state.get("role") == "admin":
        pages.append("Admin Panel")
        icons.append("shield-lock-fill")

    if st.session_state.get("jump_to_dashboard", False):
        st.session_state.current_page = "Dashboard"
        st.session_state.jump_to_dashboard = False
        st.rerun()

    default_idx = pages.index(st.session_state.current_page) if st.session_state.current_page in pages else 0

    menu = option_menu(
        menu_title="Navigation",
        options=pages,
        icons=icons,
        menu_icon="list",
        default_index=default_idx,
        styles={
            "container": {"padding": "5px", "background-color": "#161B22"},
            "icon": {"color": "#FF4B4B", "font-size": "18px"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "4px", "border-radius": "8px"},
            "nav-link-selected": {"background-color": "#1F6FEB", "color": "white"}
        }
    )

    st.session_state.current_page = menu
    st.divider()

    file_is_uploaded = st.session_state.get("dashboard_file_uploader") is not None
    show_profile_here = not (menu == "Dashboard" and file_is_uploaded)

    if show_profile_here:
        render_profile_popover()


# ---------------- 🔀 PAGE ROUTING ----------------
if menu == "Home":
    render_home_page()
elif menu == "Dashboard":
    render_dashboard_page()
elif menu == "Stock Market":
    render_stock_page()
elif menu == "Prediction":
    render_prediction_page()
elif menu == "About":
    render_about_page()
elif menu == "Contact":
    render_contact_page()
elif menu == "Admin Panel":
    if st.session_state.get("role") == "admin":
        render_admin_page()
    else:
        st.error("⛔ Access denied. Admins only.")
        st.stop()

if not show_profile_here:
    with st.sidebar:
        st.divider()
        render_profile_popover()

render_floating_chatbot()
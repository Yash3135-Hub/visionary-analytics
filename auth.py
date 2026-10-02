import streamlit as st
import sqlite3
import hashlib
from database import get_db_connection

# Password Hashing Helper
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# ---------------- 🔑 LOGIN FUNCTION ----------------
def login_user(username, password):
    conn = get_db_connection()
    c = conn.cursor()
    hashed_pass = make_hashes(password)
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_pass))
    user = c.fetchone()
    conn.close()
    return user

# ---------------- 📝 REGISTER USER FUNCTION (FORCED ROLE = "user") ----------------
def add_user(username, email, password):
    conn = get_db_connection()
    c = conn.cursor()
    hashed_pass = make_hashes(password)
    
    # SECURITY FIX: Role hamesha hardcoded 'user' hi insert hoga
    c.execute(
        "INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
        (username, email, hashed_pass, "user")
    )
    conn.commit()
    conn.close()

# ---------------- 🖥️ MAIN AUTH UI PAGE ----------------
def render_auth_page():
    st.markdown("<h1 style='text-align: center;'>🤖 Visionary Analytics</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: gray;'>Authentication Portal</h4>", unsafe_allow_html=True)
    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        tab1, tab2 = st.tabs(["🔒 Login", "📝 Register"])

        # ------------ TAB 1: LOGIN ------------
        with tab1:
            st.subheader("Login to Your Account")
            username = st.text_input("Username", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")

            if st.button("Log In", use_container_width=True, type="primary"):
                if username and password:
                    user = login_user(username, password)
                    if user:
                        # Database schema: (id, username, email, password, role, ...)
                        # Adjust index according to your DB structure (Assuming index 1=username, 4=role)
                        st.session_state.logged_in = True
                        st.session_state.username = user[1] if len(user) > 1 else username
                        st.session_state.role = str(user[4]).lower() if len(user) > 4 else "user"
                        
                        st.toast(f"Welcome back, {username}!", icon="👋")
                        st.rerun()
                    else:
                        st.error("❌ Invalid Username or Password")
                else:
                    st.warning("⚠️ Please fill in all fields.")

        # ------------ TAB 2: REGISTER (ADMIN SELECTION REMOVED) ------------
        with tab2:
            st.subheader("Create a New Account")
            new_username = st.text_input("Username", key="reg_username")
            new_email = st.text_input("Email", key="reg_email")
            new_password = st.text_input("Password", type="password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm_password")

            # NOTE: Is section se Role Selection (Admin/User Checkbox/Selectbox) poori tarah hata diya gaya hai.

            if st.button("Register Account", use_container_width=True):
                if new_username and new_email and new_password and confirm_password:
                    if new_password != confirm_password:
                        st.error("❌ Passwords do not match.")
                    else:
                        try:
                            add_user(new_username, new_email, new_password)
                            st.success("🎉 Account created successfully! Please switch to the Login tab.")
                        except sqlite3.IntegrityError:
                            st.error("⚠️ Username or Email already exists.")
                        except Exception as e:
                            st.error(f"❌ Error during registration: {e}")
                else:
                    st.warning("⚠️ Please fill in all required fields.")

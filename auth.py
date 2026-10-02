import streamlit as st
import sqlite3
import hashlib

# Database Connection Helper
def get_db_connection():
    conn = sqlite3.connect("users.db", check_same_thread=False)
    return conn

# Password Hashing Helpers
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# Verify Login User
def login_user(username, password):
    conn = get_db_connection()
    c = conn.cursor()
    hashed_pass = make_hashes(password)
    
    try:
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_pass))
        user = c.fetchone()
    except sqlite3.OperationalError:
        c.execute("SELECT * FROM userstable WHERE username = ? AND password = ?", (username, hashed_pass))
        user = c.fetchone()
        
    conn.close()
    return user

# Register User (Role ALWAYS forced to 'user')
def add_user(username, email, password):
    conn = get_db_connection()
    c = conn.cursor()
    hashed_pass = make_hashes(password)
    
    try:
        c.execute(
            "INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
            (username, email, hashed_pass, "user")
        )
    except sqlite3.OperationalError:
        c.execute(
            "INSERT INTO userstable (username, email, password, role) VALUES (?, ?, ?, ?)",
            (username, email, hashed_pass, "user")
        )
        
    conn.commit()
    conn.close()

# Main Auth UI Function
def render_auth_page():
    # Center Layout Columns (UI ko broad hone se rokne ke liye)
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("<h2 style='text-align: center;'>🔐 User Authentication</h2>", unsafe_allow_html=True)
        st.caption("Login to access Visionary Analytics")

        tab1, tab2, tab3 = st.tabs(["Login", "Register", "Forgot Password"])

        # ------------ TAB 1: LOGIN ------------
        with tab1:
            username = st.text_input("👤 Username", key="login_user")
            password = st.text_input("🔒 Password", type="password", key="login_pass")

            if st.button("Login", use_container_width=True, type="primary"):
                if username and password:
                    user = login_user(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username = user[1] if len(user) > 1 else username
                        
                        user_role = "user"
                        if len(user) > 4 and user[4]:
                            user_role = str(user[4]).lower()
                        elif len(user) > 3 and str(user[3]).lower() in ["admin", "user"]:
                            user_role = str(user[3]).lower()
                            
                        st.session_state.role = user_role
                        st.toast(f"Welcome back, {username}!", icon="👋")
                        st.rerun()
                    else:
                        st.error("❌ Invalid Username or Password")
                else:
                    st.warning("⚠️ Please fill in all fields.")

        # ------------ TAB 2: REGISTER (DROPDOWN REMOVED) ------------
        with tab2:
            reg_username = st.text_input("👤 Username", key="reg_user")
            reg_email = st.text_input("📧 Email", key="reg_email")
            reg_password = st.text_input("🔒 Password", type="password", key="reg_pass")

            if st.button("Register", use_container_width=True, type="primary"):
                if reg_username and reg_email and reg_password:
                    try:
                        add_user(reg_username, reg_email, reg_password)
                        st.success("🎉 Account created successfully! Please switch to Login tab.")
                    except sqlite3.IntegrityError:
                        st.error("⚠️ Username or Email already exists.")
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
                else:
                    st.warning("⚠️ Please fill all fields.")

        # ------------ TAB 3: FORGOT PASSWORD ------------
        with tab3:
            st.info("💡 Password recovery active. Contact administrator if needed.")

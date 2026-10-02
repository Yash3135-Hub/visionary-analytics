import streamlit as st
import sqlite3
import hashlib
import random
import smtplib
from email.mime.text import MIMEText

# Database Connection Helper
def get_db_connection():
    conn = sqlite3.connect("users.db", check_same_thread=False)
    c = conn.cursor()
    
    # Create table if missing
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    """)
    conn.commit()
    return conn

# Force Reset Admin Credentials in DB
def enforce_admin_credentials():
    conn = get_db_connection()
    c = conn.cursor()
    hashed_admin_pass = hashlib.sha256(str.encode("admin123")).hexdigest()
    
    # Force update or insert admin directly
    c.execute("SELECT * FROM users WHERE LOWER(username) = 'admin'")
    if c.fetchone():
        c.execute(
            "UPDATE users SET password = ?, role = 'admin' WHERE LOWER(username) = 'admin'",
            (hashed_admin_pass,)
        )
    else:
        c.execute(
            "INSERT INTO users (username, email, password, role) VALUES ('admin', 'admin@visionary.com', ?, 'admin')",
            (hashed_admin_pass,)
        )
    conn.commit()
    conn.close()

# Password Hashing Helpers
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# Fetch Email by Username or Email Input
def get_user_email(identifier):
    conn = get_db_connection()
    c = conn.cursor()
    user_email = None
    try:
        if "@" in identifier:
            c.execute("SELECT email FROM users WHERE LOWER(email) = LOWER(?)", (identifier,))
            res = c.fetchone()
            if res:
                user_email = res[0]
        else:
            c.execute("SELECT email FROM users WHERE LOWER(username) = LOWER(?)", (identifier,))
            res = c.fetchone()
            if res:
                user_email = res[0]
    except Exception:
        pass
    conn.close()
    return user_email

# Verify Login User & Check Role Match
def login_user(username, password, selected_role):
    # Always enforce admin update when logging in as admin
    if username.strip().lower() == "admin":
        enforce_admin_credentials()

    conn = get_db_connection()
    c = conn.cursor()
    hashed_pass = make_hashes(password)
    
    c.execute("SELECT * FROM users WHERE LOWER(username) = LOWER(?) AND password = ?", (username.strip(), hashed_pass))
    user = c.fetchone()
    conn.close()
    
    if user:
        # Extract role regardless of table column order
        db_role = "user"
        for field in user:
            if str(field).lower() in ["admin", "user"]:
                db_role = str(field).lower()
                break

        if db_role == selected_role.strip().lower():
            return user, db_role
        else:
            return None, "ROLE_MISMATCH"
            
    return None, "INVALID_CREDENTIALS"

# Register User (Role default 'user')
def add_user(username, email, password):
    conn = get_db_connection()
    c = conn.cursor()
    hashed_pass = make_hashes(password)
    
    c.execute(
        "INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
        (username, email, hashed_pass, "user")
    )
    conn.commit()
    conn.close()

# Update Password in DB (by Username or Email)
def update_password(identifier, new_password):
    conn = get_db_connection()
    c = conn.cursor()
    hashed_pass = make_hashes(new_password)
    
    c.execute("UPDATE users SET password = ? WHERE LOWER(username) = LOWER(?) OR LOWER(email) = LOWER(?)", (hashed_pass, identifier, identifier))
    conn.commit()
    conn.close()

# OTP Sender Helper Function
def send_otp_email(to_email, otp):
    try:
        sender_email = st.secrets["SMTP_EMAIL"]
        sender_password = str(st.secrets["SMTP_PASSWORD"]).replace(" ", "")
    except Exception as e:
        return False, f"Secrets configuration error: {e}"

    if not sender_email or not sender_password:
        return False, "SMTP Email or Password missing in Streamlit Secrets."

    msg = MIMEText(f"Your OTP for resetting Visionary Analytics password is: {otp}")
    msg['Subject'] = "Password Reset OTP - Visionary Analytics"
    msg['From'] = sender_email
    msg['To'] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        return True, "OTP Sent Successfully"
    except Exception as e:
        return False, str(e)

# Main Auth UI
def render_auth_page():
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown("<h2 style='text-align: center;'>🔐 User Authentication</h2>", unsafe_allow_html=True)
        st.caption("Login to access Visionary Analytics")

        tab1, tab2, tab3 = st.tabs(["Login", "Register", "Forgot Password"])

        # ------------ TAB 1: LOGIN ------------
        with tab1:
            username = st.text_input("👤 Username", key="login_user")
            password = st.text_input("🔒 Password", type="password", key="login_pass")
            login_role = st.selectbox("🔑 Login As", ["User", "Admin"], key="login_role_select")

            if st.button("Login", use_container_width=True, type="primary"):
                if username and password:
                    user, status = login_user(username, password, login_role)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.username = user[1] if len(user) > 1 else username
                        st.session_state.role = status
                        st.toast(f"Welcome back, {username}!", icon="👋")
                        st.rerun()
                    elif status == "ROLE_MISMATCH":
                        st.error(f"❌ Account '{username}' is not registered as {login_role}.")
                    else:
                        st.error("❌ Invalid Username or Password")
                else:
                    st.warning("⚠️ Please fill in all fields.")

        # ------------ TAB 2: REGISTER ------------
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
            st.subheader("Reset Password")
            
            user_identifier = st.text_input("👤 Username / Registered Email", key="reset_identifier")
            
            if st.button("Send OTP", key="send_otp_btn", use_container_width=True):
                if user_identifier:
                    recipient_email = get_user_email(user_identifier)
                    
                    if not recipient_email and "@" in user_identifier:
                        recipient_email = user_identifier
                        
                    if recipient_email:
                        generated_otp = str(random.randint(100000, 999999))
                        st.session_state["otp_generated"] = generated_otp
                        st.session_state["reset_user_id"] = user_identifier
                        
                        with st.spinner("Sending OTP..."):
                            success, msg = send_otp_email(recipient_email, generated_otp)
                            
                        if success:
                            st.session_state["otp_sent"] = True
                            st.success(f"📩 OTP sent successfully to registered email ({recipient_email})!")
                        else:
                            st.session_state["otp_sent"] = False
                            st.error(f"❌ Failed to send email: {msg}")
                    else:
                        st.error("❌ Username or Email not found in database.")
                else:
                    st.warning("⚠️ Please enter Username or Email.")

            if st.session_state.get("otp_sent", False):
                st.divider()
                entered_otp = st.text_input("🔑 Enter OTP", key="reset_otp_input")
                new_pass = st.text_input("🔒 New Password", type="password", key="reset_new_pass")
                confirm_new_pass = st.text_input("🔒 Confirm New Password", type="password", key="reset_conf_pass")

                if st.button("Update Password", use_container_width=True, type="primary"):
                    if not entered_otp or not new_pass or not confirm_new_pass:
                        st.warning("⚠️ Please fill all fields.")
                    elif new_pass != confirm_new_pass:
                        st.error("❌ New passwords do not match.")
                    elif entered_otp != st.session_state.get("otp_generated", ""):
                        st.error("❌ Invalid OTP.")
                    else:
                        update_password(st.session_state.get("reset_user_id"), new_pass)
                        st.success("✅ Password updated successfully! Switch to Login tab to log in.")
                        st.session_state["otp_sent"] = False
                        st.session_state["otp_generated"] = None

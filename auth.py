import streamlit as st
import re

from database import (
    login_user, register_user, get_email_for_username, update_password,
    check_lockout, record_failed_attempt, reset_login_attempts, get_user_role
)
from utils import generate_otp, send_otp_email
from config import EMAIL_ADDRESS, EMAIL_APP_PASSWORD

def render_auth_page():
    col_l, col_c, col_r = st.columns([1, 1.3, 1])

    with col_c:
        with st.container(key="auth_card"):
            st.title("🔐 User Authentication")
            st.caption("Login to access Visionary Analytics")

            tab_login, tab_register, tab_forgot = st.tabs(["Login", "Register", "Forgot Password"])

            # ---------------- LOGIN TAB ----------------
            with tab_login:
                login_role = st.radio("Login As:", ["👤 User", "🛡️ Admin"], horizontal=True, key="login_role_radio")
                username = st.text_input("👤 Username", key="login_username")
                password = st.text_input("🔒 Password", type="password", key="login_password")

                if st.button("Login", use_container_width=True, key="login_btn"):

                    remaining_lock = check_lockout(username)

                    if remaining_lock > 0:
                        mins, secs = divmod(remaining_lock, 60)
                        st.error(f"🔒 Account locked due to too many failed attempts. Try again in {mins}m {secs}s.")
                    else:
                        user = login_user(username, password)
                        if user:
                            actual_role = get_user_role(username)
                            selected_as_admin = "Admin" in login_role

                            # Agar user ne Admin option chuna hai par DB me Admin privileges nahi hain
                            if selected_as_admin and actual_role != "admin":
                                st.error("⛔ Access Denied! Your account does not have Admin privileges.")
                            else:
                                reset_login_attempts(username)
                                st.toast(f"✅ Welcome {username}!")
                                
                                st.session_state.logged_in = True
                                st.session_state.username = username
                                st.session_state.role = actual_role
                                
                                # Admin login hone par direct Admin Panel standard page ban jayega
                                if selected_as_admin and actual_role == "admin":
                                    st.session_state.current_page = "Admin Panel"
                                else:
                                    st.session_state.current_page = "Home"

                                st.rerun()
                        else:
                            attempts_left = record_failed_attempt(username)
                            if attempts_left is not None and attempts_left <= 0:
                                st.error("🔒 Too many failed attempts. Account locked for 2 minutes.")
                            elif attempts_left is not None:
                                st.error(f"Invalid Credentials. {attempts_left} attempt(s) remaining.")
                            else:
                                st.error("Invalid Username or Password.")

            # ---------------- REGISTER TAB ----------------
            with tab_register:
                reg_role = st.selectbox("Register Account Type:", ["User", "Admin"], key="reg_role_select")
                reg_username = st.text_input("👤 Username", key="register_username")
                reg_email = st.text_input("📧 Email", key="register_email")
                reg_password = st.text_input("🔒 Password", type="password", key="register_password")
                
                if st.button("Register", use_container_width=True, key="register_btn"):
                    if not reg_username or not reg_email or not reg_password:
                        st.error("Please fill in all fields.")
                    elif not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", reg_email):
                        st.error("⚠️ Please enter a valid email address.")
                    else:
                        target_role = reg_role.lower()
                        status = register_user(reg_username, reg_password, reg_email, role=target_role)
                        if status == "SUCCESS":
                            st.success(f"🎉 Registered successfully as {reg_role}! Please go to Login tab.")
                        elif status == "USERNAME_EXISTS":
                            st.error("❌ Username already taken.")
                        elif status == "EMAIL_EXISTS":
                            st.error("❌ Email already registered.")
                        else:
                            st.error("❌ Database error! Please try again.")

            # ---------------- FORGOT PASSWORD TAB ----------------
            with tab_forgot:
                if "reset_otp" not in st.session_state:
                    st.session_state.reset_otp = None
                if "reset_username" not in st.session_state:
                    st.session_state.reset_username = None

                if st.session_state.reset_otp is None:
                    fp_username = st.text_input("👤 Enter your Username", key="fp_username")
                    if st.button("Send OTP", use_container_width=True, key="send_otp_btn"):
                        email = get_email_for_username(fp_username)
                        if not email:
                            st.error("Username not found or no email registered.")
                        elif not EMAIL_ADDRESS or not EMAIL_APP_PASSWORD:
                            st.error("⚠️ Email service is not configured in .env file.")
                        else:
                            with st.spinner("Sending OTP..."):
                                try:
                                    otp = generate_otp()
                                    send_otp_email(email, otp)
                                    st.session_state.reset_otp = otp
                                    st.session_state.reset_username = fp_username
                                    st.success(f"OTP sent to {email[:3]}***{email[email.find('@'):]}")
                                    st.rerun()
                                except Exception as mail_error:
                                    st.error(f"Failed to send OTP: {mail_error}")

                else:
                    st.info(f"OTP sent for username: {st.session_state.reset_username}")
                    entered_otp = st.text_input("🔑 Enter OTP", key="fp_otp")
                    new_password = st.text_input("🔒 New Password", type="password", key="fp_new_password")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("Reset Password", use_container_width=True, key="reset_pw_btn"):
                            if entered_otp == st.session_state.reset_otp and new_password:
                                update_password(st.session_state.reset_username, new_password)
                                reset_login_attempts(st.session_state.reset_username)
                                st.success("Password reset successful!")
                                st.session_state.reset_otp = None
                                st.session_state.reset_username = None
                            else:
                                st.error("Incorrect OTP or empty password.")
                    with col_b:
                        if st.button("Cancel / Resend", use_container_width=True, key="cancel_reset_btn"):
                            st.session_state.reset_otp = None
                            st.session_state.reset_username = None
                            st.rerun()
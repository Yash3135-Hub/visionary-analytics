import streamlit as st
import pandas as pd
from database import login_user, update_password, get_upload_history

def render_user_profile():
    st.subheader("👤 User Profile & Settings")
    
    username = st.session_state.get("username", "User")
    
    tab_info, tab_security, tab_history = st.tabs(["📋 Profile Info", "🔐 Change Password", "📁 Upload History"])
    
    # ---------------- TAB 1: PROFILE INFO ----------------
    with tab_info:
        st.markdown(f"**Username:** `{username}`")
        st.markdown("**Account Type:** `Free Plan`")
        st.divider()
        st.markdown("##### 🖼️ Avatar Selection")
        avatar = st.selectbox("Choose Profile Avatar", ["🧑‍💻 Developer", "📊 Data Analyst", "🚀 Leader", "🤖 AI Specialist"])
        if st.button("Save Avatar", key="save_avatar_btn"):
            st.success(f"Avatar updated to {avatar}!")

    # ---------------- TAB 2: CHANGE PASSWORD ----------------
    with tab_security:
        st.markdown("##### 🔒 Change Your Password")
        old_pass = st.text_input("Current Password", type="password", key="prof_old_pass")
        new_pass = st.text_input("New Password", type="password", key="prof_new_pass")
        confirm_pass = st.text_input("Confirm New Password", type="password", key="prof_confirm_pass")
        
        if st.button("Update Password", key="update_pass_btn"):
            if not old_pass or not new_pass or not confirm_pass:
                st.warning("Please fill in all password fields.")
            elif new_pass != confirm_pass:
                st.error("New passwords do not match!")
            elif len(new_pass) < 6:
                st.error("New password must be at least 6 characters long.")
            elif not login_user(username, old_pass):
                st.error("❌ Current password is incorrect.")
            elif old_pass == new_pass:
                st.warning("New password must be different from the current password.")
            else:
                update_password(username, new_pass)
                st.success("🎉 Password updated successfully!")

    # ---------------- TAB 3: UPLOAD HISTORY ----------------
    with tab_history:
        st.markdown("##### 📂 Recent Uploaded Datasets")

        history_rows = get_upload_history(username)

        if not history_rows:
            st.info("You haven't uploaded any files yet. Upload an Excel file on the Dashboard to see it here.")
        else:
            history_data = pd.DataFrame(
                history_rows,
                columns=["File Name", "Upload Date", "Total Rows"]
            )
            st.dataframe(history_data, use_container_width=True)
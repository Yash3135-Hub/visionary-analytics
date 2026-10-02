import streamlit as st
import pandas as pd
from utils import render_kpi_cards
from database import (
    get_all_users, get_all_uploads, get_admin_stats,
    set_user_role, unlock_user, delete_user, check_lockout
)

def render_admin_page():
    st.title("🛡️ Admin Panel")
    st.caption("System-wide overview and user management")

    total_users, total_uploads, locked_accounts = get_admin_stats()
    render_kpi_cards([
     #   (str(total_users), "Total Users"),
      #  (str(total_uploads), "Total Uploads"),
      #  (str(locked_accounts), "Locked Accounts"),
    ])

    tab_users, tab_uploads = st.tabs(["👥 Manage Users", "📁 All Upload History"])

    # ---------------- TAB 1: MANAGE USERS ----------------
    with tab_users:
        st.subheader("👥 Registered Users")

        users = get_all_users()

        if not users:
            st.info("No users registered yet.")
        else:
            df = pd.DataFrame(
                users,
                columns=["Username", "Email", "Role", "Failed Attempts", "Locked Until"]
            )
            st.dataframe(df, use_container_width=True)

            st.divider()
            st.subheader("⚙️ User Actions")

            usernames = [u[0] for u in users]
            selected_user = st.selectbox("Select a user", usernames, key="admin_user_select")

            current_role = next(u[2] for u in users if u[0] == selected_user)
            is_locked = check_lockout(selected_user) > 0

            col1, col2, col3 = st.columns(3)

            with col1:
                new_role = "user" if current_role == "admin" else "admin"
                if st.button(f"Make {new_role.capitalize()}", key="admin_toggle_role"):
                    if selected_user == st.session_state.username and new_role == "user":
                        st.error("You cannot remove your own admin role.")
                    else:
                        set_user_role(selected_user, new_role)
                        st.success(f"{selected_user} is now a {new_role}.")
                        st.rerun()

            with col2:
                if st.button("🔓 Unlock Account", key="admin_unlock", disabled=not is_locked):
                    unlock_user(selected_user)
                    st.success(f"{selected_user}'s account has been unlocked.")
                    st.rerun()

            with col3:
                if st.button("🗑️ Delete User", key="admin_delete"):
                    if selected_user == st.session_state.username:
                        st.error("You cannot delete your own account while logged in.")
                    else:
                        delete_user(selected_user)
                        st.success(f"{selected_user} has been deleted.")
                        st.rerun()

    # ---------------- TAB 2: ALL UPLOAD HISTORY ----------------
    with tab_uploads:
        st.subheader("📁 Upload History (All Users)")

        uploads = get_all_uploads()

        if not uploads:
            st.info("No uploads recorded yet.")
        else:
            df = pd.DataFrame(
                uploads,
                columns=["Username", "File Name", "Upload Date", "Total Rows"]
            )
            st.dataframe(df, use_container_width=True)
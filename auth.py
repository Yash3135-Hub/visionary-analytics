import streamlit as st
import sqlite3
import hashlib

# Database connection
def get_db_connection():
    conn = sqlite3.connect("users.db", check_same_thread=False)
    return conn

# Create users table if not exists
def create_usertable():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS userstable(
            username TEXT PRIMARY KEY,
            email TEXT,
            password TEXT,
            role TEXT
        )
    ''')
    
    # Default Admin account insert karein (agar pehle se nahi hai)
    c.execute('SELECT * FROM userstable WHERE username = ?', ('admin',))
    if not c.fetchone():
        admin_pass = hashlib.sha256(str.encode("admin123")).hexdigest()
        c.execute('INSERT INTO userstable(username, email, password, role) VALUES (?,?,?,?)', 
                  ('admin', 'admin@visionary.com', admin_pass, 'Admin'))
    
    conn.commit()
    conn.close()

# Password Hash Helper
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

# Add User (Registration) - Always sets role = "User"
def add_userdata(username, email, password):
    conn = get_db_connection()
    c = conn.cursor()
    hashed_pass = make_hashes(password)
    c.execute('INSERT INTO userstable(username, email, password, role) VALUES (?,?,?,?)', 
              (username, email, hashed_pass, 'User'))
    conn.commit()
    conn.close()

# Verify Login & Return User Data (including Role)
def login_user(username, password):
    conn = get_db_connection()
    c = conn.cursor()
    hashed_pass = make_hashes(password)
    c.execute('SELECT * FROM userstable WHERE username = ? AND password = ?', (username, hashed_pass))
    data = c.fetchall()
    conn.close()
    return data

# Registration Form (NO ADMIN CHECKBOX HERE)
def render_register():
    st.subheader("Create New Account")
    new_user = st.text_input("Username", key="reg_user")
    new_email = st.text_input("Email", key="reg_email")
    new_password = st.text_input("Password", type='password', key="reg_pass")
    confirm_password = st.text_input("Confirm Password", type='password', key="reg_conf_pass")

    if st.button("Register"):
        if not new_user or not new_email or not new_password:
            st.error("Please fill in all fields.")
        elif new_password != confirm_password:
            st.error("Passwords do not match.")
        else:
            create_usertable()
            try:
                add_userdata(new_user, new_email, new_password)
                st.success("Account created successfully! You can now log in.")
            except sqlite3.IntegrityError:
                st.error("Username already exists. Please choose a different one.")

# Login Form
def render_login():
    st.subheader("Login to Your Account")
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type='password', key="login_pass")

    if st.button("Login"):
        create_usertable()
        user_data = login_user(username, password)
        if user_data:
            # Save login state and role in Session
            st.session_state["logged_in"] = True
            st.session_state["username"] = user_data[0][0]
            st.session_state["email"] = user_data[0][1]
            st.session_state["role"] = user_data[0][3]  # Stores "Admin" or "User"
            st.success(f"Welcome back, {username}!")
            st.rerun()
        else:
            st.error("Invalid Username or Password")

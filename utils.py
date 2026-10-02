import hashlib
import random
import smtplib
from email.message import EmailMessage
import streamlit as st
from config import EMAIL_ADDRESS, EMAIL_APP_PASSWORD

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(receiver_email, otp):
    msg = EmailMessage()
    msg["Subject"] = "Your Password Reset OTP - Visionary Analytics"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = receiver_email
    msg.set_content(
        f"Your OTP to reset your Visionary Analytics password is: {otp}\n\n"
        f"This OTP is valid for 10 minutes. If you did not request this, please ignore this email."
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        server.send_message(msg)

def render_kpi_cards(cards):
    html = '<div class="ai-dashboard">'
    for value, label in cards:
        html += f'<div class="dashboard-card"><h2>{value}</h2><p>{label}</p></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def render_feature_cards(features):
    html = '<div class="feature-grid">'
    for icon, title, desc in features:
        html += f'<div class="feature-card"><i class="bi {icon}"></i><h4>{title}</h4><p>{desc}</p></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def render_contact_cards(items):
    html = ""
    for icon, label, value, href in items:
        value_html = f'<a href="{href}" target="_blank">{value}</a>' if href else value
        html += f'''<div class="contact-card">
            <i class="bi {icon}"></i>
            <div><p class="label">{label}</p><p class="value">{value_html}</p></div>
        </div>'''
    st.markdown(html, unsafe_allow_html=True)

def clean_text_for_pdf(text):
    return text.encode("latin-1", "ignore").decode("latin-1")
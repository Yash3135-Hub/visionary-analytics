import streamlit as st
from utils import render_contact_cards

def render_contact_page():
    st.title("📞 Contact")
    st.markdown("Feel free to reach out for feedback, collaboration, or questions about this project.")

    render_contact_cards([
        ("bi-person-circle", "Name", "Maniyar Yash Sunilbhai", None),
        ("bi-envelope-fill", "Email", "yash@email.com", "mailto:yashmaniyar3135@gmail.com"),
        ("bi-github", "GitHub", "github.com/Yash3135-Hub", "https://github.com/Yash3135-Hub"),
        ("bi-linkedin", "LinkedIn", "linkedin.com/in/yash-maniyar-a54b51309/", "https://linkedin.com/in/yash-maniyar-a54b51309/"),
        ("bi-mortarboard-fill", "Institute", "AMPICS, Ganpat University", None),
        ("bi-geo-alt-fill", "Location", "Mehsana, Gujarat, India", None),
    ])

    st.markdown(
        '<p style="color:#8FA7B6; font-size:0.85em; margin-top:20px;">'
        'This is an academic project built for MCA Semester-III (System Development Project-I).'
        '</p>',
        unsafe_allow_html=True
    )
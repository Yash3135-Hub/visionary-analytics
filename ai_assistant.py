import streamlit as st
from config import client, GEMINI_API_KEY
from styles import CHATBOT_STYLES

def analyze_sales_data(df):
    """Analyzes uploaded sales dataframe using Gemini API."""
    if not GEMINI_API_KEY or not client:
        st.error("⚠️ GEMINI_API_KEY not found in .env file.")
        return None

    with st.spinner("Analyzing dataset with Gemini..."):
        try:
            sample_data = df.head(20).to_string(index=False)
            prompt = f"""
            You are a professional Data Analyst.
            Analyze this sales data:
            {sample_data}
            Tell me:
            1. Total Sales trend
            2. Best Performing Brand
            3. Worst Performing Brand
            4. Business Insights
            5. Recommendations
            """
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text
        except Exception as e:
            st.error(f"Gemini API Error: {e}")
            return None

def render_floating_chatbot():
    """Renders the floating chatbot widget at the bottom right corner."""
    st.markdown(CHATBOT_STYLES, unsafe_allow_html=True)

    # Custom CSS for Chatbox Dimensions, Center Close Icon & ChatGPT Loading Dots
    st.markdown("""
        <style>
        /* Chatbox Dimensions */
        div[class*="st-key-chat_panel"] {
            width: 440px !important;
            max-height: 580px !important;
        }

        /* Center Close Button Icon */
        div[class*="st-key-close_chat_btn"] button {
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            padding: 0 !important;
            height: 36px !important;
            width: 36px !important;
            line-height: 1 !important;
            border-radius: 10px !important;
        }
        div[class*="st-key-close_chat_btn"] button p {
            margin: 0 !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            line-height: 1 !important;
            font-size: 16px !important;
        }

        /* ChatGPT Style 3-Dot Typing Animation */
        .typing-dots {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 8px 12px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
        }
        .typing-dots span {
            width: 7px;
            height: 7px;
            background-color: #FF7A45;
            border-radius: 50%;
            display: inline-block;
            animation: bounce 1.4s infinite ease-in-out both;
        }
        .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
        .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
        .typing-dots span:nth-child(3) { animation-delay: 0s; }

        @keyframes bounce {
            0%, 80%, 100% { 
                transform: scale(0.4); 
                opacity: 0.3; 
            }
            40% { 
                transform: scale(1); 
                opacity: 1; 
            }
        }
        </style>
    """, unsafe_allow_html=True)

    if "chat_open" not in st.session_state:
        st.session_state.chat_open = False
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # Floating Action Button (FAB)
    with st.container(key="fab_button"):
        if st.button("🤖", key="toggle_chat_btn"):
            st.session_state.chat_open = not st.session_state.chat_open

    # Chat Panel
    if st.session_state.chat_open:
        with st.container(key="chat_panel"):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown("**🤖 AI Assistant**")
            with col2:
                if st.button("❌", key="close_chat_btn"):
                    st.session_state.chat_open = False
                    st.rerun()

            st.caption("Ask me anything — general questions or about your dashboard.")
            
            chat_box = st.container(height=360)

            prompt = st.chat_input("Type your message...")

            with chat_box:
                # 1. Render all past chat messages
                for msg in st.session_state.chat_messages:
                    with st.chat_message(msg["role"]):
                        st.write(msg["content"])

                # 2. When new prompt is submitted
                if prompt:
                    # Save user message to history & display it
                    st.session_state.chat_messages.append({"role": "user", "content": prompt})
                    with st.chat_message("user"):
                        st.write(prompt)

                    # Show ChatGPT-style animated dots while fetching response
                    with st.chat_message("assistant"):
                        loading_placeholder = st.empty()
                        loading_placeholder.markdown("""
                            <div class="typing-dots">
                                <span></span><span></span><span></span>
                            </div>
                        """, unsafe_allow_html=True)

                        # Get response from Gemini
                        if not GEMINI_API_KEY or not client:
                            answer = "⚠️ GEMINI_API_KEY not found. Check your .env file."
                        else:
                            try:
                                response = client.models.generate_content(
                                    model="gemini-2.5-flash",
                                    contents=prompt
                                )
                                answer = response.text
                            except Exception as chat_error:
                                answer = f"Error: {chat_error}"

                        # Save response to history and rerun UI
                        st.session_state.chat_messages.append({"role": "assistant", "content": answer})
                        st.rerun()
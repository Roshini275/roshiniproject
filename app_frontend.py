import streamlit as st
import requests

# Title
st.title("💰 FinMate - Personal Finance Chatbot")

# Input box for user message
user_message = st.text_input("Enter your expense:", "")

if st.button("Submit"):
    if user_message.strip():
        # Send request to Flask backend
        response = requests.post(
            "http://127.0.0.1:5000/chat",
            json={"message": user_message}
        )

        if response.status_code == 200:
            data = response.json()
            st.success(data.get("reply", "No reply"))
        else:
            st.error("Backend error: " + str(response.status_code))

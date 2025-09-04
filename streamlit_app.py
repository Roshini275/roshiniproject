import streamlit as st
import requests
import pandas as pd
import base64

st.set_page_config(page_title="💰 FinMate - Personal Finance Assistant", layout="wide")

st.title("💰 FinMate - Personal Finance Assistant")
st.write("Log your expenses in natural language and get instant insights.")

backend_url = "http://127.0.0.1:5000"

# 🟢 Input box
user_input = st.text_input("Enter a transaction (example: 'I spent 200 on food yesterday'):")

if st.button("Log Expense / Ask"):
    if user_input.strip() == "":
        st.warning("⚠️ Please enter a message.")
    else:
        try:
            response = requests.post(f"{backend_url}/chat", json={"message": user_input})
            if response.status_code == 200:
                data = response.json()
                st.success(data["reply"])

                # Show latest expenses if available
                if "expenses" in data:
                    df = pd.DataFrame(data["expenses"])
                    st.subheader("📒 Expense History")
                    st.dataframe(df)

                # Show updated chart if available
                if data.get("chart"):
                    st.subheader("📊 Chart")
                    st.image("data:image/png;base64," + data["chart"])
            else:
                st.error("❌ Backend error, please try again.")
        except Exception as e:
            st.error(f"Connection error: {e}")
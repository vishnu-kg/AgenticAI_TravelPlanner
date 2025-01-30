import os
import streamlit as st

class Config:
    def __init__(self):
        self.groq_api_key = self.get_groq_api_key()

    def get_groq_api_key(self):
        try:
            groq_api_key = st.text_input("🔑 Enter your Groq API Key", type="password")
            if groq_api_key:
                os.environ["GROQ_API_KEY"] = groq_api_key
            if not groq_api_key:
                raise ValueError("Groq API Key not provided.")
            return groq_api_key
        except Exception as e:
            # st.error(f"Error in loading API key: {e}")
            return None

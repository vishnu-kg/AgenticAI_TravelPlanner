import os
import streamlit as st
from dotenv import load_dotenv
from config import Config
from agents import TravelAgents
from chat_manager import ChatManager
from concurrent.futures import ThreadPoolExecutor
import logging
import time  # Import time for retry delay
from functools import lru_cache  # Import caching mechanism

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Load environment variables
# load_dotenv()

# Cache results to reduce API calls
@lru_cache(maxsize=50)
def cached_itinerary(travel_prompt):
    """Fetch itinerary while avoiding repeated API calls."""
    retries = 0
    max_retries = 5
    while retries < max_retries:
        try:
            response = chat_manager.generate_itinerary(travel_prompt)
            if response:  
                return response.summary  # Return response if successful
        except Exception as e:
            if "429" in str(e):  # Detect Too Many Requests
                wait_time = 2 ** retries  # Exponential backoff
                logging.warning(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                retries += 1
            else:
                logging.error(f"Error generating itinerary: {e}")
                break  # Exit loop for non-retryable errors
    return None  # Return None if max retries exceeded

def run_app():
    try:
        # Streamlit UI Configuration
        st.set_page_config(page_title="AI Travel Planner", layout="wide")

        # App Title
        st.title("🌍 AI Travel Planner ✈️🌲")
        st.markdown("### Plan your trip with AI-powered recommendations!")

        # Step 1: Initialize Configuration
        config = Config()
        llm_config = {"config_list": [{"model": "deepseek-r1-distill-llama-70b", "api_key": config.groq_api_key, "api_type": "groq"}], "max_tokens": 5000}
        global chat_manager  # Declare globally to use in cache function
        agents = TravelAgents(llm_config)
        chat_manager = ChatManager(agents, llm_config)

        # Step 2: User Input Form
        with st.form("travel_form"):
            departure_location = st.text_input("🚏 Departure Location", placeholder="Enter city or country")
            destination = st.text_input("🌆 Destination", placeholder="Enter city or country")
            travel_dates = st.text_input("📅 Travel Dates", placeholder="e.g., 10-15 March 2025")
            budget = st.number_input("💰 Budget (INR)", min_value=100, step=50)
            activities = st.multiselect(
                "🎭 Preferred Activities",
                ["Sightseeing", "Adventure", "Relaxation", "Food", "Shopping", "Nightlife"]
            )
            accommodation = st.selectbox(
                "🏨 Accommodation Type",
                ["Hotel", "Hostel", "Airbnb", "Luxury", "Budget"]
            )
            transport_mode = st.selectbox(
                "🚆 Transportation Mode",
                ["Flight", "Train", "Bus", "Rental Car", "Bike"]
            )
            submit_btn = st.form_submit_button("Plan My Trip!")

        # Define Agent Prompts
        travel_prompt = f"""
        **Task**: As an AI travel planner, create an optimized travel itinerary based on:
        - Departure Location: {departure_location}
        - Destination: {destination}
        - Travel Dates: {travel_dates}
        - Budget: {budget} INR
        - Preferred Activities: {', '.join(activities)}
        - Accommodation: {accommodation}
        - Transportation: {transport_mode}
        - Optimize for cost, comfort, and real-time availability.
        """

        # Handle Submission
        if submit_btn:
            if not destination or not travel_dates or not departure_location:
                st.error("Please fill in all required fields!")
            else:
                st.success("Generating your travel itinerary...")

                # Run AI chat in parallel using ThreadPoolExecutor
                with ThreadPoolExecutor() as executor:
                    future = executor.submit(cached_itinerary, travel_prompt)
                    response = future.result()  # Get the result when available

                if response:
                    # Display AI-generated Itinerary
                    st.subheader("📝 Your AI-Generated Itinerary:")
                    st.write(response)
                else:
                    st.error("There was an error generating the itinerary.")
    except Exception as e:
        logging.error(f"An error occurred in the app: {e}")
        st.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    run_app()

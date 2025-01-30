import os
import streamlit as st
from dotenv import load_dotenv
import autogen
from autogen import AssistantAgent, UserProxyAgent, GroupChat, GroupChatManager
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

# Load environment variables
load_dotenv()
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")




# Streamlit UI Configuration
st.set_page_config(page_title="AI Travel Planner", layout="wide")

# Add Background Image
st.markdown(
    """
    <style>
    body {
        background-image: url('https://source.unsplash.com/1600x900/?flight,travel');
        background-size: cover;
    }
    .stApp {
        background: rgba(255, 255, 255, 0.8);
        padding: 20px;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# App Title
st.title("🌍 AI Travel Planner ✈️🌲")
st.markdown("### Plan your trip with AI-powered recommendations!")

groq_api_key = st.text_input("🔑 Enter your Groq API Key", type="password")
if groq_api_key:
    os.environ["GROQ_API_KEY"] = groq_api_key


# Define AI Model Configuration
config_list = [{
    "model": "deepseek-r1-distill-llama-70b",
    "api_key": groq_api_key,
    "api_type": "groq"
}]
llm_config = {"config_list": config_list,"max_tokens": 5000}

# User Input Form
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

# Define Agents
user_proxy = UserProxyAgent(
    name="traveler",
    system_message="A Human Travel Enthusiast",
    code_execution_config={
        "last_n_messages": 2,
        "work_dir": "groupchat",
        "use_docker": False,
    },
    human_input_mode="NEVER",
)

transportation_agent = AssistantAgent(name="transport", system_message="Handles transport logistics.", llm_config=llm_config)
accommodation_agent = AssistantAgent(name="stay", system_message="Finds best stays.", llm_config=llm_config)
lead_agent = AssistantAgent(name="lead", system_message="Manages itinerary.", llm_config=llm_config)

# Define GroupChat
groupchat = GroupChat(
    agents=[user_proxy, transportation_agent, accommodation_agent, lead_agent],
    messages=[],
    max_round=6,
)

manager = GroupChatManager(groupchat=groupchat, llm_config=llm_config)

# Function to run AI chat in parallel
@lru_cache(maxsize=10)
def generate_itinerary():
    return user_proxy.initiate_chat(manager, message=travel_prompt)

# Handle Submission
if submit_btn:
    if not destination or not travel_dates or not departure_location:
        st.error("Please fill in all required fields!")
    else:
        st.success("Generating your travel itinerary...")

        # Run AI chat in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor() as executor:
            future = executor.submit(generate_itinerary)
            response = future.result()  # Get the result when available

        # Display AI-generated Itinerary
        st.subheader("📝 Your AI-Generated Itinerary:")
        st.write(response.summary)
# groq_api_key = st.text_input("🔑 Enter your Groq API Key", type="password")
# if groq_api_key:
#     os.environ["GROQ_API_KEY"] = groq_api_key

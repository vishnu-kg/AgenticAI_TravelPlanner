from autogen import AssistantAgent, UserProxyAgent

class TravelAgents:
    def __init__(self, llm_config):
        self.llm_config = llm_config
        try:
            self.user_proxy = self.create_user_proxy()
            self.transportation_agent = self.create_transportation_agent()
            self.accommodation_agent = self.create_accommodation_agent()
            self.lead_agent = self.create_lead_agent()
        except Exception as e:
            raise Exception(f"Error initializing agents: {e}")

    def create_user_proxy(self):
        try:
            return UserProxyAgent(
                name="traveler",
                system_message="A Human Travel Enthusiast",
                code_execution_config={
                    "last_n_messages": 2,
                    "work_dir": "groupchat",
                    "use_docker": False,
                },
                human_input_mode="NEVER",
            )
        except Exception as e:
            raise Exception(f"Error creating user proxy agent: {e}")

    def create_transportation_agent(self):
        try:
            return AssistantAgent(name="transport", system_message="Handles transport logistics.", llm_config=self.llm_config)
        except Exception as e:
            raise Exception(f"Error creating transportation agent: {e}")

    def create_accommodation_agent(self):
        try:
            return AssistantAgent(name="stay", system_message="Finds best stays.", llm_config=self.llm_config)
        except Exception as e:
            raise Exception(f"Error creating accommodation agent: {e}")

    def create_lead_agent(self):
        try:
            return AssistantAgent(name="lead", system_message="Manages itinerary.", llm_config=self.llm_config)
        except Exception as e:
            raise Exception(f"Error creating lead agent: {e}")

from autogen import GroupChat, GroupChatManager
from functools import lru_cache
import logging

class ChatManager:
    def __init__(self, agents, llm_config):
        self.agents = agents
        self.llm_config = llm_config
        try:
            self.groupchat = self.create_groupchat()
            self.manager = self.create_groupchat_manager()
        except Exception as e:
            logging.error(f"Error initializing chat manager: {e}")
            raise Exception(f"Error initializing chat manager: {e}")

    def create_groupchat(self):
        try:
            return GroupChat(
                agents=[
                    self.agents.user_proxy,
                    self.agents.transportation_agent,
                    self.agents.accommodation_agent,
                    self.agents.lead_agent,
                ],
                messages=[],
                max_round=6,
            )
        except Exception as e:
            raise Exception(f"Error creating groupchat: {e}")

    def create_groupchat_manager(self):
        try:
            return GroupChatManager(groupchat=self.groupchat, llm_config=self.llm_config)
        except Exception as e:
            raise Exception(f"Error creating groupchat manager: {e}")

    @lru_cache(maxsize=10)
    def generate_itinerary(self, travel_prompt):
        try:
            return self.agents.user_proxy.initiate_chat(self.manager, message=travel_prompt)
        except Exception as e:
            logging.error(f"Error generating itinerary: {e}")
            return None

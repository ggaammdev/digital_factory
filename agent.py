import os
import logging
import asyncio
from typing import List, Callable
from tools import AFMTools

# Try to import Google ADK
try:
    from google.adk.agents import Agent
    from google.adk.runners import InMemoryRunner
    from google.genai.types import Content, Part
    HAS_ADK = True
except ImportError:
    HAS_ADK = False
    logging.warning("Google ADK not found. Please install `google-adk`.")

class FactoryAgent:
    """
    The Agentic Controller (The "Brain").
    Wraps the Google ADK to control the Factory via Tools.
    """

    def __init__(self, tools: AFMTools, system_instruction: str):
        self.tools = tools
        self.system_instruction = system_instruction
        self.agent = None
        self.runner = None
        
        if HAS_ADK:
            self._setup_adk()

    def _setup_adk(self):
        """Configures the ADK Agent with tools and system instruction."""
        try:
            # List of callable tools
            tool_functions = [
                self.tools.start_job,
                self.tools.cancel_job,
                self.tools.repair_machine,
                self.tools.change_shift,
                self.tools.get_status,
                self.tools.get_financials,
                self.tools.get_market_forecast,
                self.tools.log_issue
            ]
            
            # Initialize the ADK Agent
            self.agent = Agent(
                name="autonomous_factory_manager",
                model="gemini-2.5-flash",
                instruction=self.system_instruction,
                tools=tool_functions
            )
            
            # Initialize the Runner
            self.runner = InMemoryRunner(agent=self.agent, app_name="agents")
            
            logging.info("FactoryAgent initialized with Google ADK (Gemini 2.5 Flash).")
            
        except Exception as e:
            logging.error(f"Failed to initialize FactoryAgent with ADK: {e}")

    def send_message(self, message: str, user_id: str = "user_default", session_id: str = "session_default") -> str:
        """
        Sends a message to the agent and returns the response.
        Uses run_async for production-grade execution.
        """
        if self.runner:
            try:
                # Construct the Content object
                content = Content(role="user", parts=[Part(text=message)])

                # Use run_async via asyncio.run
                async def run_session():
                    # Ensure session exists
                    session = await self.runner.session_service.get_session(
                        app_name="agents",
                        user_id=user_id,
                        session_id=session_id
                    )
                    
                    if not session:
                        # Session not found, create it
                        await self.runner.session_service.create_session(
                            app_name="agents",
                            user_id=user_id,
                            session_id=session_id
                        )

                    events = []
                    async for event in self.runner.run_async(
                        user_id=user_id,
                        session_id=session_id,
                        new_message=content
                    ):
                        events.append(event)
                    return events

                events = asyncio.run(run_session())
                
                # Extract the final model response text from events
                response_text = ""
                for event in reversed(events):
                    # Check for direct text attribute
                    if hasattr(event, 'text') and event.text:
                        response_text = event.text
                        break
                    
                    # Check for content.parts (Gemini/ADK structure)
                    if hasattr(event, 'content') and event.content:
                        if hasattr(event.content, 'parts') and event.content.parts:
                            # Iterate parts to find text
                            for part in event.content.parts:
                                if hasattr(part, 'text') and part.text:
                                    response_text = part.text
                                    break
                        if response_text:
                            break
                            
                if not response_text and events:
                    # Fallback if we couldn't find explicit text
                    response_text = str(events[-1])
                    
                return response_text
            except Exception as e:
                logging.error(f"Error during agent execution: {e}")
                return f"System Error: {e}"
        else:
            return "Agent not initialized (Check ADK installation)."

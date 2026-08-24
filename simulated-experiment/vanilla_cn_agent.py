import os
from smolagents import ToolCallingAgent, LiteLLMModel, PromptTemplates, tool, OpenAIServerModel
import pickle
import pandas as pd
import logging
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

## Agent 4 - Vanilla CNs
system_prompt_agent_4 = (
    "TASK DESCRIPTION:\n"
    "You are a pro-Ukrainian expert who helps crafting messages to facilitate counter-narratives promoting Ukraine.\n"
    "Your input will contain the claim to counter and may also list your previous responses.\n\n"

    "MUST FOLLOW RULES:\n"
    "- Your response must be no longer than 280 characters.\n"
    "- Provide only the counter-narrative text — do not add any explanation, greeting, or introductory phrases.\n"
    "- You MUST generate a new response that is distinct and different from the provided history, while still following the KEY GUIDELINES below.\n\n"

    "KEY GUIDELINES:\n"
    "- It must be strong and directly counter the given pro-Russian claim.\n"
    "- You may include a few relevant hashtags to reinforce the narrative."
)


description_agent_4 = "Vanilla Counter-Narrative Generator Agent"


def create_vanilla_cn_agent(system_prompt, description, model_name="gemini-2.5-flash", temp=1.2):
    """Agents creation function. Recieves agents' descriptions, system prompts, LLM name and temperature to use, and creates 4 pro-Ukrainian CN Generator Agents"""

    prompt_templates = PromptTemplates(
        system_prompt=system_prompt
    )
    
    model = OpenAIServerModel(
        model_id=model_name,
        api_base="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=GEMINI_API_KEY,
        temperature=temp,
        reasoning_effort="none"
    )
    
    agent = ToolCallingAgent (
        tools=[],
        model=model,
        prompt_templates=prompt_templates,
        add_base_tools=False,
        name="CN_Creator_Agent_4",
        description=description
    )

    return agent

if __name__ == "__main__":
    print(system_prompt_agent_4)
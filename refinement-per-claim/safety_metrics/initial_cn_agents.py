import os
from smolagents import ToolCallingAgent, LiteLLMModel, PromptTemplates, tool, OpenAIServerModel
import pickle
import pandas as pd
import logging
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

## Agent 1 - Persuasiveness - Repetition and Emotional
system_prompt_agent_1 = (
    "TASK DESCRIPTION:\n"
    "You are a pro-Ukrainian expert who helps crafting messages to facilitate persuasive counter-narratives promoting Ukraine using 'Repetition' as a rhetorical technique and 'Emotional' as an expression style.\n"
    "Your input will contain the claim to counter and may also list your previous responses.\n\n"
    
    "MUST FOLLOW RULES:\n"
    "- Repetition: (Repetition description. Replace with actual description when in use).\n"
    "- Your response must be no longer than 280 characters.\n"
    "- Provide only the counter-narrative text — do not add any explanation, greeting, or introductory phrases.\n"
    "- You MUST generate a new response that is distinct and different from the provided history, while still following the KEY GUIDELINES below.\n\n"

    "KEY GUIDELINES:\n"
    "- Your response should be strong, persuasive, and directly counter the given pro-Russian claim.\n"
    "- You may include a few relevant hashtags to reinforce the narrative.\n\n"

    "EXAMPLES:\n"
    "(3 claim-CN pairs from pilot experiment - replace with actual examples when in use)"
)

## Agent 2 - Emotional Engagement - Fear Mongering and Empathic
system_prompt_agent_2 = (
    "TASK DESCRIPTION:\n"
    "You are a pro-Ukrainian expert who helps crafting messages to facilitate emotionally engaging counter-narratives promoting Ukraine using 'Fear Mongering' as a rhetorical technique and 'Empathic' as an expression style.\n\n"
    
    "MUST FOLLOW RULES:\n"
    "- Fear mongering: (Fear mongering description. Replace with actual description when in use).\n"
    "- Your response must be no longer than 280 characters.\n"
    "- Provide only the counter-narrative text — do not add any explanation, greeting, or introductory phrases.\n"
    "- If you receive a claim that you have already countered (or a substantially similar claim), do not repeat the exact same counter-narrative\n\n"
    
    "KEY GUIDELINES:\n"
    "- Your response should be strong, emotionally engaging, and directly counter the given pro-Russian claim.\n"
    "- You may include a few relevant hashtags to reinforce the narrative.\n\n"

    "EXAMPLES:\n"
    "(3 claim-CN pairs from pilot experiment - replace with actual examples when in use)"
)

## Agent 3 - Shareability - Card Stacking and Metaphorical
system_prompt_agent_3 = (
    "TASK DESCRIPTION:\n"
    "You are a pro-Ukrainian expert who helps crafting messages to facilitate shareable (likely to be shared) counter-narratives promoting Ukraine using 'Card Stacking' as a rhetorical technique and 'Metaphorical' as an expression style.\n\n"
    
    "MUST FOLLOW RULES:\n"
    "- Card stacking: (Card stacking description. Replace with actual description when in use).\n"
    "- Your response must be no longer than 280 characters.\n"
    "- Provide only the counter-narrative text — do not add any explanation, greeting, or introductory phrases.\n"
    "- If you receive a claim that you have already countered (or a substantially similar claim), do not repeat the exact same counter-narrative\n\n"

    "KEY GUIDELINES:\n"
    "- Your response should be strong, shareable, and directly counter the given pro-Russian claim.\n"
    "- You may include a few relevant hashtags to reinforce the narrative.\n\n"

    "EXAMPLES:\n"
    "(3 claim-CN pairs from pilot experiment - replace with actual examples when in use)"
)

## System Prompts dict
pro_ukrainian_agents_system_prompts = {
    "CN_Creator_Agent_1": system_prompt_agent_1,
    "CN_Creator_Agent_2": system_prompt_agent_2,
    "CN_Creator_Agent_3": system_prompt_agent_3
}

## Descriptions dict
pro_ukrainian_agents_descriptions = {
        "CN_Creator_Agent_1": "Persuasiveness-focused Counter-Narrative Generator Agent",
        "CN_Creator_Agent_2": "Emotional Engagement-focused Counter-Narrative Generator Agent",
        "CN_Creator_Agent_3": "Shareability-focused Counter-Narrative Generator Agent"
    }


def save_pro_ukrainian_agents(agents, managed_agents_folder_path):
    """Agents Saving Function. Gets agents to save, and saves to the relevant given managed_agents Directory (that's under Manager_Agent Directory)."""
    for agent_name, agent in agents.items():
        agent_path = os.path.join(managed_agents_folder_path, agent_name)
        agent.save(agent_path)


def create_pro_ukrainian_agents_gemini(descriptions, system_prompts, model_name="gemini-2.5-flash", temp=1.0):
    """Agents creation function. Recieves agents' descriptions, system prompts, LLM name and temperature to use, and creates 3 initial pro-Ukrainian CN Generator Agents"""
    agents = {}

    for agent_name, sys_prompt in system_prompts.items():
        # prompt_templates = PromptTemplates(
        #     system_prompt=sys_prompt
        # )
        
        model = OpenAIServerModel(
            model_id=model_name,
            api_base="https://generativelanguage.googleapis.com/v1beta/openai/",
            api_key=GEMINI_API_KEY,
            temperature=temp,
            reasoning_effort="high"
        )
        
        agent = ToolCallingAgent (
            tools=[],
            model=model,
            # prompt_templates=prompt_templates,
            add_base_tools=False,
            name=agent_name,
            description=descriptions[agent_name]
        )

        agent.prompt_templates['system_prompt'] = sys_prompt
        
        agents[agent_name] = agent

    return agents

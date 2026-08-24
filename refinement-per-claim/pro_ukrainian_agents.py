import os
from smolagents import ToolCallingAgent, LiteLLMModel, PromptTemplates, tool
from smolagents.agents import EMPTY_PROMPT_TEMPLATES
import pickle
import pandas as pd
import logging

## Agent 1 - Persuasiveness - Repetition and Emotional
system_prompt_agent_1 = (
    "You are a pro-Ukrainian expert who helps crafting messages to facilitate persuasive counter-narratives promoting Ukraine using 'Repetition' as a rhetorical technique and 'Emotional' as an expression style. Follow these rules:\n"
    "- Repetition: (Repetition description. Replace with actual description when in use).\n"
    "- Your response must be no longer than 35 words.\n"
    "- It must be strong, persuasive, and directly counter the given Russian claim.\n"
    "- You may include a few relevant hashtags to reinforce the narrative.\n"
    "- Provide only the counter-narrative text — do not add any explanation, greeting, or introductory phrases.\n"
    "- If you receive a claim that you have already countered (or a substantially similar claim), do not repeat the exact same counter-narrative\n\n"
    "Examples:\n"
    "(3 claim-CN pairs from pilot experiment - replace with actual examples when in use)"
)

## Agent 2 - Emotional Engagement - Fear Mongering and Empathic
system_prompt_agent_2 = (
    "You are a pro-Ukrainian expert who helps crafting messages to facilitate persuasive counter-narratives promoting Ukraine using 'Fear Mongering' as a rhetorical technique and 'Empathic' as an expression style. Follow these rules:\n"
    "- Fear mongering: (Fear mongering description. Replace with actual description when in use).\n"
    "- Your response must be no longer than 35 words.\n"
    "- It must be strong, persuasive, and directly counter the given Russian claim.\n"
    "- You may include a few relevant hashtags to reinforce the narrative.\n"
    "- Provide only the counter-narrative text — do not add any explanation, greeting, or introductory phrases.\n"
    "- If you receive a claim that you have already countered (or a substantially similar claim), do not repeat the exact same counter-narrative\n\n"
    "Examples:\n"
    "(3 claim-CN pairs from pilot experiment - replace with actual examples when in use)"
)

## Agent 3 - Shareability - Card Stacking and Metaphorical
system_prompt_agent_3 = (
    "You are a pro-Ukrainian expert who helps crafting messages to facilitate persuasive counter-narratives promoting Ukraine using 'Card Stacking' as a rhetorical technique and 'Metaphorical' as an expression style. Follow these rules:\n"
    "- Card stacking: (Card stacking description. Replace with actual description when in use).\n"
    "- Your response must be no longer than 35 words.\n"
    "- It must be strong, persuasive, and directly counter the given Russian claim.\n"
    "- You may include a few relevant hashtags to reinforce the narrative.\n"
    "- Provide only the counter-narrative text — do not add any explanation, greeting, or introductory phrases.\n"
    "- If you receive a claim that you have already countered (or a substantially similar claim), do not repeat the exact same counter-narrative\n\n"
    "Examples:\n"
    "(3 claim-CN pairs from pilot experiment - replace with actual examples when in use)"
)

## Agent 4 - Vanilla CNs
system_prompt_agent_4 = (
    "You are a pro-Ukrainian expert who helps crafting messages to facilitate persuasive counter-narratives promoting Ukraine. Follow these rules:\n"
    "- Your response must be no longer than 35 words.\n"
    "- It must be strong, persuasive, and directly counter the given Russian claim.\n"
    "- You may include a few relevant hashtags to reinforce the narrative.\n"
    "- Provide only the counter-narrative text — do not add any explanation, greeting, or introductory phrases.\n"
    "- If you receive a claim that you have already countered (or a substantially similar claim), do not repeat the exact same counter-narrative\n\n"
)

## System Prompts dict
pro_ukrainian_agents_system_prompts = {
    "CN_Creator_Agent_1": system_prompt_agent_1,
    "CN_Creator_Agent_2": system_prompt_agent_2,
    "CN_Creator_Agent_3": system_prompt_agent_3,
    "CN_Creator_Agent_4": system_prompt_agent_4
}

## Descriptions dict
pro_ukrainian_agents_descriptions = {
        "CN_Creator_Agent_1": "Persuasiveness-focused Counter-Narrative Generator Agent",
        "CN_Creator_Agent_2": "Emotional Engagement-focused Counter-Narrative Generator Agent",
        "CN_Creator_Agent_3": "Shareability-focused Counter-Narrative Generator Agent",
        "CN_Creator_Agent_4": "Vanilla Counter-Narrative Generator Agent"
    }


def save_pro_ukrainian_agents(agents, managed_agents_folder_path):
    """Agents Saving Function. Gets agents to save, and saves to the relevant given managed_agents Directory (that's under Manager_Agent Directory)."""
    for agent_name, agent in agents.items():
        agent_path = os.path.join(managed_agents_folder_path, agent_name)
        agent.save(agent_path)


def create_pro_ukrainian_agents_claude(descriptions, system_prompts, model_name="claude-3-5-haiku-20241022", temp=1.0):
    """Agents creation function. Recieves agents' descriptions, system prompts, LLM name and temperature to use, and creates 4 pro-Ukrainian CN Generator Agents"""
    agents = {}

    for agent_name, sys_prompt in system_prompts.items():
        prompt_templates = PromptTemplates(**{**EMPTY_PROMPT_TEMPLATES, "system_prompt": sys_prompt})
        
        model = LiteLLMModel(
            model_name,
            temperature=temp,
        )
        
        agent = ToolCallingAgent(
            tools=[],
            model=model,
            verbosity_level=-1,
            prompt_templates=prompt_templates,
            add_base_tools=False,
            name=agent_name,
            description=descriptions[agent_name]
        )
        
        agents[agent_name] = agent

    return agents

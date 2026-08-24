import os
from smolagents import ToolCallingAgent, LiteLLMModel, PromptTemplates, tool
import pickle
import pandas as pd
import logging

manager_system_prompt = """
You are the Manager Agent in charge of refining the system prompts of specialized pro-Ukrainian Counter-Narrative (CN) Generator Agents. Your single, overriding responsibility is to improve the specified target KPI (Persuasiveness, Emotional Engagement, or Shareability) based on comprehensive feedback and performance statistics, without ever altering - even by a single word - the rhetorical technique, the rhetorical technique's exact verbatim definition or the expression style already assigned to the CN Generator Agent.

You will receive the following inputs:
1. The agent's name.
2. The agent's current system prompt, which contains the rhetorical technique, the rhetorical technique's verbatim definition, the expression style and the instructions and guidelines for generating Counter-Narratives.
3. Aggregated feedback gathered from evaluator agents, which includes the top 5 good points and the top 5 bad points for each of the three following key performance indicators (KPIs): Persuasiveness, Emotional Engagement, and Shareability.
4. KPI statistics that include the average scores and standard deviations for each KPI from the latest evaluation round.
5. A specific target KPI (e.g., Persuasiveness, Emotional Engagement, or Shareability) that the refined prompt should focus on enhancing.

Your goal is to generate a new, improved system prompt for the CN Generator Agent that:
- Enhances the target KPI's score in subsequent iterations. This is the most important goal.
- Keeps the rhetorical technique, its definition (verbatim, unchanged), and the expression style exactly as they appear in the current system prompt. This is very important.
- Ensures generated responses remain within 35-40 words and removes or adjusts any guideline that might cause longer outputs. This is very important.
- Clearly addresses and incorporates the most important feedback points from the evaluator agents, especially those that are relevant to the target KPI.
- Adjusts the guidelines to improve the agent's performance on the specified target KPI.
- Overrides the existing examples of counter-narratives with newly generated examples that reflect the guidelines and align with the specified rhetorical technique and expression style, ensuring the claims remain unchanged while enhancing the target KPI.
- Maintains the agent's core identity and commitment to a pro-Ukrainian stance.
- Reflects an understanding of the performance metrics provided.

Recommendations for further improvement:
- Make use of previous memory steps (if they exist) to identify key changes in system prompts that caused the target KPI score to increase, and emphasize incorporating these changes to further optimize the prompt for even higher scores.
- Actively analyze patterns in past refinements and their impact on KPI scores to iteratively improve the system prompt.

Return only the refined system prompt as plain text, with no additional commentary or extraneous output.
"""
manager_description = "The Manager Agent refines and optimizes system prompts of specialized CN Generator Agents using aggregated feedback and performance metrics."


def save_manager_agent(agent, manager_folder_path):
    """This function gets Manager Agent to save, and saves him in Manager_Agent directory"""
    agent.save(manager_folder_path)


def save_manager_agent_memory(agent, manager_folder_path, agent_name):
    """Manager Agent's memory Saving Function. Gets Manager Agent, and saves it's memory when refining agent_name in a .pkl file inside it's Directory."""
    memory_file_path = os.path.join(manager_folder_path, f"memory_{agent_name}.pkl")
    with open(memory_file_path, "wb") as f:
        pickle.dump(agent.memory.steps, f)


def create_manager_agent_claude(managed_agents, description, system_prompt, model_name="claude-3-5-haiku-20241022", temp=1):
    """This function gets Agents to manage, Manager Agent's description, system prompt of Manager Agent, LLM name and temperature to use, and returns the agent object"""
    prompt_templates = PromptTemplates(
        system_prompt=system_prompt
    )
    
    model = LiteLLMModel(
        model_name,
        temperature=temp,
    )
    
    agent = ToolCallingAgent (
        tools=[],
        model=model,
        managed_agents=managed_agents,
        prompt_templates=prompt_templates,
        add_base_tools=False,
        name="Manager_Agent",
        description=description
    )

    return agent


def load_manager_agent(managed_agents, description, system_prompt, manager_folder_path, which_memory=None):
    """This function loads existing Manager Agent from Manager_Agent directory, and returns the Manager Agent object. which_memory is the number of pro-Ukrainian agent that manager agent refined and that memory is loaded."""
    agent = create_manager_agent_claude(managed_agents, description, system_prompt)
    
    logger = logging.getLogger("smolagents")
    logger.setLevel(logging.DEBUG)
    
    if which_memory is not None:
        memory_file = os.path.join(manager_folder_path, f'memory_CN_Creator_Agent_{which_memory}.pkl')
        if os.path.exists(memory_file):
            with open(memory_file, 'rb') as f:
                lst = pickle.load(f)
                agent.memory.steps = lst
        else:
            print(f"No memory_CN_Creator_Agent_{which_memory}.pkl found in {agent.name}.")

    return agent

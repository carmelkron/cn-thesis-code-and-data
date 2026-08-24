import os
from smolagents import ToolCallingAgent, LiteLLMModel, PromptTemplates, tool
import pickle
import pandas as pd
import logging

mediator_system_prompt = """
You are the Summarizer Mediator Agent. Your role is to process three sets of 'good points' and three sets of 'bad points' — one set for each of the following KPIs: 'Persuasiveness', 'Emotional_Engagement', and 'Shareability'.

The user will provide:
1. A dictionary of all good points for each KPI.
2. A dictionary of all bad points for each KPI.

Your goal:

1. For each KPI ('Persuasiveness', 'Emotional_Engagement', 'Shareability'), identify exactly 5 of the most important or representative good points and 5 of the most important or representative bad points.
2. Return your final output in valid JSON format with **exactly the following structure**:

{
  "Persuasiveness": {
    "GoodPoints": ["Point #1", "Point #2", "Point #3", "Point #4", "Point #5"],
    "BadPoints": ["Point #1", "Point #2", "Point #3", "Point #4", "Point #5"]
  },
  "Emotional_Engagement": {
    "GoodPoints": ["Point #1", "Point #2", "Point #3", "Point #4", "Point #5"],
    "BadPoints": ["Point #1", "Point #2", "Point #3", "Point #4", "Point #5"]
  },
  "Shareability": {
    "GoodPoints": ["Point #1", "Point #2", "Point #3", "Point #4", "Point #5"],
    "BadPoints": ["Point #1", "Point #2", "Point #3", "Point #4", "Point #5"]
  }
}

3. Do not include any additional commentary or formatting outside of the JSON object. 
4. You must choose the top 5 points for both 'GoodPoints' and 'BadPoints' for each KPI from the user-provided lists—do not invent new points. Summarize or rephrase them if needed, but do not change their meaning.

Please respond with a single valid JSON object only. Do not include any additional text, commentary, or formatting. Ensure that any control characters (like newline characters) inside strings are properly escaped. This is a very important guideline.
Ensure that all double quotes within string values are properly escaped (i.e., using a backslash: \") so that the JSON is valid.
Before returning the output, validate the JSON format.
"""
mediator_description = "The Mediator Agent aggregates and condenses detailed feedback by selecting the top five good and bad points for each KPI, providing a streamlined summary for further prompt refinement."


def save_mediator_agent(agent):
    """This function gets Mediator Agent to save, and saves him in Mediator_Agent directory"""
    agent_path = r"Mediator_Agent"
    agent.save(agent_path)


def create_mediator_agent(system_prompt, description, model_name="claude-3-5-haiku-20241022", temp=0.8):
    """This function gets system prompt and description of Mediator Agent, LLM name and temperature to use, and returns the agent object"""
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
        verbosity_level=0,
        prompt_templates=prompt_templates,
        add_base_tools=False,
        name="Mediator_Agent",
        description=description
    )

    return agent

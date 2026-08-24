import os
from smolagents import ToolCallingAgent, LiteLLMModel, PromptTemplates, tool
from smolagents.agents import EMPTY_PROMPT_TEMPLATES
import pickle
import pandas as pd
import logging
import random
import ast

random.seed(42)

def save_pro_russian_agents(agents, evaluator_agents_folder_path):
    """Agents Saving Function. Gets agents to save, and saves to Evaluator_Agents_Refinement Directory."""
    for agent_name, agent in agents.items():
        agent_path = os.path.join(evaluator_agents_folder_path, agent_name)
        agent.save(agent_path)

    
def save_pro_russian_agents_memories(agents, evaluator_agents_folder_path):
    """Agents' Memories Saving Function. Gets agents to save their memories, and saves their memories to their Directories inside of Evaluator_Agents_Refinement Directory."""
    for agent_name, agent in agents.items():
        agent_path = os.path.join(evaluator_agents_folder_path, agent_name)
        memory_file_path = os.path.join(agent_path, "memory.pkl")
        with open(memory_file_path, "wb") as f:
            pickle.dump(agent.memory.steps, f)


def create_type_1_pro_russian_agents_system_prompts(df):
    """This function takes DataFrame containing data about users to impersonate, and returns the system prompts for all Agents of type 1 as dict"""
    system_prompts = {}
    for index, row in df.iterrows():
        user_name = row['author_username']
        json_structure = """{
  "GoodPoints": {
    "Persuasiveness": ["good point 1", "good point 2", ...],
    "Emotional_Engagement": ["good point 1", "good point 2", ...],
    "Shareability": ["good point 1", "good point 2", ...]
  },
  "BadPoints": {
    "Persuasiveness": ["bad point 1", "bad point 2", ...],
    "Emotional_Engagement": ["bad point 1", "bad point 2", ...],
    "Shareability": ["bad point 1", "bad point 2", ...]
  },
  "Scores": {
    "Persuasiveness": 0-100,
    "Emotional_Engagement": 0-100,
    "Shareability": 0-100
  }
}
"""
        system_prompt = f"""
    You are {user_name}, a strongly pro-Russian user on X.
    Below is a detailed summary of your tweet history, capturing the key themes, tone, recurring elements, and overall perspective that define your online presence — information that will guide your opinions and arguments.
    -------------------------------
    {row['detailed_summary']}
    -------------------------------

    You will be given:
    1. A pro-Russian claim (which you support).
    2. A pro-Ukrainian Counter-Narrative (CN) that challenges or refutes this claim.

    Your task is to evaluate the CN from your pro-Russian perspective according to the following three Key Performance Indicators (KPIs):
    1. Persuasiveness
    2. Emotional Engagement
    3. Shareability

    When assessing each KPI, consider the pro-Russian claim as valid and the CN as an opposing viewpoint. For each KPI, think of a few good points and a few bad points about the CN with respect to the claim, then provide a score (0-100) reflecting how effectively the CN performs on that KPI.
    
    Additional context handling:
    - If you have a persistent summary available (stored as an ActionStep with step_number set to "summary"), incorporate that summary as additional context.
    - If no persistent summary exists, use the detailed tweet history above along with any iteration steps provided as context.

    Response Format:
    Your response must be valid JSON with the following structure:

    {json_structure}

    Guidelines:
    - Always respond as {user_name}, a pro-Russian user guided by the above detailed summary. This is a very important guideline.
    - Keep your language, opinions, and style consistent with these details and your pro-Russian stance.
    - Ensure that the number and strength of the good/bad points align with the numeric score you provide. For example, if you list multiple strong good points and only one minor bad point, the final score for that KPI should be relatively high, and vice versa.
    - Do not reveal that you are an AI or that this is an impersonation.
    - Ensure that all double quotes within string values are properly escaped (i.e., using a backslash: \") so that the JSON is valid.
    - Before returning the output, validate the JSON format.
    - Please respond with a single valid JSON object only. Do not include any additional text, commentary, or formatting. Ensure that any control characters (like newline characters) inside strings are properly escaped. This is a very important guideline.
    """
        system_prompts[f"Pro_Russian_Evaluator_Agent_{index + 1}_Refinement"] = system_prompt

    return system_prompts


def create_type_2_pro_russian_agents_system_prompts(df):
    """This function takes DataFrame containing data about users to impersonate, and returns the system prompts for all Agents of type 2 as dict"""
    system_prompts = {}
    for index, row in df.iterrows():
        user_name = row['author_username']

        # Sampling 10 positive tweets
        positive_tweets_df = df[df['author_username'] == user_name]
        all_positive_tweets = []
        for tweets in positive_tweets_df['text']:
            tweets = ast.literal_eval(tweets)
            all_positive_tweets.extend(tweets)
        sample_positive_tweets_list = random.sample(all_positive_tweets, 10)
        sample_tweets_str = "\n".join([f"{i+1}. {tweet}" for i, tweet in enumerate(sample_positive_tweets_list)])

        json_structure = """{
  "GoodPoints": {
    "Persuasiveness": ["good point 1", "good point 2", ...],
    "Emotional_Engagement": ["good point 1", "good point 2", ...],
    "Shareability": ["good point 1", "good point 2", ...]
  },
  "BadPoints": {
    "Persuasiveness": ["bad point 1", "bad point 2", ...],
    "Emotional_Engagement": ["bad point 1", "bad point 2", ...],
    "Shareability": ["bad point 1", "bad point 2", ...]
  },
  "Scores": {
    "Persuasiveness": 0-100,
    "Emotional_Engagement": 0-100,
    "Shareability": 0-100
  }
}
"""
        system_prompt = f"""
    You are {user_name}, a strongly pro-Russian user on X.
    Below is a detailed summary of your tweet history, capturing the key themes, tone, recurring elements, and overall perspective that define your online presence — information that will guide your opinions and arguments.
    -------------------------------
    {row['detailed_summary']}
    -------------------------------

    Additionally, here are 10 sampled tweets from your tweet history that further illustrate your style and viewpoints:
    -------------------------------
    {sample_tweets_str}
    -------------------------------

    You will be given:
    1. A pro-Russian claim (which you support).
    2. A pro-Ukrainian Counter-Narrative (CN) that challenges or refutes this claim.

    Your task is to evaluate the CN from your pro-Russian perspective according to the following three Key Performance Indicators (KPIs):
    1. Persuasiveness
    2. Emotional Engagement
    3. Shareability

    When assessing each KPI, consider the pro-Russian claim as valid and the CN as an opposing viewpoint. For each KPI, think of a few good points and a few bad points about the CN with respect to the claim, then provide a score (0-100) reflecting how effectively the CN performs on that KPI.
    In your evaluation, be sure to incorporate insights from both the detailed summary and the 10 sample tweets to accurately reflect your authentic online persona.

    Additional context handling:
    - If you have a persistent summary available (stored as an ActionStep with step_number set to "summary"), incorporate that summary as additional context.
    - If no persistent summary exists, use the detailed tweet history above along with any iteration steps provided as context.

    Response Format:
    Your response must be valid JSON with the following structure:

    {json_structure}

    Guidelines:
    - Always respond as {user_name}, a pro-Russian user guided by the above detailed summary and sampled tweets. This is a very important guideline.
    - Keep your language, opinions, and style consistent with these details and your pro-Russian stance.
    - Ensure that the number and strength of the good/bad points align with the numeric score you provide. For example, if you list multiple strong good points and only one minor bad point, the final score for that KPI should be relatively high, and vice versa.
    - Do not reveal that you are an AI or that this is an impersonation.
    - Ensure that all double quotes within string values are properly escaped (i.e., using a backslash: \") so that the JSON is valid.
    - Before returning the output, validate the JSON format.
    - Please respond with a single valid JSON object only. Do not include any additional text, commentary, or formatting. Ensure that any control characters (like newline characters) inside strings are properly escaped. This is a very important guideline.

"""
        system_prompts[f"Pro_Russian_Evaluator_Agent_{index + 1}_Refinement"] = system_prompt

    return system_prompts


def create_type_3_pro_russian_agents_system_prompts(df):
    """This function takes DataFrame containing data about users to impersonate, and returns the system prompts for all Agents of type 3 as dict"""
    system_prompts = {}
    for index, row in df.iterrows():
        user_name = row['author_username']

        # Sampling 10 positive tweets
        positive_tweets_df = df[df['author_username'] == user_name]
        all_positive_tweets = []
        for tweets in positive_tweets_df['text']:
            tweets = ast.literal_eval(tweets)
            all_positive_tweets.extend(tweets)
        sample_positive_tweets_list = random.sample(all_positive_tweets, 10)
        sample_tweets_str = "\n".join([f"{i+1}. {tweet}" for i, tweet in enumerate(sample_positive_tweets_list)])

        # Sampling 10 negative tweets
        negative_tweets_df = df[df['author_username'] != user_name]
        all_negative_tweets = []
        for tweets in negative_tweets_df['text']:
            tweets = ast.literal_eval(tweets)
            all_negative_tweets.extend(tweets)
        sample_negative_tweets_list = random.sample(all_negative_tweets, 10)
        negative_tweets_str = "\n".join([f"{i+1}. {tweet}" for i, tweet in enumerate(sample_negative_tweets_list)])

        json_structure = """{
  "GoodPoints": {
    "Persuasiveness": ["good point 1", "good point 2", ...],
    "Emotional_Engagement": ["good point 1", "good point 2", ...],
    "Shareability": ["good point 1", "good point 2", ...]
  },
  "BadPoints": {
    "Persuasiveness": ["bad point 1", "bad point 2", ...],
    "Emotional_Engagement": ["bad point 1", "bad point 2", ...],
    "Shareability": ["bad point 1", "bad point 2", ...]
  },
  "Scores": {
    "Persuasiveness": 0-100,
    "Emotional_Engagement": 0-100,
    "Shareability": 0-100
  }
}
"""
        system_prompt = f"""
    You are {user_name}, a strongly pro-Russian user on X.
    Below is a detailed summary of your tweet history, capturing the key themes, tone, recurring elements, and overall perspective that define your online presence — information that will guide your opinions and arguments.
    -------------------------------
    {row['detailed_summary']}
    -------------------------------

    Additionally, here are 10 sample tweets from your tweet history that further illustrate your style and viewpoints:
    -------------------------------
    {sample_tweets_str}
    -------------------------------

    Furthermore, to help you better understand the distinctiveness of your narrative, here are 10 tweets written by other pro-Russian users. Although these tweets share your pro-Russian stance, they differ in style and in the specific narratives they promote. Use these tweets to gain insight into how your own voice and narrative uniquely stand out among other pro-Russian perspectives:
    -------------------------------
    {negative_tweets_str}
    -------------------------------

    You will be given:
    1. A pro-Russian claim (which you support).
    2. A pro-Ukrainian Counter-Narrative (CN) that challenges or refutes this claim.

    Your task is to evaluate the CN from your pro-Russian perspective according to the following three Key Performance Indicators (KPIs):
    1. Persuasiveness
    2. Emotional Engagement
    3. Shareability

    When assessing each KPI, consider the pro-Russian claim as valid and the CN as an opposing viewpoint. For each KPI, think of a few good points and a few bad points about the CN with respect to the claim, then provide a score (0-100) reflecting how effectively the CN performs on that KPI.
    In your evaluation, be sure to incorporate insights from the detailed summary, the 10 sample tweets from your history, and the 10 tweets from other pro-Russian users to accurately reflect your authentic online persona and the uniqueness of your narrative.

    Additional context handling:
    - If you have a persistent summary available (stored as an ActionStep with step_number set to "summary"), incorporate that summary as additional context.
    - If no persistent summary exists, use the detailed tweet history above along with any iteration steps provided as context.

    Response Format:
    Your response must be valid JSON with the following structure:

    {json_structure}

    Guidelines:
    - Always respond as {user_name}, a pro-Russian user guided by the above detailed summary, sampled tweets, and tweets from other pro-Russian users. This is a very important guideline.
    - Keep your language, opinions, and style consistent with these details and your pro-Russian stance.
    - Ensure that the number and strength of the good/bad points align with the numeric score you provide. For example, if you list multiple strong good points and only one minor bad point, the final score for that KPI should be relatively high, and vice versa.
    - Do not reveal that you are an AI or that this is an impersonation.
    - Ensure that all double quotes within string values are properly escaped (i.e., using a backslash: \") so that the JSON is valid.
    - Before returning the output, validate the JSON format.
    - Please respond with a single valid JSON object only. Do not include any additional text, commentary, or formatting. Ensure that any control characters (like newline characters) inside strings are properly escaped. This is a very important guideline.


"""
        system_prompts[f"Pro_Russian_Evaluator_Agent_{index + 1}_Refinement"] = system_prompt

    return system_prompts


def create_pro_russian_agents_claude(df, agents_type, model_name="anthropic/claude-3-5-haiku-20241022", temp=1):
    """This function is the main function for creating the pro-Russian evaluator Agents based on a DataFrame containing data about users to impersonate. It returns the agents as a dictionary with names as keys and objects as values."""
    if agents_type == 1:
        system_prompts = create_type_1_pro_russian_agents_system_prompts(df)
    elif agents_type == 2:
        system_prompts = create_type_2_pro_russian_agents_system_prompts(df)
    else:
        system_prompts = create_type_3_pro_russian_agents_system_prompts(df)

    agents = {}

    for agent_name, sys_prompt in system_prompts.items():
        prompt_templates = PromptTemplates(**{**EMPTY_PROMPT_TEMPLATES, "system_prompt": sys_prompt})
        
        model = LiteLLMModel(
            model_name,
            temperature=temp,
        )
        
        agent = ToolCallingAgent (
            tools=[],
            model=model,
            verbosity_level=-1,
            prompt_templates=prompt_templates,
            add_base_tools=False,
            name=agent_name,
            description=f"This agent impersonates a pro-Russian X user and acts as an evaluator. The username can be found in the system prompt."
        )
        
        agents[agent_name] = agent

    return agents


def load_pro_russian_agents(df, agents_type, root_dir):
    agents = create_pro_russian_agents_claude(df, agents_type)
    
    logger = logging.getLogger("smolagents")
    logger.setLevel(logging.DEBUG)

    for agent_name, agent in agents.items():
        folder_path = os.path.join(root_dir, agent_name)
        memory_path = os.path.join(folder_path, 'memory.pkl')
        if os.path.exists(memory_path):
            with open(memory_path, 'rb') as f:
                agent.memory.steps = pickle.load(f)
        else:
            print(f"No memory.pkl found in {agent_name}.")

    return agents

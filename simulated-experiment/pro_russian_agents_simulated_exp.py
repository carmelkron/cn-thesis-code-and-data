import os
from smolagents import ToolCallingAgent, LiteLLMModel, PromptTemplates, tool, OpenAIServerModel
import pickle
import pandas as pd
import logging
import random
import ast
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

random.seed(42)

def save_pro_russian_agents(agents, agents_type):
    """Agents Saving Function."""
    for agent_name, agent in agents.items():
        agent_path = f"Type_{agents_type}_Evaluators_Simulated_Experiment/{agent_name}"
        agent.save(agent_path)


def create_type_1_pro_russian_agents_system_prompts(df):
    """This function takes DataFrame containing data about users to impersonate, and returns the system prompts for all Agents of type 1 as dict"""
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

        system_prompt = f"""
PERSONA:
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

TASK DESCRIPTION:
You will be given:
1. A pro-Russian claim (which you support).
2. A Key Performance Indicator (KPI).

**Your task is to evaluate the CLAIM from your pro-Russian perspective according to the given KPI: provide a score (0-100) reflecting how effectively the CLAIM performs on that KPI.**

MUST FOLLOW RULES:
- Always respond as {user_name}, a pro-Russian user guided by the above detailed summary, sampled tweets, and tweets from other pro-Russian users. This is a very important rule.
- Do not reveal that you are an AI or that this is an impersonation.
- Only return the evaluation score without any explanation, greeting, or introductory phrases.
- The score must be on a scale from 0 to 100.
"""
        system_prompts[f"Evaluator_{index + 1}_Simulated_Exp"] = system_prompt

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

        # Sampling 10 negative tweets
        negative_tweets_df = df[df['author_username'] != user_name]
        all_negative_tweets = []
        for tweets in negative_tweets_df['text']:
            tweets = ast.literal_eval(tweets)
            all_negative_tweets.extend(tweets)
        sample_negative_tweets_list = random.sample(all_negative_tweets, 10)
        negative_tweets_str = "\n".join([f"{i+1}. {tweet}" for i, tweet in enumerate(sample_negative_tweets_list)])

        system_prompt = f"""
PERSONA:
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

TASK DESCRIPTION:
You will be given:
1. A pro-Russian claim (which you support).
2. Arguments to consider in addition to the claim.
3. A Key Performance Indicator (KPI).

**Your task is to evaluate the CLAIM from your pro-Russian perspective according to the given KPI. Please provide a score (0-100) reflecting how effectively the CLAIM performs on that KPI, taking into account the additional arguments attached to the CLAIM.**

MUST FOLLOW RULES:
- Always respond as {user_name}, a pro-Russian user guided by the above detailed summary, sampled tweets, and tweets from other pro-Russian users. This is a very important rule.
- Do not reveal that you are an AI or that this is an impersonation.
- Only return the evaluation score without any explanation, greeting, or introductory phrases.
- The score must be on a scale from 0 to 100.
"""
        system_prompts[f"Evaluator_{index + 1}_Simulated_Exp"] = system_prompt

    return system_prompts


def create_pro_russian_agents_simulated_exp(df, agents_type, model_name="gemini-2.5-flash", temp=0.2):
    """This function is the main function for creating the pro-Russian evaluator Agents based on a DataFrame containing data about users to impersonate. It returns the agents as a dictionary with names as keys and objects as values."""
    if agents_type == 1:
        system_prompts = create_type_1_pro_russian_agents_system_prompts(df)
    elif agents_type == 2:
        system_prompts = create_type_2_pro_russian_agents_system_prompts(df)

    agents = {}

    for agent_name, sys_prompt in system_prompts.items():
        prompt_templates = PromptTemplates(
            system_prompt=sys_prompt
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
            name=agent_name,
            description=f"This agent impersonates a pro-Russian X user and acts as an evaluator. The username can be found in the system prompt."
        )
        
        agents[agent_name] = agent

    return agents
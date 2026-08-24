import os
from smolagents import ToolCallingAgent, LiteLLMModel, PromptTemplates, tool
import pickle
import pandas as pd
import logging
import json

memory_summarizer_agent_system_prompt = """
You are an Agent-Specific Summarizer tasked with aggregating and updating evaluation feedback for a single evaluator agent’s outputs. Your summary will serve as the memory for that agent, capturing the most important details of its past iterations' evaluations.

Instructions:

1. Input Format:

    Initial Batch (Iterations 1–5):
    You will receive 5 iterations of evaluator outputs for a specific agent. Each iteration is provided in JSON format and includes:
    - A claim and its associated counter-narrative (CN).
    - Detailed feedback on three KPIs: Persuasiveness, Emotional Engagement, and Shareability. For each KPI, the output contains a few good points, a few bad points, and a numeric score (ranging from 0 to 100).

    Subsequent Batches (e.g., Iterations 6–10, etc.):
    In addition to the new batch of iterations for the same agent, you will also receive the existing summary (which represents the memory of all previous iterations).

    
2. Task for the Initial Batch (Iterations 1–5):

    Generate a cohesive summary between 500 and 1000 words that:
    - Accurately reflects the evaluator’s feedback and scores from these 5 iterations.
    - Highlights both strengths and areas for improvement given by the evaluator agent for each KPI.
    - Presents any trends or notable patterns in the scores.
    - Is organized in a clear, structured manner (e.g., overview, detailed sections for each KPI, observations).

    
3. Task for Subsequent Batches (When a Previous Summary is Present):

    Update the Existing Memory:
    - Integrate the previous summary (memory) with the new batch of iterations.
    - Ensure that the updated summary remains representative of the entire history of the agent’s evaluations.
    - Merge the new insights with the existing memory, keeping continuity and clarity. The summary should still fall within 500 to 1000 words.
    - The final output must retain all critical historical context while reflecting new trends, adjustments, and any shifts in feedback or scores.


4. Output Requirements:

    - Agent-Specific Representation:
    Your output should be a summary that is clearly tied to the specific agent’s evaluation history. It must not mix data from different agents.
    - Structured and Clear:
    Divide the summary into logical sections (e.g., Overall Overview, Persuasiveness, Emotional Engagement, Shareability, and Trends/Observations).
    - Comprehensive Memory:
    The summary should serve as a memory snapshot, summarizing both qualitative feedback (good/bad points) and quantitative data (numeric scores) across all past iterations.
    - Conciseness:
    While detailed, the summary must be concise enough to serve as an effective memory that can be used in subsequent iterations without unnecessary verbosity.
"""
memory_summarizer_agent_description = "This Agent provides a summary of all previous iterations, which is used for context of evaluator agents (memory)"

def save_memory_summarizer_agent(agent):
    agent_path = r"Memory_Summarizer_Agent"
    agent.save(agent_path)


def create_memory_summarizer_agent(system_prompt, description, model_name="claude-3-5-haiku-20241022", temp=0.8):
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
        name="Memory_Summarizer_Agent",
        description=description
    )

    return agent


def extract_claim_and_cn(task_text):
    """
    Extracts the pro-Russian claim and the pro-Ukrainian counter-narrative from the task text.
    Assumes that the text contains 'pro-Russian claim:' and 'pro-Ukrainian Counter-Narrative:'.
    """
    claim = ""
    counter_narrative = ""
    try:
        if "pro-Russian claim:" in task_text and "pro-Ukrainian Counter-Narrative:" in task_text:
            # Split at the claim marker
            parts = task_text.split("pro-Russian claim:")
            if len(parts) > 1:
                remainder = parts[1]
                # Split at the counter narrative marker
                claim_part, cn_part = remainder.split("pro-Ukrainian Counter-Narrative:", 1)
                claim = claim_part.strip()
                counter_narrative = cn_part.strip()
    except Exception as e:
        print("Error extracting claim and counter-narrative:", e)
    return claim, counter_narrative


def extract_evaluation(action):
    """Extracts evaluation data from the ActionStep."""
    evaluation = {}
    if action.tool_calls:
        try: 
            answer_str = action.tool_calls[0].arguments['answer']
            evaluation = json.loads(answer_str)
        except Exception as e:
            print("Error extracting evaluation:", e)
    return evaluation


def transform_memory(memory_steps, iteration_num, previous_summary=None):
    """
    Transforms the memory (a list of TaskStep and ActionStep objects) into a JSON-formatted string
    that the summarizer agent expects. Each valid iteration is represented as a dictionary containing:
       - iteration number
       - claim
       - counter_narrative
       - evaluation (parsed JSON from the ActionStep)
       
    If a previous_summary string is provided, it is added to the final dictionary.
    This function looks for a TaskStep (i.e., an object with a 'task' attribute) and then finds the next
    valid ActionStep (i.e., an object with 'model_input_messages' and valid output). If the expected ordering is not found, the step is skipped.
    """
    new_iterations = []
    i = 0
    while i < len(memory_steps):
        # Look for the next TaskStep
        if not hasattr(memory_steps[i], "task"):
            i += 1
            continue
        task_obj = memory_steps[i]
        
        # Find the next valid ActionStep after this TaskStep
        j = i + 1
        while j < len(memory_steps):
            if hasattr(memory_steps[j], "model_input_messages") and memory_steps[j].tool_calls:
                # Check if the ActionStep has valid output
                try:
                    answer_str = memory_steps[j].tool_calls[0].arguments.get('answer', None)
                    if answer_str:  # Valid output found
                        break
                except Exception as e:
                    print("Error checking ActionStep output:", e)
            j += 1
        if j >= len(memory_steps):
            break  # No valid ActionStep found.
        action_obj = memory_steps[j]

        try:
            claim, counter_narrative = extract_claim_and_cn(task_obj.task)
        except Exception as e:
            print("Error extracting claim and counter-narrative:", e)
            i = j + 1
            continue

        evaluation = extract_evaluation(action_obj)

        iteration_dict = {
            "iteration": iteration_num,
            "claim": claim,
            "counter_narrative": counter_narrative,
            "evaluation": evaluation
        }
        new_iterations.append(iteration_dict)
        iteration_num += 1
        i = j + 1  # Move past the current ActionStep

    result = {"new_iterations": new_iterations}
    if previous_summary is not None:
        result["existing_summary"] = previous_summary

    return json.dumps(result, indent=2)

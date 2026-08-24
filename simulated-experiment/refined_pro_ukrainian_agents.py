import os
from smolagents import ToolCallingAgent, LiteLLMModel, PromptTemplates, tool, OpenAIServerModel
import pickle
import pandas as pd
import logging
from dotenv import load_dotenv
import importlib.util
import glob

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# The refined prompts and the saved refined agents are produced by the
# refinement stage and live in that folder, so resolve them against the
# repository root rather than the working directory.
HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
REFINEMENT_DIR = os.path.join(REPO_ROOT, "refinement-per-claim")
REFINED_PROMPTS_DIR = os.path.join(REFINEMENT_DIR, "refined_system_prompts")
REFINED_AGENTS_DIR = os.path.join(REFINEMENT_DIR, "Refined_CN_Agents")


def create_refined_pro_ukrainian_agents(model_name="gemini-2.5-flash", temp=1.2):
    """Agents creation function."""
    pro_ukrainian_agents_system_prompts = {}

    # glob all your claim files
    for path in glob.glob(os.path.join(REFINED_PROMPTS_DIR, 'claim*.py')):

        module_name = os.path.splitext(os.path.basename(path))[0]

        # load the module from path
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # collect its public variables (skip built-ins, callables, etc.)
        vars_dict = {
            name: val
            for name, val in vars(module).items()
            if not name.startswith('_')      # skip __builtins__, etc.
            and not callable(val)         # skip functions/classes
        }

        pro_ukrainian_agents_system_prompts[module_name] = vars_dict
    
    agents = {}

    pro_ukrainian_agents_descriptions = {
        "agent_1": "Refined Persuasiveness-focused Counter-Narrative Generator Agent",
        "agent_2": "Refined Emotional Engagement-focused Counter-Narrative Generator Agent",
        "agent_3": "Refined Shareability-focused Counter-Narrative Generator Agent"
    }

    for claim_name, data in pro_ukrainian_agents_system_prompts.items():
        claim_agents = {}
        for agent_name in data.keys():
            sys_prompt = data[agent_name]
            desc = pro_ukrainian_agents_descriptions.get(agent_name) + f" For {claim_name}"

            prompt_templates = PromptTemplates(
                system_prompt=sys_prompt
            )
        
            model = OpenAIServerModel(
                model_id=model_name,
                api_base="https://generativelanguage.googleapis.com/v1beta/openai/",
                api_key=GEMINI_API_KEY,
                temperature=temp,
                reasoning_effort="medium"
            )
        
            agent = ToolCallingAgent (
                tools=[],
                model=model,
                prompt_templates=prompt_templates,
                add_base_tools=False,
                name=agent_name,
                description=desc
            )
        
            claim_agents[agent_name] = agent
        agents[claim_name] = claim_agents

    return agents


def save_refined_pro_ukrainian_agents(agents):
    for claim_name, data in agents.items():
        for agent_name, agent in data.items():
            agent.save(os.path.join(REFINED_AGENTS_DIR, claim_name, agent_name))


def save_refined_pro_ukrainian_agents_memories(agents):
    for claim_name, data in agents.items():
        for agent_name, agent in data.items():
            memory_file_path = os.path.join(REFINED_AGENTS_DIR, claim_name, agent_name, "memory.pkl")
            with open(memory_file_path, "wb") as f:
                pickle.dump(agent.memory.steps, f)


def load_refined_pro_ukrainian_agents():
    agents = create_refined_pro_ukrainian_agents()

    logger = logging.getLogger("smolagents")
    logger.setLevel(logging.DEBUG)

    for claim_name, data in agents.items():
        for agent_name, agent in data.items():
            memory_path = os.path.join(REFINED_AGENTS_DIR, claim_name, agent_name, "memory.pkl")
            if os.path.exists(memory_path):
                with open(memory_path, 'rb') as f:
                    agent.memory.steps = pickle.load(f)
            else:
                print(f"No memory.pkl found for {claim_name}/{agent_name}.")

    return agents


if __name__ == "__main__":
    agents = create_refined_pro_ukrainian_agents()
    save_refined_pro_ukrainian_agents(agents)
import yaml
import os
from smolagents import GradioUI, ToolCallingAgent, OpenAIServerModel

# Get current directory path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

from tools.final_answer import FinalAnswerTool as FinalAnswer



model = OpenAIServerModel(
temperature=1.2,
reasoning_effort='medium',
model_id='gemini-2.5-flash',
)

final_answer = FinalAnswer()


with open(os.path.join(CURRENT_DIR, "prompts.yaml"), 'r') as stream:
    prompt_templates = yaml.safe_load(stream)

agent_agent_2 = ToolCallingAgent(
    model=model,
    tools=[],
    managed_agents=[],
    max_steps=20,
    verbosity_level=1,
    grammar=None,
    planning_interval=None,
    name='agent_2',
    description='Refined Emotional Engagement-focused Counter-Narrative Generator Agent For claim6',
    prompt_templates=prompt_templates
)
if __name__ == "__main__":
    GradioUI(agent_agent_2).launch()

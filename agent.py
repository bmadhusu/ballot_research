import os
from ballot_research.util import load_instruction_from_file


from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

try:
    # GOOGLE_API_KEY = UserSecretsClient().get_secret("GOOGLE_API_KEY")
    GOOGLE_API_KEY=os.environ["GOOGLE_API_KEY"]
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"
    print("✅ Gemini API key setup complete.")
except Exception as e:
    print(f"🔑 Authentication Error: Please make sure you have added 'GOOGLE_API_KEY' to your Kaggle secrets. Details: {e}")

import uuid
from google.genai import types

from google.adk.agents import Agent, LlmAgent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.runners import InMemoryRunner, Runner
from google.adk.models.google_llm import Gemini
from google.adk.sessions import InMemorySessionService, DatabaseSessionService
from google.adk.tools import google_search, agent_tool




from google.adk.apps.app import App, ResumabilityConfig, EventsCompactionConfig
from google.adk.tools.function_tool import FunctionTool

print("✅ ADK components imported successfully.")

# FROM DAY 2A - AGENT TOOLS
def show_python_code_and_result(response):
    for i in range(len(response)):
        # Check if the response contains a valid function call result from the code executor
        if (
            (response[i].content.parts)
            and (response[i].content.parts[0])
            and (response[i].content.parts[0].function_response)
            and (response[i].content.parts[0].function_response.response)
        ):
            response_code = response[i].content.parts[0].function_response.response
            if "result" in response_code and response_code["result"] != "```":
                if "tool_code" in response_code["result"]:
                    print(
                        "Generated Python Code >> ",
                        response_code["result"].replace("tool_code", ""),
                    )
                else:
                    print("Generated Python Response >> ", response_code["result"])


print("✅ Helper functions defined.")

retry_config = types.HttpRetryOptions(
    attempts=5,  # Maximum retry attempts
    exp_base=7,  # Delay multiplier
    initial_delay=1,
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP errors
)

def create_research_agent(index, target):
    print(f"Loading instruction: {load_instruction_from_file(f"ballot_research_instructions_p{index}.txt") + load_instruction_from_file("template_target_research.txt").replace("{TARGET}",target)}")
    return Agent(
        name=f"ResearchAgent{index}",
        model="gemini-2.0-flash",
        description=f"Research agent for proposition {index}",
        instruction=load_instruction_from_file(f"ballot_research_instructions_p{index}.txt") + load_instruction_from_file("template_target_research.txt").replace("{TARGET}",target),
        tools=[google_search],
        output_key="research_findings"
    )

# Helper function to create a pipeline for a specific proposition
def create_ballot_pipeline(index):
    # Research Agent

    research_agents = [create_research_agent(index, t) for t in ["Wikipedia"]]#, "Ballotpedia", "NYCVotes"]]
    # Pipeline
    return ParallelAgent(
        name=f"BallotResearchPipeline{index}",
        sub_agents=research_agents,
    )

# Create pipelines for all 6 propositions
#pipelines = [create_ballot_pipeline(i) for i in range(1, 7)]
pipelines = [create_ballot_pipeline(i) for i in range(1, 2)]

print("✅ 6 Research Pipelines created.")

# Create a parallel agent to run multiple research agents simultaneously
ballot_pipeline_agent = ParallelAgent(
    name="BallotResearchParallelPipeline",
    sub_agents=pipelines,
)

root_agent = ballot_pipeline_agent

print("✅ Sequential Agent created.")

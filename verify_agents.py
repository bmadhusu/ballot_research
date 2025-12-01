import sys
import os

# Add the parent directory to sys.path to allow importing ballot_research
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from ballot_research.agent import ballot_pipeline_agent
    from google.adk.agents import ParallelAgent, SequentialAgent

    print("✅ Successfully imported ballot_pipeline_agent")

    if isinstance(ballot_pipeline_agent, ParallelAgent):
        print(f"✅ ballot_pipeline_agent is a ParallelAgent")
        
        sub_agents = ballot_pipeline_agent.sub_agents
        print(f"✅ Found {len(sub_agents)} sub-agents")
        
        if len(sub_agents) == 6:
            print("✅ Correct number of sub-agents (6)")
        else:
            print(f"❌ Incorrect number of sub-agents: {len(sub_agents)}")

        for i, agent in enumerate(sub_agents):
            if isinstance(agent, SequentialAgent):
                print(f"  ✅ Sub-agent {i+1} ({agent.name}) is a SequentialAgent")
            else:
                print(f"  ❌ Sub-agent {i+1} ({agent.name}) is NOT a SequentialAgent")
    else:
        print("❌ ballot_pipeline_agent is NOT a ParallelAgent")

except ImportError as e:
    print(f"❌ ImportError: {e}")
except Exception as e:
    print(f"❌ An error occurred: {e}")

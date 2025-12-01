import sys
import os

# Add the parent directory to sys.path to allow importing ballot_research
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ballot_research.agent import root_agent
from google.adk.runners import InMemoryRunner

# Create a runner
runner = InMemoryRunner()

# Test with a simple query for just one proposition
test_query = "Research NY ballot proposition 1 from the 2025 election"

print("🧪 Testing URL extraction from Google Search...")
print(f"Query: {test_query}\n")

# Run the agent
from google.genai import types

try:
    result = runner.run(
        agent=root_agent,
        user_message=test_query
    )
    
    print("\n" + "="*80)
    print("AGENT RESPONSE:")
    print("="*80)
    
    # Print the response
    for event in result:
        if hasattr(event, 'content') and event.content:
            if hasattr(event.content, 'parts') and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, 'text') and part.text:
                        print(part.text)
                        
                        # Check if URLs are present
                        if "http" in part.text.lower() or "URL:" in part.text:
                            print("\n✅ URLs FOUND in response!")
                        else:
                            print("\n⚠️  No URLs detected in text response")
    
    print("\n" + "="*80)
    
except Exception as e:
    print(f"❌ Error running test: {e}")
    import traceback
    traceback.print_exc()

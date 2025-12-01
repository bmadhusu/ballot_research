import asyncio
import uuid
import os
import sys
import re
import aiohttp

# Add the parent directory to sys.path to allow importing ballot_research
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ballot_research.agent import ballot_pipeline_agent
from google.genai import types
from google.adk.runners import InMemoryRunner, Runner
from google.adk.sessions import InMemorySessionService


async def resolve_redirect_url(redirect_url):
    """Follow the redirect to get the actual URL"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(redirect_url, allow_redirects=True, timeout=10) as response:
                return str(response.url)
    except Exception as e:
        print(f"\n[Warning] Could not resolve URL: {e}")
        return redirect_url  # Return original if fails


async def process_json_urls(json_text):
    """Find and replace all redirect URLs in JSON with actual URLs"""
    # Find all vertexaisearch URLs
    redirect_pattern = r'https://vertexaisearch\.cloud\.google\.com/grounding-api-redirect/[A-Za-z0-9_-]+={0,2}'
    redirect_urls = re.findall(redirect_pattern, json_text)
     
    if not redirect_urls:
        print("\n[Info] No redirect URLs found to resolve")
        return json_text
    
    print(f"\n[Info] Found {len(set(redirect_urls))} unique redirect URLs to resolve...")
    
    # Resolve each URL
    replacements = {}
    for i, url in enumerate(set(redirect_urls), 1):  # Use set to avoid duplicates
        print(f"[{i}/{len(set(redirect_urls))}] Resolving URL...", end="", flush=True)
        actual_url = await resolve_redirect_url(url)
        replacements[url] = actual_url
        print(" ✓")
    
    # Replace in text
    result = json_text
    for old_url, new_url in replacements.items():
        result = result.replace(old_url, new_url)
    
    print("[Info] URL resolution complete!\n")
    return result


async def main():
    runner = InMemoryRunner(agent=ballot_pipeline_agent)
    session_id = str(uuid.uuid4())
    user_id = "user_123"
    app_name = "ballot_research"

    session_service = InMemorySessionService()
    # Attempt to create a new session or retrieve an existing one
    try:
        await session_service.create_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )
    except Exception:
        await session_service.get_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
        )

    # Step 3: Create the Runner
    runner = Runner(
        agent=ballot_pipeline_agent, app_name=app_name, session_service=session_service
    )


    query = "Research the ballot propositions."
    message = types.Content(role="user", parts=[types.Part(text=query)])

    print(f"Starting research for session {session_id}...")

    full_output = ""
    
    async for event in runner.run_async(
        session_id=session_id, user_id=user_id, new_message=message
    ):
        # Print text content
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text, end="", flush=True)
                    full_output += part.text
        
        # Access grounding metadata directly from event (for debugging)
      #  if event.grounding_metadata and event.grounding_metadata.grounding_chunks:
      #      print("\n\n--- Sources (from grounding metadata) ---")
      #      for chunk in event.grounding_metadata.grounding_chunks:
      #          if hasattr(chunk, "web") and chunk.web:
      #              print(f"URL: {chunk.web.uri}")
      #              print(f"Title: {chunk.web.title}")
      #      print("--- End Sources ---\n")

    print("\n\n" + "="*60)
    print("Research complete. Now resolving URLs...")
    print("="*60)
    
    # Post-process to resolve URLs
    resolved_output = await process_json_urls(full_output)
    
    # Save both versions
    output_dir = os.path.dirname(__file__)
    
    # Save original output
    original_path = os.path.join(output_dir, "ballot_research_output_original.txt")
    with open(original_path, "w") as f:
        f.write(full_output)
    print(f"✓ Original output saved to: {original_path}")
    
    # Save resolved output
    resolved_path = os.path.join(output_dir, "ballot_research_output_resolved.txt")
    with open(resolved_path, "w") as f:
        f.write(resolved_output)
    print(f"✓ Resolved output saved to: {resolved_path}")
    
    print("\n" + "="*60)
    print("All done! Check the resolved output file for actual URLs.")
    print("="*60)



if __name__ == "__main__":
    asyncio.run(main())

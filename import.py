from agents import (
    Agent,
    Runner,
)
import os
from rich import print

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

agent = Agent(
    name="Assistant"  # name is required
)

result = Runner.run_sync(starting_agent=agent, input="Who is the founder of pakistan?")
print("Result :\n")
print(result.final_output)  
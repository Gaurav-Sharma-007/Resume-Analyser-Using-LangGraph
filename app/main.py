try:
    from langchain.agents import create_agent
except ImportError as e:
    print(f"Error importing langchain.agents: {e}")

from app.llm import llm


def get_temperature(city: str) -> str:
    """
    Generate a realistic temperature for a city using the LLM.
    """

    response = llm.invoke(
        f"""
        Give only the current approximate temperature in Celsius for {city}.
        Return ONLY the number with °C.
        Example: 22°C
        """
    )

    temperature = response.content.strip()

    return f"The temperature in {city} is {temperature}."


agent = create_agent(
    model=llm,
    tools=[get_temperature],
    system_prompt="""
    You are a helpful assistant.
    Use the get_temperature tool whenever the user asks about weather or temperature.
    """,
)

result = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "What's the temperature in Philadelphia?",
            }
        ]
    }
)

print(result["messages"][-1].content)

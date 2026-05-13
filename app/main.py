import configparser
import os
try:
    from langchain.agents import create_agent
except ImportError as e:
    print(f"Error importing langchain.agents: {e}")
try:
    from langchain_openai import AzureChatOpenAI
except ImportError as e:
    print(f"Error importing langchain_openai: {e}")


def load_azure_config(path: str = "config.ini") -> dict[str, str]:
    config = configparser.ConfigParser()
    config.read(path)

    if "AZURE" not in config:
        raise RuntimeError(f"Missing [AZURE] section in {path}")

    azure = config["AZURE"]

    settings = {
        "api_key": azure.get("OPENAI_API_KEY") or os.environ.get("AZURE_OPENAI_API_KEY"),
        "endpoint": azure.get("OPENAI_ENDPOINT") or os.environ.get("AZURE_OPENAI_ENDPOINT"),
        "deployment": azure.get("OPENAI_DEPLOYMENT_NAME")
        or os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
        "api_version": azure.get("OPENAI_API_VERSION")
        or os.environ.get("AZURE_OPENAI_API_VERSION"),
    }

    missing = [name for name, value in settings.items() if not value]

    if missing:
        raise RuntimeError(f"Missing Azure OpenAI setting(s): {', '.join(missing)}")

    return settings


azure_config = load_azure_config()


# Main LLM
llm = AzureChatOpenAI(
    api_key=azure_config["api_key"],
    azure_endpoint=azure_config["endpoint"],
    azure_deployment=azure_config["deployment"],
    api_version=azure_config["api_version"],
)


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
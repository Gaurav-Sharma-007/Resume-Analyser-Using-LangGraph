import configparser
import os
from pathlib import Path

from langchain_openai import AzureChatOpenAI


CONFIG_FILE = Path(__file__).resolve().parents[2] / "config.ini"


def load_azure_config(path: str | Path = CONFIG_FILE) -> dict[str, str]:
    settings = {
        "api_key": os.getenv("AZURE_OPENAI_KEY"),
        "endpoint": os.getenv("AZURE_OPENAI_ENDPOINT"),
        "deployment": os.getenv("AZURE_OPENAI_DEPLOYMENT"),
        "api_version": os.getenv("AZURE_OPENAI_API_VERSION"),
    }

    if all(settings.values()):
        return settings

    config_path = Path(path)
    config = configparser.ConfigParser()
    read_files = config.read(config_path)

    if not read_files:
        missing = [name for name, value in settings.items() if not value]
        env_names = {
            "api_key": "AZURE_OPENAI_KEY",
            "endpoint": "AZURE_OPENAI_ENDPOINT",
            "deployment": "AZURE_OPENAI_DEPLOYMENT",
            "api_version": "AZURE_OPENAI_API_VERSION",
        }
        missing_env = ", ".join(env_names[name] for name in missing)
        raise RuntimeError(
            "Missing Azure OpenAI configuration. Set these environment variables "
            f"or create {config_path}: {missing_env}"
        )

    if "AZURE" not in config:
        raise RuntimeError(f"Missing [AZURE] section in {config_path}")

    azure = config["AZURE"]

    settings = {
        "api_key": azure.get("AZURE_OPENAI_KEY"),
        "endpoint": azure.get("AZURE_OPENAI_ENDPOINT"),
        "deployment": azure.get("AZURE_OPENAI_DEPLOYMENT"),
        "api_version": azure.get("AZURE_OPENAI_API_VERSION"),
    }

    missing = [name for name, value in settings.items() if not value]
    if missing:
        raise RuntimeError(
            f"Missing Azure OpenAI setting(s) in {config_path}: {', '.join(missing)}"
        )

    return settings


azure_config = load_azure_config()

llm = AzureChatOpenAI(
    api_key=azure_config["api_key"],
    azure_endpoint=azure_config["endpoint"],
    azure_deployment=azure_config["deployment"],
    api_version=azure_config["api_version"],
)

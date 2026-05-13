import configparser
from pathlib import Path

from langchain_openai import AzureChatOpenAI


CONFIG_FILE = Path(__file__).resolve().parents[2] / "config.ini"


def load_azure_config(path: str | Path = CONFIG_FILE) -> dict[str, str]:
    config_path = Path(path)
    config = configparser.ConfigParser()
    read_files = config.read(config_path)

    if not read_files:
        raise RuntimeError(f"Could not read Azure OpenAI config file: {config_path}")

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

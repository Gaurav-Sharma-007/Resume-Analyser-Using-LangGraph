from langchain_openai import ChatOpenAI


llm = ChatOpenAI(model="gpt-5.4")


def parse_resume_node(state):
    prompt = f"""
    Parse this resume into structured JSON.

    Resume:
    {state['raw_text']}
    """

    response = llm.invoke(prompt)

    state["parsed_resume"] = response.content
    state["current_step"] = "resume_parsed"

    return state
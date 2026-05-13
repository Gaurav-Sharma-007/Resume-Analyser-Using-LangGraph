
from app.llm import llm


def job_match_node(state):

    prompt = f"""
    Based on these skills:

    {state['skills']}

    Suggest best matching software jobs.
    """

    response = llm.invoke(prompt)

    matches = response.content.split("\n")

    state["job_matches"] = matches

    return state

import llm

def ats_score_node(state):

    prompt = f"""
    Analyze this resume for ATS compatibility.

    Return:
    - score out of 100
    - weaknesses
    - formatting issues

    Resume:
    {state['parsed_resume']}
    """

    response = llm.invoke(prompt)

    state["feedback"] = response.content
    state["ats_score"] = 78
    print("ATS Score:", state["ats_score"])

    return state
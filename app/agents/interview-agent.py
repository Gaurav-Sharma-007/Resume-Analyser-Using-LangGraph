from app.llm import llm


def interview_questions_node(state):

    prompt = f"""
    Generate interview questions for:

    Skills:
    {state['skills']}

    Experience:
    {state['parsed_resume']}
    """

    response = llm.invoke(prompt)

    questions = response.content.split("\n")

    state["interview_questions"] = questions

    return state

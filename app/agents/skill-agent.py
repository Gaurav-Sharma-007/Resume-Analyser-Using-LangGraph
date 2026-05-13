
import llm


def skill_analysis_node(state):

    prompt = f"""
    Extract technical and soft skills from:

    {state['parsed_resume']}
    """

    response = llm.invoke(prompt)

    skills = response.content.split(",")

    state["skills"] = skills
    state["current_step"] = "skills_analyzed"

    return state
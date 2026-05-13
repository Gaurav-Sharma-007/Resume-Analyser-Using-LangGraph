import json
import re

from app.llm import llm


def _extract_json(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            return {}
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            return {}


def parse_resume_node(state):
    raw_text = state.get("raw_text", "").strip()
    if not raw_text:
        raise ValueError("Cannot parse resume because state['raw_text'] is empty.")

    prompt = f"""
    Parse this resume into structured JSON.
    Return ONLY valid JSON with this schema:
    {{
      "name": "",
      "email": "",
      "phone": "",
      "location": "",
      "summary": "",
      "skills": [],
      "experience": [],
      "education": [],
      "projects": [],
      "certifications": [],
      "links": []
    }}

    Resume:
    {raw_text}
    """

    response = llm.invoke(prompt)
    parsed_resume = _extract_json(response.content)

    state["parsed_resume"] = parsed_resume or {"raw_response": response.content}
    state["current_step"] = "resume_parsed"

    return state

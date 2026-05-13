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


def _clamp_score(value) -> int:
    try:
        score = int(round(float(value)))
    except (TypeError, ValueError):
        return 0
    return max(0, min(100, score))


def _fallback_ats_score(parsed_resume: str, skills: list[str]) -> int:
    if not isinstance(parsed_resume, str):
        parsed_resume = json.dumps(parsed_resume)

    text = parsed_resume.lower()
    score = 45

    sections = {
        "skills": 10,
        "experience": 10,
        "education": 8,
        "projects": 7,
        "contact": 5,
    }
    for section, points in sections.items():
        if section in text:
            score += points

    if re.search(r"[\w\.-]+@[\w\.-]+\.\w+", parsed_resume):
        score += 5
    if re.search(r"\+?\d[\d\s().-]{8,}\d", parsed_resume):
        score += 5
    if skills:
        score += min(10, len([skill for skill in skills if str(skill).strip()]))
    if any(word in text for word in ("achieved", "improved", "reduced", "increased", "built", "led")):
        score += 5
    if re.search(r"\d+%|\$\d+|\d+\+", parsed_resume):
        score += 5

    return _clamp_score(score)


def ats_score_node(state):
    parsed_resume = state.get("parsed_resume", "")
    skills = state.get("skills", [])

    prompt = f"""
    Analyze this resume for ATS compatibility.

    Return ONLY valid JSON with this schema:
    {{
      "ats_score": 0-100,
      "weaknesses": ["specific weakness"],
      "formatting_issues": ["specific formatting issue"],
      "recommendations": ["specific improvement"]
    }}

    Resume:
    {parsed_resume}

    Extracted skills:
    {skills}
    """

    response = llm.invoke(prompt)
    result = _extract_json(response.content)

    ats_score = _clamp_score(result.get("ats_score"))
    if ats_score == 0:
        ats_score = _fallback_ats_score(parsed_resume, skills)

    state["ats_score"] = ats_score
    state["ats_feedback"] = {
        "weaknesses": result.get("weaknesses", []),
        "formatting_issues": result.get("formatting_issues", []),
        "recommendations": result.get("recommendations", []),
    }
    state["feedback"] = response.content
    state["current_step"] = "ats_scored"

    return state

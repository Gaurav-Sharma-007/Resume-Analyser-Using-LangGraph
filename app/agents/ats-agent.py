import json
import re

from app.models.llm import llm


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
     You are an advanced and highly experienced Applicant Tracking System (ATS) with specialized knowledge in the tech industry, including but not limited to [insert specific field here, e.g., software engineering, data science, data analysis, big data engineering]. Your primary task is to meticulously evaluate resumes based on the provided job description. Considering the highly competitive job market, your goal is to offer the best possible guidance for enhancing resumes.

        Responsibilities:

        1. Assess resumes with a high degree of accuracy against the job description.
        2. Identify and highlight missing keywords crucial for the role.
        3. Provide a percentage match score reflecting the resume's alignment with the job requirements on the scale of 1-100.
        4. Offer detailed feedback for improvement to help candidates stand out.
        5. Analyze the Resume, Job description and indutry trends and provide personalized suggestions for skils, keywords and acheivements that can enhance the provided resume.
        6. Provide the suggestions for improving the language, tone and clarity of the resume content.
        7. Provide users with insights into the performance of thier resumes. Track the metrices such as - a) Application Success rates b) Views c) engagement. offers valuable feedback to improve the candidate's chances in the job market use your trained knowledge of gemini trained data . Provide  a application success rate on the scale of 1-100.

        after everytime whenever a usr refersh a page, if the provided job decription and resume is same, then always give same result. 
        

        Field-Specific Customizations:

        Software Engineering:
        You are an advanced and highly experienced Applicant Tracking System (ATS) with specialized knowledge in software engineering. Your primary task is to meticulously evaluate resumes based on the provided job description for software engineering roles. Considering the highly competitive job market, your goal is to offer the best possible guidance for enhancing resumes.

        Data Science:
        You are an advanced and highly experienced Applicant Tracking System (ATS) with specialized knowledge in data science. Your primary task is to meticulously evaluate resumes based on the provided job description for data science roles. Considering the highly competitive job market, your goal is to offer the best possible guidance for enhancing resumes.

        Data Analysis:
        You are an advanced and highly experienced Applicant Tracking System (ATS) with specialized knowledge in data analysis. Your primary task is to meticulously evaluate resumes based on the provided job description for data analysis roles. Considering the highly competitive job market, your goal is to offer the best possible guidance for enhancing resumes.

        Big Data Engineering:
        You are an advanced and highly experienced Applicant Tracking System (ATS) with specialized knowledge in big data engineering. Your primary task is to meticulously evaluate resumes based on the provided job description for big data engineering roles. Considering the highly competitive job market, your goal is to offer the best possible guidance for enhancing resumes.

        AI / MLEngineering:
        You are an advanced and highly experienced Applicant Tracking System (ATS) with specialized knowledge in AI/ML engineering. Your primary task is to meticulously evaluate resumes based on the provided job description for AI / ML engineering roles. Considering the highly competitive job market, your goal is to offer the best possible guidance for enhancing resumes.

        CLoud Engineering:
        You are an advanced and highly experienced Applicant Tracking System (ATS) with specialized knowledge in cloud engineering. Your primary task is to meticulously evaluate resumes based on the provided job description for cloud engineering roles. Considering the highly competitive job market, your goal is to offer the best possible guidance for enhancing resumes.

    Return ONLY valid JSON with this schema:
    {{
      "ats_score": 0-100,
      Job Description Match: "specific match details",
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

import json
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

if __package__ in {None, ""}:
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.models.llm import llm
from app.services.pdf_service import extract_text_from_pdf


app = FastAPI(
    title="LangChain Resume Analyser API",
    description="FastAPI backend for parsing resumes, scoring ATS fit, and generating career guidance.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ResumeAnalysisRequest(BaseModel):
    raw_text: str = Field(..., min_length=20, description="Resume content as plain text.")
    job_description: str | None = Field(
        default=None,
        description="Optional target job description for role matching and ATS feedback.",
    )


class ResumeAnalysisResponse(BaseModel):
    parsed_resume: dict[str, Any]
    skills: list[str]
    ats_score: int
    ats_feedback: dict[str, list[str]]
    job_matches: list[str]
    interview_questions: list[str]


def _extract_json(text: str) -> dict[str, Any]:
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not match:
            return {}

    try:
        parsed = json.loads(match.group(0))
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}


def _extract_json_list(text: str) -> list[str]:
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
    except json.JSONDecodeError:
        match = re.search(r"\[.*\]", text, flags=re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group(0))
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
            except json.JSONDecodeError:
                pass

    return _split_lines_or_commas(text)


def _split_lines_or_commas(text: str) -> list[str]:
    values = re.split(r"[\n,]+", text)
    cleaned = []
    for value in values:
        item = re.sub(r"^[-*\d.\s]+", "", value).strip()
        if item:
            cleaned.append(item)
    return cleaned


def _clamp_score(value: Any) -> int:
    try:
        score = int(round(float(value)))
    except (TypeError, ValueError):
        return 0
    return max(0, min(100, score))


def _fallback_ats_score(parsed_resume: dict[str, Any], skills: list[str]) -> int:
    text = json.dumps(parsed_resume).lower()
    score = 45

    for section, points in {
        "skills": 10,
        "experience": 10,
        "education": 8,
        "projects": 7,
        "contact": 5,
    }.items():
        if section in text:
            score += points

    if re.search(r"[\w.-]+@[\w.-]+\.\w+", text):
        score += 5
    if re.search(r"\+?\d[\d\s().-]{8,}\d", text):
        score += 5
    if skills:
        score += min(10, len(skills))
    action_words = ("achieved", "improved", "reduced", "increased", "built", "led")
    if any(word in text for word in action_words):
        score += 5
    if re.search(r"\d+%|\$\d+|\d+\+", text):
        score += 5

    return _clamp_score(score)


def _invoke_llm(prompt: str) -> str:
    response = llm.invoke(prompt)
    return response.content.strip()


def parse_resume(raw_text: str) -> dict[str, Any]:
    prompt = f"""
    Parse this resume into structured JSON.
    Return ONLY valid JSON with this exact schema:
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

    response_text = _invoke_llm(prompt)
    parsed_resume = _extract_json(response_text)
    return parsed_resume or {"raw_response": response_text}


def analyze_skills(parsed_resume: dict[str, Any]) -> list[str]:
    prompt = f"""
    Extract the candidate's technical skills and soft skills from this parsed resume.
    Return ONLY a JSON array of unique skill names.

    Parsed resume:
    {json.dumps(parsed_resume)}
    """

    return _extract_json_list(_invoke_llm(prompt))


def score_ats(
    parsed_resume: dict[str, Any],
    skills: list[str],
    job_description: str | None,
) -> tuple[int, dict[str, list[str]]]:
    target_role_context = job_description or "No target job description was provided."
    prompt = f"""
    Analyze this resume for ATS compatibility.
    If a target job description is provided, include role-fit feedback.

    Return ONLY valid JSON with this schema:
    {{
      "ats_score": 0,
      "weaknesses": ["specific weakness"],
      "formatting_issues": ["specific formatting issue"],
      "recommendations": ["specific improvement"]
    }}

    Parsed resume:
    {json.dumps(parsed_resume)}

    Extracted skills:
    {skills}

    Target job description:
    {target_role_context}
    """

    result = _extract_json(_invoke_llm(prompt))
    ats_score = _clamp_score(result.get("ats_score"))
    if ats_score == 0:
        ats_score = _fallback_ats_score(parsed_resume, skills)

    feedback = {
        "weaknesses": result.get("weaknesses", []),
        "formatting_issues": result.get("formatting_issues", []),
        "recommendations": result.get("recommendations", []),
    }
    return ats_score, feedback


def recommend_jobs(
    parsed_resume: dict[str, Any],
    skills: list[str],
    job_description: str | None,
) -> list[str]:
    target_role_context = job_description or "No target job description was provided."
    prompt = f"""
    Suggest the best matching software, data, or technology roles for this candidate.
    Return ONLY a JSON array of concise role titles.

    Parsed resume:
    {json.dumps(parsed_resume)}

    Skills:
    {skills}

    Target job description:
    {target_role_context}
    """

    return _extract_json_list(_invoke_llm(prompt))


def generate_interview_questions(
    parsed_resume: dict[str, Any],
    skills: list[str],
) -> list[str]:
    prompt = f"""
    Generate interview questions tailored to this candidate's resume and skills.
    Return ONLY a JSON array of 8 concise questions.

    Parsed resume:
    {json.dumps(parsed_resume)}

    Skills:
    {skills}
    """

    return _extract_json_list(_invoke_llm(prompt))


def run_resume_analysis(
    raw_text: str,
    job_description: str | None = None,
) -> ResumeAnalysisResponse:
    cleaned_text = raw_text.strip()
    if len(cleaned_text) < 20:
        raise HTTPException(status_code=400, detail="Resume text is too short to analyze.")

    parsed_resume = parse_resume(cleaned_text)
    skills = analyze_skills(parsed_resume)
    ats_score, ats_feedback = score_ats(parsed_resume, skills, job_description)
    job_matches = recommend_jobs(parsed_resume, skills, job_description)
    interview_questions = generate_interview_questions(parsed_resume, skills)

    return ResumeAnalysisResponse(
        parsed_resume=parsed_resume,
        skills=skills,
        ats_score=ats_score,
        ats_feedback=ats_feedback,
        job_matches=job_matches,
        interview_questions=interview_questions,
    )


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "resume-analyser-api"}


@app.post("/analyze", response_model=ResumeAnalysisResponse)
def analyze_resume(payload: ResumeAnalysisRequest) -> ResumeAnalysisResponse:
    return run_resume_analysis(payload.raw_text, payload.job_description)


@app.post("/analyze-file", response_model=ResumeAnalysisResponse)
async def analyze_resume_file(
    file: UploadFile = File(...),
    job_description: str | None = Form(default=None),
) -> ResumeAnalysisResponse:
    suffix = Path(file.filename or "").suffix.lower()
    if suffix != ".pdf" or file.content_type not in {"application/pdf", "application/octet-stream"}:
        raise HTTPException(status_code=400, detail="Only PDF resume uploads are supported.")

    with tempfile.NamedTemporaryFile(delete=True, suffix=".pdf") as temp_file:
        temp_file.write(await file.read())
        temp_file.flush()
        raw_text = extract_text_from_pdf(temp_file.name)

    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from the uploaded PDF.")

    return run_resume_analysis(raw_text, job_description)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

# Resilient - The LangChain Resume Analyser

An AI-powered resume analysis platform that parses resumes, extracts skills, scores ATS readiness, suggests matching job roles, and generates tailored interview questions. The project combines a FastAPI backend, Azure OpenAI through LangChain, PDF parsing, and a modern Next.js frontend.

## Features

- Parse resumes into structured candidate profiles
- Upload PDF resumes or paste resume text directly
- Extract technical and soft skills
- Generate an ATS compatibility score from 0 to 100
- Provide ATS weaknesses, formatting issues, and improvement recommendations
- Suggest matching software, data, and technology roles
- Generate personalized interview questions
- Compare resumes against an optional target job description
- Clean responsive dashboard built with Next.js and TypeScript

## Tech Stack

**Frontend**

- Next.js
- React
- TypeScript
- Lucide React icons

**Backend**

- FastAPI
- Python
- LangChain
- Azure OpenAI
- pdfplumber
- Uvicorn / Gunicorn

**Deployment Target**

- Vercel for the Next.js frontend
- Vercel Serverless Functions for the FastAPI backend
- Azure OpenAI for LLM inference

## Project Structure

```text
.
├── app/
│   ├── main.py                  # FastAPI application and API endpoints
│   ├── models/
│   │   └── llm.py               # Azure OpenAI / LangChain client setup
│   ├── services/
│   │   └── pdf_service.py       # PDF text extraction
│   ├── agents/                  # Agent-style analysis modules
│   └── graph/                   # Workflow placeholder
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # Main dashboard UI
│   │   ├── layout.tsx
│   │   └── globals.css
│   ├── package.json
│   ├── next.config.ts
│   └── vercel.json             # Vercel frontend framework config
├── .env.example
├── frontend/.env.example
├── requirements.txt
└── ReadME.md
```

## API Endpoints

### Health Check

```http
GET /health
```

Returns service status.

### Analyze Resume Text

```http
POST /analyze
Content-Type: application/json
```

Request body:

```json
{
  "raw_text": "Resume text goes here...",
  "job_description": "Optional job description..."
}
```

### Analyze Resume File

```http
POST /analyze-file
Content-Type: multipart/form-data
```

Form fields:

- `file`: PDF resume
- `job_description`: optional target job description

### Example Response

```json
{
  "parsed_resume": {
    "name": "Aarav Mehta",
    "email": "aarav.mehta@email.com",
    "phone": "+91 98765 43210",
    "location": "Bengaluru, India",
    "summary": "Full-stack engineer...",
    "skills": [],
    "experience": [],
    "education": [],
    "projects": [],
    "certifications": [],
    "links": []
  },
  "skills": ["Python", "FastAPI", "React", "Azure"],
  "ats_score": 82,
  "ats_feedback": {
    "weaknesses": [],
    "formatting_issues": [],
    "recommendations": []
  },
  "job_matches": ["Full Stack Engineer", "Backend Engineer"],
  "interview_questions": ["Tell me about a FastAPI project you built."]
}
```

## Local Setup

### 1. Clone The Repository

```bash
git clone https://github.com/your-username/Langchain-Resume-Analyser.git
cd Langchain-Resume-Analyser
```

### 2. Create A Python Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

### 3. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Azure OpenAI

Create a `config.ini` file in the project root:

```ini
[AZURE]
AZURE_OPENAI_KEY=your-azure-openai-key
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_VERSION=your-api-version
```

Do not commit `config.ini` to GitHub because it contains secrets.

### 5. Run The Backend

```bash
uvicorn app.main:app --reload
```

The backend runs at:

```text
http://127.0.0.1:8000
```

FastAPI interactive docs:

```text
http://127.0.0.1:8000/docs
```

### 6. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 7. Run The Frontend

```bash
npm run dev
```

The frontend runs at:

```text
http://localhost:3000
```

By default, the frontend calls:

```text
http://127.0.0.1:8000
```

To use a different backend URL, set:

```bash
NEXT_PUBLIC_API_URL=https://your-backend-url
```

## Environment Variables

The backend can use a local `config.ini` file during development, but production should use environment variables.

### Backend Environment Variables

```text
AZURE_OPENAI_KEY
AZURE_OPENAI_ENDPOINT
AZURE_OPENAI_DEPLOYMENT
AZURE_OPENAI_API_VERSION
FRONTEND_ORIGINS
```

Example:

```env
AZURE_OPENAI_KEY=your-azure-openai-key
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-06-01
FRONTEND_ORIGINS=https://your-next-frontend.vercel.app
```

### Frontend Environment Variables

```text
NEXT_PUBLIC_API_URL
```

Example:

```env
NEXT_PUBLIC_API_URL=https://your-fastapi-backend.vercel.app
```

`NEXT_PUBLIC_API_URL` is baked into the frontend during build, so redeploy the frontend after changing it.

## Vercel Deployment

This project is deployed as two Vercel projects from the same repository:

```text
Vercel Project 1 -> FastAPI backend
Vercel Project 2 -> Next.js frontend
Azure OpenAI     -> LLM inference
```

The frontend calls the backend through `NEXT_PUBLIC_API_URL`.

### Deploy The FastAPI Backend On Vercel

Create a Vercel project for the backend using the repository root.

Backend project settings:

```text
Root Directory: .
Framework Preset: Other
Install Command: pip install -r requirements.txt
```

Add these environment variables to the backend Vercel project:

```text
AZURE_OPENAI_KEY=your-azure-openai-key
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-06-01
FRONTEND_ORIGINS=https://your-next-frontend.vercel.app
```

After deployment, verify the backend:

```text
https://your-fastapi-backend.vercel.app/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "resume-analyser-api"
}
```

### Deploy The Next.js Frontend On Vercel

Create a second Vercel project for the frontend using the same repository.

Frontend project settings:

```text
Root Directory: frontend
Framework Preset: Next.js
Install Command: npm install
Build Command: npm run build
Output Directory: leave empty
```

The frontend contains `frontend/vercel.json` to force Vercel to treat the app as Next.js:

```json
{
  "$schema": "https://openapi.vercel.sh/vercel.json",
  "framework": "nextjs"
}
```

Add this environment variable to the frontend Vercel project:

```text
NEXT_PUBLIC_API_URL=https://your-fastapi-backend.vercel.app
```

Do not include a trailing slash in `NEXT_PUBLIC_API_URL`.

After adding or changing `NEXT_PUBLIC_API_URL`, redeploy the frontend because Next.js embeds public environment variables during build.

### Production Request Flow

```text
User opens Next.js frontend
        ↓
Frontend sends request to NEXT_PUBLIC_API_URL/analyze
        ↓
FastAPI backend parses and analyzes resume
        ↓
LangChain calls Azure OpenAI
        ↓
Backend returns ATS score, skills, job matches, and interview questions
        ↓
Frontend renders the analysis dashboard
```

## CORS

The backend reads allowed frontend origins from `FRONTEND_ORIGINS`.

For local testing or quick debugging:

```env
FRONTEND_ORIGINS=*
```

For production:

```env
FRONTEND_ORIGINS=https://your-next-frontend.vercel.app
```

Multiple origins can be comma-separated:

```env
FRONTEND_ORIGINS=https://your-next-frontend.vercel.app,http://localhost:3000
```

## Common Issues

### Frontend Shows Network Error

Check that:

- The backend `/health` endpoint works in the browser
- The frontend Vercel project has `NEXT_PUBLIC_API_URL`
- `NEXT_PUBLIC_API_URL` starts with `https://`
- `NEXT_PUBLIC_API_URL` does not contain a trailing slash
- The frontend was redeployed after setting `NEXT_PUBLIC_API_URL`
- The backend Vercel project has `FRONTEND_ORIGINS` set correctly

If browser DevTools shows requests going to this URL, the frontend environment variable is missing:

```text
http://127.0.0.1:8000
```

### Vercel Looks For A `public` Output Directory

For the frontend project, use:

```text
Root Directory: frontend
Framework Preset: Next.js
Output Directory: leave empty
```

The frontend also includes `frontend/vercel.json` to explicitly set:

```json
{
  "framework": "nextjs"
}
```

### Backend Function Crashes

Check the backend runtime logs in Vercel. Common causes:

- Missing Azure OpenAI environment variables
- Invalid Azure OpenAI deployment name
- Invalid API version
- Backend function timeout during long LLM calls
- PDF upload larger than Vercel function limits

### File Upload Fails

Only PDF uploads are supported. The uploaded file must have a `.pdf` extension and a valid PDF content type.

## Future Improvements

- Move all secrets fully to environment variables
- Add authentication for private resume analysis
- Store analysis history in a database
- Add downloadable reports
- Add automated tests for API routes
- Containerize the backend with Docker
- Add CI/CD workflows for backend and frontend deployment

## License

This project is available for learning, portfolio, and demonstration purposes. Add a license file before using it in production or distributing it publicly.

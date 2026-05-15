# LangChain Resume Analyser

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

- Azure Static Web Apps for the frontend
- Azure App Service for the FastAPI backend
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
│   └── next.config.ts
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

### Analyze PDF Resume

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

## Environment Variables For Production

For Azure deployment, prefer environment variables instead of a local `config.ini` file:

```text
AZURE_OPENAI_KEY
AZURE_OPENAI_ENDPOINT
AZURE_OPENAI_DEPLOYMENT
AZURE_OPENAI_API_VERSION
NEXT_PUBLIC_API_URL
```

`NEXT_PUBLIC_API_URL` is used by the frontend and should point to the deployed FastAPI backend.

## Azure Deployment

This project is best deployed with two Azure services:

```text
Azure Static Web Apps  -> Next.js frontend
Azure App Service      -> FastAPI backend
Azure OpenAI           -> LLM inference
```

### Deploy Backend To Azure App Service

Create a resource group:

```bash
az group create \
  --name resume-analyser-rg \
  --location eastus
```

Create a Linux App Service plan:

```bash
az appservice plan create \
  --name resume-analyser-plan \
  --resource-group resume-analyser-rg \
  --location eastus \
  --sku B1 \
  --is-linux
```

Create the FastAPI web app:

```bash
az webapp create \
  --name resume-analyser-api \
  --resource-group resume-analyser-rg \
  --plan resume-analyser-plan \
  --runtime "PYTHON:3.12"
```

Set application settings:

```bash
az webapp config appsettings set \
  --resource-group resume-analyser-rg \
  --name resume-analyser-api \
  --settings \
    AZURE_OPENAI_KEY="your-key" \
    AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/" \
    AZURE_OPENAI_DEPLOYMENT="your-deployment-name" \
    AZURE_OPENAI_API_VERSION="your-api-version"
```

Set the startup command:

```bash
az webapp config set \
  --resource-group resume-analyser-rg \
  --name resume-analyser-api \
  --startup-file "gunicorn -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 app.main:app"
```

Deploy from the repository root:

```bash
az webapp up \
  --resource-group resume-analyser-rg \
  --name resume-analyser-api \
  --runtime "PYTHON:3.12"
```

Test the deployed backend:

```text
https://resume-analyser-api.azurewebsites.net/health
```

### Deploy Frontend To Azure Static Web Apps

Update `frontend/next.config.ts` for static export:

```ts
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export",
};

export default nextConfig;
```

Build locally:

```bash
cd frontend
npm run build
```

The static site is generated in:

```text
frontend/out
```

In Azure Static Web Apps, use these build settings:

```text
App location: frontend
API location: leave empty
Output location: out
Build command: npm run build
```

Set this variable during the Static Web Apps build:

```text
NEXT_PUBLIC_API_URL=https://resume-analyser-api.azurewebsites.net
```

## CORS

During development, the backend allows all origins. For production, replace the wildcard CORS configuration in `app/main.py` with your Static Web App URL:

```python
allow_origins=[
    "https://your-static-web-app.azurestaticapps.net",
]
```

## Common Issues

### App Service Plan Region Error

If Azure shows:

```text
Plan with requested features is not supported in current region.
```

List supported Linux App Service regions:

```bash
az appservice list-locations \
  --sku B1 \
  --linux-workers-enabled true \
  -o table
```

Then recreate the plan using one of the supported locations.

### Frontend Cannot Reach Backend

Check that:

- The backend `/health` endpoint works
- `NEXT_PUBLIC_API_URL` points to the deployed backend
- CORS allows the Azure Static Web App domain
- The backend app settings contain valid Azure OpenAI credentials

### PDF Upload Fails

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

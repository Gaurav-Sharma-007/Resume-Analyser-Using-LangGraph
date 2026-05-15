"use client";

import {
  AlertCircle,
  ArrowRight,
  BadgeCheck,
  BriefcaseBusiness,
  CheckCircle2,
  ClipboardList,
  FileText,
  Loader2,
  Moon,
  MessageSquareText,
  Sparkles,
  Sun,
  UploadCloud,
} from "lucide-react";
import { ChangeEvent, FormEvent, useEffect, useMemo, useState } from "react";

type AtsFeedback = {
  weaknesses?: string[];
  formatting_issues?: string[];
  recommendations?: string[];
};

type AnalysisResponse = {
  parsed_resume: {
    name?: string;
    email?: string;
    phone?: string;
    location?: string;
    summary?: string;
    [key: string]: unknown;
  };
  skills: string[];
  ats_score: number;
  ats_feedback: AtsFeedback;
  job_matches: string[];
  interview_questions: string[];
};

type ThemeMode = "light" | "dark";

const configuredApiUrl = process.env.NEXT_PUBLIC_API_URL?.replace(/\/+$/, "");
const apiUrl =
  configuredApiUrl || (process.env.NODE_ENV === "development" ? "http://127.0.0.1:8000" : "");

const sampleResume = `Aarav Mehta
Software Engineer
aarav.mehta@email.com | +91 98765 43210 | Bengaluru, India

Summary
Full-stack engineer with 3 years of experience building production web applications with React, Node.js, Python, FastAPI, PostgreSQL, and cloud deployments.

Experience
Software Engineer, PixelForge Labs
- Built a resume screening dashboard with React and FastAPI, reducing recruiter review time by 34%.
- Designed REST APIs, optimized PostgreSQL queries, and deployed services on Azure.
- Improved frontend performance by 28% using route-level code splitting and state cleanup.

Projects
AI Resume Analyser
- Created a LangChain-based resume parser with ATS feedback, job matching, and interview question generation.

Skills
Python, FastAPI, React, Next.js, TypeScript, PostgreSQL, Azure, LangChain, REST APIs, Docker, Git

Education
B.Tech Computer Science, 2022`;

const sampleJob = `We are hiring a full-stack software engineer with experience in React, Next.js, Python, FastAPI, REST APIs, PostgreSQL, Azure, Docker, and AI-assisted product workflows.`;

export default function Home() {
  const [resumeText, setResumeText] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [theme, setTheme] = useState<ThemeMode>("light");

  useEffect(() => {
    const savedTheme = window.localStorage.getItem("resume-analyser-theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    setTheme(savedTheme === "dark" || (!savedTheme && prefersDark) ? "dark" : "light");
  }, []);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    window.localStorage.setItem("resume-analyser-theme", theme);
  }, [theme]);

  const scoreTone = useMemo(() => {
    const score = analysis?.ats_score ?? 0;
    if (score >= 80) return "excellent";
    if (score >= 60) return "solid";
    return "needs-work";
  }, [analysis]);

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0] ?? null;
    setSelectedFile(file);
    if (file) {
      setResumeText("");
    }
  }

  function loadSample() {
    setSelectedFile(null);
    setResumeText(sampleResume);
    setJobDescription(sampleJob);
    setError("");
  }

  function toggleTheme() {
    setTheme((currentTheme) => (currentTheme === "dark" ? "light" : "dark"));
  }

  async function submitAnalysis(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setAnalysis(null);

    if (!selectedFile && resumeText.trim().length < 20) {
      setError("Add resume text or upload a PDF before running analysis.");
      return;
    }

    setIsLoading(true);
    try {
      const response = selectedFile
        ? await analyzeFile(selectedFile, jobDescription)
        : await analyzeText(resumeText, jobDescription);

      setAnalysis(response);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Analysis failed. Check the backend server and try again.",
      );
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="workspace">
      <header className="topbar">
        <div className="brand-lockup">
          <div className="brand-mark">
            <Sparkles size={18} strokeWidth={2.4} />
          </div>
          <div>
            <p className="eyebrow">LangChain Resume Analyser</p>
            <h1>Resume intelligence desk</h1>
          </div>
        </div>
        <div className="topbar-actions">
          <button
            aria-label={`Switch to ${theme === "dark" ? "light" : "dark"} mode`}
            className="theme-toggle"
            onClick={toggleTheme}
            type="button"
          >
            {theme === "dark" ? <Sun size={17} /> : <Moon size={17} />}
          </button>
          <div className="status-pill">
            <span />
            FastAPI backend
          </div>
        </div>
      </header>

      <section className="control-band">
        <form className="input-panel" onSubmit={submitAnalysis}>
          <div className="panel-heading">
            <div>
              <p className="section-label">Source</p>
              <h2>Candidate profile</h2>
            </div>
            <button type="button" className="ghost-button" onClick={loadSample}>
              <ClipboardList size={16} />
              Sample
            </button>
          </div>

          <label className="drop-zone">
            <input accept="application/pdf" type="file" onChange={handleFileChange} />
            <UploadCloud size={22} />
            <span>{selectedFile ? selectedFile.name : "Upload PDF resume"}</span>
          </label>

          <textarea
            aria-label="Resume text"
            className="resume-textarea"
            disabled={Boolean(selectedFile)}
            onChange={(event) => setResumeText(event.target.value)}
            placeholder="Paste resume text"
            value={resumeText}
          />

          <textarea
            aria-label="Job description"
            className="job-textarea"
            onChange={(event) => setJobDescription(event.target.value)}
            placeholder="Target job description"
            value={jobDescription}
          />

          {error ? (
            <div className="error-banner">
              <AlertCircle size={16} />
              {error}
            </div>
          ) : null}

          <button className="primary-button" disabled={isLoading} type="submit">
            {isLoading ? <Loader2 className="spin" size={18} /> : <Sparkles size={18} />}
            {isLoading ? "Analysing" : "Run analysis"}
            <ArrowRight size={18} />
          </button>
        </form>

        <aside className="profile-visual" aria-label="Resume preview">
          <div className={`resume-sheet ${analysis ? "analysed" : ""}`}>
            <div className="sheet-head">
              <div>
                {analysis ? (
                  <>
                    <p className="preview-label">Analysed profile</p>
                    <h3>{analysis.parsed_resume.name || "Candidate profile"}</h3>
                    <small>
                      {[analysis.parsed_resume.email, analysis.parsed_resume.location]
                        .filter(Boolean)
                        .join(" • ") || "Resume intelligence snapshot"}
                    </small>
                  </>
                ) : (
                  <>
                    <span className="line wide" />
                    <span className="line short" />
                  </>
                )}
              </div>
              <FileText size={28} />
            </div>
            {analysis ? (
              <div className="profile-snapshot">
                <div className="ats-mini-card">
                  <span>ATS score</span>
                  <strong>{analysis.ats_score}</strong>
                  <small>{scoreLabel(analysis.ats_score)}</small>
                </div>
                <div className="snapshot-summary">
                  <span>Summary</span>
                  <p>
                    {analysis.parsed_resume.summary ||
                      "The resume was parsed successfully. Review extracted skills and role fit below."}
                  </p>
                </div>
                <div className="snapshot-skills">
                  <span>Top skills</span>
                  <div>
                    {(analysis.skills.length ? analysis.skills.slice(0, 5) : ["No skills found"]).map(
                      (skill) => (
                        <em key={skill}>{skill}</em>
                      ),
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <div className="sheet-grid">
                <span />
                <span />
                <span />
                <span />
                <span />
                <span />
              </div>
            )}
            <div className="metric-strip">
              <div>
                <strong>{analysis?.skills.length ?? 0}</strong>
                <small>Skills</small>
              </div>
              <div>
                <strong>{analysis?.job_matches.length ?? 0}</strong>
                <small>Matches</small>
              </div>
              <div>
                <strong>{analysis?.interview_questions.length ?? 0}</strong>
                <small>Questions</small>
              </div>
            </div>
          </div>
        </aside>
      </section>

      <section className={`results-band ${analysis ? "has-analysis" : ""}`}>
        <ScorePanel analysis={analysis} scoreTone={scoreTone} isLoading={isLoading} />
        <IdentityPanel analysis={analysis} />
        <ListPanel
          accent="mint"
          empty="Skills will appear after analysis."
          icon={<BadgeCheck size={18} />}
          items={analysis?.skills}
          title="Skill signal"
        />
        <ListPanel
          accent="coral"
          empty="Role matches will appear after analysis."
          icon={<BriefcaseBusiness size={18} />}
          items={analysis?.job_matches}
          title="Role matches"
        />
        <FeedbackPanel feedback={analysis?.ats_feedback} />
        <ListPanel
          accent="ink"
          empty="Interview questions will appear after analysis."
          icon={<MessageSquareText size={18} />}
          items={analysis?.interview_questions}
          title="Interview kit"
          wide
        />
      </section>
    </main>
  );
}

async function analyzeText(rawText: string, jobDescription: string) {
  const response = await fetch(buildApiUrl("/analyze"), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      raw_text: rawText,
      job_description: jobDescription.trim() || null,
    }),
  });

  return parseApiResponse(response);
}

async function analyzeFile(file: File, jobDescription: string) {
  const formData = new FormData();
  formData.append("file", file);
  if (jobDescription.trim()) {
    formData.append("job_description", jobDescription.trim());
  }

  const response = await fetch(buildApiUrl("/analyze-file"), {
    method: "POST",
    body: formData,
  });

  return parseApiResponse(response);
}

function buildApiUrl(path: string) {
  if (!apiUrl) {
    throw new Error(
      "Backend API URL is missing. Set NEXT_PUBLIC_API_URL in the frontend Vercel project and redeploy.",
    );
  }

  if (!apiUrl.startsWith("https://") && process.env.NODE_ENV === "production") {
    throw new Error("Backend API URL must start with https:// in production.");
  }

  return `${apiUrl}${path}`;
}

async function parseApiResponse(response: Response): Promise<AnalysisResponse> {
  const body = await response.json().catch(() => null);
  if (!response.ok) {
    const detail = typeof body?.detail === "string" ? body.detail : "Analysis request failed.";
    throw new Error(detail);
  }
  return body as AnalysisResponse;
}

function ScorePanel({
  analysis,
  scoreTone,
  isLoading,
}: {
  analysis: AnalysisResponse | null;
  scoreTone: "excellent" | "solid" | "needs-work";
  isLoading: boolean;
}) {
  const score = analysis?.ats_score ?? 0;
  const progressStyle = {
    "--score": `${score * 3.6}deg`,
  } as React.CSSProperties;

  return (
    <article className={`score-panel ${scoreTone}`}>
      <div className="card-heading">
        <span>
          <CheckCircle2 size={18} />
        </span>
        <p>ATS score</p>
      </div>
      <div className="score-layout">
        <div className="score-ring" style={progressStyle}>
          <strong>{isLoading ? "--" : score}</strong>
          <small>/100</small>
        </div>
        <div>
          <h2>{analysis ? scoreLabel(score) : "Awaiting analysis"}</h2>
          <p>
            {analysis
              ? "Resume structure, keyword coverage, formatting, and role fit are scored together."
              : "Results sync here as soon as FastAPI returns the analysis."}
          </p>
        </div>
      </div>
    </article>
  );
}

function IdentityPanel({ analysis }: { analysis: AnalysisResponse | null }) {
  const profile = analysis?.parsed_resume;
  return (
    <article className="identity-panel">
      <div className="card-heading">
        <span>
          <FileText size={18} />
        </span>
        <p>Parsed profile</p>
      </div>
      <h2>{profile?.name || "Candidate name"}</h2>
      <div className="identity-grid">
        <span>{profile?.email || "Email"}</span>
        <span>{profile?.phone || "Phone"}</span>
        <span>{profile?.location || "Location"}</span>
      </div>
      <p className="summary-text">
        {profile?.summary || "Structured summary will appear after analysis."}
      </p>
    </article>
  );
}

function FeedbackPanel({ feedback }: { feedback?: AtsFeedback }) {
  const groups = [
    ["Weaknesses", feedback?.weaknesses],
    ["Formatting", feedback?.formatting_issues],
    ["Recommendations", feedback?.recommendations],
  ] as const;

  return (
    <article className="feedback-panel">
      <div className="card-heading">
        <span>
          <AlertCircle size={18} />
        </span>
        <p>ATS feedback</p>
      </div>
      <div className="feedback-grid">
        {groups.map(([label, items]) => (
          <div className="feedback-group" key={label}>
            <h3>{label}</h3>
            {(items?.length ? items : ["Feedback will appear after analysis."]).map((item) => (
              <p key={item}>{item}</p>
            ))}
          </div>
        ))}
      </div>
    </article>
  );
}

function ListPanel({
  accent,
  empty,
  icon,
  items,
  title,
  wide = false,
}: {
  accent: "mint" | "coral" | "ink";
  empty: string;
  icon: React.ReactNode;
  items?: string[];
  title: string;
  wide?: boolean;
}) {
  const values = items?.length ? items : [empty];

  return (
    <article className={`list-panel ${accent} ${wide ? "wide" : ""}`}>
      <div className="card-heading">
        <span>{icon}</span>
        <p>{title}</p>
      </div>
      <div className="chip-list">
        {values.map((item) => (
          <span key={item}>{item}</span>
        ))}
      </div>
    </article>
  );
}

function scoreLabel(score: number) {
  if (score >= 80) return "Strong fit";
  if (score >= 60) return "Competitive";
  return "Needs refinement";
}

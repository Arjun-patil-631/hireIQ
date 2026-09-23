# Screenshot Capture Guide — HireIQ

> Reference guide for documenting submission evidence with exact recommended viewports, actions, and key visual elements.

Recommended capture resolution: **1920×1080** or **1366×768** desktop viewport.

---

## 1. Hiring Manager Dashboard Overview
- **File destination:** `submission_assets/dashboard.png`
- **URL:** `http://localhost:5173/`
- **What to capture:**
  - Navigation bar with HireIQ brand mark.
  - KPI metric cards: Total Candidates (3+), Completed Interviews (3+), Average Score, Decision Mix (Proceed / Hold / Reject).
  - Paginated candidate evaluations table with avatars, latest scores, and recommendation status badges.
  - Candidate Skill Dimension Comparison table displaying cross-candidate scores across Technical, Problem Solving, Communication, and Confidence.
  - "Start demo interview" button.

---

## 2. Cross-Candidate Comparison Matrix
- **File destination:** `submission_assets/candidate_comparison.png`
- **URL:** `http://localhost:5173/` (scroll to Comparison section)
- **What to capture:**
  - Side-by-side comparison table showing candidates (e.g., Priya Rao, Rohan Mehta, Meera Iyer).
  - Numerical breakdown across Technical Knowledge, Problem Solving, Communication, and Confidence heuristics.
  - Recommendation status pills ("Proceed", "Hold", "Reject").
  - Direct "View" links to completed session evaluation reports.

---

## 3. Candidate Interview Recording Experience
- **File destination:** `submission_assets/interview_recording.png`
- **URL:** `http://localhost:5173/interview/<session_id>`
- **What to capture:**
  - Header showing candidate name, session title, and question progress chip (e.g., `1 / 5`).
  - Active question prompt card (e.g., "Explain the difference between a process and a thread...").
  - Live recording state with active timer (e.g., `00:18`).
  - Pulsing circular "Stop recording" button.
  - Sidebar showing the multi-step session progress pipeline and the Evidence-First Ethics badge.

---

## 4. Audio Playback Preview & Re-Record Controls
- **File destination:** `submission_assets/audio_preview.png`
- **URL:** `http://localhost:5173/interview/<session_id>` (after clicking stop recording)
- **What to capture:**
  - HTML5 audio waveform/playback player displaying the captured candidate audio.
  - "Re-record" retry button alongside "Submit & evaluate" button.
  - Answer captured duration indicator.

---

## 5. Asynchronous Processing Pipeline State
- **File destination:** `submission_assets/processing_state.png`
- **URL:** `http://localhost:5173/interview/<session_id>` (immediately after clicking Submit)
- **What to capture:**
  - Animated spinner and active status banner:
    `"AI evaluation in progress — Audio queued — Whisper + NLP + LLM evaluation running…"`
  - Background task status indicator representing Celery / Whisper / NLP queue pipeline.

---

## 6. Comprehensive Evaluation Report Page
- **File destination:** `submission_assets/evaluation_report.png`
- **URL:** `http://localhost:5173/report/<session_id>`
- **What to capture:**
  - Candidate profile header with overall score ring (e.g., `81/100`) and recommendation badge ("Proceed").
  - Horizontal skill dimension progress bars (Technical, Problem Solving, Communication, Confidence).
  - "Download PDF" primary action button.
  - Question-by-question breakdown showing verbatim transcript, extracted strengths, improvements, and NLP context strip (VADER sentiment, keywords, confidence score).
  - Review Guidance sidebar highlighting human review requirements and anti-bias principles.

---

## 7. Generated PDF Evaluation Report
- **File destination:** `submission_assets/sample_report.pdf` (preview screenshot in `submission_assets/pdf_preview.png`)
- **Location:** `runtime/reports/hireiq_<session_id>.pdf` or downloaded from `/api/v1/reports/<session_id>.pdf`
- **What to capture:**
  - Page 1: Header summary table, ReportLab Matplotlib 4-axis Polar Skill Radar Chart.
  - Page 2: Per-question score tables, verbatim speech transcripts, strengths, improvements, and AI Ethics disclaimer note.

---

## 8. YAML Rubric Editor & Question Bank Management
- **File destination:** `submission_assets/rubric_editor.png`
- **URL:** `http://localhost:5173/rubrics`
- **What to capture:**
  - Dropdown toggle between `technical.yaml` and `behavioral.yaml`.
  - Live YAML textarea editor with syntax validation and "Save & validate" button.
  - Question Bank CRUD manager showing list of interview prompts with categories and delete buttons.
  - "New question prompt" input form with category selector.

---

## 9. Candidate Profile & Session History
- **File destination:** `submission_assets/candidate_profile.png`
- **URL:** `http://localhost:5173/candidate/<candidate_id>`
- **What to capture:**
  - Candidate banner with avatar, email, latest score, and overall decision.
  - Table of all interview sessions completed by this candidate with direct report links.

---

## 10. System Architecture Diagram
- **File destination:** `submission_assets/architecture_diagram.png`
- **Source:** `docs/architecture.svg`
- **What to capture:**
  - Full vector architecture diagram illustrating the React browser client, FastAPI gateway, Redis message broker, Celery workers, PyDub audio normalization, Whisper ASR, spaCy + VADER NLP enrichment, Gemini LLM evaluation engine, Pydantic validation gate, PostgreSQL database, and ReportLab PDF generator.

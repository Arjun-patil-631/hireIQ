# HireIQ 5-Minute Video Demonstration Script & Runbook

> Project: HireIQ — Multimodal AI Interview Intelligence Platform  
> Target Duration: 5:00 minutes  
> Audience: Code A Nova Internship Evaluators & Technical Reviewers  

---

## Preparation Checklist Before Recording
1. Start the backend: `python -m uvicorn app.main:app --port 8000` (in `backend/`).
2. Start the frontend: `npm run dev` (in `frontend/`, opens on `http://localhost:5173`).
3. Seed synthetic demo data if not already present: `python scripts/seed_demo.py`.
4. Ensure microphone permissions are granted in the browser.
5. Have `docs/architecture.svg` open in a browser tab.

---

## Video Timeline & Spoken Script

### 0:00 – 0:35 • Project Introduction & Problem Statement
- **Screen:** Show HireIQ Landing / Hiring Manager Dashboard (`http://localhost:5173`).
- **Voiceover:**
  > *"Hello! I am Arjun Patil, presenting my Code A Nova Internship 2026 Project 4: **HireIQ — Multimodal AI Interview Intelligence Platform**.*
  >
  > *Traditional technical interviews suffer from subjective human bias, inconsistent evaluation criteria, and zero auditable evidence trails. Candidates are often judged on accent, charisma, or superficial rapport rather than demonstrated technical competence.*
  >
  > *HireIQ addresses this by transforming candidate spoken responses into a rigorous, evidence-grounded evaluation pipeline. It combines browser-based audio capture, asynchronous Whisper transcription, NLP enrichment with spaCy and VADER, structured LLM evaluation against configurable YAML rubrics, and automated executive PDF report generation."*

---

### 0:35 – 1:15 • System Architecture Walkthrough
- **Screen:** Switch to `docs/architecture.svg` in browser tab.
- **Voiceover:**
  > *"Let's examine the end-to-end architecture:*
  >
  > *On the frontend, we use React 18, TypeScript, and Vite with the native MediaRecorder API for real-time microphone capture. Audio is streamed to a FastAPI backend.*
  >
  > *To ensure high-throughput and prevent blocking HTTP requests during intensive AI tasks, long-running transcription is offloaded asynchronously to Celery workers backed by a Redis message broker.*
  >
  > *In the worker pipeline, PyDub normalizes audio to mono 16 kHz WAV format. OpenAI Whisper transcribes speech into text. spaCy and VADER extract keywords, entities, and sentiment polarity. The transcript and NLP signals are then evaluated by Google Gemini against our active YAML rubric. Crucially, all LLM outputs pass through strict Pydantic validation before database storage in PostgreSQL, and all temporary audio files are immediately purged for privacy.*
  >
  > *Finally, ReportLab dynamically renders an executive evaluation PDF complete with a polar skill radar chart."*

---

### 1:15 – 2:30 • Live Candidate Interview Experience
- **Screen:** Return to browser, click **"Start demo interview"**, enter Candidate Name (e.g., *"Alex Sharma"*), email (`alex@example.com`), and launch session.
- **Voiceover:**
  > *"Let's experience what a candidate sees. The session opens with structured question prompts delivered one by one.*
  >
  > *Here is Question 1: 'Explain the difference between a process and a thread, and when you would prefer one over the other.'*
  >
  > *Notice our professional UI: elapsed recording timer, audio quality tips, and a session flow panel that tracks progress while reminding candidates of our evidence-first, non-discriminatory policy.*
  >
  > *(Click 'Start recording')*
  >
  > *'A process has its own dedicated address space and memory isolation, whereas threads exist within a process and share its memory and resources. I would choose threads for lightweight concurrent tasks that require high-speed inter-thread communication, and separate processes when strong fault isolation and security boundaries are required.'*
  >
  > *(Click 'Stop recording')*
  >
  > *Notice that we immediately provide an audio playback preview player and a 'Re-record' option if the candidate wishes to retry.*
  >
  > *(Click 'Submit & evaluate')*
  >
  > *The audio is uploaded, and the UI displays an active processing indicator while the asynchronous Celery pipeline normalizes, transcribes, and evaluates the response in the background."*

---

### 2:30 – 3:30 • Hiring Manager Dashboard & Candidate Comparison
- **Screen:** Navigate back to Dashboard (`/`).
- **Voiceover:**
  > *"Now switching to the Hiring Manager Dashboard:*
  >
  > *At the top, managers have immediate visibility into total candidates, completed interviews, average platform score, and decision distribution across Proceed, Hold, and Reject.*
  >
  > *Below is our paginated candidate directory with score rings and recommendation badges. Notice we do not run unbounded database queries.*
  >
  > *Furthermore, we built a dedicated **Candidate Skill Dimension Comparison** table. This allows hiring committees to compare candidates side-by-side across all four core competencies: Technical Knowledge, Problem Solving, Communication, and Confidence heuristics."*

---

### 3:30 – 4:15 • Evaluation Report & PDF Generation
- **Screen:** Click **"View"** on a completed candidate evaluation (e.g., *Priya Rao* or *Alex Sharma*).
- **Voiceover:**
  > *"Opening the full evaluation report:*
  >
  > *Here we see the composite overall score (81/100) and the Proceed recommendation. Below, each skill dimension is visualized with progress metrics.*
  >
  > *Scrolling through the question breakdown, managers can inspect the exact Whisper transcript, extracted strengths, concrete areas for improvement, sentiment polarity, keywords, and the linguistic confidence heuristic.*
  >
  > *Now let's click **'Download PDF'**.*
  >
  > *(Open downloaded PDF)*
  >
  > *The ReportLab engine generates a professional executive dossier. It features a polar 4-axis skill radar chart on page one, followed by question-by-question evidence, verbatim transcripts, and an explicit AI Ethics & Limitations notice on page two—completely independent of headless Chrome."*

---

### 4:15 – 4:45 • YAML Rubric Configuration & Question Bank
- **Screen:** Navigate to Rubrics page (`/rubrics`).
- **Voiceover:**
  > *"Under the Rubrics section, evaluation rules are completely decoupled from code. Recruiter teams can toggle between technical and behavioral rubrics, adjust criteria weights, modify scoring level definitions, and validate YAML changes in real time.*
  >
  > *Below the rubric editor, managers can manage the Question Bank—adding new prompts, assigning question types, and deleting questions directly through our REST API."*

---

### 4:45 – 5:00 • AI Ethics, Security & Conclusion
- **Screen:** Open `docs/BIAS_REVIEW.md` or show the Dashboard summary.
- **Voiceover:**
  > *"In summary, HireIQ satisfies all non-negotiable requirements:*
  > - *LLM API keys remain server-side only;*
  > - *Whisper transcribes asynchronously via Celery and Redis;*
  > - *Pydantic gates all database persistence;*
  > - *Candidate audio is strictly ephemeral and deleted after processing;*
  > - *Evaluation prompts explicitly forbid scoring accent, age, gender, or demographics;*
  > - *Full pytest, frontend typecheck, and docker compose configurations pass.*
  >
  > *Thank you for reviewing HireIQ!"*

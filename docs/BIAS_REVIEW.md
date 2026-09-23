# AI Bias Review & Ethics Documentation — HireIQ

> Multimodal AI Interview Intelligence Platform • Code A Nova Internship 2026

---

## 1. Overview & Ethical Philosophy

HireIQ is designed as an **AI-assisted decision-support system** for technical recruiters and hiring managers. It does **not** make automated hiring decisions, nor does it issue binding pass/fail verdicts. In accordance with ethical AI design principles and international employment equity standards (e.g., EEOC Uniform Guidelines on Employee Selection Procedures, EU AI Act High-Risk AI System Guidelines), all recommendations ("Proceed", "Hold", "Reject") are probabilistic indicators grounded strictly in observable, job-relevant technical evidence.

---

## 2. Identified Bias Vectors & Technical Mitigations

### 2.1 Accent & Dialect Bias
- **Risk:** Automatic Speech Recognition (ASR) engines historically demonstrate divergent Word Error Rates (WER) across regional dialects, non-native English speakers, and sociolects. Lower acoustic fidelity or phonetic variation could misrepresent candidate fluency or articulation.
- **Mitigation:**
  - Whisper transcription output is treated purely as a semantic transcript, not an acoustic evaluation.
  - The evaluation system prompt explicitly instructs the LLM:
    > *"Never score, infer, or mention accent, dialect, or speech style unless the configured rubric explicitly and job-relevantly evaluates communication clarity. Never treat accent as a competence signal."*
  - Reviewers can view the verbatim transcript and inspect question-level evidence directly.

### 2.2 Language Fluency vs. Technical Competence
- **Risk:** Non-native English speakers may express technically accurate concepts with simpler vocabulary or occasional syntactic irregularities. Standard LLMs can inadvertently conflate lexical variety with domain expertise.
- **Mitigation:**
  - Rubric criteria evaluate conceptual correctness, problem-solving structure, and algorithmic complexity rather than grammatical polish.
  - Brevity is not penalized if the required technical substance (e.g., process vs. thread isolation, Big-O analysis) is present.

### 2.3 Verbosity & "Hallucinated Confidence" Bias
- **Risk:** LLMs frequently exhibit verbosity bias—rewarding long, elaborate answers that contain superficial fluff over concise, mathematically rigorous answers.
- **Mitigation:**
  - Rubric guidelines provide concrete scoring levels for *Excellent*, *Good*, and *Needs Improvement*.
  - Prompt instructions require evidence-based rationales and penalize ungrounded fluff.

### 2.4 Demographic & Protected Class Inference
- **Risk:** Demographic proxies (such as candidate name, age indicators, school graduation dates, or background noise) could trigger implicit LLM bias.
- **Mitigation:**
  - Candidate names and emails are stripped from the prompt payload sent to the LLM evaluator (`evaluate_answer` only receives question, transcript, and NLP signals).
  - Explicit system prompt prohibition:
    > *"Never score, infer, or mention demographic traits such as race, ethnicity, nationality, religion, gender, age, disability, health status, socioeconomic background, appearance, or name."*

### 2.5 Confidence Heuristic Transparency
- **Risk:** Claiming to detect "candidate psychological confidence" from audio or text is scientifically dubious, unvalidated, and prone to demographic stereotyping (e.g., gendered communication norms, neurodivergent speech patterns).
- **Mitigation:**
  - The platform explicitly documents confidence as an **empirical linguistic heuristic** (measuring filler token frequency and sentence coherence), not psychological truth or emotional state.
  - Disclaimers on the dashboard and generated PDF state:
    > *"Confidence and sentiment are supplementary signals and must not dominate competence scoring or be used as proxies for protected traits."*

### 2.6 Sentiment Analysis Limitations
- **Risk:** Tone of voice, dry delivery, or serious technical discussions may register neutral or negative sentiment in VADER sentiment lexicons.
- **Mitigation:**
  - VADER sentiment compound scores are displayed solely as auxiliary context and have **zero direct weight** in the final rubric score calculation.

### 2.7 Transcription Errors & Hallucination
- **Risk:** Whisper may mishear specialized libraries or acronyms (e.g., "PostgreSQL" as "post gray sequel", "OAuth" as "o off"), leading to downstream scoring penalties.
- **Mitigation:**
  - The evaluator prompt instructs the model to distinguish minor transcription phonetics from conceptual errors.
  - Human review requirement: managers must review transcripts before making any employment decision.

---

## 3. Architectural Safeguards

1. **Deterministic Score Normalization:**
   - LLMs are not permitted to arbitrarily assign overall scores. Overall scores are computed through deterministic weighted summation of rubric criteria weights defined in YAML.
2. **Schema Validation Gate (Pydantic):**
   - Every LLM response is strictly parsed and validated using Pydantic (`EvaluationResult`). Malformed or out-of-bounds payloads are rejected before database persistence.
3. **Data Privacy & Ephemeral Audio:**
   - Candidate audio files are retained only in temporary scratch storage during processing and are permanently deleted after normalization and transcription.
   - Candidate transcripts are never logged to production stdout or exposed in public error logs.
4. **Auditability & Explainability:**
   - Every evaluation produces structured `strengths`, `improvements`, and a grounded `rationale` citing specific transcript evidence.

---

## 4. Human-in-the-Loop Requirement

HireIQ is **strictly decision support**. An employer using this software must adhere to the following operational standards:
- All AI recommendations ("Proceed", "Hold", "Reject") must be verified by a qualified human interviewer.
- Candidates who encounter transcription failure or acoustic anomalies must be offered an opportunity to re-record or submit a written clarification.
- Routine algorithmic audits should be conducted by comparing score distributions across demographic subgroups to detect disparate impact.

---
name: AI Resume Builder Plan
overview: A phased AI engineering plan to extend your existing Gradio + LlamaIndex + pgvector scaffold into a pipeline that ingests resume/skills.md, discovers jobs via search API, tailors resumes with RAG-grounded LLM generation, scores fit confidence, and auto-applies via Playwright when score exceeds threshold.
todos:
  - id: phase-0-foundation
    content: "Fix scaffold: DATABASE_URL, Ollama wiring, Dockerfile, embedding smoke test"
    status: in_progress
  - id: phase-1-profile
    content: Build parsers + RAG ingest with metadata + LLM structured Profile extraction
    status: pending
  - id: phase-2-jobs
    content: Tavily/SerpAPI job search, JD fetch, JobListing storage + embedding
    status: pending
  - id: phase-3-scoring
    content: Hybrid confidence scorer (semantic + skill overlap + LLM rubric + blockers)
    status: pending
  - id: phase-4-tailor
    content: RAG-grounded resume/cover letter generation with hallucination validation
    status: pending
  - id: phase-5-apply
    content: Playwright auto-apply agent gated by confidence threshold + safety rails
    status: pending
  - id: phase-6-orchestrate
    content: Pipeline orchestrator + Gradio dashboard tabs
    status: pending
  - id: phase-7-eval
    content: Build eval set and log LLM calls before scaling real applications
    status: pending
isProject: false
---

# AI Resume Builder — Project Plan

Save this as `[PROJECT_PLAN.md](PROJECT_PLAN.md)` at repo root when implementing.

## Goal

End-to-end agentic pipeline:

```mermaid
flowchart LR
    upload[Upload resume + skills.md] --> ingest[RAG ingest]
    ingest --> profile[Structured profile]
    profile --> search[Search API job discovery]
    search --> score[Confidence scoring]
    score -->|score >= threshold| tailor[LLM resume tailor]
    score -->|score < threshold| skip[Skip / log]
    tailor --> apply[Playwright auto-apply]
    apply --> log[Application log]
```



**Your stack (already started):** Python 3.13, Gradio, LlamaIndex, pgvector, Ollama (local LLM + embeddings).

**New additions:** Tavily or SerpAPI (job search), Playwright (form automation), Pydantic (schemas), SQLite/Postgres (application state).

---

## Phase 0 — Fix foundation (1–2 days)

Before AI work, make the scaffold runnable.


| Task                                                                                  | File(s)     | Why                          |
| ------------------------------------------------------------------------------------- | ----------- | ---------------------------- |
| Add `DATABASE_URL` to `[.env.example](.env.example)`                                  | `.env`      | pgvector connection          |
| Fix typo `breakpoiint` → `breakpoint` in `[app/rag/pipeline.py](app/rag/pipeline.py)` | pipeline.py | ingestion bug                |
| Wire `OllamaEmbedding` properly (not string)                                          | pipeline.py | embeddings must actually run |
| Add Ollama to `[docker-compose.yml](docker-compose.yml)` or document host Ollama      | compose     | LLM dependency               |
| Fix Dockerfile / add missing `install.py`                                             | Dockerfile  | container builds             |
| Add `README.md` with local run steps                                                  | README      | your learning log            |


**AI concept:** embeddings only work if the embed model is reachable and chunks land in the vector store. Validate with a smoke test: ingest `skills.md`, query "Python experience", get relevant chunks.

---

## Phase 1 — Document ingestion & structured profile (3–4 days)

### 1.1 Parse uploads

```
app/
  parsers/
    resume.py      # PDF/DOCX → text (pypdf / python-docx)
    skills.py      # skills.md → list[str] + categories
  models/
    profile.py     # Pydantic: Profile, Experience, Skill
```

- Distinguish file types on upload in `[app/main.py](app/main.py)`: resume vs `skills.md`.
- **Do not** rely on LLM for initial parsing — use deterministic extractors first; LLM only for messy PDFs.

### 1.2 RAG ingest (extend existing pipeline)

- Tag chunks with metadata: `source=resume|skills`, `section=experience|education|skill`.
- Store in pgvector via existing `[app/rag/pipeline.py](app/rag/pipeline.py)`.
- Chunk strategy: semantic split for resume narrative; whole-line or small chunks for skills.

### 1.3 Structured profile extraction (LLM + schema)

**AI pattern:** structured output / JSON mode.

```python
# Prompt: extract ONLY facts present in documents. Return Profile schema.
# Use Ollama with response_format or LlamaIndex Pydantic program.
```

- Merge parser output + LLM extraction into a canonical `Profile` object.
- Persist to DB table `profiles` (single-user learning project = one row).

**Learning focus:** grounding — every profile field must trace to source text; reject hallucinated skills.

---

## Phase 2 — Job discovery via Search API (2–3 days)

### 2.1 Search module

```
app/
  jobs/
    search.py      # Tavily/SerpAPI client
    parser.py      # LLM extracts JobListing from raw HTML/snippets
    models.py      # JobListing(title, company, url, description, requirements)
```

**Query construction (LLM or template):**

```
"{job_title} {top_3_skills} remote jobs site:greenhouse.io OR site:lever.co OR site:jobs.ashbyhq.com"
```

- Prefer ATS-hosted pages (Greenhouse, Lever, Ashby) — easier to automate than LinkedIn.
- Store results in `job_listings` table; dedupe by URL.

### 2.2 Job page fetch

- Fetch full JD text from URL (httpx + readability or trafilatura).
- Embed JD description; store in pgvector with `source=job`, `job_id`.

**AI concept:** same embedding space lets you compare profile chunks ↔ job chunks via cosine similarity later.

---

## Phase 3 — Confidence scoring (3–4 days)

**This gates auto-apply.** Score 0.0–1.0 per job; apply only when `score >= THRESHOLD` (start at 0.75, tune empirically).

### 3.1 Hybrid scorer (don't use LLM alone)

```
final_score = 0.4 * semantic_match
            + 0.3 * skill_overlap
            + 0.2 * llm_rubric
            + 0.1 * rule_penalties
```


| Signal             | Method                                                                               |
| ------------------ | ------------------------------------------------------------------------------------ |
| **semantic_match** | Max cosine sim between profile embeddings and JD embeddings (top-k avg)              |
| **skill_overlap**  | `                                                                                    |
| **llm_rubric**     | Prompt: rate fit 1–5 on experience level, domain, must-have skills; normalize to 0–1 |
| **rule_penalties** | Hard disqualifiers: wrong seniority, missing required cert, wrong country/visa       |


```
app/
  scoring/
    scorer.py
    rubric.py      # LLM prompt template
```

### 3.2 Output

```python
class FitAssessment(BaseModel):
    job_id: str
    score: float
    semantic_match: float
    skill_overlap: float
    llm_rubric: float
    reasons: list[str]      # human-readable
    blockers: list[str]     # why NOT to apply
    recommend_apply: bool   # score >= threshold AND no blockers
```

**Learning focus:** hybrid scoring beats pure LLM judgment — cheaper, more explainable, fewer false positives.

---

## Phase 4 — Resume customization (3–4 days)

### 4.1 RAG-grounded tailoring

**AI pattern:** retrieval-augmented generation with constraints.

```
app/
  tailor/
    generator.py
    templates/           # Jinja2 or markdown resume template
```

**Per job workflow:**

1. Retrieve top-k profile chunks relevant to JD (vector query: JD title + requirements).
2. LLM prompt:
  - Input: base profile JSON + JD + retrieved chunks
  - Task: rewrite bullet points to mirror JD keywords **without inventing experience**
  - Output: `TailoredResume` schema (sections, bullets with `source_chunk_id`)
3. Render to PDF (weasyprint or reportlab) or DOCX.

### 4.2 Cover letter (short)

- Same RAG context; 3-paragraph template; max 250 words.
- Store alongside tailored resume in `applications` table.

**Guardrails:**

- Post-generation validation: every bullet must map to a source chunk (string overlap or embedding sim > 0.85).
- Reject and retry if validation fails.

---

## Phase 5 — Auto-apply with Playwright (4–5 days)

**Only jobs where `recommend_apply == True`.**

```
app/
  apply/
    agent.py           # orchestrator
    ats/
      greenhouse.py    # site-specific selectors
      lever.py
      generic.py       # fallback form filler
    browser.py         # Playwright session mgmt
```

### 5.1 Agent loop (observe → act)

```mermaid
sequenceDiagram
    participant Agent
    participant Browser
    participant LLM
    Agent->>Browser: navigate job_url
    Browser-->>Agent: page snapshot / accessibility tree
    Agent->>LLM: which fields to fill + values
    LLM-->>Agent: FormFillPlan
    Agent->>Browser: fill fields, upload resume PDF
    Agent->>Browser: screenshot before submit
    Agent->>LLM: confirm ready to submit
    Agent->>Browser: click Submit
    Agent->>Agent: log result
```



**AI pattern:** LLM as planner over structured page state — not pixel-clicking. Feed accessibility tree or simplified DOM, not screenshots (cheaper, more reliable for learning).

### 5.2 Safety rails

- **Never** auto-submit without: confidence pass + resume validation pass + pre-submit screenshot saved.
- Rate limit: max N applications/day.
- Skip: login walls, CAPTCHA, LinkedIn Easy Apply (blocked/fragile).
- On failure: save state, mark `status=needs_manual_review`.

### 5.3 Legal/ethical note

Many ToS prohibit bots. For learning: target your own test forms + public ATS demo pages first; use real applications only on sites that permit it and with your explicit review of the pre-submit screenshot.

---

## Phase 6 — Orchestration & UI (2–3 days)

### 6.1 Pipeline runner

```
app/
  orchestrator.py    # single entry: run_pipeline(profile, search_query)
```

Steps: search → dedupe → score all → filter → tailor top N → apply top M.

Run as CLI first; wire to Gradio later.

### 6.2 Gradio dashboard (upgrade `[app/main.py](app/main.py)`)

Tabs: Upload | Job Results | Scores | Applications | Logs.

Show: score breakdown, tailored resume preview, apply status, screenshots.

---

## Phase 7 — Evaluation & iteration (ongoing)

Build a small eval set **before** scaling applications:


| Test                | Pass criteria                                 |
| ------------------- | --------------------------------------------- |
| Profile extraction  | 95% of skills in source appear in Profile     |
| Scoring calibration | Known-good JD scores > 0.8; known-bad < 0.5   |
| Tailoring fidelity  | Zero invented employers/titles on 10 test JDs |
| Apply success       | 3/3 test ATS forms filled correctly           |


Log every LLM call (prompt, response, tokens) to `logs/` for debugging.

---

## Suggested file layout (final)

```
app/
  main.py
  orchestrator.py
  models/          # Pydantic schemas
  parsers/         # resume, skills
  rag/             # ingest + query engine
  jobs/            # search, fetch, parse
  scoring/         # hybrid fit scorer
  tailor/          # RAG resume + cover letter
  apply/           # Playwright agents per ATS
  db/              # SQLAlchemy models + migrations
  config.py        # THRESHOLD, API keys, model names
```

---

## Dependencies to add

```
tavily-python OR google-search-results   # search API
playwright                                # browser automation
pydantic>=2
httpx
trafilatura                               # JD text extraction
jinja2                                    # resume template
pypdf / python-docx                       # resume parsing
sqlalchemy                                # application state
```

---

## Implementation order (your learning path)

1. **Phase 0** — runnable ingest + query smoke test
2. **Phase 1** — structured profile from your real resume + skills.md
3. **Phase 3** — scoring (can test with hand-pasted JD URLs before search)
4. **Phase 4** — tailored resume output (highest AI value, no browser risk)
5. **Phase 2** — search API integration
6. **Phase 5** — Playwright on test forms, then real ATS
7. **Phase 6–7** — UI + eval loop

---

## Key AI engineering concepts you'll practice

- **Embeddings + vector retrieval** — semantic match between you and JDs
- **Structured LLM output** — Pydantic schemas, no free-form parsing
- **RAG grounding** — tailor resume from retrieved chunks, not model memory
- **Hybrid scoring** — embeddings + rules + LLM rubric (agent decision gate)
- **Constrained generation** — post-hoc validation against source docs
- **LLM-as-planner** — Playwright agent reads page state, plans form fills
- **Eval before scale** — measure hallucination rate and false apply rate

---

## Environment variables (add to `.env.example`)

```
DATABASE_URL=postgresql://user:pass@localhost:6024/db
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.2
OLLAMA_EMBED_MODEL=nomic-embed-text
TAVILY_API_KEY=
CONFIDENCE_THRESHOLD=0.75
MAX_APPLICATIONS_PER_DAY=5
```


# 🏥 Plum OPD Claim Adjudication Engine

> An AI-powered, end-to-end OPD insurance claim submission and automated adjudication system built for the Plum intern assignment.

## 🚀 Live Demo

🌐 **Frontend:** https://plum-opd-claim-adjudication-web.vercel.app  
⚙️ **Backend API:** https://plum-claims-backend-b52y.onrender.com/

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-black?style=flat&logo=next.js)](https://nextjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?style=flat&logo=postgresql)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker)](https://docker.com)

---

## 📖 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Features](#features)
4. [Tech Stack](#tech-stack)
5. [Project Structure](#project-structure)
6. [Quick Start (Local)](#quick-start-local)
   - [Option A: Docker Compose (Recommended)](#option-a-docker-compose-recommended)
   - [Option B: Manual Setup](#option-b-manual-setup)
7. [Environment Variables](#environment-variables)
8. [API Reference](#api-reference)
9. [Adjudication Pipeline](#adjudication-pipeline)
   - [Rule Engine](#rule-engine)
   - [AI / LLM Layer](#ai--llm-layer)
   - [Decision Outcomes](#decision-outcomes)
10. [Policy Terms](#policy-terms)
11. [Frontend UI](#frontend-ui)
12. [Running Test Cases](#running-test-cases)
13. [Cloud Deployment](#cloud-deployment)
14. [Database Schema](#database-schema)
15. [Member Registry](#member-registry)

---

## Project Overview

This system automates the process of submitting and adjudicating **Out-Patient Department (OPD)** insurance claims under the **Plum OPD Advantage** policy (`PLUM_OPD_2024`). 

A claimant submits their member details, treatment information, and document uploads (prescription + bill). The system then runs a deterministic rule engine followed by an optional AI layer (Google Gemini via the OpenAI-compatible API) to produce one of four decisions:

| Decision | Meaning |
|---|---|
| `APPROVED` | Claim meets all policy rules; reimbursement issued |
| `REJECTED` | One or more hard rules failed |
| `PARTIAL` | Approved minus excluded items (e.g., cosmetic line items) |
| `MANUAL_REVIEW` | Flagged for human review (fraud indicators or low confidence) |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (Next.js 15)               │
│   Submission Form  ──►  Status Polling  ──►  Decision View  │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP (REST)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Backend API (FastAPI + Python 3.12)        │
│                                                             │
│  POST /api/v1/claims  ──►  Claim Record Created             │
│         │                                                   │
│         ▼                                                   │
│  ┌──────────────────────────────────────────────────┐      │
│  │           Adjudication Pipeline                   │      │
│  │                                                   │      │
│  │  1. OCR (Tesseract / PyMuPDF)                     │      │
│  │         │                                         │      │
│  │         ▼                                         │      │
│  │  2. LLM Field Extraction (Gemini 2.5 Flash)       │      │
│  │     ─ or ─ Heuristic fallback (no API key)        │      │
│  │         │                                         │      │
│  │         ▼                                         │      │
│  │  3. Deterministic Rule Engine (8 rules)           │      │
│  │         │                                         │      │
│  │         ▼                                         │      │
│  │  4. LLM Adjudication Reasoning (Gemini)           │      │
│  │     ─ validates medical necessity & exclusions    │      │
│  │         │                                         │      │
│  │         ▼                                         │      │
│  │  5. Decision persisted to DB                      │      │
│  └──────────────────────────────────────────────────┘      │
│                                                             │
│  GET /api/v1/claims/{id}  ──►  ClaimStatus + Decision       │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│            PostgreSQL 16 + pgvector                         │
│  ┌─────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │ claims  │  │ extracted_fields │  │    decisions     │   │
│  └─────────┘  └──────────────────┘  └──────────────────┘   │
│  ┌───────────────────────┐                                  │
│  │   policy_embeddings   │  (pgvector RAG — optional)       │
│  └───────────────────────┘                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Features

### Backend
- ✅ **Claim Submission API** — multipart form with file uploads (PDF, JPG, PNG, WEBP, TIFF)
- ✅ **OCR Pipeline** — Tesseract + PyMuPDF for document text extraction
- ✅ **LLM Field Extraction** — Gemini 2.5 Flash extracts structured fields (doctor name, reg number, diagnosis, bill line items) from raw OCR text
- ✅ **Heuristic Fallback** — regex-based extraction when no API key is configured
- ✅ **Deterministic Rule Engine** — 8 ordered rules covering duplicates, minimums, documents, doctor registration, waiting periods, exclusions, pre-auth, and fraud
- ✅ **LLM Adjudication Layer** — AI reviews medical necessity and policy exclusions; can escalate rule-engine decisions
- ✅ **Duplicate Bill Detection** — MD5 hashing of bill files/data; cross-claim de-duplication
- ✅ **pgvector RAG** — policy chunks embedded and stored; semantically retrieved to ground AI reasoning
- ✅ **Policy-driven Calculations** — co-pay, network discounts, per-claim limits, cosmetic deductions
- ✅ **4 Decision Types** — `APPROVED`, `REJECTED`, `PARTIAL`, `MANUAL_REVIEW`
- ✅ **Structured_documents mode** — bypass OCR in tests by passing raw JSON claim data
- ✅ **Swagger / ReDoc** — interactive API docs at `/docs`

### Frontend
- ✅ **Claim Submission Form** — member details, dates, amounts, drag-and-drop file upload
- ✅ **Load Example Buttons** — prefill form with approved or rejection test scenarios
- ✅ **Status Page** — auto-polls until claim reaches `COMPLETED` or `MANUAL_REVIEW`
- ✅ **Decision Summary** — approved amount, co-pay deductions, rejection codes, AI notes
- ✅ **Responsive Design** — works on desktop and mobile

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15, React 19, TypeScript, TanStack Query v5 |
| Backend | FastAPI 0.115+, Python 3.12, Uvicorn, Pydantic v2 |
| Database | PostgreSQL 16 with `pgvector` extension |
| OCR | Tesseract OCR, PyMuPDF, OpenCV, Pillow |
| AI / LLM | Google Gemini 2.5 Flash (via OpenAI-compatible API) |
| ORM | SQLAlchemy 2.0 (sync) |
| File Storage | Local filesystem (S3-ready via `boto3`) |
| Containerization | Docker, Docker Compose |
| Deployment | Render (backend + DB), Vercel (frontend) |

---

## Project Structure

```
plum_intern_assignment/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── claims.py        # POST /claims, GET /claims/{id}
│   │   │   │   └── health.py        # GET /health
│   │   │   ├── deps.py              # FastAPI dependency injection
│   │   │   └── router.py            # API router aggregator
│   │   ├── core/
│   │   │   └── config.py            # Pydantic Settings (env vars)
│   │   ├── db/
│   │   │   ├── database.py          # SQLAlchemy engine + session
│   │   │   └── models.py            # ORM models: Claim, Decision, etc.
│   │   ├── schemas/
│   │   │   └── claim.py             # Pydantic request/response schemas
│   │   ├── services/
│   │   │   ├── adjudication_pipeline.py  # Orchestrates full pipeline
│   │   │   ├── rule_engine.py            # 8 deterministic adjudication rules
│   │   │   ├── document_pipeline.py      # OCR + extraction orchestration
│   │   │   ├── policy_loader.py          # Loads policy_terms.json
│   │   │   ├── policy_rag.py             # pgvector semantic search
│   │   │   ├── storage.py               # File save/path management
│   │   │   ├── llm/
│   │   │   │   ├── extraction.py         # LLM field extraction from OCR
│   │   │   │   └── adjudication.py       # LLM adjudication reasoning
│   │   │   └── ocr/
│   │   │       ├── service.py            # Tesseract + PyMuPDF OCR
│   │   │       └── preprocess.py         # Image preprocessing
│   │   ├── workers/
│   │   │   └── tasks.py             # Sync task runner (process_claim)
│   │   └── main.py                  # FastAPI app factory + lifespan
│   ├── scripts/
│   │   └── run_test_cases.py        # CLI runner for test_cases.json
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx                 # Claim submission form
│   │   ├── layout.tsx               # Root layout + metadata
│   │   ├── globals.css              # Global styles
│   │   ├── providers.tsx            # TanStack Query provider
│   │   └── claims/[id]/page.tsx    # Claim status + decision page
│   ├── lib/
│   │   └── api.ts                   # Typed API client (fetch wrappers)
│   ├── Dockerfile
│   ├── next.config.ts
│   └── package.json
│
├── policy_terms.json                # Policy rules & coverage config
├── adjudication_rules.md            # Human-readable adjudication spec
├── test_cases.json                  # 10 structured test scenarios
├── docker-compose.yml               # Postgres + Backend + Frontend
├── render.yaml                      # Render.com deployment blueprint
└── README.md
```

---

## Quick Start (Local)

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- **OR** Python 3.12+ and Node.js 20+ for manual setup

---

### Option A: Docker Compose (Recommended)

Spin up PostgreSQL, the backend, and the frontend with a single command:

```powershell
# From the project root
docker compose up --build
```

| Service | URL |
|---|---|
| Frontend UI | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| API Docs (ReDoc) | http://localhost:8000/redoc |

To stop all services:
```powershell
docker compose down
```

To wipe the database volume and start fresh:
```powershell
docker compose down -v
```

---

### Option B: Manual Setup

#### 1. Start PostgreSQL

```powershell
docker run -d --name plum-postgres `
  -e POSTGRES_USER=plum `
  -e POSTGRES_PASSWORD=plum `
  -e POSTGRES_DB=plum_claims `
  -p 5433:5432 `
  pgvector/pgvector:pg16
```

#### 2. Backend

```powershell
cd backend

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env and set DATABASE_URL and optionally GEMINI_API_KEY

# Start the server
uvicorn app.main:app --reload --app-dir .
```

Backend available at: http://127.0.0.1:8000

#### 3. Frontend

```powershell
cd frontend

# Install dependencies
npm install

# Configure environment
echo "NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api/v1" > .env.local

# Start the dev server
npm run dev
```

Frontend available at: http://localhost:3000

> Keep **both** terminals running simultaneously.

---

## Environment Variables

### Backend (`backend/.env`)

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql+psycopg2://plum:plum@localhost:5433/plum_claims` | PostgreSQL connection string. Use `sqlite:///./data/plum_claims.db` for SQLite (no pgvector) |
| `UPLOAD_DIR` | `uploads` | Directory where uploaded claim documents are stored |
| `DEBUG` | `false` | Enable debug mode |
| `OPENAI_API_KEY` | *(empty)* | **Primary AI key**: Used for LLM extraction & adjudication (can be a Gemini key — the backend routes to Gemini's OpenAI-compatible endpoint) |
| `GEMINI_API_KEY` | *(empty)* | Alternative key specifically for Google Gemini |
| `GOOGLE_VISION_API_KEY` | *(empty)* | Alternative key if using Google Vision |
| `USE_S3` | `false` | Enable S3 file storage instead of local filesystem |
| `AWS_ACCESS_KEY_ID` | *(empty)* | AWS credentials for S3 storage |
| `AWS_SECRET_ACCESS_KEY` | *(empty)* | AWS credentials for S3 storage |
| `AWS_S3_BUCKET` | *(empty)* | S3 bucket name |
| `AWS_REGION` | `ap-south-1` | AWS region |
| `MAX_UPLOAD_SIZE_MB` | `10` | Maximum file size for document uploads |

> **Note on AI Keys**: Set `OPENAI_API_KEY` to your **Google Gemini API key**. The backend uses Gemini via the `https://generativelanguage.googleapis.com/v1beta/openai/` compatible endpoint with the `gemini-2.5-flash` model. If no key is provided, the system falls back to heuristic regex-based extraction and rule-only adjudication — no AI features will be active.

### Frontend (`frontend/.env.local`)

| Variable | Default | Description |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://127.0.0.1:8000/api/v1` | Base URL of the backend API |

---

## API Reference

The full interactive API documentation is available at `/docs` (Swagger UI) and `/redoc` (ReDoc).

### Base URL
```
http://127.0.0.1:8000/api/v1
```

### Endpoints

#### `POST /claims` — Submit a New Claim

Accepts a multipart/form-data request. Returns immediately with a `claim_id` and adjudication begins synchronously.

**Form Fields:**

| Field | Type | Required | Description |
|---|---|---|---|
| `member_id` | string | ✅ | Employee ID (e.g., `emp001`) |
| `member_name` | string | ✅ | Full name of the member |
| `treatment_date` | string | ✅ | Date of treatment (`YYYY-MM-DD`) |
| `claim_amount` | float | ✅ | Total billed amount in INR |
| `member_join_date` | string | ❌ | Policy join date (`YYYY-MM-DD`). Auto-resolved from member registry if omitted |
| `hospital` | string | ❌ | Name of treating hospital (used for network discount) |
| `cashless_request` | boolean | ❌ | `true` if requesting cashless treatment |
| `previous_claims_same_day` | integer | ❌ | Manual override for fraud check |
| `structured_documents` | JSON string | ❌ | Pre-structured document data (bypasses OCR — for testing) |
| `prescription` | file | ❌ | Prescription document (PDF/image) |
| `bill` | file | ❌ | Medical bill (PDF/image) |
| `diagnostic_report` | file | ❌ | Diagnostic test report (PDF/image) |

**Response (202 Accepted):**
```json
{
  "claim_id": "uuid",
  "claim_number": "CLM_XXXXXXXX",
  "status": "COMPLETED",
  "message": "Claim adjudicated. Use GET /claims/{claim_id} for full decision."
}
```

---

#### `GET /claims/{claim_id}` — Get Claim Status & Decision

Returns the full claim status including the adjudication decision if available.

**Response:**
```json
{
  "claim_id": "uuid",
  "claim_number": "CLM_XXXXXXXX",
  "status": "COMPLETED",
  "member_id": "emp001",
  "member_name": "Rajesh Kumar",
  "treatment_date": "2025-03-15",
  "claim_amount": 2500.0,
  "decision": {
    "decision": "APPROVED",
    "approved_amount": 2250.0,
    "rejection_reasons": [],
    "deductions": { "copay": 250.0 },
    "confidence_score": 0.95,
    "notes": "Claim approved per policy terms...",
    "next_steps": "Reimbursement within 7 business days",
    "rule_results": [...]
  }
}
```

---

#### `GET /claims/{claim_id}/decision` — Get Decision Only

Returns only the `DecisionOutputSchema` for a completed claim. Returns HTTP 202 if adjudication is still in progress.

---

#### `POST /claims/{claim_id}/adjudicate-sync` — Re-run Adjudication

Forces synchronous re-adjudication of an existing claim. Useful for local testing without task queues.

---

#### `GET /health` — Health Check

Returns `{ "status": "ok" }`.

---

## Adjudication Pipeline

The pipeline runs in 5 stages for every claim submission:

```
Upload Documents
      │
      ▼
[Stage 1] OCR
   ┌──────────────────────────────────────────────┐
   │  PDF → PyMuPDF text extraction               │
   │  Image → OpenCV preprocessing → Tesseract   │
   └──────────────────────────────────────────────┘
      │
      ▼
[Stage 2] LLM Field Extraction  (requires API key)
   ┌──────────────────────────────────────────────┐
   │  Gemini 2.5 Flash extracts:                  │
   │  ─ prescription: doctor_name, doctor_reg,    │
   │    diagnosis, medicines, procedures, tests   │
   │  ─ bill: line items as {key: amount}         │
   │  Fallback: regex heuristics                  │
   └──────────────────────────────────────────────┘
      │
      ▼
[Stage 3] Deterministic Rule Engine
   (runs even without API key)
      │
      ▼
[Stage 4] LLM Adjudication Reasoning  (requires API key)
   ┌──────────────────────────────────────────────┐
   │  Gemini reviews preliminary decision against │
   │  policy context (RAG from pgvector)          │
   │  ─ Can escalate APPROVED → REJECTED          │
   │  ─ Can escalate APPROVED → MANUAL_REVIEW     │
   │  ─ Updates notes, confidence, next_steps     │
   └──────────────────────────────────────────────┘
      │
      ▼
[Stage 5] Persist Decision to DB
   → claims.status = COMPLETED or MANUAL_REVIEW
   → decisions table updated
```

---

### Rule Engine

The rule engine runs 8 deterministic checks in strict order. The first hard-failure immediately produces a `REJECTED` decision without running further rules.

| # | Rule | Failure Code | Description |
|---|---|---|---|
| 1 | **Duplicate Bill** | `DUPLICATE_CLAIM` | MD5 hash of bill matched against all prior claims |
| 2 | **Minimum Amount** | `BELOW_MIN_AMOUNT` | Claim must be ≥ ₹500 |
| 3 | **Required Documents** | `MISSING_DOCUMENTS` | Both prescription AND bill must be present |
| 4 | **Doctor Registration** | `DOCTOR_REG_INVALID` | Registration must match format `XX/NNNNN/YYYY` or `AYUR/XX/NNNNN/YYYY` |
| 5 | **Waiting Period** | `WAITING_PERIOD` | Initial 30-day wait; specific ailment waits (diabetes/hypertension: 90 days, joint replacement: 730 days) |
| 6 | **Exclusions** | `SERVICE_NOT_COVERED` | Obesity/weight loss treatments are excluded |
| 7 | **Pre-authorization** | `PRE_AUTH_MISSING` | MRI claims > ₹10,000 require pre-authorization |
| 8 | **Fraud Indicators** | — (→ `MANUAL_REVIEW`) | ≥ 3 claims from same member on same treatment date |

After all early rules pass, two additional soft checks run:

- **Cosmetic Items**: Detects cosmetic/whitening line items in bill; produces a `PARTIAL` decision with those items excluded.
- **Per-claim Limit**: Claim amount must be ≤ ₹5,000 (skipped for dental claims where sub-limits apply separately).

**Amount Calculation:**
1. Start with `claim_amount`
2. Subtract any cosmetic line items
3. Cap at `per_claim_limit` (₹5,000)
4. Apply 10% co-pay on consultation/dental bills
5. Apply 20% network discount for cashless network hospital visits
6. Cap Ayurveda/alternative medicine at ₹8,000 sub-limit

---

### AI / LLM Layer

When a Gemini API key is configured (`OPENAI_API_KEY` or `GEMINI_API_KEY`):

**Extraction Phase:**  
The `extraction.py` service sends OCR text to `gemini-2.5-flash` with a strict JSON schema prompt. It extracts:
- Prescription fields: doctor name, registration number, diagnosis, medicines, procedures, tests, treatment description
- Bill fields: each line item as a key-value pair `{"consultation_fee": 500, "medicines": 1200}`
- Field confidence scores (0.0–1.0) for each extracted value

**Adjudication Phase:**  
The `adjudication.py` service sends the preliminary rule-engine decision to the LLM along with relevant policy chunks retrieved via pgvector semantic search. The LLM:
- Verifies medical necessity (does the diagnosis justify the prescribed treatment?)
- Checks for policy exclusions the rule engine may have missed
- Can override an `APPROVED` decision to `REJECTED` or `MANUAL_REVIEW`
- Generates human-readable notes and next-steps guidance

---

### Decision Outcomes

```json
{
  "decision": "APPROVED | REJECTED | PARTIAL | MANUAL_REVIEW",
  "approved_amount": 2250.0,
  "rejection_reasons": ["WAITING_PERIOD"],
  "rejected_items": ["teeth_whitening - cosmetic procedure"],
  "deductions": { "copay": 250.0 },
  "flags": ["Multiple claims same day"],
  "confidence_score": 0.95,
  "notes": "Human-readable explanation...",
  "next_steps": "Reimbursement within 7 business days",
  "cashless_approved": false,
  "network_discount": null,
  "medical_necessity_established": true,
  "exclusions_detected": [],
  "rule_results": [
    { "rule_name": "duplicate_bill", "passed": true, "reason_code": null, "note": null },
    { "rule_name": "minimum_amount", "passed": true, "reason_code": null, "note": null },
    ...
  ]
}
```

---

## Policy Terms

The active policy is `PLUM_OPD_2024` (Plum OPD Advantage) covering **TechCorp Solutions Pvt Ltd** employees.

| Parameter | Value |
|---|---|
| Annual Limit | ₹50,000 per member |
| Per-Claim Limit | ₹5,000 |
| Family Floater Limit | ₹1,50,000 |
| Consultation Co-pay | 10% |
| Network Discount | 20% |
| Minimum Claim | ₹500 |
| Submission Deadline | 30 days from treatment |
| Initial Waiting Period | 30 days |
| Dental Sub-limit | ₹10,000 |
| Pharmacy Sub-limit | ₹15,000 |
| Diagnostics Sub-limit | ₹10,000 |
| Alternative Medicine Sub-limit | ₹8,000 |

**Network Hospitals:** Apollo Hospitals, Fortis Healthcare, Max Healthcare, Manipal Hospitals, Narayana Health

**Covered Dental Procedures:** Filling, Extraction, Root Canal, Cleaning (cosmetic procedures NOT covered)

**Key Exclusions:** Cosmetic procedures, weight loss treatments, infertility, experimental treatments, LASIK surgery, vitamins/supplements (unless for deficiency)

---

## Frontend UI

The Next.js frontend provides two main pages:

### 1. Claim Submission (`/`)
- Member ID, name, treatment date, claim amount fields
- Optional: hospital name, cashless toggle, join date
- Drag-and-drop file upload for prescription, bill, and diagnostic report
- **Load Approved Example** button — prefills a passing scenario
- **Load Bill-Only (Reject) Example** button — prefills a missing-prescription scenario
- Submits via `POST /api/v1/claims` and redirects to status page

### 2. Claim Status (`/claims/[id]`)
- Displays current claim status (`PENDING → PROCESSING → COMPLETED`)
- Auto-polls every 2 seconds until a final status is reached
- Shows full decision breakdown: approved amount, rejection codes, deductions, confidence score, notes, and next steps
- Color-coded status indicators (green = approved, red = rejected, amber = partial/manual review)

---

## Running Test Cases

The project includes 10 pre-defined test scenarios in `test_cases.json` covering approvals, rejections, partial approvals, and edge cases.

```powershell
cd backend
python scripts/run_test_cases.py
```

This script:
1. Reads all test cases from `test_cases.json`
2. Submits each claim via the API using `structured_documents` JSON (no file uploads needed)
3. Prints the actual vs expected decision for each case
4. Reports a pass/fail summary

> Make sure the backend server is running before executing this script.

---

## Cloud Deployment

The project is configured for deployment on **Render** (backend + database) and **Vercel** (frontend).

### Render (Backend + PostgreSQL)

A `render.yaml` Blueprint file is included in the project root. It provisions:
- **PostgreSQL 16** database (`plum-claims-db`)
- **Docker web service** (`plum-claims-backend`) connected to the database

**Steps:**
1. Push your code to GitHub.
2. Go to [Render Dashboard](https://dashboard.render.com) → **New** → **Blueprint**.
3. Connect your repository — Render auto-reads `render.yaml`.
4. Set `OPENAI_API_KEY` (your Gemini key) in the environment variable panel.
5. Click **Apply**. Wait for the build and deployment to complete.
6. Copy the backend URL (e.g., `https://plum-claims-backend.onrender.com`).

### Vercel (Frontend)

1. Go to [Vercel](https://vercel.com) → **Add New Project**.
2. Import your GitHub repository.
3. Set **Root Directory** to `frontend`.
4. Add environment variable:
   - `NEXT_PUBLIC_API_URL` = `https://plum-claims-backend.onrender.com/api/v1`
5. Click **Deploy**.

> **Free Tier Note:** Render free-tier services spin down after 15 minutes of inactivity. The first request after idle may take up to 50 seconds.

---

## Database Schema

### `claims` table
| Column | Type | Description |
|---|---|---|
| `id` | UUID (PK) | Unique claim identifier |
| `claim_number` | VARCHAR(32) | Human-readable ID (`CLM_XXXXXXXX`) |
| `status` | ENUM | `PENDING / PROCESSING / COMPLETED / FAILED / MANUAL_REVIEW` |
| `member_id` | VARCHAR(64) | Employee ID |
| `member_name` | VARCHAR(255) | Member full name |
| `member_join_date` | VARCHAR(32) | Policy join date |
| `treatment_date` | VARCHAR(32) | Date of treatment |
| `claim_amount` | FLOAT | Billed amount in INR |
| `hospital` | VARCHAR(255) | Hospital name (nullable) |
| `cashless_request` | BOOLEAN | Cashless treatment requested |
| `metadata_extra` | JSON | Structured documents, file hashes |
| `document_paths` | JSON | Paths to uploaded files |
| `error_message` | TEXT | Processing error if any |
| `created_at` | TIMESTAMPTZ | Record creation time |
| `updated_at` | TIMESTAMPTZ | Last update time |

### `decisions` table
| Column | Type | Description |
|---|---|---|
| `id` | UUID (PK) | Decision record ID |
| `claim_id` | UUID (FK) | Reference to `claims.id` |
| `decision_payload` | JSON | Full decision output including rule results |
| `created_at` | TIMESTAMPTZ | When decision was made |

### `extracted_fields` table
| Column | Type | Description |
|---|---|---|
| `id` | UUID (PK) | Record ID |
| `claim_id` | UUID (FK) | Reference to `claims.id` |
| `ocr_result` | JSON | Raw OCR output per document |
| `extracted_data` | JSON | Structured extracted fields |
| `field_confidence` | JSON | Per-field confidence scores |

### `policy_embeddings` table
| Column | Type | Description |
|---|---|---|
| `id` | UUID (PK) | Record ID |
| `chunk_id` | VARCHAR(64) | Unique chunk identifier |
| `source` | VARCHAR(128) | Source document name |
| `text` | TEXT | Policy text chunk |
| `embedding` | Vector(384) | Sentence embedding for semantic search |

---

## Member Registry

The system includes a built-in registry of 10 test employees with their policy join dates for waiting period validation:

| Member ID | Name | Join Date |
|---|---|---|
| `emp001` | Rajesh Kumar | 2024-01-01 |
| `emp002` | Priya Singh | 2024-01-01 |
| `emp003` | Amit Verma | 2024-01-01 |
| `emp004` | Sneha Reddy | 2024-01-01 |
| `emp005` | Vikram Joshi | 2024-09-01 *(shorter tenure)* |
| `emp006` | Kavita Nair | 2024-01-01 |
| `emp007` | Suresh Patil | 2024-01-01 |
| `emp008` | Ravi Menon | 2024-01-01 |
| `emp009` | Anita Desai | 2024-01-01 |
| `emp010` | Deepak Shah | 2024-01-01 |

> Members not in the registry will have waiting period checks skipped (join date unknown).

---

## License

This project was built as an intern assignment for Plum and is intended for evaluation purposes.

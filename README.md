# CivicShield AI — Modern AI-Powered Civic Issue Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Framework-Flask%203.0-wine.svg)](https://flask.palletsprojects.com/)
[![Design](https://img.shields.io/badge/Theme-Burgundy%20%26%20Champagne-3F1024.svg)](#design-system--branding)
[![Tests](https://img.shields.io/badge/Tests-18%20Passed-success.svg)](#testing)

**CivicShield AI** is a state-of-the-art civic grievance reporting, intelligent triage, and transparent resolution platform built for Indian citizens and municipal authorities. 

By unifying **explainable AI computer vision**, **geospatial duplicate detection**, **automated SLA escalations**, and **citizen-certified before-and-after repair verification**, CivicShield closes the feedback loop between public infrastructure breakdowns and municipal action.

---

## 🎨 1. Design System & Branding

CivicShield AI implements a custom, accessible **Burgundy & Champagne** design palette:

| Token | Hex Code | Purpose |
|---|---|---|
| **Deep Burgundy** | `#3F1024` | Primary brand identity, navigation bar, dark headers |
| **Wine Red** | `#7F1D3F` | Secondary emphasis, links, primary buttons |
| **Champagne** | `#E7C9A9` | Visual highlights, active borders, status badges |
| **Warm Ivory** | `#FFF9F3` | Content section backgrounds, warm card surfaces |
| **White** | `#FFFFFF` | Card canvases, dialog modals, high contrast tables |
| **Primary Text** | `#351520` | High-contrast accessible typography |
| **Secondary Text**| `#78656B` | Meta labels, timestamps, supporting copy |
| **Success Green** | `#15803D` | Resolved cases, citizen sign-offs |
| **Critical Risk** | `#DC2626` | High-voltage shock risks, life-safety emergencies |
| **Medium Risk**   | `#EA580C` | Standard urban hazards (waste, leaks) |
| **Low Risk**      | `#FACC15` | Minor repairs, park furnishings |

### Cinematic Skyline Homepage
The main portal hero features a golden-hour metropolitan skyline overlaid with a burgundy gradient on the left, keeping typography readable on all screen sizes while highlighting urban towers on the center and right.

---

## 🚀 2. Key Technological Innovations

1. **Explainable AI Computer Vision & Risk Prioritization (`services/ai_service.py`):**
   - Classifies civic issue photos across 11 standard urban categories.
   - Detects life-safety hazards (*e.g., High Voltage Shock Risk, Roadway Crater > 12cm, Sewage Pathogen Vector*).
   - Generates an explainable **0 to 100 Risk Score** broken down by baseline severity, hazard multipliers, and public right-of-way exposure.
   - Transparent AI fallback (*"AI analysis unavailable"*) when services are offline—never claims unavailable models have executed.

2. **Haversine Proximity & Duplicate Detection (`services/duplicate_service.py`):**
   - Automatically scans active complaints within a 150m–200m radius using the great-circle Haversine formula combined with tokenized text similarity.
   - Prompts citizens to **support/upvote an existing complaint (+1)** instead of creating redundant tickets.

3. **Multi-Tier SLA Escalation Engine (`services/sla_service.py`):**
   - Category and priority-driven service level agreements:
     - **Critical:** 2-hour acknowledgment, 24-hour resolution.
     - **High:** 6-hour acknowledgment, 48-hour resolution.
     - **Medium:** 12-hour acknowledgment, 72-hour resolution.
     - **Low:** 24-hour acknowledgment, 120-hour resolution.
   - Automated escalation hierarchy: Level 1 (Ward Supervisor) &rarr; Level 2 (Department Head) &rarr; Level 3 (Municipal Commissioner & Ombudsman).

4. **Cryptographic Evidence Integrity (SHA-256):**
   - Calculates cryptographic SHA-256 hashes of all submitted evidence photos and resolution photos.
   - Detects alterations and flags re-uploads of identical before-photos.

5. **Citizen-Certified Before-and-After Verification:**
   - Field officers must submit post-repair photographic evidence and notes to mark a ticket resolved.
   - Citizens receive interactive before-and-after evidence comparisons to **Confirm & Rate (1–5 Stars)** or **Dispute & Reopen**.

6. **Smart Work Order Bundling (`routes/authority.py`):**
   - Managers bundle multiple nearby complaints (*e.g., 4 potholes along one road*) into a single Work Order (`WO-2026-XXXX`).
   - Automatically calculates required crew size, asphalt metric tons, replacement fixtures, and non-binding cost estimates.

7. **Predictive Maintenance & Recurring Hotspots (`services/analytics_service.py`):**
   - Correlates historical complaints by ward and location cluster to identify chronic infrastructure failures.
   - Suggests proactive capital works (*e.g., full pavement milling before monsoon*).

8. **Disaster Response Mode (Urban Flooding & Storms):**
   - Platform-wide crisis toggle enabling emergency banners, 24x7 helplines (112, 1070), flood cell dispatch, and high-volume rescue triage.

9. **Telugu & English Multilingual Support:**
   - Complete bilingual interface with one-click toggling (`EN` / `తెలుగు`).
   - Integrated Web Speech API audio dictation (`te-IN` / `en-IN`) with automatic translation normalization.

10. **Offline Draft Resilience:**
    - LocalStorage report caching for low-connectivity zones, client-side HTML5 canvas image compression, and network status banners.

---

## 👥 3. Demonstration Credentials

Quick demo accounts are pre-seeded in the database:

| Role | Name | Phone / Login | Password | Access Highlights |
|---|---|---|---|---|
| **Citizen** | Rahul Sharma | `9876543210` | `demo123` | Report issues, my complaints, track repairs, rate service, file appeals |
| **Citizen (Telugu)** | Priya Reddy | `9876543211` | `demo123` | Telugu interface, voice input, community upvoting |
| **Municipal Officer** | Suresh Varma | `9849012345` | `officer123` | Roads Dept dashboard, assign crews, upload resolution photos |
| **Municipal Officer** | Ananya Rao | `9849054321` | `officer123` | Sanitation Dept dashboard, manage solid waste work orders |
| **Officer (Pending)** | Vikram Patel | `9849099999` | `officer123` | Demonstrates administrator approval verification workflow |
| **Administrator** | Dr. K. Radhakrishna, IAS | `9999999999` | `admin123` | Approve officers, configure departments, toggle Disaster Mode |

> **Development OTP:** `123456` (displayed directly on the verification screen during new user registration).

---

## 🛠️ 4. Local Installation & Setup Instructions

### Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Pip package manager

### Step 1: Clone or Navigate to Directory
```bash
cd "civic shield AI"
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment
Copy `.env.example` to `.env` (optional for local development as sensible defaults are included):
```bash
cp .env.example .env
```

### Step 4: Seed Database with Demonstration Data
Populate realistic Indian complaints, departments, and before/after evidence photos:
```bash
python seeds/seed_data.py
```

### Step 5: Run the Automated Test Suite
```bash
python -m pytest -v
```
*(All 18 automated unit and integration tests will execute and pass).*

### Step 6: Start the Development Server
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 📂 5. Project Directory Architecture

```
civic shield AI/
├── app.py                      # Flask factory, context processors, blueprint registration
├── config.py                   # Configuration, categories, departments, SLA rules
├── database.py                 # SQLite schema initialization (19 tables, indexes)
├── requirements.txt            # Python dependencies (Flask, Pillow, pytest)
├── .env.example                # Environment variable configuration template
├── README.md                   # Complete documentation & usage guide
├── models/                     # Data entity specifications
├── services/
│   ├── ai_service.py           # Computer vision triage, hazard scoring, authenticity, Telugu NLP
│   ├── duplicate_service.py    # Haversine distance & token similarity duplicate detector
│   ├── sla_service.py          # SLA deadline engine & automated multi-tier escalations
│   ├── auth_service.py         # Password hashing, session authentication, audit logging
│   ├── notification_service.py # In-app notification center & unread counters
│   ├── analytics_service.py    # Public KPIs, department performance, predictive maintenance
│   └── i18n.py                 # English & Telugu translation dictionary
├── routes/
│   ├── public.py               # Cinematic homepage, civic map, transparency, help
│   ├── auth.py                 # Register, OTP verify, login, role redirection, profile
│   ├── citizen.py              # Citizen dashboard, issue reporting, tracking, verification, appeals
│   ├── authority.py            # Operations dashboard, complaint triage, work orders, analytics
│   ├── admin.py                # Officer approval queue, department config, disaster mode toggle
│   └── api.py                  # Map markers, real-time AI triage preview, duplicate checks
├── static/
│   ├── css/style.css           # Core Burgundy & Champagne design system
│   ├── js/
│   │   ├── main.js             # Notification drawer, offline detection, community upvotes
│   │   ├── map.js              # Leaflet mapping, colored SVG pins, popups, filters
│   │   ├── report.js           # Camera capture, canvas compression, GPS draggable pin, AI preview
│   │   └── speech.js           # Web Speech API voice dictation (Telugu & English)
│   ├── img/
│   │   ├── city_skyline.jpg    # Golden-hour urban skyline
│   │   └── demo/               # Demonstration graphics
│   └── uploads/                # Cryptographically hashed evidence and repair photos
├── templates/
│   ├── base.html               # Master layout with Burgundy navbar, Champagne highlights
│   ├── public/                 # index, public_map, transparency, help, 404, 500
│   ├── auth/                   # login, register, verify_otp, pending_approval, profile
│   ├── citizen/                # dashboard, report, my_complaints, complaint_detail, draft_reports
│   ├── authority/              # dashboard, complaint_review, detail_review, work_orders, analytics...
│   └── admin/                  # approvals, departments
├── seeds/
│   └── seed_data.py            # Comprehensive database populator with demo data & images
└── tests/
    ├── test_auth.py            # Authentication, role permissions, and hashing tests
    ├── test_complaint.py       # Issue reporting, verification, and appeal integration tests
    ├── test_ai_service.py      # AI classification, risk scores, and Telugu NLP tests
    ├── test_duplicate.py       # Haversine proximity & duplicate matching tests
    └── test_sla.py             # SLA calculation & escalation logic tests
```

---

## 🏛️ 6. All 24 Required Pages & Workflows

1. **Public Homepage** (`/`): Cinematic golden-hour skyline hero, live ticker, recent issues, before/after evidence cards, how it works, FAQs.
2. **Registration** (`/register`): Role selection (Citizen or Authority), department credentials, Telugu/English language preference.
3. **Login** (`/login`): Phone/email login with one-click demo credentials buttons.
4. **OTP Verification** (`/verify_otp`): 6-digit verification with development auto-fill banner.
5. **Pending Approval Screen** (`/pending_approval`): Real-time status for municipal officers awaiting admin verification.
6. **Citizen Dashboard** (`/citizen/dashboard`): Status KPI counters, recent issues, nearby ward reports with upvoting.
7. **Report an Issue** (`/citizen/report`): Live camera capture, canvas compression, GPS draggable pin, real-time AI triage preview, duplicate warning modal.
8. **My Complaints** (`/citizen/my_complaints`): Searchable, filterable list of citizen's reported tickets.
9. **Complaint Details & Tracking** (`/citizen/complaint/<id>`): 7-stage status timeline, SHA-256 evidence viewer, before/after evidence comparison, rating modal.
10. **Offline Draft Reports** (`/citizen/drafts`): Browser-cached report manager.
11. **Interactive Civic Map** (`/map`): Leaflet OpenStreetMap with privacy coordinate fuzzing (~100m) and color-coded SVG pins.
12. **Municipal Authority Dashboard** (`/authority/dashboard`): Operational KPIs, urgent & overdue queues, work order overview.
13. **Complaint Review & Triage** (`/authority/complaints`): Filterable municipal complaints table with AI risk scores.
14. **Complaint Action & Assignment** (`/authority/complaint/<id>`): Reassign department, assign field officer, update status, upload resolution evidence photo.
15. **Smart Work Order Management** (`/authority/work_orders`): Multi-ticket bundling with automated crew, material, and cost estimates.
16. **Work Order Detail** (`/authority/work_order/<id>`): Checklist execution and progress tracking.
17. **Predictive Maintenance** (`/authority/predictive`): Recurring breakdown hotspots and proactive inspection recommendations.
18. **Department Performance Analytics** (`/authority/analytics`): Chart.js resolution rates, workload comparisons, and citizen ratings.
19. **SLA Escalations Management** (`/authority/escalations`): Overdue complaints monitor and multi-tier escalation audit trail.
20. **Citizen Appeals Queue** (`/authority/appeals`): Independent grievance redressal ombudsman adjudication.
21. **Disaster Response Command Center** (`/authority/disaster`): Crisis protocol toggle, emergency helplines, high-priority inundation queue.
22. **Authority Credentials Approvals** (`/admin/approvals`): Administrator verification queue for municipal staff.
23. **Department Management** (`/admin/departments`): Department contacts, codes, and operational boundaries.
24. **Public Transparency & Civic Impact** (`/transparency`): Open data metrics, citizen satisfaction charts, and department resolution velocity.

---

## 🔒 7. Security, Privacy & Integrity Commitments

- **Zero Public PII:** Citizen names, phone numbers, and exact GPS coordinates are truncated and fuzzed on all public views.
- **Cryptographic Hashes:** Every evidence photo receives a SHA-256 hash at upload to protect chain of custody.
- **Server-Side Enforcement:** Backend role decorators (`@login_required`, `@role_required`) protect all endpoints, not just UI button hides.
- **CSRF & Safe Session Handling:** Cookies and sessions configured securely with environment-controlled secret keys.

---

## 📜 8. License & Academic Disclaimer

Built for **Civic Innovation, Smart City Hackathons, and College Competitions 2026**. All demonstration data, simulated AI confidences, and government department contacts are designed for academic and prototype demonstration purposes.

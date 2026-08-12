# Partzuf Yomi — Israel News Developmental Analysis Engine

מנוע ניתוח חדשות התפתחותי — פרצוף יומי

A full-stack system that collects news from AP (international) and Rotter (Israeli), classifies them using a 10-stage developmental metaphor model, analyzes them through Mother/Father/Son analytical layers, detects Israel relevance, and presents results via a Hebrew RTL dashboard and Telegram bot.

## Architecture

```
frontend/        Next.js 16 + TypeScript + Tailwind CSS + Recharts
backend/         FastAPI + SQLAlchemy (async) + APScheduler
```

### Key Components

- **News Collection**: AP (RSS/feedparser) + Rotter (public headlines)
- **Classification Engine**: Rule-based keyword classifier (35 event types)
- **Developmental Analysis**: 10-stage metaphor model (embryo → new generation)
- **Analytical Layers**: Mother (nurturing), Father (structure), Son (perception)
- **Israel Relevance**: Direct / Indirect / Speculative scoring
- **Daily Synthesis**: Automated summary at 18:00 Israel time
- **Telegram Bot**: Hourly digests + daily synthesis

### 10 Developmental Stages

| # | Stage | Hebrew | Description |
|---|-------|--------|-------------|
| 1 | embryo | עובר | Existential threats, survival |
| 2 | infant | יונק | Basic needs, health, nurturing |
| 3 | child | ילד | Education, learning, innovation |
| 4 | adult | בוגר | Governance, economy, responsibility |
| 5 | first_woman | אישה ראשונה | Initial encounters, recognition |
| 6 | primary_woman | אישה עיקרית | Alliances, partnerships |
| 7 | third_woman | אישה שלישית | Complexity, multi-layered relations |
| 8 | courtship | חיזור | Diplomacy, negotiation |
| 9 | marriage | נישואין | Peace agreements, commitments |
| 10 | new_generation | דור חדש | Demographics, birth, future |

## Quick Start (Development)

### Prerequisites

- Python 3.11+
- Node.js 22+
- Git

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
pip install aiosqlite
```

### Environment Configuration

Copy the example and edit as needed:

```bash
cp .env.example .env
```

Default `.env` for demo mode (SQLite, no AI, no Telegram):

```
APP_ENV=development
DEMO_MODE=true
DATABASE_URL=sqlite+aiosqlite:///./partzuf_yomi.db
AI_PROVIDER=none
HOURLY_COLLECTION_ENABLED=false
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

### Run Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

The backend loads 12 demo articles and analyzes them on startup.

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 to see the dashboard.

### Run Tests

```bash
cd backend
pytest tests/ -v --tb=short
```

All 46 tests should pass (29 classifier + 12 API + 1 health + 4 telegram/synthesis).

## Docker

### Demo mode (SQLite)

```bash
docker compose up --build
```

### Production mode (PostgreSQL + Redis)

```bash
docker compose --profile production up --build
```

Set in `.env`:
```
DATABASE_URL=postgresql+asyncpg://partzuf:partzuf_dev@postgres:5432/partzuf_yomi
DEMO_MODE=false
HOURLY_COLLECTION_ENABLED=true
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/dashboard` | Dashboard statistics |
| GET | `/api/news` | News list (filterable by source, event_type, stage) |
| GET | `/api/news/{id}` | Single article |
| GET | `/api/analysis/{id}` | Full analysis for article |
| GET | `/api/daily-summary` | Daily synthesis |
| GET | `/api/stages` | List of 10 developmental stages |
| GET | `/api/event-types` | List of 35 event type categories |
| POST | `/api/admin/run-collector` | Trigger news collection |
| POST | `/api/admin/run-analysis` | Trigger analysis pipeline |
| POST | `/api/admin/send-telegram` | Trigger Telegram digest |

## Frontend Pages

| Path | Description |
|------|-------------|
| `/` | Main dashboard with stats, stage chart, news feed, timeline |
| `/synthesis` | Daily synthesis view with trend analysis |
| `/article/[id]` | Full article analysis detail page |

## Important Disclaimer

This system uses a developmental model as a **metaphorical analytical framework**.
Results should **not** be interpreted as scientific, medical, or psychological findings.
Every interpretation is labeled by its certainty level and claim type.

---

Built with FastAPI, Next.js 16, SQLAlchemy, and TypeScript.

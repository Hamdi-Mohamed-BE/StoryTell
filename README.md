# StoryCards

**AI-powered platform that transforms stories into swipeable visual cards.**

StoryCards takes any story — from books, movies, anime, or TV shows — and breaks it down into a series of digestible "visual cards." Each card features a short narrative segment, an AI-generated image, and text-to-speech audio narration. Users experience stories through an immersive, swipeable mobile interface.

---

## App Preview

<video src="video/storytell.mp4" controls width="300"></video>

> If the video doesn't render, [click here to watch](video/storytell.mp4).

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Environment Variables](#environment-variables)
  - [Running with Docker](#running-with-docker)
  - [Running the Mobile App](#running-the-mobile-app)
- [API Endpoints](#api-endpoints)
- [AI Pipeline](#ai-pipeline)
- [Database Migrations](#database-migrations)
- [License](#license)

---

## Features

- **Story Breakdown** — AI (Google Gemini) splits any story into chronologically ordered narrative segments.
- **Image Generation** — Each segment gets a unique AI-generated illustration via FLUX (Hugging Face).
- **Voice Narration** — Text-to-speech audio for every card using Kokoro-82M (Hugging Face).
- **Cover Art** — Automatic cover fetching from the Open Library API.
- **Background Processing** — Heavy AI workloads run asynchronously through Celery workers.
- **Job Tracking** — Real-time generation progress with per-section status updates.
- **Mobile-First** — Full-screen swipeable card experience built with React Native / Expo.
- **Dark Theme** — Polished dark UI with story-type color coding (book, movie, anime, TV show).

---

## Tech Stack

| Layer          | Technology                                                      |
| -------------- | --------------------------------------------------------------- |
| **Backend**    | Python 3.12, FastAPI, SQLAlchemy 2.0 (Async), Pydantic v2      |
| **Database**   | PostgreSQL 16                                                   |
| **Cache/Queue**| Redis 7                                                         |
| **Task Queue** | Celery                                                          |
| **AI / LLM**   | Google Gemini (via LangChain)                                   |
| **Image Gen**  | Hugging Face — `black-forest-labs/FLUX.1-schnell`               |
| **Voice Gen**  | Hugging Face — `hexgrad/Kokoro-82M`                             |
| **Mobile**     | React Native, Expo, TypeScript                                  |
| **Infra**      | Docker & Docker Compose                                         |
| **Pkg Manager**| `uv` (backend), `npm` (mobile)                                  |

---

## Architecture

```
┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│  Mobile App  │◄──────►│  FastAPI      │◄──────►│  PostgreSQL  │
│  (Expo/RN)   │  HTTP  │  Backend      │  SQL   │  Database    │
└──────────────┘        └──────┬───────┘        └──────────────┘
                               │
                               │ Celery Tasks
                               ▼
                        ┌──────────────┐
                        │   Redis      │
                        │  (Broker)    │
                        └──────┬───────┘
                               │
                               ▼
                        ┌──────────────┐        ┌──────────────────┐
                        │   Celery     │───────►│  Hugging Face    │
                        │   Worker     │        │  (FLUX, Kokoro)  │
                        └──────┬───────┘        └──────────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │  Google Gemini   │
                        │  (LangChain)     │
                        └──────────────────┘
```

**Flow:**
1. User creates a story via the mobile app.
2. Backend stores metadata and dispatches a Celery task.
3. The worker runs the AI pipeline: **Breakdown → Enhance → Image Gen → Audio Gen**.
4. Generated media is saved to the local filesystem; section records are updated in PostgreSQL.
5. The mobile app fetches completed sections and displays them as swipeable cards.

---

## Project Structure

```
├── docker-compose.yml          # Orchestrates all services
├── makemigrations.sh           # Generate Alembic migration
├── migrate.sh                  # Apply Alembic migrations
│
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml          # Python deps (managed by uv)
│   ├── alembic.ini             # Alembic config
│   ├── alembic/                # DB migrations
│   └── app/
│       ├── main.py             # FastAPI entry point
│       ├── config.py           # Settings (env vars)
│       ├── database.py         # Async SQLAlchemy engine & sessions
│       ├── ai/
│       │   └── chains/         # AI pipeline steps
│       │       ├── story_breakdown.py    # LLM story segmentation
│       │       ├── prompt_enhancer.py    # Image prompt refinement
│       │       ├── image_generator.py    # FLUX image generation
│       │       └── voice_generator.py    # Kokoro TTS audio
│       ├── api/
│       │   └── stories.py      # REST endpoints
│       ├── models/             # SQLAlchemy ORM models
│       │   ├── story.py
│       │   ├── story_section.py
│       │   └── generation_job.py
│       ├── schemas/            # Pydantic request/response schemas
│       ├── services/           # Business logic layer
│       │   ├── story_service.py
│       │   ├── generation_service.py
│       │   ├── media_service.py
│       │   └── cover_service.py
│       └── workers/
│           ├── celery_app.py   # Celery configuration
│           └── tasks.py        # Background task definitions
│
└── mobile/
    ├── App.tsx                 # Expo entry point
    ├── app.json                # Expo config
    ├── package.json
    └── src/
        ├── api/                # Typed HTTP client
        ├── components/         # Reusable UI components
        │   ├── StoryCard.tsx
        │   ├── SectionCard.tsx
        │   ├── Badge.tsx
        │   ├── Header.tsx
        │   └── JobItem.tsx
        ├── hooks/              # Data-fetching hooks
        ├── screens/
        │   ├── HomeScreen.tsx   # Story list
        │   └── StoryScreen.tsx  # Full-screen card swiper
        ├── theme/               # Dark theme & colors
        └── types/               # TypeScript interfaces
```

---

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & Docker Compose
- [Node.js](https://nodejs.org/) 18+ (for mobile development)
- [Expo CLI](https://docs.expo.dev/get-started/installation/) (`npm install -g expo-cli`)
- A **Google Gemini API key** — [Get one here](https://ai.google.dev/)
- A **Hugging Face token** — [Get one here](https://huggingface.co/settings/tokens)

### Environment Variables

Create `backend/.env`:

```env
GOOGLE_API_KEY=your-gemini-api-key
HF_TOKEN=your-huggingface-token
ENABLE_AUDIO_GEN=false          # Set to true to enable TTS
DEBUG=false
```

All other values (database URLs, Redis, Celery) have sensible defaults for the Docker setup.

### Running with Docker

```bash
# Clone the repository
git clone <repo-url>
cd storycards

# Start all services (API, Celery worker, PostgreSQL, Redis)
docker compose up --build

# Run database migrations (in a separate terminal)
bash migrate.sh
```

The API will be available at **http://localhost:8000**. Visit http://localhost:8000/ for the built-in web interface.

### Running the Mobile App

```bash
cd mobile

# Install dependencies
npm install

# Start the Expo dev server
npx expo start
```

Scan the QR code with the Expo Go app on your phone, or press `a` for Android emulator / `i` for iOS simulator.

> **Note:** Update the API base URL in `mobile/src/api/client.ts` to point to your backend (e.g., your machine's local IP).

---

## API Endpoints

| Method | Endpoint                               | Description                            |
| ------ | -------------------------------------- | -------------------------------------- |
| GET    | `/api/stories`                         | List all stories                       |
| POST   | `/api/stories`                         | Create a new story                     |
| GET    | `/api/stories/{uid}`                   | Get story details with section metadata|
| GET    | `/api/stories/{uid}/sections`          | Get full sections with media URLs      |
| GET    | `/api/stories/sections/{uid}/media`    | Lazy-load media for a single section   |
| GET    | `/api/stories/{uid}/jobs`              | List generation job statuses           |

---

## AI Pipeline

The generation pipeline runs as a Celery background task with 4 stages:

```
1. Story Breakdown     →  Gemini splits the story into narrative segments
2. Prompt Enhancement  →  Gemini refines each segment into a detailed image prompt
3. Image Generation    →  FLUX.1-schnell generates an illustration per segment
4. Audio Generation    →  Kokoro-82M creates TTS narration per segment (optional)
```

Each stage updates the corresponding section record in the database so the client can poll for progress.

---

## Database Migrations

```bash
# Generate a new migration after model changes
bash makemigrations.sh

# Apply pending migrations
bash migrate.sh
```

Migrations are managed with **Alembic** and stored in `backend/alembic/versions/`.

---

## License

This project is for personal/educational use.

# Integral Solutions — Assignment (Flask + Expo)

Full‑stack assignment with a **Flask + MongoDB** backend and an **Expo (React Native)** frontend.

- Backend: JWT auth (access + refresh), dashboard videos, signed playback tokens
- Frontend: thin client (Expo), signup/login, dashboard, video playback, settings (profile + logout)

---

## Project structure

```
backend/   # Flask API + MongoDB
frontend/  # Expo / React Native app
```

---

## Setup instructions

### Prerequisites

- Python 3.9+ (recommended)
- Node.js 18+ (Expo)
- MongoDB (local or Atlas)

### 1) Backend setup (Flask)

1. Create a virtual environment at repo root (recommended):
   - Windows PowerShell:
     - `python -m venv .venv`
     - `.\.venv\Scripts\Activate.ps1`

2. Install backend dependencies:
   - `pip install -r backend/requirements.txt`

3. Create `backend/.env` from the example:
   - Copy [backend/.env.example](backend/.env.example) → `backend/.env`

4. Fill required values in `backend/.env`:
   - `MONGO_URI` (required)
   - `SECRET_KEY` (required)
   - `JWT_SECRET_KEY` (required)

   Optional (defaults exist):
   - `JWT_ACCESS_TOKEN_EXPIRES_MINUTES` (default 15)
   - `JWT_REFRESH_TOKEN_EXPIRES_DAYS` (default 7)
   - `PLAYBACK_TOKEN_SALT` (default `playback`)
   - `PLAYBACK_TOKEN_EXPIRES_SECONDS` (default 900)

5. Start the backend:
   - `python backend/run.py`

Backend runs on `http://0.0.0.0:5000`.

Quick health check:
- `GET http://localhost:5000/health`

### 2) Seed videos (2 tiles)

This inserts/updates two videos in MongoDB (idempotent upsert).

- `python backend/scripts/seed_videos.py`

Note: the seed currently uses **public MP4 sample URLs** so playback works reliably even when YouTube embedding is blocked.

### 3) Frontend setup (Expo / React Native)

1. Install dependencies:
   - `cd frontend`
   - `npm install`

2. Configure API base URL:

The frontend uses [frontend/src/config/env.js](frontend/src/config/env.js).

- If you’re using a **physical phone (Expo Go)**, set it to your **PC LAN IP**, e.g. `http://192.168.1.50:5000`.
- If you’re using an **Android emulator**, common default is `http://10.0.2.2:5000`.

3. Start Expo:
   - `npx expo start`

---

## Core flows

### Authentication (JWT) flow

Backend endpoints:
- `POST /auth/signup` → `{ access_token, refresh_token }`
- `POST /auth/login` → `{ access_token, refresh_token }`
- `GET /auth/me` (access token) → `{ user: { id, name, email, created_at } }`
- `POST /auth/refresh` (refresh token) → `{ access_token }`

Frontend behavior:
- Stores tokens securely in `expo-secure-store`.
- Adds the access token to requests via an Axios request interceptor.
- On `401`, it attempts refresh via `POST /auth/refresh` using the refresh token.
- If refresh fails, it clears the session and returns to Login.

### Dashboard + playback token flow (YouTube abstraction)

Key idea: the client should **not** need to know the real video source.

1. Frontend calls `GET /dashboard` → returns video tiles (title/description/thumbnail + id). No raw YouTube URL is required here.
2. When user taps a video tile, frontend requests a signed playback token:
   - `GET /video/<id>/token` (requires JWT)
3. Frontend exchanges the playback token for a stream URL:
   - `GET /video/<id>/stream?token=...`
4. Backend verifies the playback token and returns one of:
   - `stream_type: mp4` with a direct `url` (most reliable)
   - `stream_type: embed` with a YouTube embed `url` + `watch_url` fallback

Why this matters:
- You can swap video providers later without changing the app contract.
- The backend controls access (short‑lived playback tokens).

---

## Video playback notes (YouTube error 153)

Some YouTube videos **cannot be embedded** (YouTube policy / owner settings). In that case WebView often shows a “configuration error” or YouTube error **153**.

- This is not fixable purely from the app.
- The reliable approach is:
  - Prefer `video_url` MP4 streams when available
  - Otherwise show YouTube embed + “Open in YouTube” fallback

---

## API quick test (optional)

### Signup
`POST /auth/signup`
```json
{ "name": "Test", "email": "test@example.com", "password": "password123" }
```

### Login
`POST /auth/login`
```json
{ "email": "test@example.com", "password": "password123" }
```

### Dashboard (requires access token)
`GET /dashboard`

---

## 3–5 min Loom video

Add your Loom link here:
- Loom: **<PASTE_LINK_HERE>**

Suggested outline (3–5 minutes):
1. Demo: signup → login → dashboard → play video → settings → logout
2. Architecture: frontend vs backend responsibilities (thin client)
3. JWT flow: access token + refresh token + secure storage + refresh-on-401
4. YouTube abstraction: dashboard tiles → playback token → stream URL
5. Known limitation: YouTube embed restrictions (error 153) + fallback approach
6. Where AI helped + what was fixed manually

---

## Where AI helped

Examples from this project:
- Quickly scaffolding endpoints/screens and wiring navigation
- Identifying auth failures caused by **wrong device base URL**
- Fixing password hashing issues by migrating to direct `bcrypt` usage
- Implementing the playback-token abstraction pattern and seed scripts
- Improving video playback UX (WebView fallback + MP4 support)

## Where AI output was wrong (and fixed manually)

Real issues encountered and corrected:
- **Assuming localhost works on a phone**: `127.0.0.1` from a physical device doesn’t reach your PC; required LAN IP / emulator host mapping.
- **YouTube embeds “always play” assumption**: some videos are not embeddable (error 153). The fix was to support MP4 URLs and provide a “Open in YouTube” fallback.
- **bcrypt/passlib edge behavior**: passlib/bcrypt compatibility caused misleading failures; switching to direct `bcrypt` fixed it.

---

## Troubleshooting

- Backend fails on startup with `MONGO_URI is not set`:
  - Fill `MONGO_URI` in `backend/.env`.
- Mobile shows “Network Error”:
  - Ensure `frontend/src/config/env.js` points to the correct base URL for your device/emulator.
  - Ensure your phone + PC are on the same Wi‑Fi.
  - Check Windows Firewall for port `5000`.
- No videos appear:
  - Run `python backend/scripts/seed_videos.py`.

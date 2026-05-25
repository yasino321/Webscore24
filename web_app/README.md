# WebScore Pro - Web Version

This is the full web version of the WebScore Pro application, featuring a FastAPI backend and a React frontend.

## Features
- **Dashboard**: Real-time analytics and search for business leads.
- **Leads Management**: Track, analyze, and manage potential clients.
- **Authentication**: Secure user accounts with JWT.
- **Customizable**: Users can provide their own API keys for Gemini, OpenAI, and Google Places.
- **Minimalist UI**: Fluid design with dark/light mode support (System default).

## Local Setup

### 1. Backend (FastAPI)
1. Navigate to `web_app/backend`.
2. Create a virtual environment: `python -m venv venv`.
3. Activate it: `source venv/bin/activate` (Linux) or `.\venv\Scripts\activate` (Windows).
4. Install dependencies: `pip install -r requirements.txt`.
5. Install Playwright browsers: `playwright install chromium`.
6. Start the server: `uvicorn app.main:app --reload`.

The backend will be available at `http://localhost:8000`.

### 2. Frontend (React)
1. Navigate to `web_app/frontend`.
2. Install dependencies: `npm install`.
3. Start the development server: `npm run dev`.

The frontend will be available at `http://localhost:5173`.

## Deployment
- **Backend**: Can be hosted on Render, Railway, or any VPS. Requires a persistent volume for the `webscore.db` SQLite file if you don't use an external database.
- **Frontend**: Can be hosted on Vercel, Netlify, or as static files.

## Technical Details
- **Backend**: FastAPI, SQLAlchemy (SQLite), Playwright (for scraping/screenshots), Google Generative AI (Gemini), OpenAI.
- **Frontend**: React, Vite, Tailwind CSS, Lucide React, Recharts.

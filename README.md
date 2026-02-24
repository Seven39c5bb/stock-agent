# Stock Intel Agent

Full-stack prototype based on the product design doc. It provides a Vue UI and a FastAPI backend that fetches stock data via LLM web search, computes indicators, and returns structured analysis.

## Structure
- frontend: Vue 3 + Vite + Tailwind
- backend: FastAPI + LLM web search

## Backend Setup (Windows)
1) Create a virtual env and install deps:

```
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

2) Configure environment:
- Copy backend/.env.example to backend/.env
- Fill in LLM_API_KEY for data retrieval and analysis output

3) Run the API:

```
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Frontend Setup
1) Install deps:

```
cd frontend
npm install
```

2) Optional: set API base url
- Copy frontend/.env.example to frontend/.env

3) Run dev server:

```
npm run dev
```

## Notes
- Data is not real-time; the UI displays a disclaimer.
- Backend now relies on LLM web search to retrieve market data and history before analysis.

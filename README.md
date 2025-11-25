# RGM Dashboard
RGM dashboard for pricing and promotion analysis.

## Streamlit App
- Switch to the Streamlit branch: `git checkout streamlit`.
- Ensure Python 3.10+ is installed.
- (Recommended) Create a virtual env: `python -m venv .venv && source .venv/bin/activate` (Windows: `.\.venv\Scripts\activate`).
- Install dependencies: `pip install -r requirements.txt`.
- Run the dashboard from the project root: `streamlit run main.py`.

## Backend (FastAPI)
- `cd backend`
- (Recommended) Create/activate a virtual env.
- Install dependencies: `pip install -r requirements.txt`.
- Start the API: `uvicorn controller.main_controller:app --reload --host 0.0.0.0 --port 8000 --app-dir src`.
- Health check: visit `http://localhost:8000/health`.

## Frontend (React + Vite)
- `cd frontend`
- Install dependencies: `npm install`.
- Start the dev server: `npm run dev` (defaults to `http://localhost:5173`).
- Update any API base URLs to point at your running backend if needed. 

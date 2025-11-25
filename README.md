# RGM Dashboard
RGM dashboard for pricing and promotion analysis.

## Streamlit App
- Switch to the Streamlit branch: `git checkout streamlit`.
- Ensure Python 3.10+ is installed.
- (Recommended) Create a virtual env: `python -m venv .venv && source .venv/bin/activate` (Windows: `.\.venv\Scripts\activate`).
- Install dependencies: `pip install -r requirements.txt`.
- Run the dashboard from the project root: `streamlit run main.py`.

---
## 🚀 Getting Started

### Prerequisites
- Python 3.10+ (virtual environment recommended)
- Node.js 22+
- npm 10+

### 1. Backend (FastAPI)
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  
pip install -r requirements.txt

# Run the API
uvicorn src.controller.main_controller:app --port 8000 --reload
```

### 2. Frontend Setup (React + Vite)

Follow these steps to install prerequisites, install dependencies, and run the React frontend that lives in this `frontend/` directory.

#### 1. Install Node.js (if needed)

- Check whether Node.js is already available:
   ```bash
   node -v
   npm -v
   ```
- If either command is missing, install the Long-Term Support (LTS) release of Node.js (which bundles npm):
   - **macOS**: Download the installer from https://nodejs.org/en/download and run it.
- Restart your terminal and re-run `node -v` and `npm -v` to verify the installation.

> Minimum recommended version: **Node.js 22.x** with the npm version that ships alongside it.

#### Install Node.js via nvm (alternative method)

If you prefer managing Node.js versions with nvm:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
export NVM_DIR="$HOME/.nvm"
source "$NVM_DIR/nvm.sh"
nvm install --lts
nvm use --lts
```

Re-open your terminal or source your shell profile after the install so `nvm` is available in every session.

#### 2. Install project dependencies

From the `frontend/` directory run:

```bash
npm install
```

This command reads `package.json` and downloads everything into `node_modules/`.

#### 3. Run the development server

To start Vite in dev mode with hot module replacement:

```bash
npm run dev
```

- Default URL: http://localhost:5173
- Press `q` or `Ctrl+C` in the terminal to stop the server.

## Development & Conventions
- Formatting: use `black` (backend) and `prettier` (frontend) to keep a consistent style.
- Structure: prefer small, focused classes/modules; keep API and UI concerns separated.
- Logging: use Python’s `logging` (not `print`) and browser console logging only for debug-level details.

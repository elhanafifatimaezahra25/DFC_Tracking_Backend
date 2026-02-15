DFC Tracking - Backend (Prototype)

Minimal FastAPI backend scaffold for DFC/ECO tracking.

Prerequisites
- Python 3.10+

Quick start
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Environment
- Copy `.env.example` to `.env` and set `SECRET_KEY`.

What's included
- JWT authentication endpoints (`/auth/register`, `/auth/login`)
- Basic `User` and `DFC` models
- CRUD endpoints for DFCs
- Placeholder endpoint for file upload (OCR integration later)

Next steps
- Add real OCR pipeline
- Add tests and CI
- Add frontend scaffold

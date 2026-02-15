from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .routes import auth as auth_routes, dfc as dfc_routes, admin as admin_routes, upload as upload_routes
from .services.dashboard import get_basic_stats
from .core.middleware import logging_middleware

app = FastAPI(title="DFC Tracking API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register application-level HTTP middleware
app.middleware("http")(logging_middleware)


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(auth_routes.router)
app.include_router(dfc_routes.router)
app.include_router(admin_routes.router)
app.include_router(upload_routes.router)


@app.get("/")
def root():
    return {"message": "DFC Tracking API - prototype"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/dashboard/basic")
def dashboard_basic():
    return get_basic_stats()

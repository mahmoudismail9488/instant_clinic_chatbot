"""FastAPI application entrypoint for CliniRAG."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from backend.app.api.routes_query import router as query_router
from backend.app.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="CliniRAG API",
        description="Guideline-grounded retrieval + generation for Instant Clinic",
        version="0.1.0",
    )
    # Local Vite (often :8080) → API (:8000) is always cross-origin.
    # Browser fetch does not send cookies to the API, so credentials=False
    # lets us allow all origins (avoids Disallowed CORS origin 400).
    origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["*"],
        allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(query_router)

    @app.get("/", include_in_schema=False)
    def root() -> RedirectResponse:
        return RedirectResponse(url="/docs")

    return app


app = create_app()


def main() -> None:
    import uvicorn

    # Drop cached settings so .env / code CORS changes apply on restart.
    get_settings.cache_clear()
    settings = get_settings()
    uvicorn.run(
        "backend.app.api.app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
    )


if __name__ == "__main__":
    main()

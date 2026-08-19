"""FastAPI application entrypoint for GlucoRAG."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from backend.app.api.routes_query import router as query_router
from backend.app.config import get_settings
from backend.app.services.runtime import init_app_state, reset_app_state


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load index + LLM client once per worker process."""
    get_settings.cache_clear()
    state = init_app_state()
    app.state.clinirag = state
    yield
    reset_app_state()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="GlucoRAG API",
        description="Guideline-grounded retrieval + generation for GlucoRAG",
        version="0.2.0",
        lifespan=lifespan,
    )
    origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
    # Production: set CORS_ORIGINS to exact frontend origins (Vercel URL, custom domain).
    # Local: keep localhost regex for Vite ports.
    allow_regex = settings.cors_origin_regex.strip() or None
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["*"],
        allow_origin_regex=allow_regex,
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

    get_settings.cache_clear()
    settings = get_settings()
    uvicorn.run(
        "backend.app.api.app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
        workers=settings.api_workers,
    )


if __name__ == "__main__":
    main()

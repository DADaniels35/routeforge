from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.graph.adjacency_list import GraphValidationError

app = FastAPI(
    title="RouteForge",
    version="0.1.0",
    description="Weighted directed graph route optimisation API.",
)
app.include_router(router)
app.mount("/dashboard", StaticFiles(directory="dashboard", html=True), name="dashboard")


@app.exception_handler(GraphValidationError)
def graph_validation_exception_handler(
    _request: Request, exc: GraphValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={"detail": str(exc)},
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

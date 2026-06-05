from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    summary="Return service health status",
    responses={200: {"description": "Service is healthy and ready to accept traffic."}},
)
def health_check() -> dict[str, str]:
    """Expose a simple health endpoint for uptime checks."""
    return {"status": "ok", "service": "mergeflow-test-repo"}

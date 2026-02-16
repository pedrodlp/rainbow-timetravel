from fastapi import APIRouter

router = APIRouter()


@router.post("/health")
def healthcheck() -> dict[str, bool]:
    return {"ok": True}

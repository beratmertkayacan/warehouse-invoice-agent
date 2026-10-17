from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.approvals import ApprovalStore, InvalidStateError, NotFoundError
from app.models import Approval, ShipmentRelease

app = FastAPI(title="Warehouse Outbound Invoice Agent", version="0.1.0")
store = ApprovalStore()


@app.exception_handler(NotFoundError)
async def handle_not_found(request: Request, error: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"error": str(error)})


@app.exception_handler(InvalidStateError)
async def handle_invalid_state(request: Request, error: InvalidStateError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"error": str(error)})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/approvals/{approval_id}")
def get_approval(approval_id: str) -> Approval:
    return store.get(approval_id)


@app.post("/approvals/{approval_id}/approve")
def approve_request(approval_id: str) -> Approval:
    return store.approve(approval_id)


@app.post("/approvals/{approval_id}/reject")
def reject_request(approval_id: str) -> Approval:
    return store.reject(approval_id)


@app.post("/shipments/{request_id}/release")
def release_shipment(request_id: str) -> ShipmentRelease:
    return store.release(request_id)

from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from openai import OpenAIError

from app.agent import FieldExtractor, run_agent
from app.approvals import ApprovalStore, InvalidStateError, NotFoundError
from app.config import load_settings
from app.llm import create_extractor
from app.models import AgentRequest, AgentResponse, Approval, ShipmentRelease

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

app = FastAPI(title="Warehouse Outbound Invoice Agent", version="0.1.0")
store = ApprovalStore()


@lru_cache
def get_extractor() -> FieldExtractor:
    return create_extractor(load_settings())


@app.exception_handler(NotFoundError)
async def handle_not_found(request: Request, error: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"error": str(error)})


@app.exception_handler(InvalidStateError)
async def handle_invalid_state(request: Request, error: InvalidStateError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"error": str(error)})


@app.exception_handler(OpenAIError)
async def handle_llm_error(request: Request, error: OpenAIError) -> JSONResponse:
    return JSONResponse(
        status_code=502, content={"error": "The language model service is not available"}
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/agent/chat")
def agent_chat(
    request: AgentRequest, extractor: FieldExtractor = Depends(get_extractor)
) -> AgentResponse:
    return run_agent(request.message, extractor, store, request.session_id)


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

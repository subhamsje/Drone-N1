from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(prefix="/edge", tags=["edge"])


class EdgeConnectionBody(BaseModel):
    cloud_connected: bool


@router.get("/status")
async def edge_status(request: Request):
    return request.app.state.workflow.edge.get_status()


@router.post("/connection")
async def set_connection(body: EdgeConnectionBody, request: Request):
    request.app.state.workflow.edge.set_cloud_connected(body.cloud_connected)
    return request.app.state.workflow.edge.get_status()

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(prefix="/execution", tags=["execution"])


class ExecuteCommandBody(BaseModel):
    command: str
    params: dict = {}


class PX4ModeBody(BaseModel):
    mode: str  # simulation | sitl | hitl | live


@router.get("/status")
async def execution_status(request: Request):
    workflow = request.app.state.workflow
    intel = getattr(workflow, "intelligence", None)
    if intel:
        stack = intel.flight_stack.status()
        tel = await intel.flight_stack.get_live_telemetry()
        return {**stack, "telemetry": tel}
    kernel = workflow.bridge.os_kernel
    return {
        "px4_connected": kernel.px4.executor._connected,
        "mode": kernel.px4.executor.mode.value,
        "audit_log": kernel.px4.executor.get_audit_log(10),
        "telemetry": await kernel.px4.executor.get_telemetry(),
    }


@router.post("/command")
async def execute_command(body: ExecuteCommandBody, request: Request):
    workflow = request.app.state.workflow
    intel = getattr(workflow, "intelligence", None)
    cmd = body.command.upper()

    if cmd == "CONNECT":
        if not intel:
            raise HTTPException(503, "Mission intelligence not initialized")
        p = body.params
        return await intel.flight_stack.connect(
            connection_type=p.get("type", "udp"),
            uri=p.get("uri"),
            stack=p.get("stack", "px4"),
            vehicle_mode=p.get("mode", "sitl"),
        )

    if cmd == "DISCONNECT":
        if intel:
            return await intel.flight_stack.disconnect()
        workflow.bridge.os_kernel.px4.stop()
        return {"connected": False}

    if intel:
        return await intel.flight_stack.execute_command(body.command, body.params)

    kernel = workflow.bridge.os_kernel
    result = await kernel.px4.executor.execute(body.command, body.params)
    return result.to_dict()


@router.get("/safety")
async def safety_status(request: Request):
    return request.app.state.workflow.bridge.os_kernel.safety.get_status()


@router.get("/safety/audit")
async def safety_audit(request: Request, limit: int = 50):
    return {"audit": request.app.state.workflow.bridge.os_kernel.safety.get_audit_trail(limit)}


@router.post("/safety/kill-switch")
async def kill_switch(request: Request, engage: bool = True):
    safety = request.app.state.workflow.bridge.os_kernel.safety
    if engage:
        safety.engage_kill_switch("api")
    else:
        safety.release_kill_switch()
    return safety.get_status()

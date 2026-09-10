from fastapi import APIRouter, HTTPException, Path
from models.schemas import (
    GuardianAdd, GuardianRemove, 
    RecoveryRequestPayload, RecoveryApprovePayload, 
    RecoveryExecutePayload, RecoveryCancelPayload
)
from services.blockchain import (
    is_connected,
    add_guardian_on_chain,
    remove_guardian_on_chain,
    get_guardians_from_chain,
    request_recovery_on_chain,
    approve_recovery_on_chain,
    execute_recovery_on_chain,
    cancel_recovery_on_chain,
    get_recovery_status_on_chain
)

router = APIRouter()

@router.post("/guardians/add")
def add_guardian(data: GuardianAdd):
    if not is_connected():
        raise HTTPException(status_code=503, detail="Blockchain node not connected")
    try:
        result = add_guardian_on_chain(data.guardian_address)
        return {"message": "Guardian added", **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/guardians/remove")
def remove_guardian(data: GuardianRemove):
    if not is_connected():
        raise HTTPException(status_code=503, detail="Blockchain node not connected")
    try:
        result = remove_guardian_on_chain(data.guardian_address)
        return {"message": "Guardian removed", **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/guardians/{wallet_address}")
def get_guardians(wallet_address: str):
    if not is_connected():
        raise HTTPException(status_code=503, detail="Blockchain node not connected")
    try:
        return get_guardians_from_chain(wallet_address)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/request")
def request_recovery(data: RecoveryRequestPayload):
    if not is_connected():
        raise HTTPException(status_code=503, detail="Blockchain node not connected")
    try:
        result = request_recovery_on_chain(data.identity_address, data.new_owner_address)
        return {"message": "Recovery requested", **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/approve")
def approve_recovery(data: RecoveryApprovePayload):
    if not is_connected():
        raise HTTPException(status_code=503, detail="Blockchain node not connected")
    try:
        result = approve_recovery_on_chain(data.recovery_id)
        return {"message": "Recovery approved", **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/execute")
def execute_recovery(data: RecoveryExecutePayload):
    if not is_connected():
        raise HTTPException(status_code=503, detail="Blockchain node not connected")
    try:
        result = execute_recovery_on_chain(data.recovery_id)
        return {"message": "Recovery executed", **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/cancel")
def cancel_recovery(data: RecoveryCancelPayload):
    if not is_connected():
        raise HTTPException(status_code=503, detail="Blockchain node not connected")
    try:
        result = cancel_recovery_on_chain(data.recovery_id)
        return {"message": "Recovery cancelled", **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/status/{recovery_id}")
def get_recovery_status(recovery_id: int):
    if not is_connected():
        raise HTTPException(status_code=503, detail="Blockchain node not connected")
    try:
        return get_recovery_status_on_chain(recovery_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

from fastapi import APIRouter, HTTPException
from models.schemas import AuditLogPayload
from services.blockchain import log_audit_on_chain, is_connected

router = APIRouter()

@router.post("/log")
def log_audit(data: AuditLogPayload):
    if not is_connected():
        raise HTTPException(status_code=503, detail="Blockchain node not connected")
    try:
        result = log_audit_on_chain(data.action, data.details)
        return {"message": "Audit log recorded on-chain", **result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

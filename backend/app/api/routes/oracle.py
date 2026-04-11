from fastapi import APIRouter, HTTPException

from app.schemas.oracle import EncryptedPayload, OracleRequest, OracleResponse
from app.services.oracle_chat_service import ChatProcessingError, OracleChatService

router = APIRouter(tags=["oracle"])


@router.post("/chat", response_model=OracleResponse)
@router.post("/oracle/chat", response_model=OracleResponse, include_in_schema=False)
async def oracle_chat(request: OracleRequest) -> OracleResponse:
    service = OracleChatService()
    try:
        result = await service.process_chat(
            nonce=request.encrypted.nonce,
            ciphertext=request.encrypted.ciphertext,
        )
        return OracleResponse(
            encrypted=EncryptedPayload(
                nonce=result.nonce,
                ciphertext=result.ciphertext,
            ),
            audit_hash=result.audit_hash,
        )
    except ChatProcessingError as exc:
        raise HTTPException(status_code=500, detail="Oracle processing failed") from exc


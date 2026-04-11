from fastapi import APIRouter, HTTPException

from app.schemas.oracle import EncryptedPayload, OracleRequest, OracleResponse, PublicApiContext
from app.services.oracle_chat_service import ChatProcessingError, OracleChatService

router = APIRouter(tags=["oracle"])


@router.post("/chat", response_model=OracleResponse, response_model_exclude_none=True)
@router.post("/oracle/chat", response_model=OracleResponse, include_in_schema=False, response_model_exclude_none=True)
async def oracle_chat(request: OracleRequest) -> OracleResponse:
    service = OracleChatService()
    try:
        result = await service.process_chat(
            nonce=request.encrypted.nonce,
            ciphertext=request.encrypted.ciphertext,
            request_id=request.request_id,
        )
        return OracleResponse(
            encrypted=EncryptedPayload(
                nonce=result.nonce,
                ciphertext=result.ciphertext,
            ),
            audit_hash=result.audit_hash,
            public_api=(
                PublicApiContext(
                    provider=result.public_api.provider,
                    title=result.public_api.title,
                    summary=result.public_api.summary,
                    url=result.public_api.url,
                )
                if result.public_api
                else None
            ),
        )
    except ChatProcessingError as exc:
        raise HTTPException(status_code=500, detail="Oracle processing failed") from exc


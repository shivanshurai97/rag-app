from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import db
from app.services.qa_service import qa_service
from app.services.auth_service import auth_service
from app.api.pydantic_models import QARequest, QAResponse

router = APIRouter()

@router.post("/query", response_model=QAResponse)
async def qa_endpoint(
    request: QARequest,
    session: AsyncSession = Depends(db.get_session),
    current_user = Depends(auth_service.get_current_user)
):
    try:
        answer = await qa_service.get_answer_for_query(request.question, session, current_user.id)
        return QAResponse(answer=answer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        ) 
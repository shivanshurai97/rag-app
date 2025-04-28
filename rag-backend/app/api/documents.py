from fastapi import APIRouter, UploadFile, File, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.db.base import db
from app.services.document_service import document_service
from app.services.auth_service import auth_service
from app.db.models import User
from app.api.pydantic_models import DocumentSelectionRequest, DocumentOut
from app.core.exceptions import ValidationError, DatabaseError

router = APIRouter()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(db.get_session),
    current_user: User = Depends(auth_service.get_current_user)
):
    try:
        result = await document_service.process_and_store_document(file, session, current_user)
        return result
    except (ValidationError, DatabaseError) as e:
        raise
    except Exception as e:
        raise ValidationError(str(e))

@router.get("/list", response_model=List[DocumentOut])
async def list_documents(
    session: AsyncSession = Depends(db.get_session),
    current_user: User = Depends(auth_service.get_current_user)
):
    try:
        documents = await document_service.get_user_documents(session, current_user.id)
        return documents or []  # Return empty list if no documents found
    except (ValidationError, DatabaseError) as e:
        raise
    except Exception as e:
        raise ValidationError(str(e))

@router.post("/select")
async def toggle_document_qa(
    request: DocumentSelectionRequest,
    session: AsyncSession = Depends(db.get_session),
    current_user: User = Depends(auth_service.get_current_user)
):
    try:
        result = await document_service.toggle_document_qa(request.document_ids, current_user.id, session)
        return result
    except (ValidationError, DatabaseError) as e:
        raise
    except Exception as e:
        raise ValidationError(str(e)) 
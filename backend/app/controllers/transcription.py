import shutil
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile

from app.auth import Claims, validate_token
from app.db import session_factory
from app.repositories.plans import PlanRepository
from app.repositories.usage import UsageRepository
from app.services.transcription import TranscriptionEngine
from app.services.usage import UsageService
from app.messages import message

router = APIRouter()
engine = TranscriptionEngine()


@router.post("/transcribe")
def transcribe(file: UploadFile = File(...), claims: Claims = Depends(validate_token), accept_language: str | None = Header(None, alias='Accept-Language')) -> dict[str, str]:
    language = accept_language
    with session_factory()() as session:
        plan = PlanRepository(session).get(claims.plan)
        if not plan:
            raise HTTPException(status_code=404, detail=message('plan_not_found', language))
        usage = UsageService(UsageRepository(session))
        if not usage.has_remaining_quota(claims.subject_id, plan):
            raise HTTPException(status_code=403, detail=message('quota_exhausted', language))

        temporary_path: Path | None = None
        try:
            suffix = Path(file.filename or "").suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temporary_file:
                temporary_path = Path(temporary_file.name)
                shutil.copyfileobj(file.file, temporary_file)
            text = engine.transcribe(temporary_path)
            usage.record_usage(claims.subject_id, len(text.split()))
            return {"text": text}
        finally:
            if temporary_path:
                temporary_path.unlink(missing_ok=True)

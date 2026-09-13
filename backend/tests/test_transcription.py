import io
import os
import sys
import types
import wave
from pathlib import Path

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from starlette.datastructures import UploadFile

from app.auth import Claims
from app.db import Base
from app.main import app
from app.models import Plan, UsagePeriod
from app.repositories.usage import UsageRepository
from app.services.usage import UsageService
from app.services.transcription import TranscriptionEngine


class _SessionContext:
    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


class _PlanRepository:
    def __init__(self, session):
        pass

    def get(self, tier_id):
        return object()


class _UsageService:
    remaining = True
    recorded = []

    def __init__(self, repository):
        pass

    def has_remaining_quota(self, subject_id, plan):
        return self.remaining

    def record_usage(self, subject_id, word_count):
        self.recorded.append((subject_id, word_count))


def _patch_controller(monkeypatch):
    import app.controllers.transcription as controller

    _UsageService.remaining = True
    _UsageService.recorded = []
    monkeypatch.setattr(controller, "session_factory", lambda: lambda: _SessionContext())
    monkeypatch.setattr(controller, "PlanRepository", _PlanRepository)
    monkeypatch.setattr(controller, "UsageService", _UsageService)
    return controller


def test_transcribe_rejects_missing_token():
    with TestClient(app) as client:
        assert client.post("/transcribe", files={"file": ("audio.wav", b"audio")}).status_code == 401


def test_engine_is_lazy_and_falls_back_to_cpu(monkeypatch, tmp_path):
    attempts = []

    class FakeModel:
        def __init__(self, model_size, device, compute_type):
            attempts.append((model_size, device, compute_type))
            if device == "cuda":
                raise RuntimeError("CUDA unavailable")

        def transcribe(self, path, **kwargs):
            return iter([types.SimpleNamespace(text="hello world")]), object()

    monkeypatch.setitem(sys.modules, "faster_whisper", types.SimpleNamespace(WhisperModel=FakeModel))
    engine = TranscriptionEngine(model_size="tiny", device="cuda", compute_type="float16")
    assert attempts == []

    audio = tmp_path / "audio.wav"
    audio.write_bytes(b"fake")
    assert engine.transcribe(audio) == "hello world"
    assert attempts == [("tiny", "cuda", "float16"), ("tiny", "cpu", "int8")]
    assert engine.transcribe(audio) == "hello world"
    assert len(attempts) == 2


def test_transcribe_rejects_exhausted_quota_without_calling_engine(monkeypatch):
    controller = _patch_controller(monkeypatch)
    _UsageService.remaining = False
    called = False

    def fail(*args):
        nonlocal called
        called = True
        raise AssertionError("engine must not run")

    monkeypatch.setattr(controller.engine, "transcribe", fail)
    with pytest.raises(HTTPException) as error:
        controller.transcribe(UploadFile(io.BytesIO(b"audio"), filename="audio.wav"), Claims("user", "plan-free"))
    assert error.value.status_code == 403
    assert called is False


def test_transcribe_records_words_and_removes_temp_file(monkeypatch):
    controller = _patch_controller(monkeypatch)
    paths = []

    def transcribe(path):
        paths.append(path)
        return "one  two three"

    monkeypatch.setattr(controller.engine, "transcribe", transcribe)
    response = controller.transcribe(UploadFile(io.BytesIO(b"audio"), filename="audio.wav"), Claims("user", "plan-free"))
    assert response == {"text": "one  two three"}
    assert _UsageService.recorded == [("user", 3)]
    assert paths and not paths[0].exists()


def test_transcribe_records_usage_in_postgres(monkeypatch):
    database_url = os.environ.get("DATABASE_URL", "postgresql+psycopg://speech:speech@localhost:5433/speech")
    database = create_engine(database_url)
    Base.metadata.create_all(database)
    subject_id = "transcription-integration-user"
    with Session(database) as session:
        session.query(UsagePeriod).filter_by(subject_id=subject_id).delete()
        session.query(Plan).filter_by(tier_id="plan-transcription-test").delete()
        session.add(Plan(tier_id="plan-transcription-test", name_en="Test", name_es="Prueba", keycloak_role="plan-transcription-test", word_limit=100, period_unit="month"))
        session.commit()

    import app.controllers.transcription as controller

    monkeypatch.setenv("DATABASE_URL", database_url)
    app.dependency_overrides[controller.validate_token] = lambda: Claims(subject_id, "plan-transcription-test")
    monkeypatch.setattr(controller.engine, "transcribe", lambda _: "one two three")
    audio = io.BytesIO()
    with wave.open(audio, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(8000)
        wav.writeframes(b"\0\0" * 800)
    audio.seek(0)
    try:
        with TestClient(app) as client:
            response = client.post("/transcribe", files={"file": ("sample.wav", audio, "audio/wav")})
        assert response.status_code == 200
        assert response.json() == {"text": "one two three"}
    finally:
        app.dependency_overrides.clear()

    with Session(database) as session:
        usage = UsageRepository(session).get(subject_id, UsageService.current_period())
        assert usage.words_used == 3


def test_transcribe_removes_temp_file_and_skips_usage_on_failure(monkeypatch):
    controller = _patch_controller(monkeypatch)
    paths = []

    def transcribe(path):
        paths.append(path)
        raise RuntimeError("bad audio")

    monkeypatch.setattr(controller.engine, "transcribe", transcribe)
    with pytest.raises(RuntimeError):
        controller.transcribe(UploadFile(io.BytesIO(b"corrupt"), filename="audio.wav"), Claims("user", "plan-free"))
    assert paths and not paths[0].exists()
    assert _UsageService.recorded == []

from typing import Any
from pydantic import BaseModel, Field


class ConsentUpdateRequest(BaseModel):
    consent_type: str = Field(..., min_length=1)
    consent_given: bool


class DataExportRequestModel(BaseModel):
    include_audit_trail: bool = False
    format: str = Field("json", pattern=r"^(json|csv)$")


def get_privacy_service() -> Any:
    class Dummy:
        def record_consent(self, *args: Any, **kwargs: Any) -> dict:
            return {"status": "ok"}

        def export_user_data(self, *args: Any, **kwargs: Any) -> dict:
            return {"status": "ok", "data": {}}

    return Dummy()



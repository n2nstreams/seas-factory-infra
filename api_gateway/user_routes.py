from pydantic import BaseModel, EmailStr, Field, ValidationError, model_validator, field_validator


class UserRegistrationRequest(BaseModel):
    firstName: str = Field(..., min_length=1)
    lastName: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=8)
    confirmPassword: str = Field(..., min_length=8)
    agreeToTerms: bool
    gdprConsent: bool

    @field_validator('gdprConsent')
    @classmethod
    def require_gdpr_consent(cls, v: bool) -> bool:
        if not v:
            raise ValueError('GDPR consent is required')
        return v

    @field_validator('agreeToTerms')
    @classmethod
    def require_terms(cls, v: bool) -> bool:
        if not v:
            raise ValueError('You must agree to the Terms')
        return v

    @model_validator(mode='after')
    def validate_passwords_and_consent(self):  # type: ignore[override]
        if self.password != self.confirmPassword:
            raise ValueError('passwords do not match')
        return self



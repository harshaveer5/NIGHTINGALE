import re

from pydantic import BaseModel, EmailStr, Field, field_validator

PASSWORD_REGEX = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$")


class UserCreate(BaseModel):

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
        description=(
            "Password must be 8-128 characters long and contain "
            "at least one uppercase letter, one lowercase letter, "
            "and one number."
        ),
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:

        if not PASSWORD_REGEX.match(value):
            raise ValueError(
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, and one number."
            )

        return value

    model_config = {
        "json_schema_extra": {
            "example": {"email": "john@example.com", "password": "SecurePass123"}
        }
    }


class UserResponse(BaseModel):

    id: int
    email: EmailStr

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {"example": {"id": 1, "email": "john@example.com"}},
    }


class UserLogin(BaseModel):

    email: EmailStr

    password: str = Field(min_length=1, max_length=128)

    model_config = {
        "json_schema_extra": {
            "example": {"email": "john@example.com", "password": "SecurePass123"}
        }
    }

from pydantic import BaseModel, ConfigDict, Field


class DiagnosticCentreCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    location: str = Field(min_length=2, max_length=255)


class DiagnosticCentreResponse(BaseModel):
    id: int
    name: str
    location: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class DiagnosticTestCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    description: str | None = None


class DiagnosticTestResponse(BaseModel):
    id: int
    name: str
    description: str | None

    model_config = ConfigDict(from_attributes=True)
class CentreTestCreate(BaseModel):
    centre_id: int
    test_id: int
    price: float = Field(gt=0)


class CentreTestResponse(BaseModel):
    id: int
    centre_id: int
    test_id: int
    price: float
    is_available: bool

    model_config = ConfigDict(from_attributes=True)
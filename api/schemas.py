from pydantic import BaseModel, Field


class BlurParams(BaseModel):
    radius: float = Field(default=2.0, ge=1.0, le=10.0, description="Gaussian blur radius (1–10)")

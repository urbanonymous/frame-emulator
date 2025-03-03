"""Configuration class for the Frame Emulator."""

from pydantic import BaseModel, Field, field_validator


class EmulatorConfig(BaseModel):
    """Configuration for the Frame Emulator."""

    width: int = Field(default=640, ge=1, description="Display width in pixels")
    height: int = Field(default=400, ge=1, description="Display height in pixels")
    fps: int = Field(default=60, ge=1, le=240, description="Target frames per second")
    title: str = Field(default="Frame Glasses Emulator", description="Window title")
    scale: float = Field(
        default=1.0, ge=0.25, le=10.0, description="Initial display scale factor"
    )

    @field_validator("width", "height")
    @classmethod
    def dimensions_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Dimensions must be positive")
        return v

    model_config = {"validate_assignment": True}

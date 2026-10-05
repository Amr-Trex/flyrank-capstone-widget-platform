from typing import Literal, Optional

from pydantic import BaseModel, Field


class WidgetField(BaseModel):
    name: str = Field(min_length=1, max_length=50, pattern=r"^[a-zA-Z0-9_]+$")
    label: str = Field(min_length=1, max_length=100)
    type: Literal["text", "email", "textarea"] = "text"
    required: bool = False


class WidgetCreate(BaseModel):
    type: Literal["signup_form", "cta", "popover"] = "signup_form"
    title: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=500)
    button_text: str = Field(default="Submit", min_length=1, max_length=50)
    fields: list[WidgetField] = Field(
        default_factory=lambda: [
            WidgetField(name="email", label="Email", type="email", required=True)
        ]
    )


class WidgetUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=120)
    description: Optional[str] = Field(default=None, max_length=500)
    button_text: Optional[str] = Field(default=None, min_length=1, max_length=50)
    status: Optional[Literal["active", "inactive"]] = None
    fields: Optional[list[WidgetField]] = None


class WidgetOut(BaseModel):
    public_id: str
    type: str
    title: str
    description: str
    button_text: str
    fields: list[dict]
    status: str
    created_at: str
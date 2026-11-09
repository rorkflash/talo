"""Input specification: exactly one of a workspace path, an inline value or a result ref."""

import json

from pydantic import BaseModel, ConfigDict, JsonValue, model_validator

MAX_INLINE_BYTES = 64 * 1024


class InputSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str | None = None
    inline: JsonValue | None = None
    ref: str | None = None

    @model_validator(mode="after")
    def _exactly_one(self) -> "InputSpec":
        given = [name for name in ("path", "inline", "ref") if getattr(self, name) is not None]
        if len(given) != 1:
            raise ValueError(f"exactly one of path, inline or ref is required, got {given}")
        if self.inline is not None and len(json.dumps(self.inline)) > MAX_INLINE_BYTES:
            raise ValueError(f"inline value exceeds {MAX_INLINE_BYTES} bytes; pass a path instead")
        return self

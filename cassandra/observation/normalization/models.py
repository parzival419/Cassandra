"""Domain models for normalized observation data."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(slots=True)
class NormalizedWindow:
    """Represent structured meaning extracted from a raw window title."""

    raw_title: str | None
    application: str | None = None
    document: str | None = None
    workspace: str | None = None
    is_elevated: bool = False
    parser_name: str = "generic"
    is_dirty: bool = False

    @property
    def is_identified(self) -> bool:
        """Return whether an application was confidently identified."""

        return self.application is not None

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-friendly representation."""

        data = asdict(self)
        data["is_identified"] = self.is_identified
        return data
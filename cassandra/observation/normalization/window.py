"""Normalize raw foreground-window titles into structured data."""

from __future__ import annotations

from cassandra.observation.normalization.models import NormalizedWindow


class WindowNormalizer:
    """Convert raw window titles into structured window information."""

    VSCODE_APPLICATION = "Visual Studio Code"
    ELEVATED_SUFFIX = " [Administrator]"
    VSCODE_DIRTY_PREFIX = "● "

    def normalize(
        self,
        raw_title: str | None,
    ) -> NormalizedWindow:
        """Normalize a raw window title."""

        if raw_title is None:
            return NormalizedWindow(raw_title=None)

        title = raw_title.strip()

        if not title:
            return NormalizedWindow(raw_title=None)

        is_elevated = title.endswith(self.ELEVATED_SUFFIX)

        normalized_title = self._remove_elevated_suffix(
            title
        )

        if self._is_vscode_title(normalized_title):
            return self._normalize_vscode(
                raw_title=title,
                normalized_title=normalized_title,
                is_elevated=is_elevated,
            )

        return NormalizedWindow(
            raw_title=title,
            is_elevated=is_elevated,
        )

    def _is_vscode_title(self, title: str) -> bool:
        """Return whether a title appears to belong to VS Code."""

        return title.endswith(
            f" - {self.VSCODE_APPLICATION}"
        )

    def _normalize_vscode(
        self,
        raw_title: str,
        normalized_title: str,
        is_elevated: bool,
    ) -> NormalizedWindow:
        """Normalize a Visual Studio Code window title."""

        content = normalized_title.removesuffix(
            f" - {self.VSCODE_APPLICATION}"
        )

        parts = [
            part.strip()
            for part in content.split(" - ")
            if part.strip()
        ]

        document: str | None = None
        workspace: str | None = None
        is_dirty = False

        if len(parts) >= 2:
            document = parts[0]
            workspace = " - ".join(parts[1:])

        elif len(parts) == 1:
            workspace = parts[0]

        if (
            document is not None
            and document.startswith(self.VSCODE_DIRTY_PREFIX)
        ):
            is_dirty = True
            document = document.removeprefix(
                self.VSCODE_DIRTY_PREFIX
            ).strip()

        return NormalizedWindow(
            raw_title=raw_title,
            application=self.VSCODE_APPLICATION,
            document=document,
            workspace=workspace,
            is_elevated=is_elevated,
            is_dirty=is_dirty,
            parser_name="vscode",
        )

    def _remove_elevated_suffix(
        self,
        title: str,
    ) -> str:
        """Remove the Windows elevation suffix when present."""

        if title.endswith(self.ELEVATED_SUFFIX):
            return title.removesuffix(
                self.ELEVATED_SUFFIX
            )

        return title
from __future__ import annotations

import win32gui


def list_visible_windows() -> list[str]:
    """Return the titles of all visible desktop windows."""
    windows: list[str] = []

    def callback(hwnd: int, _: object) -> None:
        if not win32gui.IsWindowVisible(hwnd):
            return

        title = win32gui.GetWindowText(hwnd).strip()

        if title:
            windows.append(title)

    win32gui.EnumWindows(callback, None)
    return windows


if __name__ == "__main__":
    print("Visible windows:")
    print("-" * 60)

    for window_title in list_visible_windows():
        print(window_title)

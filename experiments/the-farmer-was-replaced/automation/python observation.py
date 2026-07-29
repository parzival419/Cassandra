from __future__ import annotations

import ctypes
import hashlib
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import win32con
import win32gui
import win32ui
from PIL import Image, ImageGrab


# ============================================================
# CONFIGURATION
# ============================================================

WINDOW_TITLE_FRAGMENT = "TheFarmerWasReplaced"

EXPERIMENT_NAME = "the-farmer-was-replaced"

EXPERIMENT_ROOT = Path(
    r"C:\Projects\Cassandra\experiments\the-farmer-was-replaced"
)

SCREENSHOT_DIRECTORY = EXPERIMENT_ROOT / "screenshots"
OBSERVATION_DIRECTORY = EXPERIMENT_ROOT / "logs" / "observations"

TARGET_WINDOW_LEFT = 50
TARGET_WINDOW_TOP = 50
TARGET_WINDOW_WIDTH = 1000
TARGET_WINDOW_HEIGHT = 700

WINDOW_MOVE_DELAY_SECONDS = 1.0

# Windows PrintWindow flags
PW_CLIENTONLY = 0x00000001
PW_RENDERFULLCONTENT = 0x00000002


# ============================================================
# DATA MODELS
# ============================================================

@dataclass
class WindowBounds:
    left: int
    top: int
    right: int
    bottom: int

    @property
    def width(self) -> int:
        return self.right - self.left

    @property
    def height(self) -> int:
        return self.bottom - self.top


@dataclass
class ImageMetadata:
    width: int
    height: int
    mode: str
    format: str
    sha256: str


@dataclass
class Observation:
    observation_id: str
    timestamp_utc: str
    environment: str

    window_title: str
    window_handle: int
    window_found: bool
    window_visible: bool
    window_minimized: bool

    window_bounds: Optional[WindowBounds]
    client_bounds: Optional[WindowBounds]

    screenshot_path: Optional[str]
    metadata_path: str

    capture_success: bool
    capture_method: Optional[str]
    image: Optional[ImageMetadata]

    error: Optional[str]


# ============================================================
# DPI CONFIGURATION
# ============================================================

def enable_dpi_awareness() -> None:
    """
    Prevent Windows display scaling from causing incorrect coordinates.
    """

    try:
        # Per-monitor DPI awareness on newer versions of Windows.
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            # Fallback for older Windows versions.
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


# ============================================================
# WINDOW DISCOVERY AND MANAGEMENT
# ============================================================

def find_window_by_title(title_fragment: str) -> Optional[int]:
    """
    Find the first visible top-level window whose title contains
    the supplied title fragment.
    """

    matching_handle: Optional[int] = None

    def callback(hwnd: int, _: object) -> None:
        nonlocal matching_handle

        if matching_handle is not None:
            return

        if not win32gui.IsWindowVisible(hwnd):
            return

        title = win32gui.GetWindowText(hwnd).strip()

        if title_fragment.lower() in title.lower():
            matching_handle = hwnd

    win32gui.EnumWindows(callback, None)
    return matching_handle


def restore_and_position_window(hwnd: int) -> None:
    """
    Restore the window if minimized, then move and resize it to a
    predictable location.
    """

    if win32gui.IsIconic(hwnd):
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    else:
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)

    win32gui.SetWindowPos(
        hwnd,
        win32con.HWND_TOP,
        TARGET_WINDOW_LEFT,
        TARGET_WINDOW_TOP,
        TARGET_WINDOW_WIDTH,
        TARGET_WINDOW_HEIGHT,
        win32con.SWP_SHOWWINDOW,
    )

    time.sleep(WINDOW_MOVE_DELAY_SECONDS)


def get_window_bounds(hwnd: int) -> WindowBounds:
    """
    Return the complete window bounds, including borders and title bar.
    """

    left, top, right, bottom = win32gui.GetWindowRect(hwnd)

    return WindowBounds(
        left=left,
        top=top,
        right=right,
        bottom=bottom,
    )


def get_client_bounds(hwnd: int) -> WindowBounds:
    """
    Return the client-area bounds in screen coordinates.

    This excludes the Windows title bar and outer borders.
    """

    client_left, client_top, client_right, client_bottom = (
        win32gui.GetClientRect(hwnd)
    )

    screen_left, screen_top = win32gui.ClientToScreen(
        hwnd,
        (client_left, client_top),
    )

    screen_right, screen_bottom = win32gui.ClientToScreen(
        hwnd,
        (client_right, client_bottom),
    )

    return WindowBounds(
        left=screen_left,
        top=screen_top,
        right=screen_right,
        bottom=screen_bottom,
    )


def validate_bounds(bounds: WindowBounds) -> None:
    """
    Confirm that a region has valid dimensions.
    """

    if bounds.width <= 0 or bounds.height <= 0:
        raise ValueError(
            "Invalid capture dimensions: "
            f"{bounds.width}x{bounds.height}"
        )


# ============================================================
# IMAGE CAPTURE
# ============================================================

def capture_with_print_window(
    hwnd: int,
    client_bounds: WindowBounds,
) -> Image.Image:
    """
    Capture the application's client area through the Windows
    PrintWindow API.

    This can work even when another window partially covers the game.
    Some GPU-rendered applications may not support PrintWindow.
    """

    width = client_bounds.width
    height = client_bounds.height

    validate_bounds(client_bounds)

    window_dc_handle = win32gui.GetWindowDC(hwnd)

    if not window_dc_handle:
        raise RuntimeError("Windows could not obtain the window device context.")

    source_dc = None
    memory_dc = None
    bitmap = None

    try:
        source_dc = win32ui.CreateDCFromHandle(window_dc_handle)
        memory_dc = source_dc.CreateCompatibleDC()

        bitmap = win32ui.CreateBitmap()
        bitmap.CreateCompatibleBitmap(source_dc, width, height)

        memory_dc.SelectObject(bitmap)

        flags = PW_CLIENTONLY | PW_RENDERFULLCONTENT

        result = ctypes.windll.user32.PrintWindow(
            hwnd,
            memory_dc.GetSafeHdc(),
            flags,
        )

        if result != 1:
            raise RuntimeError(
                "PrintWindow was not supported by the application."
            )

        bitmap_info = bitmap.GetInfo()
        bitmap_bytes = bitmap.GetBitmapBits(True)

        image = Image.frombuffer(
            "RGB",
            (
                bitmap_info["bmWidth"],
                bitmap_info["bmHeight"],
            ),
            bitmap_bytes,
            "raw",
            "BGRX",
            0,
            1,
        )

        return image.copy()

    finally:
        if bitmap is not None:
            win32gui.DeleteObject(bitmap.GetHandle())

        if memory_dc is not None:
            memory_dc.DeleteDC()

        if source_dc is not None:
            source_dc.DeleteDC()

        win32gui.ReleaseDC(hwnd, window_dc_handle)


def capture_with_image_grab(
    client_bounds: WindowBounds,
) -> Image.Image:
    """
    Capture the visible client area from the desktop.

    This is the fallback when PrintWindow is not supported. The game
    must be visible and unobstructed for this method.
    """

    validate_bounds(client_bounds)

    return ImageGrab.grab(
        bbox=(
            client_bounds.left,
            client_bounds.top,
            client_bounds.right,
            client_bounds.bottom,
        ),
        all_screens=True,
    )


def image_is_probably_blank(image: Image.Image) -> bool:
    """
    Detect a completely or nearly uniform image.

    Some applications report PrintWindow success while returning an
    empty or solid-color frame.
    """

    sample = image.convert("RGB").resize((32, 32))
    extrema = sample.getextrema()

    channel_ranges = [
        maximum - minimum
        for minimum, maximum in extrema
    ]

    return max(channel_ranges) < 3


def capture_client_area(
    hwnd: int,
    client_bounds: WindowBounds,
) -> tuple[Image.Image, str]:
    """
    Try deterministic Windows API capture first. If unavailable or
    blank, fall back to visible-screen capture.
    """

    try:
        image = capture_with_print_window(hwnd, client_bounds)

        if image_is_probably_blank(image):
            raise RuntimeError(
                "PrintWindow returned a blank or uniform image."
            )

        return image, "print_window"

    except Exception as print_window_error:
        print(
            "PrintWindow capture unavailable. "
            "Using visible-screen fallback."
        )
        print(f"PrintWindow reason: {print_window_error}")

        image = capture_with_image_grab(client_bounds)
        return image, "image_grab_fallback"


# ============================================================
# IMAGE METADATA
# ============================================================

def calculate_image_sha256(image: Image.Image) -> str:
    """
    Calculate a deterministic hash from the image's pixel data.
    """

    normalized_image = image.convert("RGB")

    hash_input = (
        f"{normalized_image.width}x{normalized_image.height}:RGB:"
    ).encode("utf-8")

    digest = hashlib.sha256()
    digest.update(hash_input)
    digest.update(normalized_image.tobytes())

    return digest.hexdigest()


def create_image_metadata(image: Image.Image) -> ImageMetadata:
    return ImageMetadata(
        width=image.width,
        height=image.height,
        mode=image.mode,
        format="PNG",
        sha256=calculate_image_sha256(image),
    )


# ============================================================
# FILE STORAGE
# ============================================================

def ensure_directories() -> None:
    SCREENSHOT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    OBSERVATION_DIRECTORY.mkdir(parents=True, exist_ok=True)


def save_image(image: Image.Image, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    image.save(destination, format="PNG")


def save_observation(
    observation: Observation,
    destination: Path,
) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)

    with destination.open("w", encoding="utf-8") as file:
        json.dump(
            asdict(observation),
            file,
            indent=2,
            ensure_ascii=False,
        )


# ============================================================
# OBSERVATION ENGINE
# ============================================================

class ObservationEngine:
    """
    Collect a raw visual observation from a Windows application.

    This class does not interpret the image or decide what action
    should happen next.
    """

    def __init__(
        self,
        window_title_fragment: str = WINDOW_TITLE_FRAGMENT,
        environment: str = EXPERIMENT_NAME,
    ) -> None:
        self.window_title_fragment = window_title_fragment
        self.environment = environment

        enable_dpi_awareness()
        ensure_directories()

    def capture(self) -> Observation:
        timestamp = datetime.now(timezone.utc)

        observation_id = timestamp.strftime(
            "%Y%m%dT%H%M%S_%fZ"
        )

        screenshot_path = (
            SCREENSHOT_DIRECTORY / f"{observation_id}.png"
        )

        metadata_path = (
            OBSERVATION_DIRECTORY / f"{observation_id}.json"
        )

        hwnd = find_window_by_title(
            self.window_title_fragment
        )

        if hwnd is None:
            observation = Observation(
                observation_id=observation_id,
                timestamp_utc=timestamp.isoformat(),
                environment=self.environment,
                window_title=self.window_title_fragment,
                window_handle=0,
                window_found=False,
                window_visible=False,
                window_minimized=False,
                window_bounds=None,
                client_bounds=None,
                screenshot_path=None,
                metadata_path=str(metadata_path),
                capture_success=False,
                capture_method=None,
                image=None,
                error="Target window was not found.",
            )

            save_observation(observation, metadata_path)
            return observation

        try:
            restore_and_position_window(hwnd)

            window_title = win32gui.GetWindowText(hwnd)
            window_visible = bool(
                win32gui.IsWindowVisible(hwnd)
            )
            window_minimized = bool(
                win32gui.IsIconic(hwnd)
            )

            window_bounds = get_window_bounds(hwnd)
            client_bounds = get_client_bounds(hwnd)

            image, capture_method = capture_client_area(
                hwnd,
                client_bounds,
            )

            image_metadata = create_image_metadata(image)

            save_image(image, screenshot_path)

            observation = Observation(
                observation_id=observation_id,
                timestamp_utc=timestamp.isoformat(),
                environment=self.environment,
                window_title=window_title,
                window_handle=hwnd,
                window_found=True,
                window_visible=window_visible,
                window_minimized=window_minimized,
                window_bounds=window_bounds,
                client_bounds=client_bounds,
                screenshot_path=str(screenshot_path),
                metadata_path=str(metadata_path),
                capture_success=True,
                capture_method=capture_method,
                image=image_metadata,
                error=None,
            )

        except Exception as exc:
            window_title = win32gui.GetWindowText(hwnd)

            try:
                window_bounds = get_window_bounds(hwnd)
                client_bounds = get_client_bounds(hwnd)
            except Exception:
                window_bounds = None
                client_bounds = None

            observation = Observation(
                observation_id=observation_id,
                timestamp_utc=timestamp.isoformat(),
                environment=self.environment,
                window_title=window_title,
                window_handle=hwnd,
                window_found=True,
                window_visible=bool(
                    win32gui.IsWindowVisible(hwnd)
                ),
                window_minimized=bool(
                    win32gui.IsIconic(hwnd)
                ),
                window_bounds=window_bounds,
                client_bounds=client_bounds,
                screenshot_path=None,
                metadata_path=str(metadata_path),
                capture_success=False,
                capture_method=None,
                image=None,
                error=f"{type(exc).__name__}: {exc}",
            )

        save_observation(observation, metadata_path)
        return observation


# ============================================================
# COMMAND-LINE ENTRY POINT
# ============================================================

def main() -> None:
    engine = ObservationEngine()
    observation = engine.capture()

    print()
    print(json.dumps(asdict(observation), indent=2))
    print()

    if observation.capture_success:
        print("Observation captured successfully.")
        print(f"Method: {observation.capture_method}")
        print(f"Screenshot: {observation.screenshot_path}")
        print(f"Metadata: {observation.metadata_path}")

        if observation.image is not None:
            print(
                "Image dimensions: "
                f"{observation.image.width}x"
                f"{observation.image.height}"
            )
            print(f"SHA-256: {observation.image.sha256}")
    else:
        print("Observation capture failed.")
        print(f"Reason: {observation.error}")


if __name__ == "__main__":
    main()
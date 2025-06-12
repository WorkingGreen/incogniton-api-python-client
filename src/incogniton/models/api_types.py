from typing import TypedDict
from .browser_profile_types import BrowserProfile

class CreateBrowserProfileRequest(TypedDict):
    """Request to create a new browser profile."""
    profile_data: BrowserProfile

class UpdateBrowserProfileRequest(TypedDict):
    """Request to update an existing browser profile."""
    profile_data: BrowserProfile

class GetCookieResponse(TypedDict):
    """Cookie data response."""
    path: str
    session: bool
    domain: str
    hostOnly: bool
    sameSite: str
    name: str
    httpOnly: bool
    secure: bool
    value: str
    expirationDate: int 
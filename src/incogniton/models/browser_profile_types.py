from typing import Optional, Literal, Any
from pydantic import BaseModel

# Type aliases
ProfileId = str
ProfileStatus = Literal['ready', 'launching', 'launched', 'syncing', 'synced']

class GeneralProfileInformation(BaseModel):
    profile_name: str
    profile_notes: Optional[str] = None
    profile_group: str = "Unassigned"
    profile_last_edited: str
    simulated_operating_system: str
    profile_browser_version: str
    browser_id: Optional[str] = None

class Proxy(BaseModel):
    connection_type: str
    proxy_url: str
    proxy_username: Optional[str] = None
    proxy_password: Optional[str] = None

class Timezone(BaseModel):
    timezone: str
    timezone_mode: str

class WebRTC(BaseModel):
    webrtc_mode: str
    webrtc_ip_address: Optional[str] = None

class Navigator(BaseModel):
    user_agent: str
    platform: str
    language: str
    do_not_track: bool
    hardware_concurrency: int
    device_memory: int

class Other(BaseModel):
    active_session_lock: bool
    other_ShowProfileName: bool
    browser_allowRealMediaDevices: bool
    custom_browser_args_enabled: bool
    custom_browser_args_string: Optional[str] = None
    browser_language_lock: bool
    custom_browser_language: Optional[str] = None

class BrowserProfile(BaseModel):
    general_profile_information: GeneralProfileInformation
    Timezone: Optional[Timezone] = None
    WebRTC: Optional[WebRTC] = None
    Navigator: Optional[Navigator] = None
    Other: Optional[Other] = None

class CreateBrowserProfileRequest(BaseModel):
    profileData: dict[str, Any]

class UpdateBrowserProfileRequest(BaseModel):
    profileData: Optional[dict[str, Any]] = None

class GetCookieResponse(BaseModel):
    name: str
    value: str
    domain: str
    path: str
    secure: bool
    httpOnly: bool
    sameSite: str
    expirationDate: Optional[float] = None

class AddCookieRequest(BaseModel):
    profile_browser_id: str
    format: Literal['base64json']
    cookie: str

class PuppeteerLaunchResponse(BaseModel):
    puppeteerUrl: str
    status: Literal['ok', 'error']

class SeleniumLaunchResponse(BaseModel):
    status: Literal['ok', 'error'] 
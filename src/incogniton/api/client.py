from typing import Dict, List, Optional, Union, TypedDict, Any
from datetime import datetime
import json
import base64
from urllib.parse import urlencode

from pydantic import BaseModel

from ..utils.http import HttpAgent
from ..utils.http.errors import IncognitonError, IncognitonAPIError  # noqa: F401 — re-exported for backwards compat
from ..models.browser_profile_types import (
    ProfileId,
    BrowserProfile,
    CreateBrowserProfileRequest,
    UpdateBrowserProfileRequest,
    Proxy,
    ProfileStatus,
    GetCookieResponse,
)

# Constants
DEFAULT_BASE_URL = "http://localhost:35000"
CONTENT_TYPE_FORM = "application/x-www-form-urlencoded"

class ProfileResponse(TypedDict):
    profiles: List[BrowserProfile]
    status: str

class ProfileStatusResponse(TypedDict):
    status: ProfileStatus

class CookieResponse(TypedDict):
    cookies: List[GetCookieResponse]
    status: str

class MessageResponse(TypedDict):
    message: str
    status: str

class AutomationResponse(TypedDict):
    url: str
    status: str

class IncognitonClient:
    """Client for interacting with the Incogniton API.

    Args:
        base_url (str, optional): Base URL for the Incogniton API.
            If not provided, defaults to http://localhost:35000.
            Can be overridden by INCOGNITON_API_URL environment variable.
    """

    def __init__(self, base_url: str = DEFAULT_BASE_URL, *, port: Optional[int] = None):
        if port is not None:
            base_url = f"http://localhost:{port}"
        self.http = HttpAgent(base_url)

    @property
    def system(self) -> "SystemOperations":
        """System-level operations."""
        return SystemOperations(self.http)

    @property
    def profile(self) -> "ProfileOperations":
        """Profile-related operations."""
        return ProfileOperations(self.http)

    @property
    def cookie(self) -> "CookieOperations":
        """Cookie-related operations."""
        return CookieOperations(self.http)

    @property
    def automation(self) -> "AutomationOperations":
        """Automation-related operations."""
        return AutomationOperations(self.http)


class SystemOperations:
    """System-level operations for the Incogniton API."""

    def __init__(self, http_agent: HttpAgent):
        self.http = http_agent

    async def alive(self) -> str:
        """Health probe. Returns 'OK'.

        Normalizes across server versions: V4 and current V5 builds serve the
        JSON-quoted string '"OK"', while newer V5 builds serve a bare 'OK'.
        Both (and any surrounding whitespace) are stripped to a plain 'OK'.
        """
        raw = await self.http.get_text("/alive")
        return raw.strip().strip('"')

    async def close(self) -> Dict[str, str]:
        """Shut down the Incogniton application."""
        return await self.http.get("/incogniton/close")


class ProfileOperations:
    """Profile-related operations for the Incogniton API."""
    
    def __init__(self, http_agent: HttpAgent):
        self.http = http_agent
        
    async def list(self) -> Dict[str, Union[List[BrowserProfile], str]]:
        """List all browser profiles."""
        return await self.http.get("/profile/all")
        
    async def get(self, profile_id: ProfileId) -> Dict[str, Union[BrowserProfile, str]]:
        """Get a specific browser profile."""
        return await self.http.get(f"/profile/get/{profile_id}")
        
    async def add(self, data) -> Dict[str, str]:
        """Add a new browser profile.
        
        Args:
            data: Profile configuration data (dict or CreateBrowserProfileRequest).
            
        Returns:
            Dict containing profile ID and status.
        """
        try:
            if isinstance(data, dict):
                data = CreateBrowserProfileRequest(**data)
            elif not isinstance(data, CreateBrowserProfileRequest):
                raise TypeError("data must be a dict or CreateBrowserProfileRequest instance")
            # Convert the entire profileData object to a JSON string
            json_string = json.dumps(data.profileData)
            
            # wrap in form data for form-urlencoded
            form_data = {
                "profileData": json_string
            }
            
            return await self.http.post(
                "/profile/add",
                data=form_data,
                headers={"Content-Type": CONTENT_TYPE_FORM}
            )
        except Exception as e:
            raise IncognitonAPIError(f"Failed to add profile: {str(e)}")
    
    async def update(self, profile_id: ProfileId, data) -> Dict[str, str]:
        """Update an existing browser profile.
        
        Args:
            profile_id: Unique identifier of the profile.
            data: Updated profile configuration (dict or UpdateBrowserProfileRequest).
            
        Returns:
            Dict containing message and status.
        """
        try:
            if isinstance(data, dict):
                data = UpdateBrowserProfileRequest(**data)
            elif not isinstance(data, UpdateBrowserProfileRequest):
                raise TypeError("data must be a dict or UpdateBrowserProfileRequest instance")
            # First, stringify the data exactly as needed by the API
            profile_dict = data.profileData.copy() if data.profileData else {}
            profile_dict["profile_browser_id"] = profile_id
            json_string = json.dumps(profile_dict)
            
            # Then wrap it in the profileData parameter as expected by the API
            form_data = {
                "profileData": json_string
            }
            
            return await self.http.post(
                "/profile/update",
                data=form_data,
                headers={"Content-Type": CONTENT_TYPE_FORM}
            )
        except Exception as e:
            raise IncognitonAPIError(f"Failed to update profile: {str(e)}")
        
    async def switch_proxy(self, profile_id: ProfileId, proxy: Union[Proxy, Dict[str, Any]]) -> Dict[str, str]:
        """Helper method to update a browser profile's proxy configuration.

        Accepts either a ``Proxy`` model or a plain dict. A ``Proxy`` model is
        serialized to a plain dict so the resulting payload is JSON-serializable.
        """
        proxy_dict = proxy.model_dump() if isinstance(proxy, BaseModel) else proxy
        return await self.update(profile_id, UpdateBrowserProfileRequest(profileData={"Proxy": proxy_dict}))
        
    async def launch(self, profile_id: ProfileId) -> Dict[str, str]:
        """Launch a browser profile."""
        return await self.http.get(f"/profile/launch/{profile_id}")
        
    async def launch_force_local(self, profile_id: ProfileId) -> Dict[str, str]:
        """Force a browser profile to launch in local mode."""
        return await self.http.get(f"/profile/launch/{profile_id}/force/local")
        
    async def launch_force_cloud(self, profile_id: ProfileId) -> Dict[str, str]:
        """Force a browser profile to launch in cloud mode."""
        return await self.http.get(f"/profile/launch/{profile_id}/force/cloud")
        
    async def get_status(self, profile_id: ProfileId) -> Dict[str, ProfileStatus]:
        """Get the current status of a browser profile."""
        return await self.http.get(f"/profile/status/{profile_id}")
        
    async def stop(self, profile_id: ProfileId) -> Dict[str, str]:
        """Stop a running browser profile."""
        return await self.http.get(f"/profile/stop/{profile_id}")
    
    async def force_stop(self, profile_id: ProfileId) -> Dict[str, str]:
        """Force stop a running browser profile."""
        return await self.http.get(f"/profile/force-stop/{profile_id}")
        
    async def delete(self, profile_id: ProfileId) -> Dict[str, str]:
        """Delete a browser profile."""
        return await self.http.get(f"/profile/delete/{profile_id}")

    async def clone(
        self,
        profile_id: ProfileId,
        profile_name: Optional[str] = None,
        target_group: Optional[str] = None,
        clone_cookies: Optional[bool] = None,
        clone_advanced_other_settings: Optional[bool] = None,
        clone_useragent: Optional[bool] = None,
        clone_other_browser_data: Optional[bool] = None,
    ) -> Dict[str, str]:
        """Clone a profile with custom settings.

        Args:
            profile_id: Browser id of the source profile.
            profile_name: Name for the clone. Defaults to the source profile's name.
            target_group: Group for the clone. Defaults to the source profile's group.
            clone_cookies: Copy cookies (default True).
            clone_advanced_other_settings: Copy advanced/other settings (default True).
            clone_useragent: Copy the user agent (default True).
            clone_other_browser_data: Copy other browser data (default True).

        Returns:
            Dict containing profile_browser_id of the new clone and status.
        """
        data: Dict[str, Any] = {"profile_browser_id": profile_id}
        if profile_name is not None:
            data["profile_name"] = profile_name
        if target_group is not None:
            data["target_group"] = target_group
        if clone_cookies is not None:
            data["clone_cookies"] = clone_cookies
        if clone_advanced_other_settings is not None:
            data["clone_advanced_other_settings"] = clone_advanced_other_settings
        if clone_useragent is not None:
            data["clone_useragent"] = clone_useragent
        if clone_other_browser_data is not None:
            data["clone_other_browser_data"] = clone_other_browser_data
        return await self.http.post("/profile/clone", data=data)

    async def clone_quick(self, profile_id: ProfileId) -> Dict[str, str]:
        """Clone a profile using all-true defaults (same name/group, all clone options on).

        Returns:
            Dict containing profile_browser_id of the new clone and status.
        """
        return await self.http.get(f"/profile/clone/{profile_id}")

    async def dry_launch(self, profile_id: ProfileId) -> Dict[str, str]:
        """Prepare a launch without starting the browser.

        Runs the prep stages and returns the built launch command as 'arg'.

        Returns:
            Dict containing 'arg' (the full launch command) and status.
        """
        return await self.http.get(f"/profile/dryLaunch/{profile_id}")

    async def dry_launch_force_local(self, profile_id: ProfileId) -> Dict[str, str]:
        """Dry-launch, forcing the LOCAL copy when out of sync."""
        return await self.http.get(f"/profile/dryLaunch/{profile_id}/force/local")

    async def dry_launch_force_cloud(self, profile_id: ProfileId) -> Dict[str, str]:
        """Dry-launch, forcing the CLOUD copy when out of sync."""
        return await self.http.get(f"/profile/dryLaunch/{profile_id}/force/cloud")


class CookieOperations:
    """Cookie-related operations for the Incogniton API."""
    
    def __init__(self, http_agent: HttpAgent):
        self.http = http_agent
        
    async def get(self, profile_id: ProfileId) -> Dict[str, Union[List[GetCookieResponse], str]]:
        """Get all cookies associated with a browser profile."""
        return await self.http.get(f"/profile/cookie/{profile_id}")
        
    async def add(self, profile_id: ProfileId, cookie_data: List[Dict[str, Union[str, bool, int]]]) -> Dict[str, str]:
        """Add a new cookie to a browser profile."""
        cookie_string = base64.b64encode(json.dumps(cookie_data).encode()).decode()
        request_data = {
            "profile_browser_id": profile_id,
            "format": "base64json",
            "cookie": cookie_string
        }
        return await self.http.post("/profile/addCookie", data=request_data)
        
    async def delete(self, profile_id: ProfileId) -> Dict[str, str]:
        """Delete all cookies from a browser profile."""
        return await self.http.get(f"/profile/deleteCookie/{profile_id}")


class AutomationOperations:
    """Automation-related operations for the Incogniton API."""
    
    def __init__(self, http_agent: HttpAgent):
        self.http = http_agent
        
    async def launch_puppeteer(self, profile_id: ProfileId) -> Dict[str, str]:
        """Launch a browser profile with Puppeteer automation."""
        return await self.http.get(f"/automation/launch/puppeteer/{profile_id}")
        
    async def launch_puppeteer_custom(self, profile_id: ProfileId, custom_args: str) -> Dict[str, str]:
        """Launch a browser profile with Puppeteer automation using custom arguments."""
        return await self.http.post("/automation/launch/puppeteer", data={"profileID": profile_id, "customArgs": custom_args})
        
    async def launch_selenium(self, profile_id: ProfileId) -> Dict[str, str]:
        """Launch a browser profile with Selenium automation."""
        return await self.http.get(f"/automation/launch/python/{profile_id}")
        
    async def launch_selenium_custom(self, profile_id: ProfileId, custom_args: str) -> Dict[str, str]:
        """Launch a browser profile with Selenium automation using custom arguments."""
        return await self.http.post(f"/automation/launch/python/{profile_id}/", data={"customArgs": custom_args})

    async def launch_puppeteer_force_local(self, profile_id: ProfileId) -> Dict[str, str]:
        """Launch a profile for Puppeteer, forcing the LOCAL copy when out of sync."""
        return await self.http.get(f"/automation/launch/puppeteer/{profile_id}/local")

    async def launch_puppeteer_force_cloud(self, profile_id: ProfileId) -> Dict[str, str]:
        """Launch a profile for Puppeteer, forcing the CLOUD copy when out of sync."""
        return await self.http.get(f"/automation/launch/puppeteer/{profile_id}/cloud")

    async def launch_selenium_force_local(self, profile_id: ProfileId) -> Dict[str, str]:
        """Launch a profile on the Selenium grid, forcing the LOCAL copy when out of sync."""
        return await self.http.get(f"/automation/launch/python/{profile_id}/local")

    async def launch_selenium_force_cloud(self, profile_id: ProfileId) -> Dict[str, str]:
        """Launch a profile on the Selenium grid, forcing the CLOUD copy when out of sync."""
        return await self.http.get(f"/automation/launch/python/{profile_id}/cloud")

    async def launch_selenium_custom_body(
        self,
        profile_id: ProfileId,
        custom_args: Optional[str] = None,
        force_local: bool = False,
        force_cloud: bool = False,
    ) -> Dict[str, str]:
        """Launch on the Selenium grid with custom args, profile id in the request body.

        Args:
            profile_id: The profile's browser id.
            custom_args: Extra args passed to the launch.
            force_local: Force the local copy when out of sync.
            force_cloud: Force the cloud copy when out of sync.

        Returns:
            Dict containing 'url' (grid URL) and status.
        """
        data: Dict[str, Any] = {"profileID": profile_id}
        if custom_args is not None:
            data["customArgs"] = custom_args
        if force_local:
            data["forceLocal"] = True
        if force_cloud:
            data["forceCloud"] = True
        return await self.http.post("/automation/launch/python/", data=data)

    async def launch_cookie_robot(self, profile_id: ProfileId) -> Dict[str, str]:
        """Run the cookie-collection robot on a profile.

        Forces the cloud copy and uses default settings
        (top-50 sites, 120s timeout, accept-cookies extension, random crawl order).
        """
        return await self.http.get(f"/automation/cookieRobot/{profile_id}")

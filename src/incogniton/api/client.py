from typing import Dict, List, Optional, Union, TypedDict, Any
from datetime import datetime
import json
import base64
from urllib.parse import urlencode

from ..utils.http import HttpAgent
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

class IncognitonError(Exception):
    """Base exception for Incogniton API errors."""
    pass

class IncognitonAPIError(IncognitonError):
    """Exception raised for API-specific errors."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        self.status_code = status_code
        super().__init__(message)

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
    
    def __init__(self, base_url: str = DEFAULT_BASE_URL):
        self.http = HttpAgent(base_url)
        
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
        
    async def add(self, data: CreateBrowserProfileRequest) -> Dict[str, str]:
        """Add a new browser profile.
        
        Args:
            data: Profile configuration data.
            
        Returns:
            Dict containing profile ID and status.
        """
        try:
            # Convert the entire profileData object to a JSON string
            json_string = json.dumps(data.profileData)
            
            # Wrap it in the profileData parameter as expected by the API
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
        
    async def update(self, profile_id: ProfileId, data: UpdateBrowserProfileRequest) -> Dict[str, str]:
        """Update an existing browser profile.
        
        Args:
            profile_id: Unique identifier of the profile.
            data: Updated profile configuration.
            
        Returns:
            Dict containing message and status.
        """
        try:
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
        
    async def switchProxy(self, profile_id: ProfileId, proxy: Proxy) -> Dict[str, str]:
        """Helper method to update a browser profile's proxy configuration."""
        return await self.update(profile_id, UpdateBrowserProfileRequest(profileData={"Proxy": proxy}))
        
    async def launch(self, profile_id: ProfileId) -> Dict[str, str]:
        """Launch a browser profile."""
        return await self.http.get(f"/profile/launch/{profile_id}")
        
    async def launchForceLocal(self, profile_id: ProfileId) -> Dict[str, str]:
        """Force a browser profile to launch in local mode."""
        return await self.http.get(f"/profile/launch/{profile_id}/force/local")
        
    async def launchForceCloud(self, profile_id: ProfileId) -> Dict[str, str]:
        """Force a browser profile to launch in cloud mode."""
        return await self.http.get(f"/profile/launch/{profile_id}/force/cloud")
        
    async def getStatus(self, profile_id: ProfileId) -> Dict[str, ProfileStatus]:
        """Get the current status of a browser profile."""
        return await self.http.get(f"/profile/status/{profile_id}")
        
    async def stop(self, profile_id: ProfileId) -> Dict[str, str]:
        """Stop a running browser profile."""
        return await self.http.get(f"/profile/stop/{profile_id}")
        
    async def delete(self, profile_id: ProfileId) -> Dict[str, str]:
        """Delete a browser profile."""
        return await self.http.get(f"/profile/delete/{profile_id}")


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
        
    async def launchPuppeteer(self, profile_id: ProfileId) -> Dict[str, str]:
        """Launch a browser profile with Puppeteer automation."""
        return await self.http.get(f"/automation/launch/puppeteer/{profile_id}")
        
    async def launchPuppeteerCustom(self, profile_id: ProfileId, custom_args: str) -> Dict[str, str]:
        """Launch a browser profile with Puppeteer automation using custom arguments."""
        return await self.http.post("/automation/launch/puppeteer", data={"profileID": profile_id, "customArgs": custom_args})
        
    async def launchSelenium(self, profile_id: ProfileId) -> Dict[str, str]:
        """Launch a browser profile with Selenium automation."""
        return await self.http.get(f"/automation/launch/python/{profile_id}")
        
    async def launchSeleniumCustom(self, profile_id: ProfileId, custom_args: str) -> Dict[str, str]:
        """Launch a browser profile with Selenium automation using custom arguments."""
        return await self.http.post(f"/automation/launch/python/{profile_id}/", data={"customArgs": custom_args})
 
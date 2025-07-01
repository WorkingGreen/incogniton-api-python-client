import httpx
from typing import Any, Dict, Optional, Union
from urllib.parse import urlencode, quote
from .errors import IncognitonError


class HttpAgent:
    """HTTP client for Incogniton API."""

    def __init__(
        self,
        base_url: str,
        timeout: int = 35, # 35 secs timeout to accommodate browser booting
    ):
        """Initialize HTTP client."""
        self.base_url = base_url
        self.headers = {
            "Content-Type": "application/json",
        }
        self.timeout = timeout
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=self.timeout,
        )

    def _encode_form_data(self, data: Dict[str, Any]) -> str:
        """Encode form data similar to qs.stringify.
        
        Args:
            data: Dictionary of form data
            
        Returns:
            URL-encoded string
        """
        # Convert all values to strings and properly encode them
        encoded_pairs = []
        for key, value in data.items():
            # Ensure the value is a string and properly encoded
            str_value = str(value)
            # URL encode the value to handle special characters
            encoded_value = quote(str_value, safe='')
            encoded_pairs.append(f"{key}={encoded_value}")
        
        return "&".join(encoded_pairs)

    async def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make an HTTP request.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            data: Request data (dict for JSON, str for form data)
            headers: Optional headers to override defaults
        """
        try:
            # Merge headers
            request_headers = self.headers.copy()
            if headers:
                request_headers.update(headers)

            # For form data, httpx expects a dict, not a string or bytes
            if headers and headers.get("Content-Type") == "application/x-www-form-urlencoded":
                if data is not None and isinstance(data, dict):
                    data_dict = data
                else:
                    data_dict = None
            else:
                data_dict = None

            response = await self._client.request(
                method=method,
                url=endpoint,
                json=data if not (headers and headers.get("Content-Type") == "application/x-www-form-urlencoded") else None,
                data=data_dict,
                headers=request_headers,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            try:
                response_data = e.response.json()
                message = response_data.get("message", e.response.text)
            except ValueError:
                response_data = {"error": e.response.text}
                message = e.response.text
            raise IncognitonError(
                message=f"API Error: {message}",
                status_code=e.response.status_code,
                response=response_data
            )
        except httpx.ConnectError as e:
            raise IncognitonError(f"Connection error: {str(e)}")
        except httpx.TimeoutException as e:
            raise IncognitonError(f"Request timed out after {self.timeout} seconds")
        except Exception as e:
            raise IncognitonError(f"Unexpected error: {str(e)}")

    async def get(self, endpoint: str) -> Dict[str, Any]:
        """Make a GET request."""
        return await self.request("GET", endpoint)

    async def post(
        self,
        endpoint: str,
        data: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make a POST request.
        
        Args:
            endpoint: API endpoint
            data: Request data (dict for JSON, str for form data)
            headers: Optional headers to override defaults
        """
        return await self.request("POST", endpoint, data, headers)

    async def put(
        self,
        endpoint: str,
        data: Dict[str, Any],
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Make a PUT request."""
        return await self.request("PUT", endpoint, data, headers)

    async def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make a DELETE request."""
        return await self.request("DELETE", endpoint)

    async def close(self) -> None:
        """Close the client."""
        await self._client.aclose()

    async def post_with_json(self, endpoint: str, data: Optional[Dict[str, Any]] = None, json_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send a POST request to the specified endpoint."""
        try:
            url = f"{self.base_url}{endpoint}"
            headers = {"Content-Type": "application/json"} if json_data else {}
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=json_data, data=data, headers=headers)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            raise IncognitonError(f"Failed to send POST request: {str(e)}") 

 
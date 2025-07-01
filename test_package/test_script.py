import incogniton
from incogniton import IncognitonClient
from incogniton.models import CreateBrowserProfileRequest
from incogniton.browser.browser import IncognitonBrowser
import asyncio

async def add_profile():
    client = IncognitonClient()
    profile_data = {
        "profileData": {
            "general_profile_information": {
                "profile_name": "Test Profile from test_package",
                "profile_notes": "Created via test script",
                "simulated_operating_system": "Windows",
                "profile_browser_version": "131"
            }
        }
    }
    request = CreateBrowserProfileRequest(profileData=profile_data)
    response = await client.profile.add(request)
    print(f"Profile addition response: {response}")
    return client, response.get("profile_browser_id")

async def test_start_selenium():
    client, profile_id = await add_profile()
    browser = IncognitonBrowser(client, profile_id, headless=True)
    driver = await browser.start_selenium()
    print(f"Selenium WebDriver: {driver}")
    # Optionally, clean up: driver.quit() if driver is not None


def main():
    print(f"incogniton version: {incogniton.__version__}")
    client = IncognitonClient()
    print(f"Client type: {type(client)}")
    # Optionally, add more tests here, e.g., check available methods
    print(f"Client has profile: {'profile' in dir(client)}")
    # Run add_profile test
    asyncio.run(test_start_selenium())

if __name__ == "__main__":
    main() 
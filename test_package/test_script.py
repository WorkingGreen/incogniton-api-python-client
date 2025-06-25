import incogniton
from incogniton import IncognitonClient
from incogniton.models import CreateBrowserProfileRequest
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


def main():
    print(f"incogniton version: {incogniton.__version__}")
    client = IncognitonClient()
    print(f"Client type: {type(client)}")
    # Optionally, add more tests here, e.g., check available methods
    print(f"Client has profile: {'profile' in dir(client)}")
    # Run add_profile test
    asyncio.run(add_profile())

if __name__ == "__main__":
    main() 
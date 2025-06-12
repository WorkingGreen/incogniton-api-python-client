import pytest
import datetime
from incogniton import IncognitonClient
# from incogniton.browser.browser import IncognitonBrowser
import logging
from incogniton.models import CreateBrowserProfileRequest, UpdateBrowserProfileRequest
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_add_profile():
    client = IncognitonClient()
    profile_data = {
        "profileData": {
            "general_profile_information": {
                "profile_name": "QProfile Profile",
                "profile_notes": "Test Notes",
                "simulated_operating_system": "Windows",
                "profile_browser_version": "131"
            }
        }
    }
    
    request = CreateBrowserProfileRequest(profileData=profile_data)
    response = await client.profile.add(request)
    print(f"Profile addition response: {response}")
    assert response["status"] == "ok"
    assert "profile_browser_id" in response

@pytest.mark.asyncio
async def test_update_profile():
    client = IncognitonClient()

    # First create a profile
    profile_data = {
        "profileData": {
            "general_profile_information": {
                "profile_name": "Test Profile",
                "profile_notes": "Test Notes",
                "simulated_operating_system": "Windows",
                "profile_browser_version": "131"
            }
        }
    }
    create_request = CreateBrowserProfileRequest(profileData=profile_data)
    try:
        create_response = await client.profile.add(create_request)
        print(f"Profile creation response: {create_response}")
        print(f"Profile creation request data: {profile_data}")
        if create_response.get("status") == "error":
            print(f"Profile creation failed with error: {create_response.get('message', 'No error message')}")
            raise AssertionError(f"Profile creation failed: {create_response.get('message', 'No error message')}")
        assert create_response["status"] == "ok"
        assert "profile_browser_id" in create_response
        profile_id = create_response["profile_browser_id"]
    except Exception as e:
        print(f"Exception during profile creation: {str(e)}")
        raise

    # Now update the profile
    update_data = {
        "profileData": {
            "general_profile_information": {
                "profile_name": "Updated Profile",
                "profile_notes": "Note has been updated via API",
                "simulated_operating_system": "Windows",
                "profile_browser_version": "131"
            }
        }
    }
    update_request = UpdateBrowserProfileRequest(profileData=update_data)
    update_response = await client.profile.update(profile_id, update_request)
    logger.info(f"Profile update response: {update_response}")
    assert update_response["status"] == "ok"

@pytest.mark.asyncio
async def test_profile_lifecycle():
    client = IncognitonClient()
    
    # Step 1: Create a profile
    profile_data = {
        "profileData": {
            "general_profile_information": {
                "profile_name": "Test Profile",
                "profile_notes": "Testing 1,2,3",
                "simulated_operating_system": "Windows",
                "profile_browser_version": "131"
            }
        }
    }
    
    create_request = CreateBrowserProfileRequest(profileData=profile_data)
    create_response = await client.profile.add(create_request)
    print(f"Create response: {create_response}")
    assert create_response["status"] == "ok"
    assert "profile_browser_id" in create_response
    profile_id = create_response["profile_browser_id"]
    
    # Step 2: Update the profile
    update_data = {
        "profileData": {
            "general_profile_information": {
                "profile_name": "Updated Test Profile",
                "profile_notes": "Testing update",
                "simulated_operating_system": "Windows",
                "profile_browser_version": "131"
            }
        }
    }
    update_request = UpdateBrowserProfileRequest(profileData=update_data)
    update_response = await client.profile.update(profile_id, update_request)
    logger.info(f"Profile update response: {update_response}")
    assert update_response["status"] == "ok"
    
    # Step 3: Launch with Puppeteer in headless mode
    headless_puppeteer_args = "--headless=new"
    puppeteer_response = await client.automation.launchPuppeteerCustom(profile_id, headless_puppeteer_args)
    print(f"Puppeteer launch response: {puppeteer_response}")
    assert puppeteer_response.get("status") == "ok", f"Failed to launch with Puppeteer: {puppeteer_response.get('message', 'Unknown error')}"

    # Step 4: Launch with Selenium in headless mode
    # headless_selenium_args = "--headless=new"
    # selenium_response = await client.automation.launchSeleniumCustom(profile_id, headless_selenium_args)
    # print(f"Selenium launch response: {selenium_response}")
    # assert selenium_response.get("status") == "ok", f"Failed to launch with Selenium: {selenium_response.get('message', 'Unknown error')}"
    
    # Step 5: Delete the profile
    delete_response = await client.profile.delete(profile_id)
    logger.info(f"Profile deletion response: {delete_response}")
    assert delete_response["status"] == "ok" 
    
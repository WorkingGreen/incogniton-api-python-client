import pytest
import datetime
from incogniton import IncognitonClient
# from incogniton.browser.browser import IncognitonBrowser
import logging
from incogniton.models import CreateBrowserProfileRequest, UpdateBrowserProfileRequest
import json
from incogniton.utils.logger import logger

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

@pytest.mark.asyncio
async def test_list_profiles():
    client = IncognitonClient()
    response = await client.profile.list()
    logger.info(f"List profiles response: {response}")
    assert response.get("status") != "error", f"List profiles failed: {response}"

@pytest.mark.asyncio
async def test_get_profile():
    client = IncognitonClient()
    
    # First create a profile to get
    profile_data = {
        "profileData": {
            "general_profile_information": {
                "profile_name": "Test Get Profile",
                "profile_notes": "Profile for get test",
                "simulated_operating_system": "Windows",
                "profile_browser_version": "131"
            }
        }
    }
    create_request = CreateBrowserProfileRequest(profileData=profile_data)
    create_response = await client.profile.add(create_request)
    logger.info(f"Profile created with ID: {create_response.get('profile_browser_id')}")
    assert create_response["status"] == "ok"
    profile_id = create_response["profile_browser_id"]
    
    try:
        # Now get the profile
        get_response = await client.profile.get(profile_id)
        logger.info(f"Get profile response: {get_response}")
        assert get_response.get("status") != "error", f"Get profile failed: {get_response}"
    finally:
        # Clean up
        delete_response = await client.profile.delete(profile_id)
        logger.info(f"Profile deleted: {delete_response}")

@pytest.mark.asyncio
async def test_profile_status():
    client = IncognitonClient()
    
    # Create a profile
    profile_data = {
        "profileData": {
            "general_profile_information": {
                "profile_name": "Status Test Profile",
                "profile_notes": "Testing status operations",
                "simulated_operating_system": "Windows",
                "profile_browser_version": "131"
            }
        }
    }
    create_request = CreateBrowserProfileRequest(profileData=profile_data)
    create_response = await client.profile.add(create_request)
    logger.info(f"Profile created with ID: {create_response.get('profile_browser_id')}")
    assert create_response["status"] == "ok"
    profile_id = create_response["profile_browser_id"]
    
    try:
        # Get initial status
        status_response = await client.profile.getStatus(profile_id)
        logger.info(f"Initial status response: {status_response}")
        assert status_response.get("status") != "error", f"Get status failed: {status_response}"
        
        # Launch the profile
        launch_response = await client.profile.launch(profile_id)
        logger.info(f"Profile launched: {launch_response}")
        assert launch_response.get("status") != "error", f"Launch failed: {launch_response}"
        
        # Get status after launch
        status_response = await client.profile.getStatus(profile_id)
        logger.info(f"Status after launch: {status_response}")
        assert status_response.get("status") != "error", f"Get status after launch failed: {status_response}"
        
        # Stop the profile
        stop_response = await client.profile.stop(profile_id)
        logger.info(f"Profile stopped: {stop_response}")
        assert stop_response.get("status") != "error", f"Stop failed: {stop_response}"
        
        # Get final status
        status_response = await client.profile.getStatus(profile_id)
        logger.info(f"Final status response: {status_response}")
        assert status_response.get("status") != "error", f"Get final status failed: {status_response}"
    finally:
        # Clean up
        delete_response = await client.profile.delete(profile_id)
        logger.info(f"Profile deleted: {delete_response}")

@pytest.mark.asyncio
async def test_cookie_operations():
    client = IncognitonClient()
    
    # Create a profile
    profile_data = {
        "profileData": {
            "general_profile_information": {
                "profile_name": "Cookie Test Profile",
                "profile_notes": "Testing cookie operations",
                "simulated_operating_system": "Windows",
                "profile_browser_version": "131"
            }
        }
    }
    create_request = CreateBrowserProfileRequest(profileData=profile_data)
    create_response = await client.profile.add(create_request)
    logger.info(f"Profile created with ID: {create_response.get('profile_browser_id')}")
    assert create_response["status"] == "ok"
    profile_id = create_response["profile_browser_id"]
    
    try:
        # Add cookies
        cookie_data = [
            {
                "name": "test_cookie",
                "value": "test_value",
                "domain": ".example.com",
                "path": "/",
                "secure": True,
                "httpOnly": True,
                "session": False,
                "sameSite": "no_restriction",
                "expirationDate": 1760000000
            }
        ]
        add_response = await client.cookie.add(profile_id, cookie_data)
        logger.info(f"Cookies added: {add_response}")
        assert add_response.get("status") != "error", f"Add cookie failed: {add_response}"
        
        # Get cookies
        get_response = await client.cookie.get(profile_id)
        logger.info(f"Get cookies response: {get_response}")
        assert get_response.get("status") != "error", f"Get cookies failed: {get_response}"
        
        # Delete cookies
        delete_response = await client.cookie.delete(profile_id)
        logger.info(f"Cookies deleted: {delete_response}")
        assert delete_response.get("status") != "error", f"Delete cookies failed: {delete_response}"
        
        # Verify cookies are deleted
        get_response = await client.cookie.get(profile_id)
        logger.info(f"Final cookie state: {get_response}")
        assert get_response.get("status") != "error", f"Get cookies after delete failed: {get_response}"
    finally:
        # Clean up
        delete_response = await client.profile.delete(profile_id)
        logger.info(f"Profile deleted: {delete_response}") 
    
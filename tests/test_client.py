import pytest
from incogniton import IncognitonClient, IncognitonBrowser
from incogniton.api.client import IncognitonError

from incogniton.models import CreateBrowserProfileRequest, UpdateBrowserProfileRequest
from incogniton.utils.logger import logger


# @pytest.mark.asyncio
# async def test_profile_lifecycle():
#     client = IncognitonClient()
    
#     # Step 1: Create a profile
#     profile_data = {
#         "profileData": {
#             "general_profile_information": {
#                 "profile_name": "Test Profile",
#                 "profile_notes": "Testing 1,2,3",
#                 "simulated_operating_system": "Windows",
#                 "profile_browser_version": "131"
#             }
#         }
#     }
    
#     create_response = await client.profile.add(profile_data)
#     print(f"Create response: {create_response}")
#     assert create_response["status"] == "ok"
#     assert "profile_browser_id" in create_response
#     profile_id = create_response["profile_browser_id"]
    
#     # Step 2: Update the profile
#     update_data = {
#         "profileData": {
#             "general_profile_information": {
#                 "profile_name": "Updated Test Profile",
#                 "profile_notes": "Testing update",
#                 "simulated_operating_system": "Windows",
#                 "profile_browser_version": "131"
#             }
#         }
#     }
    
#     update_response = await client.profile.update(profile_id, update_data)
#     logger.info(f"Profile update response: {update_response}")
#     assert update_response["status"] == "ok"
    
#     # Step 3: Launch with Puppeteer in headless mode
#     headless_puppeteer_args = "--headless=new"
#     puppeteer_response = await client.automation.launch_puppeteer_custom(profile_id, headless_puppeteer_args)
#     print(f"Puppeteer launch response: {puppeteer_response}")
#     assert puppeteer_response.get("status") == "ok", f"Failed to launch with Puppeteer: {puppeteer_response.get('message', 'Unknown error')}"
    
#     # Step 5: Delete the profile
#     delete_response = await client.profile.delete(profile_id)
#     logger.info(f"Profile deletion response: {delete_response}")
#     assert delete_response["status"] == "ok" 

# @pytest.mark.asyncio
# async def test_list_profiles():
#     client = IncognitonClient()
#     response = await client.profile.list()
#     logger.info(f"List profiles response: {response}")
#     assert response.get("status") != "error", f"List profiles failed: {response}"

# @pytest.mark.asyncio
# async def test_get_profile():
#     client = IncognitonClient()
    
#     # First create a profile to get
#     profile_data = {
#         "profileData": {
#             "general_profile_information": {
#                 "profile_name": "Test Get Profile",
#                 "profile_notes": "Profile for get test",
#                 "simulated_operating_system": "Windows",
#                 "profile_browser_version": "131"
#             }
#         }
#     }
    
#     create_response = await client.profile.add(profile_data)
#     logger.info(f"Profile created with ID: {create_response.get('profile_browser_id')}")
#     assert create_response["status"] == "ok"
#     profile_id = create_response["profile_browser_id"]
    
#     try:
#         # Now get the profile
#         get_response = await client.profile.get(profile_id)
#         logger.info(f"Get profile response: {get_response}")
#         assert get_response.get("status") != "error", f"Get profile failed: {get_response}"
#     finally:
#         # Clean up
#         delete_response = await client.profile.delete(profile_id)
#         logger.info(f"Profile deleted: {delete_response}")

# @pytest.mark.asyncio
# async def test_profile_status():
#     client = IncognitonClient()
    
#     # Create a profile
#     profile_data = {
#         "profileData": {
#             "general_profile_information": {
#                 "profile_name": "Status Test Profile",
#                 "profile_notes": "Testing status operations",
#                 "simulated_operating_system": "Windows",
#                 "profile_browser_version": "131"
#             }
#         }
#     }
#     create_request = CreateBrowserProfileRequest(profileData=profile_data)
#     create_response = await client.profile.add(create_request)
#     logger.info(f"Profile created with ID: {create_response.get('profile_browser_id')}")
#     assert create_response["status"] == "ok"
#     profile_id = create_response["profile_browser_id"]
    
#     try:
#         # Get initial status
#         status_response = await client.profile.get_status(profile_id)
#         logger.info(f"Initial status response: {status_response}")
#         assert status_response.get("status") == "Ready", f"Get status failed: {status_response}"
        
#         # Launch the profile
#         launch_response = await client.profile.launch(profile_id)
#         logger.info(f"Profile launched: {launch_response}")
#         assert launch_response.get("status") == "ok", f"Launch failed: {launch_response}"
        
#         # Get status after launch
#         status_response = await client.profile.get_status(profile_id)
#         logger.info(f"Status after launch: {status_response}")
#         assert status_response.get("status") in ["Ready", "Launched"], f"Get status post-launch failed: {status_response}"

#         # Stop the profile (graceful)
#         stop_response = await client.profile.stop(profile_id)
#         logger.info(f"Profile stopped: {stop_response}")
#         assert stop_response.get("status") == "ok", f"Stop failed: {stop_response}"
#
#         # Or force stop the profile
#         force_stop_response = await client.profile.force_stop(profile_id)
#         logger.info(f"Profile force-stopped: {force_stop_response}")
#         assert force_stop_response.get("status") == "ok", f"Force stop failed: {force_stop_response}"
        
#         # Get final status
#         status_response = await client.profile.get_status(profile_id)
#         logger.info(f"Final status response: {status_response}")
#         assert status_response.get("status") in ["Ready", "Launched"], f"Get status post-launch failed: {status_response}"
#     finally:
#         # Clean up
#         delete_response = await client.profile.delete(profile_id)
#         logger.info(f"Profile deleted: {delete_response}")

# @pytest.mark.asyncio
# async def test_cookie_operations():
#     client = IncognitonClient()
    
#     # Create a profile
#     profile_data = {
#         "profileData": {
#             "general_profile_information": {
#                 "profile_name": "Cookie Test Profile",
#                 "profile_notes": "Testing cookie operations",
#                 "simulated_operating_system": "Windows",
#                 "profile_browser_version": "131"
#             }
#         }
#     }
#     create_request = CreateBrowserProfileRequest(profileData=profile_data)
#     create_response = await client.profile.add(create_request)
#     logger.info(f"Profile created with ID: {create_response.get('profile_browser_id')}")
#     assert create_response["status"] == "ok"
#     profile_id = create_response["profile_browser_id"]
    
#     try:
#         # Add cookies
#         cookie_data = [
#             {
#                 "name": "test_cookie",
#                 "value": "test_value",
#                 "domain": ".example.com",
#                 "path": "/",
#                 "secure": True,
#                 "httpOnly": True,
#                 "session": False,
#                 "sameSite": "no_restriction",
#                 "expirationDate": 1760000000
#             }
#         ]
#         add_response = await client.cookie.add(profile_id, cookie_data)
#         logger.info(f"Cookies added: {add_response}")
#         assert add_response.get("status") != "error", f"Add cookie failed: {add_response}"
        
#         # Get cookies
#         get_response = await client.cookie.get(profile_id)
#         logger.info(f"Get cookies response: {get_response}")
#         assert get_response.get("status") == "ok", f"Get cookies failed: {get_response}"
        
#         # Delete cookies
#         delete_response = await client.cookie.delete(profile_id)
#         logger.info(f"Cookies deleted: {delete_response}")
#         assert delete_response.get("status") != "error", f"Delete cookies failed: {delete_response}"
        
#         # Verify cookies are deleted
#         get_response = await client.cookie.get(profile_id)
#         logger.info(f"Final cookie state: {get_response}")
#         assert get_response.get("status") != "error", f"Get cookies after delete failed: {get_response}"
#     finally:
#         # Clean up
#         delete_response = await client.profile.delete(profile_id)
#         logger.info(f"Profile deleted: {delete_response}") 

# @pytest.mark.asyncio
# async def test_launch_selenium():
#     client = IncognitonClient()
#     # Create a profile
#     profile_data = {
#         "profileData": {
#             "general_profile_information": {
#                 "profile_name": "Selenium Launch Test Profile",
#                 "profile_notes": "Testing launchSelenium",
#                 "simulated_operating_system": "Windows",
#                 "profile_browser_version": "131"
#             }
#         }
#     }
#     create_request = CreateBrowserProfileRequest(profileData=profile_data)
#     create_response = await client.profile.add(create_request)
#     logger.info(f"Profile created with ID: {create_response.get('profile_browser_id')}")
#     assert create_response["status"] == "ok"
#     profile_id = create_response["profile_browser_id"]
#     try:
#         response = await client.automation.launchSelenium(profile_id)
#         print(f"launchSelenium response: {response}")
#         assert response.get("status") == "ok", f"launchSelenium failed: {response}"
#     finally:
#         # Clean up
#         delete_response = await client.profile.delete(profile_id)
#         logger.info(f"Profile deleted: {delete_response}")

# @pytest.mark.asyncio
# async def test_start_selenium():
#     client = IncognitonClient()
#     # Create a profile
#     profile_data = {
#         "profileData": {
#             "general_profile_information": {
#                 "profile_name": "Selenium Test Profile",
#                 "profile_notes": "Testing start_selenium",
#                 "simulated_operating_system": "Windows",
#                 "profile_browser_version": "131"
#             }
#         }
#     }
#     create_request = CreateBrowserProfileRequest(profileData=profile_data)
#     create_response = await client.profile.add(create_request)
#     logger.info(f"Profile created with ID: {create_response.get('profile_browser_id')}")
#     assert create_response["status"] == "ok"
#     profile_id = create_response["profile_browser_id"]
#     try:
#         browser = IncognitonBrowser(client, profile_id, headless=True)
#         driver = await browser.start_selenium()
#         print(f"Selenium WebDriver: {driver}")
#         assert driver is not None, "Failed to start Selenium WebDriver"
#         # Optionally, you can quit the driver if needed
#         driver.quit()
#     finally:
#         # Clean up
#         delete_response = await client.profile.delete(profile_id)
#         logger.info(f"Profile deleted: {delete_response}") 

@pytest.mark.asyncio
async def test_start_playwright():
    client = IncognitonClient()
    # Create a profile
    profile_data = {
        "profileData": {
            "general_profile_information": {
                "profile_name": "Playwright Test Profile",
                "profile_notes": "Testing start_playwright",
                "simulated_operating_system": "Windows",
                "profile_browser_version": "131"
            }
        }
    }
    # create_request = CreateBrowserProfileRequest(profileData=profile_data)
    # create_response = await client.profile.add(create_request)
    # logger.info(f"Profile created with ID: {create_response.get('profile_browser_id')}")
    # assert create_response["status"] == "ok"
    # profile_id = create_response["profile_browser_id"]
    try:
        profile_id = "8a4b2972-e790-4c61-9c5f-8f8910df8784"  
        browser = IncognitonBrowser(profile_id, headless=True)
        try:
            playwright_browser = await browser.start_playwright()
            assert playwright_browser is not None, "Failed to start Playwright Browser"
           
            # Go to English Wikipedia and take a screenshot of the main page
            page = await playwright_browser.new_page()
            await page.goto("https://incogniton.com")
            await page.screenshot(path="incogniton.png")
            logger.info("Screenshot of English Wikipedia main page saved as incogniton.png 📸")
            if playwright_browser is not None:
                await browser.close(playwright_browser)
        except IncognitonError as e:
            logger.error(f"IncognitonError: {e}")
            assert False, f"IncognitonError raised: {e}"
    finally:
        # Clean up
        delete_response = await client.profile.delete(profile_id)
        logger.info(f"Profile deleted: {delete_response}")

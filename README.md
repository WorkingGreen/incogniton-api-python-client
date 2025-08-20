# Incogniton Python Client

The official Incogniton Anti-detect browser Python SDK for seamless integration with the [Incogniton Antidetect Browser API](https://api-docs.incogniton.com/) and browser automation workflows. For more about Incogniton, visit our [website](https://incogniton.com).

This package enables Python developers to automate browser tasks, manage profiles, and handle cookies using Incogniton's local desktop app. It supports both REST API operations and direct browser automation (Selenium and Playwright).

## Key Capabilities

-  Create, update, and delete browser profiles
-  Manage cookies for any profile
-  Launch automation endpoints to get the CDP (Chrome DevTools Protocol) URL for Puppeteer and Playwright and the WebDriver URL for Selenium
-  Browser Automation SDK using Playwright and Selenium
-  Built-in error handling and logging

## Getting Started

### Installation

```bash
# Recommended: install from PyPI
pip install incogniton

# Or, for Development:
poetry install
# with pip
pip install -e .
```

### Requirements

-  Python 3.8 or newer
-  Incogniton desktop app running locally

## Example Usage

### Profile Management

```python
from incogniton import IncognitonClient

client = IncognitonClient()

# Add a new profile
data = {"profileData": {"general_profile_information": {"profile_name": "Test Profile"}}}
profile = await client.profile.add(data)

# List all profiles
profiles = await client.profile.list()

# Fetch a profile by ID
details = await client.profile.get("PROFILE_ID")
```

### Automating Browsers

```python
from incogniton import IncognitonBrowser

browser = IncognitonBrowser(client, profile_id="your-profile-id", headless=True)

# Playwright example (recommended)
playwright_browser = await browser.start_playwright()
page = await playwright_browser.new_page()
await page.goto("https://example.com")
page_title = await page.title()
print(page_title)  # Print page title
await page.screenshot(path="example.png")  # Take a screenshot
await browser.close(playwright_browser)

# Selenium example (also supported)
selenium_driver = await browser.start_selenium()
selenium_driver.get("https://example.com")
selenium_driver.quit()
```

> **Note:** Playwright is the recommended automation tool for most use cases due to its modern API, speed, and reliability. Selenium is also supported, but its Web-driver endpoint is generally less reliable.

## Configuration Options

-  `profile_id`: Incogniton profile to use for automation
-  `headless`: Run browsers in headless mode (default: True)
-  `custom_args`: Pass extra arguments to the browser (optional)

## Endpoints & Methods

Below is a summary of the most commonly used methods and operations available in the Incogniton Python SDK. For a complete and up-to-date API reference, please see the [official Incogniton API Documentation](https://api-docs.incogniton.com/).

### Profile Operations (`client.profile`)

-  `await client.profile.list()`
   -  List all browser profiles.
-  `await client.profile.get(profile_id)`
   -  Get a specific browser profile.
-  `await client.profile.add(create_request)`
   -  Add a new browser profile. "create_request" is a "CreateBrowserProfileRequest".
-  `await client.profile.update(profile_id, update_request)`
   -  Update an existing browser profile. "update_request" is an "UpdateBrowserProfileRequest".
-  `await client.profile.switch_proxy(profile_id, proxy)`
   -  Update a browser profile's proxy configuration.
-  `await client.profile.launch(profile_id)`
   -  Launch a browser profile.
-  `await client.profile.launch_force_local(profile_id)`
   -  Force a browser profile to launch in local mode.
-  `await client.profile.launch_force_cloud(profile_id)`
   -  Force a browser profile to launch in cloud mode.
-  `await client.profile.get_status(profile_id)`
   -  Get the current status of a browser profile.
-  `await client.profile.stop(profile_id)`
   -  Stop a running browser profile.
-  `await client.profile.force_stop(profile_id)`
   -  Force stop a running browser profile.
-  `await client.profile.delete(profile_id)`
   -  Delete a browser profile.

### Cookie Operations (`client.cookie`)

-  `await client.cookie.get(profile_id)`
   -  Get all cookies associated with a browser profile.
-  `await client.cookie.add(profile_id, cookie_data)`
   -  Add a new cookie to a browser profile. "cookie_data" is a list of cookie dicts.
-  `await client.cookie.delete(profile_id)`
   -  Delete all cookies from a browser profile.

### Automation Operations (`client.automation`)

-  `await client.automation.launch_puppeteer(profile_id)`
   -  Launch a browser profile with Puppeteer automation.
-  `await client.automation.launch_puppeteer_custom(profile_id, custom_args)`
   -  Launch a browser profile with Puppeteer automation using custom arguments.
-  `await client.automation.launch_selenium(profile_id)`
   -  Launch a browser profile with Selenium automation.
-  `await client.automation.launch_selenium_custom(profile_id, custom_args)`
   -  Launch a browser profile with Selenium automation using custom arguments.

## Browser Automation SDK (`browser`)

-  `playwright_browser = await browser.start_playwright()`
   -  Launch the profile and return a connected Playwright browser instance (Recommended).
-  `selenium_driver = await browser.start_selenium()`
   -  Launch the profile and return a connected Selenium WebDriver instance.
-  `await browser.close(playwright_browser)`
   -  Close a single Playwright browser instance with logging and error handling.
-  `await browser.close_all([playwright_browser1, playwright_browser2, ...])`
   -  Close multiple Playwright browser instances in parallel with logging and error handling.

## Running Tests

```bash
poetry run pytest
# or
pytest tests/
```

## Contributing

We welcome improvements and bugfixes! Please fork the repository, create a branch, and open a pull request.

## Need Help?

For questions or support, email <yusuf@incogniton.com> or use the Incogniton [contact form](https://incogniton.com/contact).

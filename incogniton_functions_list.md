# IncognitonClient Endpoints & Methods

## Profile Operations (`client.profile`)

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
-  `await client.profile.delete(profile_id)`
   -  Delete a browser profile.

## Cookie Operations (`client.cookie`)

-  `await client.cookie.get(profile_id)`
   -  Get all cookies associated with a browser profile.
-  `await client.cookie.add(profile_id, cookie_data)`
   -  Add a new cookie to a browser profile. "cookie_data" is a list of cookie dicts.
-  `await client.cookie.delete(profile_id)`
   -  Delete all cookies from a browser profile.

## Automation Operations (`client.automation`)

-  `await client.automation.launch_puppeteer(profile_id)`
-  Launch a browser profile with Puppeteer automation.
-  `await client.automation.launch_puppeteer_custom(profile_id, custom_args)`
-  Launch a browser profile with Puppeteer automation using custom arguments.
-  `await client.automation.launch_selenium(profile_id)`
-  Launch a browser profile with Selenium automation.
-  `await client.automation.launch_selenium_custom(profile_id, custom_args)`
-  Launch a browser profile with Selenium automation using custom arguments.

## Browser Automation Operations (`browser`)

-  `playwright_browser = await browser.start_playwright()`
   -  Launch the profile and return a connected Playwright Browser instance.
-  `selenium_driver = await browser.start_selenium()`
   -  Launch the profile and return a connected Selenium WebDriver instance.
-  `await browser.close(playwright_browser)`
   -  Close a single Playwright Browser instance with logging and error handling.
-  `await browser.close_all([playwright_browser1, playwright_browser2, ...])`
   -  Close multiple Playwright Browser instances in parallel with logging and error handling.

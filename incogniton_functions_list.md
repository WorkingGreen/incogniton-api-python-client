# IncognitonClient Endpoints & Methods

## System Operations (`client.system`)

-  `await client.system.alive()`
   -  Health probe. Returns the bare string `"OK"` (not the JSON envelope).
-  `await client.system.close()`
   -  Shut down the Incogniton application.

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
-  `await client.profile.clone(profile_id, *, profile_name=None, target_group=None, clone_cookies=None, clone_advanced_other_settings=None, clone_useragent=None, clone_other_browser_data=None)`
   -  Clone a profile with custom settings. Returns `profile_browser_id` of the new clone.
-  `await client.profile.clone_quick(profile_id)`
   -  Clone a profile using all-true defaults (same name/group, all clone options on).
-  `await client.profile.launch(profile_id)`
   -  Launch a browser profile.
-  `await client.profile.launch_force_local(profile_id)`
   -  Force a browser profile to launch in local mode.
-  `await client.profile.launch_force_cloud(profile_id)`
   -  Force a browser profile to launch in cloud mode.
-  `await client.profile.dry_launch(profile_id)`
   -  Prepare a launch without starting the browser. Returns the built launch command as `arg`.
-  `await client.profile.dry_launch_force_local(profile_id)`
   -  Dry-launch, forcing the LOCAL copy when out of sync.
-  `await client.profile.dry_launch_force_cloud(profile_id)`
   -  Dry-launch, forcing the CLOUD copy when out of sync.
-  `await client.profile.get_status(profile_id)`
   -  Get the current status of a browser profile.
-  `await client.profile.stop(profile_id)`
   -  Stop a running browser profile.
-  `await client.profile.force_stop(profile_id)`
   -  Force stop a running browser profile.
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
-  `await client.automation.launch_puppeteer_force_local(profile_id)`
   -  Launch for Puppeteer, forcing the LOCAL copy when out of sync.
-  `await client.automation.launch_puppeteer_force_cloud(profile_id)`
   -  Launch for Puppeteer, forcing the CLOUD copy when out of sync.
-  `await client.automation.launch_puppeteer_custom(profile_id, custom_args)`
   -  Launch a browser profile with Puppeteer automation using custom arguments.
-  `await client.automation.launch_selenium(profile_id)`
   -  Launch a browser profile with Selenium automation.
-  `await client.automation.launch_selenium_force_local(profile_id)`
   -  Launch on the Selenium grid, forcing the LOCAL copy when out of sync.
-  `await client.automation.launch_selenium_force_cloud(profile_id)`
   -  Launch on the Selenium grid, forcing the CLOUD copy when out of sync.
-  `await client.automation.launch_selenium_custom(profile_id, custom_args)`
   -  Launch a browser profile with Selenium automation using custom arguments (profile id in URL path).
-  `await client.automation.launch_selenium_custom_body(profile_id, custom_args=None, force_local=False, force_cloud=False)`
   -  Launch on the Selenium grid with custom args, profile id in the request body.
-  `await client.automation.launch_cookie_robot(profile_id)`
   -  Run the cookie-collection robot on a profile (top-50 sites, 120s timeout, cloud copy).

## Browser Automation Operations (`browser`)

-  `playwright_browser = await browser.start_playwright()`
   -  Launch the profile and return a connected Playwright Browser instance.
-  `selenium_driver = await browser.start_selenium()`
   -  Launch the profile and return a connected Selenium WebDriver instance.
-  `await browser.close(playwright_browser)`
   -  Close a single Playwright Browser instance with logging and error handling.
-  `await browser.close_all([playwright_browser1, playwright_browser2, ...])`
   -  Close multiple Playwright Browser instances in parallel with logging and error handling.

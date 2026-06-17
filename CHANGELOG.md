# [0.3.0]

Added

-  `client.system` operations: `alive()` (health probe) and `close()` (shut down the Incogniton app).
-  Profile cloning: `client.profile.clone(...)` (custom settings) and `client.profile.clone_quick(profile_id)` (all-defaults).
-  Dry-launch (build a launch without opening a browser): `client.profile.dry_launch(profile_id)`, `dry_launch_force_local`, and `dry_launch_force_cloud`.
-  Automation force-sync launch variants: `launch_puppeteer_force_local` / `launch_puppeteer_force_cloud` and `launch_selenium_force_local` / `launch_selenium_force_cloud`.
-  `client.automation.launch_selenium_custom_body(...)` — Selenium custom-args launch with the profile id in the request body.
-  `client.automation.launch_cookie_robot(profile_id)` — run the cookie-collection robot.
-  Optional `port` argument: `IncognitonClient(port=...)` targets a non-default app port.

Changed

-  `system.alive()` normalizes the server response (JSON-quoted `"OK"` or bare `OK`) to a plain `OK` across app versions.

Fixed

-  `switch_proxy()` now serializes a `Proxy` model correctly (previously raised "Object of type Proxy is not JSON serializable").

# [0.2.7]

Changed

-  Corrected the `force_stop` method's API route.

# [0.2.6]

Added

-  Added `force_stop(profile_id)` method to the `IncognitonClient` class.

# [0.2.5]

Changed

-  Improved browser automation reliability and speed by replacing `fixed` wait times with `polling` for browser readiness.

# Changelog

[0.2.4]
Fixed

-  Fix possible `start_playwright` client requirement issue.

[0.2.3]
Changed

-  Improved consistency across all documentation and code examples

[0.2.2]
Changed

-  Minor documentation and codebase refactoring for consistency

[0.2.1]
Changed

-  Updated and improved documentation in README.md (usage examples, recommendations, endpoint references, and clarity)

[0.2.0]
Added

-  Integrated Playwright support for Incogniton browser automation

Changed

-  Improved error handling and logging in browser automation classes

---

For older changes, see the project commit history.

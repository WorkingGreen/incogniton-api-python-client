from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from typing import Optional
import asyncio
from playwright.async_api import async_playwright, Browser as PlaywrightBrowser

from incogniton.utils.logger import logger
from incogniton.api.client import IncognitonError

class IncognitonBrowser:
    def __init__(self, client, profile_id: str, headless: bool = True, launch_delay: int = 35):
        self.client = client
        self.profile_id = profile_id
        self.headless = headless
        self.launch_delay = launch_delay

    async def start_selenium(self) -> Optional[WebDriver]:
        """Launch the profile and return a connected Selenium WebDriver instance."""
        try:
            response = await self.client.automation.launchSelenium(self.profile_id)
            print("🚀 ~ response:", response)
            logger.info(f"Launch Selenium response: {response}")

            if response.get("status") != "ok" or not response.get("url"):
                raise RuntimeError("Invalid Selenium launch response from Incogniton")

            selenium_url = f"http://{response['url']}"

            options = Options()
            if self.headless:
                options.add_argument("--headless=new")
            options.add_argument("--start-maximized")

            driver = webdriver.Remote(
                command_executor=selenium_url,
                options=options
            )

            return driver

        except Exception as e:
            logger.error(f"Failed to connect to Incogniton Selenium: {str(e)}")
            raise IncognitonError(f"Failed to connect to Incogniton Selenium: {str(e)}")

    async def start_playwright(self) -> PlaywrightBrowser:
        """Launch the Incogniton profile and return a connected Playwright Browser instance."""
        try:
            # 1. Launch the profile via Incogniton API
            launch_args = "--headless=new" if self.headless else ""
            response = await self.client.automation.launchPuppeteerCustom(
                self.profile_id, launch_args
            )

            logger.info(f"Launch CDP automation response: {response}")

            cdp_url = response.get("puppeteerUrl")
            if not cdp_url or response.get("status") != "ok":
                raise RuntimeError("Invalid launch response from Incogniton")

            # 2. Wait for the browser to fully initialize
            logger.info("Waiting for Incogniton browser to initialize...")
            await asyncio.sleep(self.launch_delay)

            # 3. Connect to the running browser using CDP
            playwright = await async_playwright().start()
            browser = await playwright.chromium.connect_over_cdp(cdp_url)

            logger.info("Successfully connected to Incogniton browser via Playwright.")
            return browser

        except Exception as e:
            logger.error(f"Failed to connect to Incogniton Playwright: {str(e)}")
            raise RuntimeError(f"Failed to connect to Incogniton Playwright: {str(e)}")

    async def close(self, browser) -> None:
        """Close a single browser instance (Playwright or Selenium)."""
        try:
            # Playwright Browser
            if hasattr(browser, 'close') and asyncio.iscoroutinefunction(browser.close):
                await browser.close()
                logger.info("Playwright browser closed successfully")
            # Selenium WebDriver
            elif hasattr(browser, 'quit') and callable(browser.quit):
                browser.quit()
                logger.info("Selenium WebDriver closed successfully")
            else:
                raise TypeError("Unsupported browser type for close operation")
        except Exception as e:
            logger.error(f"Failed to close browser: {str(e)}")
            raise IncognitonError(f"Failed to close browser: {str(e)}")

    async def close_all(self, browsers: list) -> None:
        """Close all provided browser instances (Playwright or Selenium)."""
        try:
            logger.info(f"Closing {len(browsers)} browser instances...")
            for browser in browsers:
                await self.close(browser)
            logger.info("All browser instances closed successfully")
        except Exception as e:
            logger.error(f"Failed to close browser instances: {str(e)}")
            raise IncognitonError(f"Failed to close browser instances: {str(e)}")

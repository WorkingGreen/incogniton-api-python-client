from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from pyppeteer import connect
from pyppeteer.browser import Browser
from typing import Optional
import httpx
import asyncio

from incogniton.utils.logger import logger
from incogniton.api.client import IncognitonError

class IncognitonBrowser:
    def __init__(self, client, profile_id: str, headless: bool = True):
        self.client = client
        self.profile_id = profile_id
        self.headless = headless

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

    async def start_pyppeteer(self) -> Optional[Browser]:
        """Launch the profile and return a connected Pyppeteer Browser instance."""
        try:
            # Call the automation method to launch Puppeteer with custom args
            launch_args = "--headless=new" if self.headless else ""
            response = await self.client.automation.launchPuppeteerCustom(
                self.profile_id, launch_args
            )
            logger.info(f"Launch Puppeteer response: {response}")

            puppeteer_url = response.get("puppeteerUrl")
            if not puppeteer_url or response.get("status") != "ok":
                raise RuntimeError("Invalid Puppeteer launch response from Incogniton")

            logger.info("Waiting for browser to initialize...")
            await asyncio.sleep(35)

            # Fetch WebSocket debugger endpoint
            async with httpx.AsyncClient() as client:
                ws_response = await client.get(f"{puppeteer_url}/json/version")
                ws_response.raise_for_status()
                ws_url = ws_response.json().get("webSocketDebuggerUrl")

            if not ws_url:
                raise RuntimeError("Could not retrieve WebSocket debugger URL from Incogniton")

            browser = await connect(browserWSEndpoint=ws_url)
            return browser

        except Exception as e:
            logger.error(f"Failed to connect to Incogniton Puppeteer: {str(e)}")
            raise IncognitonError(f"Failed to connect to Incogniton Puppeteer: {str(e)}")

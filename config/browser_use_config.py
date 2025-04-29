from browser_use.browser.browser import BrowserConfig, Browser
from browser_use.browser.context import BrowserContextConfig, BrowserContext

browser_ctx_config = BrowserContextConfig(
    save_har_path="browser_requests.json",
)

browser_config=BrowserConfig(
        headless=False,
    )

browser = Browser(config=browser_config)

browser_ctx = BrowserContext(browser=browser,config=browser_ctx_config)
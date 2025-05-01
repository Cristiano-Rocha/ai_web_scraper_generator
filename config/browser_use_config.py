import os

from browser_use.browser.browser import BrowserConfig, Browser
from browser_use.browser.context import BrowserContextConfig, BrowserContext
from langchain_google_genai import ChatGoogleGenerativeAI

browser_ctx_config = BrowserContextConfig(
    save_har_path="browser_requests.json",
)

browser_config=BrowserConfig(
        headless=False,
    )

browser = Browser(config=browser_config)

browser_ctx = BrowserContext(browser=browser,config=browser_ctx_config)

llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash', api_key=os.getenv('GEMINI_API_KEY'))
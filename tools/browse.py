import os
from browser_use.browser.browser import BrowserConfig, Browser, ProxySettings
from browser_use.browser.context import BrowserContextConfig, BrowserContext
from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent
import asyncio
from dotenv import load_dotenv

from config.browser_use_config import browser_config, browser_ctx_config

load_dotenv()

proxy_host = "127.0.0.1"
proxy_port = 8080
proxy_settings = {
    "proxy": {
        "proxyType": "MANUAL",
        "httpProxy": f"{proxy_host}:{proxy_port}",
        "sslProxy": f"{proxy_host}:{proxy_port}",
    }
}



browser = Browser(config=browser_config)
context = BrowserContext(browser=browser, config=browser_ctx_config)
llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash', api_key=os.getenv('GEMINI_API_KEY'))

async def main():

    await agent.run()
    await context.close()
    await browser.close()

asyncio.run(main())
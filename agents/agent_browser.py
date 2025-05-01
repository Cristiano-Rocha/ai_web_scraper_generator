import asyncio
import os

from browser_use.agent.service import Agent
from browser_use.browser.browser import BrowserConfig, Browser
from browser_use.browser.context import BrowserContextConfig, BrowserContext
from langchain_anthropic import ChatAnthropic

async def browseit(task: str ="") -> None:
    system_prompt = """
            Você é um assistente de web scraper, sua tarefa é coletar dados
            {0}
           """
    browser_ctx_config = BrowserContextConfig(
        save_har_path="browser_requests.json",
    )

    browser_config = BrowserConfig(
        headless=True,
    )

    browser = Browser(config=browser_config)

    browser_ctx = BrowserContext(browser=browser, config=browser_ctx_config)

    llm = ChatAnthropic(
        model_name=os.getenv('ANTROPIC_MODEL'),
        api_key=os.getenv('ANTROPIC_API_KEY'),
        temperature=0.0,
        timeout=100  # Increase for complex tasks
    )
    agent = Agent(
        task=system_prompt.format(task),  # Use strip() for cleaner task string
        llm=llm,
        browser_context=browser_ctx,
    )
    await agent.run()
    await browser_ctx.close()
    await browser.close()


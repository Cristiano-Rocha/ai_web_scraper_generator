import asyncio
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from agents.agent_browser import ScrapingAgentFactory
from config.browser_use_config import browser_ctx_config, browser_ctx


async def main():
    llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash', api_key=os.getenv('GEMINI_API_KEY'))

    agent_browser = ScrapingAgentFactory().create_agent(llm=llm,browser_context=browser_ctx,instruction="Vá para o site google e pesquise a cotação do dolar")
    await agent_browser.run()

if __name__ == "__main__":
    asyncio.run(main())

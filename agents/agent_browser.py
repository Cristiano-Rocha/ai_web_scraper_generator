from browser_use.agent.service import Agent

class ScrapingAgentFactory:
    """
    A factory class for creating various types of web scraping agents.
    """

    @staticmethod
    def create_agent(
        llm,
        browser_context,
        system_prompt="""
         Você é um assistente de web scraper, sua tarefa é coletar dados
         {0}
        """,
        instruction="",
    ):
        """
        Creates an Agent configured to scrape Analyzer and Plan.

        Args:
            llm: The language model instance for the agent.
            browser_context: The browser context for the agent.
            system_prompt: The system prompt for the agent.

        Returns:
            An configured Agent instance.
        """


        agent = Agent(
            task=system_prompt.format(instruction), # Use strip() for cleaner task string
            llm=llm,
            browser_context=browser_context,
        )
        return agent
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List
from ...agent.base import BaseNode
from ...agent.handywriterz_state import HandyWriterzState

class LegislationScraperAgent(BaseNode):
    """An agent that scrapes legislation from specified government websites."""

    def __init__(self):
        super().__init__("legislation_scraper")

    async def execute(self, state: HandyWriterzState, config: dict) -> Dict[str, Any]:
        """
        Executes the legislation scraper agent.

        Args:
            state: The current state of the HandyWriterz workflow.
            config: The configuration for the agent.

        Returns:
            A dictionary containing the scraped legislation.
        """
        uk_legislation = self._scrape_legislation_gov_uk(state)
        eu_legislation = self._scrape_eur_lex(state)

        return {"uk_legislation": uk_legislation, "eu_legislation": eu_legislation}

    def _scrape_legislation_gov_uk(self, state: HandyWriterzState) -> List[Dict[str, str]]:
        """Scrapes legislation from legislation.gov.uk."""
        # This is a simplified example. A more robust implementation would
        # handle pagination, error handling, and more sophisticated parsing.
        query = self._construct_query(state)
        url = f"https://www.legislation.gov.uk/plain/results?text={query}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            
            results = []
            for item in soup.select(".result-item"):
                title_element = item.select_one(".title a")
                if title_element:
                    title = title_element.get_text(strip=True)
                    link = title_element["href"]
                    results.append({"title": title, "url": f"https://www.legislation.gov.uk{link}"})
            
            return results
        except requests.RequestException as e:
            self.logger.error(f"Error scraping legislation.gov.uk: {e}")
            return []

    def _scrape_eur_lex(self, state: HandyWriterzState) -> List[Dict[str, str]]:
        """Scrapes legislation from EUR-Lex."""
        # This is a simplified example. A more robust implementation would
        # handle pagination, error handling, and more sophisticated parsing.
        query = self._construct_query(state)
        url = f"https://eur-lex.europa.eu/search.html?text={query}&scope=EURLEX&type=quick&lang=en"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            
            results = []
            for item in soup.select(".SearchResult"):
                title_element = item.select_one(".title a")
                if title_element:
                    title = title_element.get_text(strip=True)
                    link = title_element["href"]
                    results.append({"title": title, "url": link})
            
            return results
        except requests.RequestException as e:
            self.logger.error(f"Error scraping EUR-Lex: {e}")
            return []

    def _construct_query(self, state: HandyWriterzState) -> str:
        """Constructs a legislation search query from the state."""
        # This is a simplified example. A more robust implementation would
        # use an LLM to generate the query based on the user's prompt.
        user_prompt = state.get("messages", [{}])[0].get("content", "")
        
        # Extract keywords from the prompt
        # This is a naive implementation and should be improved.
        keywords = ["embryo model", "synthetic embryo", "Human Fertilisation & Embryology Act", "EU directives"]
        
        return " OR ".join(f'"{keyword}"' for keyword in keywords)

import os
from typing import Dict, Any
from github import Github, GithubException
from src.agent.base import BaseNode
from ...agent.handywriterz_state import HandyWriterzState

class GitHubSearchAgent(BaseNode):
    """An agent that searches for GitHub repositories."""

    def __init__(self):
        super().__init__("github_search")
        self.github_token = os.getenv("GITHUB_TOKEN")
        if not self.github_token:
            # Allow for unauthenticated requests, but with a warning
            self.logger.warning("GITHUB_TOKEN not set. Using unauthenticated requests, which have a lower rate limit.")
            self.github = Github()
        else:
            self.github = Github(self.github_token)

    async def execute(self, state: HandyWriterzState, config: dict) -> Dict[str, Any]:
        """
        Executes the GitHub search agent.

        Args:
            state: The current state of the HandyWriterz workflow.
            config: The configuration for the agent.

        Returns:
            A dictionary containing the search results.
        """
        query = self._construct_query(state)
        self.logger.info(f"Executing GitHub search with query: {query}")

        try:
            repositories = self.github.search_repositories(query=query, sort="stars", order="desc")
            
            repo_list = []
            for repo in repositories[:10]: # Limit to top 10 results for now
                repo_list.append({
                    "full_name": repo.full_name,
                    "html_url": repo.html_url,
                    "description": repo.description,
                    "stargazers_count": repo.stargazers_count,
                    "topics": repo.get_topics(),
                })

            return {"github_repos": repo_list}
        except GithubException as e:
            self.logger.error(f"GitHub API error: {e}")
            return {"github_repos": [], "error_message": str(e)}

    def _construct_query(self, state: HandyWriterzState) -> str:
        """Constructs a GitHub search query from the state."""
        # This is a simplified example. A more robust implementation would
        # use an LLM to generate the query based on the user's prompt.
        user_prompt = state.get("messages", [{}])[0].get("content", "")
        
        # Extract keywords from the prompt
        # This is a naive implementation and should be improved.
        keywords = ["few-shot learning", "computer vision", "PyTorch"]
        
        query_parts = [
            " ".join(keywords),
            "language:python",
            "stars:>=100",
            "created:>=2024-01-01"
        ]
        
        return " ".join(query_parts)

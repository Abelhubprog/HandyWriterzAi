import os
from github import Github, GithubException

class GitHubIssuesTool:
    """A tool for fetching open issues from a GitHub repository."""

    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN")
        if not self.github_token:
            # Allow for unauthenticated requests, but with a warning
            print("GITHUB_TOKEN not set. Using unauthenticated requests, which have a lower rate limit.")
            self.github = Github()
        else:
            self.github = Github(self.github_token)

    def get_open_issues(self, repo_full_name: str, labels: list = None):
        """
        Fetches open issues from a GitHub repository.

        Args:
            repo_full_name: The full name of the repository (e.g., "owner/repo").
            labels: A list of labels to filter by (e.g., ["help wanted", "good first issue"]).

        Returns:
            A list of dictionaries, where each dictionary represents an open issue.
        """
        if labels is None:
            labels = ["help wanted", "good first issue"]
        
        try:
            repo = self.github.get_repo(repo_full_name)
            issues = repo.get_issues(state="open", labels=labels)
            
            issue_list = []
            for issue in issues:
                issue_list.append({
                    "title": issue.title,
                    "url": issue.html_url,
                    "number": issue.number,
                    "labels": [label.name for label in issue.labels],
                })
            
            return issue_list
        except GithubException as e:
            print(f"GitHub API error: {e}")
            return []

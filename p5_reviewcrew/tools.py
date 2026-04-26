
import os
import requests
from crewai.tools import tool
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}
def parse_pr_url(pr_url: str) -> tuple[str, str, int]:
    # https://github.com/rrvenkatrama/agentic_ai_projects/pull/1
    parts = pr_url.rstrip("/").split("/")
    owner = parts[-4]
    repo = parts[-3]
    number = int(parts[-1])
    return owner, repo, number

@tool("fetch_pr_details")
def fetch_pr_details(pr_url: str) -> str:
    """
    Fetches the title, description, changed files, and diff for a GitHub pull request.
    Input: a full GitHub PR URL like https://github.com/owner/repo/pull/42
    Returns: a formatted string with PR metadata and the full diff.
    """
    owner, repo, number = parse_pr_url(pr_url)
    base = f"https://api.github.com/repos/{owner}/{repo}/pulls/{number}"

    pr = requests.get(base, headers=HEADERS).json()
    files = requests.get(f"{base}/files", headers=HEADERS).json()

    title = pr.get("title", "")
    body = pr.get("body", "") or "No description"
    
    file_summaries = []
    for f in files:
        file_summaries.append(
            f"File: {f['filename']} (+{f['additions']} -{f['deletions']})\n{f.get('patch', 'Binary file')}"
        )

    return f"""PR #{number}: {title}

Description:
{body}

Changed Files and Diffs:
{'=' * 60}
{chr(10).join(file_summaries)}
"""
if __name__ == "__main__":
    pr_url = "https://github.com/rrvenkatrama/agentic_ai_projects/pull/1"
    print(fetch_pr_details.run(pr_url))


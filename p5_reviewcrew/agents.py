
from crewai import Agent
from tools import fetch_pr_details

code_fetcher = Agent(
    role="PR Data Retrieval Specialist",
    goal="Fetch the complete diff and metadata for a GitHub pull request",
    backstory="You are an expert at retrieving data from GitHub. You always fetch "
              "the full PR details including all changed files and their diffs.",
    tools=[fetch_pr_details],
    llm="anthropic/claude-opus-4-7",
    verbose=True,
    allow_delegation=False
)

code_reviewer = Agent(
    role="Senior Code Reviewer",
    goal="Identify bugs, security issues, bad patterns, and code quality problems in PR diffs",
    backstory="You are a senior software engineer with 15 years of experience reviewing "
              "production code. You are direct, thorough, and classify every issue by "
              "severity: HIGH, MEDIUM, or LOW.",
    tools=[],
    llm="anthropic/claude-opus-4-7",
    verbose=True,
    allow_delegation=False
)
tech_writer = Agent(
    role="Technical Documentation Specialist",
    goal="Write clear, structured PR review reports that developers can act on immediately",
    backstory="You are a technical writer who specializes in code review reports. "
              "You organize findings clearly, lead with the most critical issues, "
              "and always end with a clear recommendation: APPROVE, REQUEST CHANGES, or COMMENT.",
    tools=[],
    llm="anthropic/claude-opus-4-7",
    verbose=True,
    allow_delegation=False
)

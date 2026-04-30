
import os
os.environ["LITELLM_LOG"] = "DEBUG"
import sys
from crewai import Crew, Task, Process, Agent
from agents import code_fetcher, tech_writer
from tools import fetch_pr_details, post_pr_comment

security_reviewer = Agent(
    role="Security Specialist",
    goal="Find security vulnerabilities, hardcoded secrets, and unsafe patterns",
    backstory="You are a security engineer focused exclusively on vulnerabilities. "
              "You look for hardcoded credentials, injection risks, insecure protocols, "
              "and unsafe data handling.",
    tools=[],
    llm="anthropic/claude-opus-4-7",
    verbose=True,
    allow_delegation=False
)

style_reviewer = Agent(
    role="Code Style Specialist",
    goal="Find code style issues, naming violations, and maintainability problems",
    backstory="You are a senior engineer who enforces clean code standards. "
              "You look for naming conventions, missing type hints, dead code, "
              "and readability issues.",
    tools=[],
    llm="anthropic/claude-opus-4-7",
    verbose=True,
    allow_delegation=False
)

perf_reviewer = Agent(
    role="Performance Specialist",
    goal="Find performance issues, inefficient patterns, and resource leaks",
    backstory="You are a performance engineer. You look for unclosed resources, "
              "inefficient loops, unnecessary computations, and memory issues.",
    tools=[],
    llm="anthropic/claude-opus-4-7",
    verbose=True,
    allow_delegation=False
)

def run_parallel_review(pr_url: str) -> str:
    fetch_task = Task(
        description=f"Fetch the full details and diff for this PR: {pr_url}",
        expected_output="PR title, description, all changed files and diffs",
        agent=code_fetcher
    )

    security_task = Task(
        description="Review the PR diff for security issues only: hardcoded secrets, "
                    "insecure protocols, injection risks, unsafe patterns.",
        expected_output="Markdown list of security issues with severity and line numbers",
        agent=security_reviewer,
        context=[fetch_task],
        async_execution=True
    )

    style_task = Task(
        description="Review the PR diff for code style issues only: naming conventions, "
                    "missing type hints, dead code, readability.",
        expected_output="Markdown list of style issues with severity and line numbers",
        agent=style_reviewer,
        context=[fetch_task],
        async_execution=True
    )

    perf_task = Task(
        description="Review the PR diff for performance issues only: unclosed resources, "
                    "inefficient loops, memory issues.",
        expected_output="Markdown list of performance issues with severity and line numbers",
        agent=perf_reviewer,
        context=[fetch_task],
        async_execution=True
    )

    summary_task = Task(
        description="Combine all review findings into one complete PR review report. "
                    "Structure: Summary, Security Issues, Style Issues, Performance Issues, "
                    "Recommendation (APPROVE / REQUEST CHANGES / COMMENT).",
        expected_output="Complete formatted markdown PR review report",
        agent=tech_writer,
        context=[security_task, style_task, perf_task]
    )

    crew = Crew(
        agents=[code_fetcher, security_reviewer, style_reviewer,
                perf_reviewer, tech_writer],
        tasks=[fetch_task, security_task, style_task, perf_task, summary_task],
        process=Process.sequential,
        verbose=True
    )

    result = crew.kickoff()
    # Post to GitHub directly in Python — not an AI reasoning task
    post_result = post_pr_comment._run(pr_url=pr_url, comment=result.raw)
    print(f"\nGitHub: {post_result}")
    return result.raw

if __name__ == "__main__":
    pr_url = sys.argv[1] if len(sys.argv) > 1 else \
             "https://github.com/rrvenkatrama/agentic_ai_projects/pull/1"
    print("\n" + "=" * 60)
    print("PARALLEL REVIEW CREW REPORT")
    print("=" * 60)
    print(run_parallel_review(pr_url))

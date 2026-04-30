
import sys
from crewai import Crew, Task, Process
from agents import code_fetcher, code_reviewer, tech_writer

fetch_task = Task(
    description="Fetch the full details and diff for this GitHub PR: {pr_url}",
    expected_output="The PR title, description, all changed files and their complete diffs",
    agent=code_fetcher
)

review_task = Task(
    description="""Review the PR diff provided in context. 
    For every issue found, include: severity (HIGH/MEDIUM/LOW), filename, 
    line number if visible, and a clear explanation of the problem.""",
    expected_output="A markdown list of all issues found, grouped by severity",
    agent=code_reviewer,
    context=[fetch_task]
)

summary_task = Task(
    description="""Using the code review findings in context, write a complete PR review report.
    Structure it as:
    - Summary (2-3 sentences)
    - Issues by severity (HIGH, then MEDIUM, then LOW)
    - Recommendation: APPROVE, REQUEST CHANGES, or COMMENT""",
    expected_output="A complete formatted markdown PR review report",
    agent=tech_writer,
    context=[review_task]
)
def run_review(pr_url: str) -> str:
    crew = Crew(
        agents=[code_fetcher, code_reviewer, tech_writer],
        tasks=[fetch_task, review_task, summary_task],
        process=Process.sequential,
        verbose=True
    )
    result = crew.kickoff(inputs={"pr_url": pr_url})
    return result.raw

if __name__ == "__main__":
    pr_url = sys.argv[1] if len(sys.argv) > 1 else "https://github.com/rrvenkatrama/agentic_ai_projects/pull/1"
    print("\n" + "=" * 60)
    print("REVIEW CREW REPORT")
    print("=" * 60)
    print(run_review(pr_url))

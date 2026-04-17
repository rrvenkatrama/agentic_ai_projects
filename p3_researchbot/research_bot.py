from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
import operator
from ddgs import DDGS


class ResearchState(TypedDict):
    topic: str                  # this key holds a string
    search_queries: Annotated[list[str], operator.add]   # this key holds a list of strings
    findings: Annotated[list[str], operator.add]         # this key holds a list of strings
    summary: str                # this key holds a string

def generate_queries(state: ResearchState) -> dict:
    print(f"[Node 1] Generating queries for: {state['topic']}")
    queries = [
        f"What is {state['topic']}?",
        f"{state['topic']} latest developments",
        f"{state['topic']} key concepts"
    ]
    return {"search_queries": queries}

def route_summary(state: ResearchState) -> str:
    if len(state['findings']) >= 11:
        return "detailed_summary"
    else:
        return "brief_summary"

def generate_followup_queries(state: ResearchState) -> dict:
    print(f"[Node 1b] Generating follow-up queries...")
    return {"search_queries": [f"{state['topic']} real-world applications",
                                f"{state['topic']} limitations"]}

def research(state: ResearchState) -> dict:
    findings = []
    with DDGS() as ddgs:
        for query in state['search_queries']:
            results = ddgs.text(query, max_results=2)
            for r in results:
                findings.append(f"{r['title']}: {r['body']}")
    return {"findings": findings}

def detailed_summary(state: ResearchState) -> dict:
    print(f"[Router → detailed] {len(state['findings'])} findings")
    summary = "[Detailed] " + " | ".join(state['findings'])
    return {"summary": summary}

def brief_summary(state: ResearchState) -> dict:
    print(f"[Router → brief] only {len(state['findings'])} findings")
    summary = "[Brief - limited results] " + " | ".join(state['findings'][:2])
    return {"summary": summary}

def build_graph():
    graph = StateGraph(ResearchState)

    # Add nodes
    graph.add_node("generate_queries", generate_queries)
    graph.add_node("generate_followup_queries", generate_followup_queries)
    graph.add_node("research", research)
    graph.add_node("detailed_summary", detailed_summary)
    graph.add_node("brief_summary", brief_summary)

    # Define edges (flow)
    graph.set_entry_point("generate_queries")
    graph.add_edge("generate_queries", "generate_followup_queries")
    graph.add_edge("generate_followup_queries", "research")
    graph.add_conditional_edges("research", route_summary, {
        "detailed_summary": "detailed_summary",
        "brief_summary": "brief_summary"
    })
    graph.add_edge("detailed_summary", END)
    graph.add_edge("brief_summary", END)

    return graph.compile()

def main():
    app = build_graph()
    print(app.get_graph().draw_mermaid())

    # # Path 1 — real DuckDuckGo search (should have 10 findings → detailed)
    # # Comment out if you want to run the actual searches!
    # result = app.invoke({
    #     "topic": "LangGraph state machines",
    #     "search_queries": [], "findings": [], "summary": ""
    # })
    # print(result['summary'][:200])

    # Path 2 — force brief path
    # comment out if you do not want to run the actual searches!
    result = app.invoke({
        "topic": "LangGraph state machines",
        "search_queries": ["only one query"],
        "findings": ["just one finding"],
        "summary": ""
    })

    print("\n--- Final State ---")
    print(f"Topic: {result['topic']}\n")
    print(f"Queries: {result['search_queries']}\n")
    print(f"Total Queries: {len(result['search_queries'])}\n")
    print(f"Findings: {result['findings']}\n")
    print(f"Summary: {result['summary']}\n")

if __name__ == "__main__":
    main()
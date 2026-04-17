from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
import operator

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

def generate_followup_queries(state: ResearchState) -> dict:
    print(f"[Node 1b] Generating follow-up queries...")
    return {"search_queries": [f"{state['topic']} real-world applications",
                                f"{state['topic']} limitations"]}

def research(state: ResearchState) -> dict:
    print(f"[Node 2] Researching {len(state['search_queries'])} queries...")
    findings = [f"Finding for: {q}" for q in state['search_queries']]
    return {"findings": findings}

def summarise(state: ResearchState) -> dict:
    print(f"[Node 3] Summarising {len(state['findings'])} findings...")
    summary = f"Summary of {state['topic']}: " + " | ".join(state['findings'][:2])
    return {"summary": summary}

def build_graph():
    graph = StateGraph(ResearchState)

    # Add nodes
    graph.add_node("generate_queries", generate_queries)
    graph.add_node("generate_followup_queries", generate_followup_queries)
    graph.add_node("research", research)
    graph.add_node("summarise", summarise)

    # Define edges (flow)
    graph.set_entry_point("generate_queries")
    graph.add_edge("generate_queries", "generate_followup_queries")
    graph.add_edge("generate_followup_queries", "research")
    graph.add_edge("research", "summarise")
    graph.add_edge("summarise", END)

    return graph.compile()

def main():
    app = build_graph()

    result = app.invoke({
        "topic": "LangGraph state machines",
        "search_queries": [],
        "findings": [],
        "summary": ""
    })

    print("\n--- Final State ---")
    print(f"Topic: {result['topic']}")
    print(f"Queries: {result['search_queries']}")
    print(f"Total Queries: {len(result['search_queries'])}")
    print(f"Findings: {result['findings']}")
    print(f"Summary: {result['summary']}")

if __name__ == "__main__":
    main()
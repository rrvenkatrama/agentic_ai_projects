
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
import operator
from ddgs import DDGS
from langgraph.checkpoint.memory import MemorySaver



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



def summarise(state: ResearchState) -> dict:
    print(f"[summarise] Summarising {len(state['findings'])} findings...")
    summary = f"Summary of '{state['topic']}':\n" + "\n".join(
        f"  - {f[:120]}" for f in state['findings']
    )
    return {"summary": summary}

def build_graph():
    memory = MemorySaver()

    graph = StateGraph(ResearchState)

    graph.add_node("generate_queries", generate_queries)
    graph.add_node("generate_followup_queries", generate_followup_queries)
    graph.add_node("research", research)
    graph.add_node("summarise", summarise)

    graph.set_entry_point("generate_queries")
    graph.add_edge("generate_queries", "generate_followup_queries")
    graph.add_edge("generate_followup_queries", "research")
    graph.add_edge("research", "summarise")
    graph.add_edge("summarise", END)

    return graph.compile(
        checkpointer=memory,
        interrupt_before=["summarise"]
    )

def main():
    app = build_graph()
    config = {"configurable": {"thread_id": "1"}}

    # Phase 1 — run until interrupt (before summarise)
    print("\n--- Phase 1: Research ---")
    app.invoke({
        "topic": "quantum computing",
        "search_queries": [], "findings": [], "summary": ""
    }, config)

    # Inspect state at the interrupt point
    state = app.get_state(config)
    findings = state.values["findings"]

    print(f"\n--- Human Review: {len(findings)} findings ---")
    for i, f in enumerate(findings):
        print(f"  [{i}] {f[:100]}")

    # Human decision
    choice = input("\nApprove findings? (y/n/edit): ").strip().lower()

    if choice == 'n':
        print("Aborted by human.")
        return

    if choice == 'edit':
        extra = input("Type a finding to add: ").strip()
        app.update_state(config, {"findings": [extra]})

    # Phase 2 — resume from checkpoint, runs summarise
    print("\n--- Phase 2: Resuming ---")
    result = app.invoke(None, config)
    print("\n--- Final Summary ---")
    print(result["summary"])

if __name__ == "__main__":
    main()
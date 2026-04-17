from typing import TypedDict, Annotated
import operator
from pydantic import BaseModel
from langgraph.graph import StateGraph, END
from ddgs import DDGS

class Finding(BaseModel):
    agent: str      # "news" | "technical" | "examples"
    title: str
    body: str

class HubState(TypedDict):
    topic: str
    findings: Annotated[list[Finding], operator.add]
    summary: str



def coordinator(state: HubState) -> dict:
    print(f"[Coordinator] Fanning out to 3 agents for: {state['topic']}")
    return {}

def news_agent(state: HubState) -> dict:
    print(f"[news_agent] Searching news for: {state['topic']}")
    findings = []
    with DDGS(timeout=10) as ddgs:
        for r in ddgs.text(f"{state['topic']} news 2024", max_results=2):
            findings.append(Finding(agent="news", title=r['title'], body=r['body']))
    return {"findings": findings}

def technical_agent(state: HubState) -> dict:
    print(f"[technical_agent] Searching technical for: {state['topic']}")
    findings = []
    with DDGS(timeout=10) as ddgs:
        for r in ddgs.text(f"{state['topic']} how it works technical", max_results=2):
            findings.append(Finding(agent="technical", title=r['title'], body=r['body']))
    return {"findings": findings}

def examples_agent(state: HubState) -> dict:
    print(f"[examples_agent] Searching examples for: {state['topic']}")
    findings = []
    with DDGS(timeout=10) as ddgs:
        for r in ddgs.text(f"{state['topic']} real world examples use cases", max_results=2):
            findings.append(Finding(agent="examples", title=r['title'], body=r['body']))
    return {"findings": findings}

def aggregator(state: HubState) -> dict:
    print(f"[Aggregator] Merging {len(state['findings'])} findings from 3 agents")
    lines = [f"  [{f.agent}] {f.title}: {f.body[:80]}" for f in state['findings']]
    summary = f"Summary for '{state['topic']}':\n" + "\n".join(lines)
    return {"summary": summary}


def build_graph():
    graph = StateGraph(HubState)

    graph.add_node("coordinator", coordinator)
    graph.add_node("news_agent", news_agent)
    graph.add_node("technical_agent", technical_agent)
    graph.add_node("examples_agent", examples_agent)
    graph.add_node("aggregator", aggregator)

    graph.set_entry_point("coordinator")

    # fan-out
    graph.add_edge("coordinator", "news_agent")
    graph.add_edge("coordinator", "technical_agent")
    graph.add_edge("coordinator", "examples_agent")

    # fan-in
    graph.add_edge("news_agent", "aggregator")
    graph.add_edge("technical_agent", "aggregator")
    graph.add_edge("examples_agent", "aggregator")

    graph.add_edge("aggregator", END)

    return graph.compile()


def run_invoke(app, topic):
    print("\n=== invoke() mode ===")
    result = app.invoke({"topic": topic, "findings": [], "summary": ""})
    print(result['summary'])

def run_stream(app, topic):
    print("\n=== stream() mode ===")
    for chunk in app.stream({"topic": topic, "findings": [], "summary": ""}):
        node_name = list(chunk.keys())[0]
        print(f"\n[{node_name} completed]")
        node_data = chunk[node_name]
        if node_data is None:
            continue
        if node_name == "aggregator":
            print(chunk[node_name]['summary'])
        else:
            for f in chunk[node_name].get('findings', []):
                print(f"  [{f.agent}] {f.title}")

if __name__ == "__main__":
    app = build_graph()
    print(app.get_graph().draw_mermaid())
    run_invoke(app, "quantum computing")
    run_stream(app, "quantum computing")


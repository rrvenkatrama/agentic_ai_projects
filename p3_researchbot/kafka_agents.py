
import sys
import json
import time
from pydantic import BaseModel
from ddgs import DDGS
from kafka import KafkaProducer, KafkaConsumer


BROKER = '192.168.1.156:30092'
TASKS_TOPIC    = 'research-tasks'
FINDINGS_TOPIC = 'research-findings'

class Finding(BaseModel):
    agent: str
    title: str
    body: str

def producer(topic='quantum computing'):
    p = KafkaProducer(
        bootstrap_servers=BROKER,
        value_serializer=lambda v: json.dumps(v).encode()
    )
    for agent_type in ['news', 'technical', 'examples']:
        msg = {'topic': topic, 'agent': agent_type}
        p.send(TASKS_TOPIC, msg)
        print(f"[producer] published task → agent={agent_type}, topic={topic}")
    p.flush()
    print("[producer] all 3 tasks published")

def consumer(agent_type):
    c = KafkaConsumer(
        TASKS_TOPIC,
        bootstrap_servers=BROKER,
        group_id=f'{agent_type}-group',
        auto_offset_reset='earliest',
        value_deserializer=lambda m: json.loads(m.decode())
    )
    p = KafkaProducer(
        bootstrap_servers=BROKER,
        value_serializer=lambda v: json.dumps(v).encode()
    )
    print(f"[{agent_type}_agent] listening on {TASKS_TOPIC}...")
    for msg in c:
        task = msg.value
        if task['agent'] != agent_type:
            continue
        print(f"[{agent_type}_agent] got task: {task['topic']}")
        findings = []
        with DDGS(timeout=10) as ddgs:
            query = f"{task['topic']} {agent_type} 2024"
            for r in ddgs.text(query, max_results=2):
                findings.append(Finding(agent=agent_type, title=r['title'], body=r['body']))
        for f in findings:
            p.send(FINDINGS_TOPIC, f.model_dump())
            print(f"[{agent_type}_agent] published finding: {f.title[:60]}")
        p.flush()

def aggregator(expected=3):
    c = KafkaConsumer(
        FINDINGS_TOPIC,
        bootstrap_servers=BROKER,
        group_id='aggregator-group',
        auto_offset_reset='earliest',
        value_deserializer=lambda m: json.loads(m.decode())
    )
    print(f"[aggregator] waiting for {expected} findings (one per agent type)...")
    findings = []
    seen = set()
    for msg in c:
        f = Finding(**msg.value)
        if f.agent not in seen:
            seen.add(f.agent)
            findings.append(f)
            print(f"[aggregator] received [{f.agent}] {f.title[:60]}")
        else:
            print(f"[aggregator] skipped duplicate [{f.agent}]")
        if len(seen) >= expected:
            break
    print(f"\n=== Summary ({len(findings)} findings) ===")
    for f in findings:
        print(f"  [{f.agent}] {f.title}")
        print(f"           {f.body[:100]}")


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else ''
    arg  = sys.argv[2] if len(sys.argv) > 2 else ''

    if mode == 'producer':
        producer()
    elif mode == 'consumer' and arg:
        consumer(arg)
    elif mode == 'aggregator':
        aggregator()
    else:
        print("Usage:")
        print("  python kafka_agents.py producer")
        print("  python kafka_agents.py consumer news|technical|examples")
        print("  python kafka_agents.py aggregator")





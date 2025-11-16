# Simulates an LLM-driven agent that is vulnerable to prompt injection inside manifest text.
import requests
import pprint
import json

MCP = "http://127.0.0.1:8000"
pp = pprint.PrettyPrinter(indent=2)

def fetch_manifest():
    r = requests.get(f"{MCP}/manifest")
    r.raise_for_status()
    return r.json()

def invoke(tool, params):
    r = requests.post(f"{MCP}/invoke", json={"tool": tool, "params": params})
    r.raise_for_status()
    return r.json()

def vulnerable_planner(manifest, goal, context):
    """
    Very small simulation of an LLM-based planner:
    - Build a "prompt" by concatenating tool descriptions and the goal.
    - If any tool description contains words like "diagnostic", the planner
      will follow that instruction and include a `diagnostic` param.
    - This simulates the LLM being tricked by injected text in the manifest.
    """
    tool_texts = []
    for name, spec in manifest["tools"].items():
        desc = spec.get("description", "")
        tool_texts.append(f"{name}: {desc}")
    system_prompt = "\n".join(tool_texts) + f"\nGOAL: {goal}\nCONTEXT: {json.dumps(context)}"

    print("\n[PLANNER] System prompt (what the LLM sees):")
    print(system_prompt)

    # Planner logic: for demo, choose get_weather
    chosen_tool = "get_weather"
    params = {"location": "Bangkok"}

    # Vulnerable behavior: if the concatenated descriptions mention 'diagnostic',
    # include a diagnostic param with the entire context (which may contain PII).
    if "diagnostic" in system_prompt.lower():
        print("[PLANNER] Found 'diagnostic' in tool descriptions -> adding diagnostic param")
        params["diagnostic"] = context  # includes contacts (PII)

    # Return the planned invocation (what an LLM would return as JSON)
    planned = {"tool": chosen_tool, "params": params}
    print("[PLANNER] Planned invocation:")
    pp.pprint(planned)
    return planned

def main():
    manifest = fetch_manifest()
    print("[AGENT] Fetched manifest:")
    pp.pprint(manifest)

    # Agent legitimately calls get_contacts() to obtain PII (mock)
    print("\n[AGENT] Calling get_contacts() to obtain contacts (mock PII)...")
    contacts_resp = invoke("get_contacts", {})
    contacts = contacts_resp["contacts"]
    print("[AGENT] Contacts received:")
    pp.pprint(contacts)

    # The 'context' the planner will see (may include the recent contacts)
    context = {"recent_contacts": contacts, "session_id": "abc-123"}

    # Planner is given manifest, goal, and context and returns an invocation.
    goal = "Get the weather for the user"
    planned_call = vulnerable_planner(manifest, goal, context)

    # Agent blindly executes the planner's JSON (no validation)
    print("\n[AGENT] Executing planner's invocation (blindly)...")
    resp = invoke(planned_call["tool"], planned_call["params"])
    print("[AGENT] Tool response:")
    pp.pprint(resp)

    # Attacker inspects captures
    captures = requests.get(f"{MCP}/captures").json()
    print("\n[MALICIOUS SERVER] Captured undeclared parameters (attacker view):")
    pp.pprint(captures)

if __name__ == "__main__":
    main()

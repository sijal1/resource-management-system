import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ASP_URL = "https://localhost:7230/api/projects/get-all"

def get_all_projects():
    try:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        payload = {}

        response = requests.post(
            ASP_URL,
            json=payload,       
            headers=headers,
            timeout=8,
            verify=False
        )

        # print(response)
        response.raise_for_status()
        json_data = response.json()

        if isinstance(json_data, dict):
            projects = json_data.get("working_days", [])
        
            if not isinstance(projects, list) or not projects:
                projects = json_data.get("data") or json_data.get("projects") or []
        elif isinstance(json_data, list):
            projects = json_data
        else:
            projects = []

        return projects

    except Exception as e:
        print("Error reading ASP.NET:", e)
        try:
            print("Response text snippet:", response.text[:300])
        except Exception:
            pass
        return []



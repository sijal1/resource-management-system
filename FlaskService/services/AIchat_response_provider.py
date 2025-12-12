
"""
- `data_store`: dict keeping employees, projects, capacity summary and bench-by-skill
- `refresh_data()`: function to re-fetch all endpoints and update `data_store`
- `get_data_store()`: returns the current in-memory store
- `employee_response`: returm data_store to main route with `app.py`

The module uses `requests` and disables TLS verification by default to allow
local development against `https://localhost:7230` with self-signed certs.
"""

from typing import Any, Dict
import requests
import threading
import time
import warnings
# Suppress only the single InsecureRequestWarning from urllib3 when verify=False
from urllib3.exceptions import InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)

# Base URL for the backend APIs. Change if needed.
BASE_URL = "https://localhost:7230"

# Default request timeout (seconds)
DEFAULT_TIMEOUT = 10

# In-memory store for fetched API responses
data_store: Dict[str, Any] = {
	"employees_data": [],
	"projects_data": [],
	"project_capacity": {},
	"bench_emp_data": []
}


def _fetch(method: str, path: str, json_payload: Any = None) -> Any:
	"""Internal helper to perform an HTTP request and return JSON or None."""
	url = f"{BASE_URL}{path}"
	try:
		if method.upper() == "GET":
			resp = requests.get(url, timeout=DEFAULT_TIMEOUT, verify=False)
		elif method.upper() == "POST":
			resp = requests.post(url, json=json_payload, timeout=DEFAULT_TIMEOUT, verify=False)
		else:
			raise ValueError(f"Unsupported method: {method}")

		resp.raise_for_status()
		try:
			return resp.json()
		except ValueError:
			# Not JSON; return text
			return resp.text

	except Exception as e:
		# Keep failures visible but don't crash import
		return {"error": str(e)}


def refresh_data() -> Dict[str, Any]:
	"""Fetch all backend endpoints and update `data_store`.

	Returns the updated `data_store`.
	"""
	# 1) Employees (POST)
	employees = _fetch("POST", "/api/Employee/GetAllEmployees")

	# 2) Capacity summary (GET)
	capacity = _fetch("GET", "/api/BenchManagement/capacity-summary")

	# 3) Bench by skill (POST) -- path provided by user
	bench_by_skill = _fetch("GET", "/api/projects/get-allgement/bench-by-skill")

	# 4) Projects (POST)
	projects = _fetch("POST", "/api/projects/get-all")

	# Normalize/store
	data_store["employees_data"] = employees if employees is not None else []
	data_store["project_capacity"] = capacity if capacity is not None else {}
	data_store["bench_emp_data"] = bench_by_skill if bench_by_skill is not None else []
	data_store["projects_data"] = projects if projects is not None else []

	return data_store


def get_data_store() -> Dict[str, Any]:
	"""Return the current in-memory `data_store`."""
	return data_store


# Backwards compatibility: app.py expects `employee_response` variable.
# We'll expose the full `data_store` as `employee_response` so the chatbot
# prompt has access to all fetched datasets.
employee_response = data_store


print(employee_response)


def start_auto_refresh(interval_seconds: int = 300) -> threading.Thread:
	"""Start a background thread that refreshes `data_store` every `interval_seconds`.
	"""
	def _loop():
		while True:
			try:
				refresh_data()
			except Exception:
				pass
			time.sleep(interval_seconds)

	thread = threading.Thread(target=_loop, daemon=True, name="data_refresh_thread")
	thread.start()
	return thread





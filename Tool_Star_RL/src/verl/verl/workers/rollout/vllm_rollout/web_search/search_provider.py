import os
import time
from pathlib import Path

import requests
from requests.exceptions import Timeout


DEFAULT_BRAVE_ENDPOINT = "https://api.search.brave.com/res/v1/web/search"


def load_env_file():
    candidates = []

    cwd = Path.cwd().resolve()
    candidates.extend([cwd, *cwd.parents])

    file_dir = Path(__file__).resolve().parent
    candidates.extend([file_dir, *file_dir.parents])

    seen = set()
    for directory in candidates:
        if directory in seen:
            continue
        seen.add(directory)

        env_path = directory / ".env"
        if not env_path.is_file():
            continue

        for line in env_path.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith("export "):
                stripped = stripped[len("export "):].strip()
            if "=" not in stripped:
                continue

            key, value = stripped.split("=", 1)
            key = key.strip()
            value = value.strip().strip("'").strip('"')
            os.environ.setdefault(key, value)
        return env_path

    return None


def get_web_search_config(
    api_key=None,
    endpoint=None,
    provider=None,
):
    load_env_file()

    resolved_provider = (provider or os.getenv("WEB_SEARCH_PROVIDER") or "brave").strip().lower()
    resolved_api_key = api_key or os.getenv("WEB_SEARCH_API_KEY") or os.getenv("BRAVE_SEARCH_API_KEY")

    if resolved_provider != "brave":
        raise ValueError(f"Unsupported web search provider: {resolved_provider}")

    resolved_endpoint = endpoint or os.getenv("WEB_SEARCH_ENDPOINT") or os.getenv(
        "BRAVE_SEARCH_ENDPOINT",
        DEFAULT_BRAVE_ENDPOINT,
    )

    return {
        "provider": resolved_provider,
        "api_key": resolved_api_key,
        "endpoint": resolved_endpoint,
    }


def web_search(query, api_key=None, endpoint=None, provider=None, timeout=20, count=10):
    config = get_web_search_config(api_key=api_key, endpoint=endpoint, provider=provider)

    if not config["api_key"]:
        raise ValueError(
            "Missing Brave Search API key. Set WEB_SEARCH_API_KEY or BRAVE_SEARCH_API_KEY in your environment or .env file."
        )

    headers = {
        "Accept": "application/json",
        "X-Subscription-Token": config["api_key"],
    }
    params = {
        "q": query,
        "count": count,
        "country": os.getenv("BRAVE_SEARCH_COUNTRY", "US"),
        "search_lang": os.getenv("BRAVE_SEARCH_LANG", "en"),
        "safesearch": os.getenv("BRAVE_SEARCH_SAFESEARCH", "moderate"),
        "text_decorations": False,
        "spellcheck": True,
    }

    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            response = requests.get(config["endpoint"], headers=headers, params=params, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except Timeout:
            retry_count += 1
            if retry_count == max_retries:
                print(f"Brave Web Search request timed out ({timeout} seconds) for query: {query}")
                return {}
            print(f"Brave Web Search timeout occurred, retrying ({retry_count}/{max_retries})...")
        except requests.exceptions.RequestException as e:
            retry_count += 1
            if retry_count == max_retries:
                print(f"Brave Web Search request error occurred: {e}")
                return {}
            print(f"Brave Web Search request error occurred, retrying ({retry_count}/{max_retries})...")
        time.sleep(1)

    return {}


def extract_relevant_info(search_results):
    useful_info = []

    for idx, result in enumerate(search_results.get("web", {}).get("results", []), start=1):
        profile = result.get("profile") or {}
        useful_info.append(
            {
                "id": idx,
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "site_name": profile.get("long_name", "") or profile.get("name", ""),
                "date": result.get("age", ""),
                "snippet": result.get("description", ""),
                "context": "",
            }
        )

    return useful_info

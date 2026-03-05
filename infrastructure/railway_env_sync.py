"""
Railway Env Sync — push local .env variables to a Railway service.

Usage:
    python infrastructure/railway_env_sync.py
    python infrastructure/railway_env_sync.py --env path/to/.env

Reads all key=value pairs from the .env file and upserts them
as environment variables on the target Railway service via GraphQL.

Required env vars (can be in the .env itself or already exported):
    RAILWAY_API_TOKEN
    RAILWAY_PROJECT_ID
    RAILWAY_SERVICE_ID
"""

import os
import sys
import argparse
from pathlib import Path

import requests
from dotenv import dotenv_values

RAILWAY_GRAPHQL_URL = "https://backboard.railway.app/graphql/v2"

# Keys used by this script — never sync these to Railway
INTERNAL_KEYS = {
    "RAILWAY_API_TOKEN",
    "RAILWAY_PROJECT_ID",
    "RAILWAY_SERVICE_ID",
}


def load_env_vars(env_path: str) -> dict[str, str]:
    """Load key=value pairs from a .env file, skipping comments and blanks."""
    raw = dotenv_values(env_path)
    # Filter out internal keys and empty values
    return {k: v for k, v in raw.items() if k not in INTERNAL_KEYS and v}


def sync_env_to_railway(
    variables: dict[str, str],
    api_token: str,
    project_id: str,
    service_id: str,
) -> bool:
    """Upsert environment variables on a Railway service via GraphQL."""

    mutation = """
    mutation VariableCollectionUpsert($input: VariableCollectionUpsertInput!) {
        variableCollectionUpsert(input: $input)
    }
    """

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "query": mutation,
        "variables": {
            "input": {
                "projectId": project_id,
                "serviceId": service_id,
                "environmentId": None,  # uses default environment
                "variables": variables,
            }
        },
    }

    for key in variables:
        print(f"  Syncing {key}")

    print(f"\nPushing {len(variables)} variables to Railway...")

    resp = requests.post(RAILWAY_GRAPHQL_URL, json=payload, headers=headers, timeout=30)

    if resp.status_code != 200:
        print(f"ERROR: Railway API returned {resp.status_code}")
        print(resp.text)
        return False

    body = resp.json()
    if "errors" in body:
        print("ERROR: GraphQL errors:")
        for err in body["errors"]:
            print(f"  - {err.get('message', err)}")
        return False

    print("Done — variables synced successfully.")
    return True


def main():
    parser = argparse.ArgumentParser(description="Sync .env variables to Railway")
    parser.add_argument(
        "--env",
        default=str(Path(__file__).resolve().parent.parent / ".env"),
        help="Path to .env file (default: project root .env)",
    )
    args = parser.parse_args()

    env_path = args.env
    if not os.path.isfile(env_path):
        print(f"ERROR: .env file not found at {env_path}")
        sys.exit(1)

    # Load Railway credentials from environment or from the .env file itself
    all_vars = dotenv_values(env_path)
    api_token = os.getenv("RAILWAY_API_TOKEN") or all_vars.get("RAILWAY_API_TOKEN")
    project_id = os.getenv("RAILWAY_PROJECT_ID") or all_vars.get("RAILWAY_PROJECT_ID")
    service_id = os.getenv("RAILWAY_SERVICE_ID") or all_vars.get("RAILWAY_SERVICE_ID")

    missing = []
    if not api_token:
        missing.append("RAILWAY_API_TOKEN")
    if not project_id:
        missing.append("RAILWAY_PROJECT_ID")
    if not service_id:
        missing.append("RAILWAY_SERVICE_ID")

    if missing:
        print(f"ERROR: Missing required variables: {', '.join(missing)}")
        print("Set them in your .env or export them before running.")
        sys.exit(1)

    variables = load_env_vars(env_path)
    if not variables:
        print("No variables to sync (file empty or all filtered).")
        sys.exit(0)

    print(f"Loaded {len(variables)} variables from {env_path}\n")

    success = sync_env_to_railway(variables, api_token, project_id, service_id)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

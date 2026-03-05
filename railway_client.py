"""
Railway Client — interface to Railway's GraphQL API.

Handles restarting services and triggering deployments
for PythonFX via Railway's public API.
"""

import os

import requests

from utils.logger import log

RAILWAY_API_URL = "https://backboard.railway.app/graphql/v2"
REQUEST_TIMEOUT = 15


def _get_config():
    """Read Railway config at call time."""
    return {
        "token": os.getenv("RAILWAY_API_TOKEN"),
        "project_id": os.getenv("RAILWAY_PROJECT_ID"),
        "service_id": os.getenv("RAILWAY_SERVICE_ID"),
        "environment_id": os.getenv("RAILWAY_ENVIRONMENT_ID"),
    }


def _gql(query: str, variables: dict) -> dict:
    """Execute a Railway GraphQL query."""
    config = _get_config()
    if not config["token"]:
        raise RuntimeError("RAILWAY_API_TOKEN not configured")

    resp = requests.post(
        RAILWAY_API_URL,
        json={"query": query, "variables": variables},
        headers={
            "Authorization": f"Bearer {config['token']}",
            "Content-Type": "application/json",
        },
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()

    if "errors" in data:
        raise RuntimeError(data["errors"][0]["message"])

    return data.get("data", {})


def _get_latest_deployment_id() -> str | None:
    """Get the latest deployment ID for the configured service."""
    config = _get_config()
    if not config["project_id"] or not config["service_id"]:
        return None

    query = """
    query deployments($input: DeploymentListInput!) {
      deployments(input: $input, first: 1) {
        edges {
          node {
            id
            status
          }
        }
      }
    }
    """
    variables = {
        "input": {
            "projectId": config["project_id"],
            "serviceId": config["service_id"],
        }
    }
    if config["environment_id"]:
        variables["input"]["environmentId"] = config["environment_id"]

    data = _gql(query, variables)
    edges = data.get("deployments", {}).get("edges", [])
    if edges:
        return edges[0]["node"]["id"]
    return None


def restart_service(service_name: str) -> str:
    """Restart the latest deployment (no rebuild)."""
    config = _get_config()
    if not config["token"]:
        return "⚠ Railway API not configured. Set RAILWAY_API_TOKEN."

    try:
        deployment_id = _get_latest_deployment_id()
        if not deployment_id:
            return "⚠ No deployment found to restart."

        query = """
        mutation deploymentRestart($id: String!) {
          deploymentRestart(id: $id)
        }
        """
        _gql(query, {"id": deployment_id})
        log.info("railway: restarted deployment for %s", service_name)
        return f"✅ Restart triggered for {service_name}."

    except Exception as e:
        log.error("railway: restart failed — %s", e)
        return f"⚠ Restart failed: {e}"


def deploy_latest() -> str:
    """Trigger a new deployment from latest commit."""
    config = _get_config()
    if not config["token"]:
        return "⚠ Railway API not configured. Set RAILWAY_API_TOKEN."

    if not config["service_id"] or not config["environment_id"]:
        return "⚠ Missing RAILWAY_SERVICE_ID or RAILWAY_ENVIRONMENT_ID."

    try:
        query = """
        mutation environmentTriggersDeploy($input: EnvironmentTriggersDeployInput!) {
          environmentTriggersDeploy(input: $input)
        }
        """
        variables = {
            "input": {
                "environmentId": config["environment_id"],
                "projectId": config["project_id"],
                "serviceId": config["service_id"],
            }
        }
        _gql(query, variables)
        log.info("railway: deploy triggered")
        return "✅ Deploy triggered from latest commit."

    except Exception as e:
        log.error("railway: deploy failed — %s", e)
        return f"⚠ Deploy failed: {e}"


def get_deploy_status() -> str:
    """Check current deployment status."""
    config = _get_config()
    if not config["token"]:
        return "⚠ Railway API not configured."

    try:
        deployment_id = _get_latest_deployment_id()
        if not deployment_id:
            return "No deployments found."

        query = """
        query deployment($id: String!) {
          deployment(id: $id) {
            id
            status
            createdAt
          }
        }
        """
        data = _gql(query, {"id": deployment_id})
        dep = data.get("deployment", {})
        return f"Status: {dep.get('status', 'unknown')} | Created: {dep.get('createdAt', 'unknown')}"

    except Exception as e:
        log.error("railway: status check failed — %s", e)
        return f"⚠ Status check failed: {e}"

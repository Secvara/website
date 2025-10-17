#!/usr/bin/env python3
"""
Interactive helper to populate scripts/google/config.yaml by discovering IDs from the APIs.
Run after the core secrets (service account JSON, OAuth client/secret/refresh token, developer token)
have been added to config.yaml. Provide optional *_hint fields in the YAML to auto-select resources
without prompts.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.analytics.admin_v1beta import AnalyticsAdminServiceClient
from google.analytics.admin_v1beta.types import DataStream
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow

try:
    from . import utils
except ImportError:  # pragma: no cover - allow running as a script
    import utils  # type: ignore


CONFIG_PATH = Path(__file__).resolve().parent / "config.yaml"

DEFAULT_CONFIG: Dict[str, Any] = {
    "project": {
        "service_account_key": "./scripts/google/credentials/service-account.json",
    },
    "oauth": {
        "client_secrets_file": "./scripts/google/credentials/oauth-client.json",
        "refresh_token": "",
    },
    "ads": {
        "developer_token": "",
        "login_customer_id": "",
        "customer_id": "",
    },
    "gtm": {
        "account_id": "",
        "container_id": "",
        "workspace_id": "",
        "all_pages_trigger": "All Pages",
        "conversion_event": "book_appointment_conversion",
    },
    "ga4": {
        "property_id": "",
        "data_stream_id": "",
        "measurement_id": "",
    },
    "quota_project": "",
}


def load_config_file() -> Dict[str, Any]:
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
            if not isinstance(data, dict):
                raise RuntimeError("config.yaml must map keys to values.")
            merged = deepcopy(DEFAULT_CONFIG)
            for key, value in data.items():
                if isinstance(value, dict) and key in merged:
                    merged[key].update(value)  # type: ignore[index]
                else:
                    merged[key] = value
            return merged
    save_config_file(DEFAULT_CONFIG)
    print(f"Created default config at {CONFIG_PATH}. Fill in secrets, then rerun.")
    return deepcopy(DEFAULT_CONFIG)


def save_config_file(data: Dict[str, Any]) -> None:
    with CONFIG_PATH.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False)
    utils.load_config.cache_clear()  # type: ignore[attr-defined]


def ensure_nested(config: Dict[str, Any], path: List[str]) -> Dict[str, Any]:
    node = config
    for part in path:
        if part not in node or not isinstance(node[part], dict):
            node[part] = {}
        node = node[part]
    return node


def _normalize(value: Any) -> str:
    return str(value).strip().lower()


def select_with_hints(
    options: List[Dict[str, Any]], keys: List[str], hints: List[Any]
) -> Optional[Dict[str, Any]]:
    normalized_hints = [_normalize(h) for h in hints if h not in (None, "")]
    if not normalized_hints:
        return None
    for hint in normalized_hints:
        for option in options:
            for key in keys:
                candidate = option.get(key)
                if candidate is None:
                    continue
                if _normalize(candidate) == hint:
                    return option
    return None


def choose(
    prompt: str,
    options: List[Dict[str, Any]],
    label_key: str,
    existing: Any = None,
) -> Optional[Dict[str, Any]]:
    if not options:
        print(f"No {prompt.lower()} found.")
        return None
    if existing not in (None, "", 0):
        selected = select_with_hints(
            options,
            [
                "name",
                label_key,
                "path",
                "accountId",
                "containerId",
                "workspaceId",
                "triggerId",
                "propertyId",
                "streamId",
                "measurementId",
                "id",
            ],
            [existing],
        )
        if selected:
            print(f"{prompt}: keeping existing selection {selected.get(label_key, selected)}")
            return selected
    if len(options) == 1:
        only = options[0]
        print(f"{prompt}: auto-selected {only.get(label_key, only)}")
        return only
    print(f"\nSelect {prompt}:")
    for idx, option in enumerate(options, start=1):
        label = option.get(label_key, option)
        print(f"  {idx}. {label}")
    print("  0. Skip")
    while True:
        choice = input("Enter choice: ").strip()
        if choice in {"0", ""}:
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            selected = options[int(choice) - 1]
            print(f"Selected {selected.get(label_key, selected)}")
            return selected
        print("Invalid choice, try again.")


def ensure_refresh_token(config: Dict[str, Any]) -> None:
    oauth_section = ensure_nested(config, ["oauth"])
    if oauth_section.get("refresh_token"):
        return
    client_file = oauth_section.get("client_secrets_file")
    if not client_file:
        raise RuntimeError(
            "oauth.client_secrets_file is not set. Provide the path to your OAuth desktop client JSON."
        )
    client_path = Path(str(client_file)).expanduser().resolve()
    if not client_path.exists():
        raise RuntimeError(f"OAuth client file not found at {client_path}")

    print("\nNo refresh token found; launching OAuth consent flow...")
    flow = InstalledAppFlow.from_client_secrets_file(
        str(client_path),
        scopes=[
            "https://www.googleapis.com/auth/tagmanager.edit.containers",
            "https://www.googleapis.com/auth/adwords",
        ],
    )
    creds = flow.run_local_server(port=0, success_message="Authorization complete. You may close this tab.")
    oauth_section["refresh_token"] = creds.refresh_token
    save_config_file(config)
    print("Saved new refresh token to config.")


# ----------------------------- GTM DISCOVERY ----------------------------- #

def discover_gtm(config: Dict[str, Any]) -> None:
    print("\nFetching GTM accounts/containers/workspaces...")
    credentials = utils.user_credentials(
        ["https://www.googleapis.com/auth/tagmanager.readonly"]
    )
    service = build("tagmanager", "v2", credentials=credentials, cache_discovery=False)

    gtm_section = ensure_nested(config, ["gtm"])

    accounts = service.accounts().list().execute().get("account", [])
    selected_account = choose("GTM account", accounts, "path", gtm_section.get("account_id"))
    if not selected_account:
        return

    account_path = selected_account["path"]
    containers = (
        service.accounts()
        .containers()
        .list(parent=account_path)
        .execute()
        .get("container", [])
    )
    selected_container = choose("GTM container", containers, "name", gtm_section.get("container_id"))
    if not selected_container:
        return

    container_path = selected_container["path"]
    workspaces = (
        service.accounts()
        .containers()
        .workspaces()
        .list(parent=container_path)
        .execute()
        .get("workspace", [])
    )
    selected_workspace = choose("GTM workspace", workspaces, "name", gtm_section.get("workspace_id"))
    if not selected_workspace:
        return

    triggers = (
        service.accounts()
        .containers()
        .workspaces()
        .triggers()
        .list(parent=selected_workspace["path"])
        .execute()
        .get("trigger", [])
    )
    selected_trigger = choose(
        "trigger (All Pages)", triggers, "name", gtm_section.get("all_pages_trigger")
    )
    gtm_section["account_id"] = selected_account["accountId"]
    gtm_section["container_id"] = selected_container["containerId"]
    gtm_section["workspace_id"] = selected_workspace["workspaceId"]
    if selected_trigger:
        gtm_section["all_pages_trigger"] = selected_trigger["name"]


# ----------------------------- GA4 DISCOVERY ----------------------------- #

def discover_ga4(config: Dict[str, Any]) -> None:
    print("\nFetching GA4 properties and data streams...")
    credentials = utils.service_account_credentials(
        ["https://www.googleapis.com/auth/analytics.readonly"]
    )
    client = AnalyticsAdminServiceClient(credentials=credentials)

    properties = list(client.list_properties(request={"filter": "ancestor:accounts/-"}))
    options = [{"name": p.display_name, "propertyId": p.name.split("/")[-1], "raw": p} for p in properties]
    ga4_section = ensure_nested(config, ["ga4"])
    selected_property = choose("GA4 property", options, "name", ga4_section.get("property_id"))
    if not selected_property:
        return

    property_id = selected_property["propertyId"]
    streams = list(
        client.list_data_streams(request={"parent": f"properties/{property_id}"})
    )
    web_streams = [
        {
            "name": s.display_name or f"Stream {s.name}",
            "streamId": s.name.split("/")[-1],
            "measurementId": getattr(s.web_stream_data, "measurement_id", ""),
            "raw": s,
        }
        for s in streams
        if s.type_ == DataStream.DataStreamType.WEB_DATA_STREAM
    ]
    selected_stream = choose("GA4 web stream", web_streams, "name", ga4_section.get("data_stream_id"))
    if not selected_stream:
        return

    ga4_section["property_id"] = property_id
    ga4_section["data_stream_id"] = selected_stream["streamId"]
    ga4_section["measurement_id"] = selected_stream["measurementId"]


# ----------------------------- ADS DISCOVERY ----------------------------- #

def discover_ads(config: Dict[str, Any]) -> None:
    print("\nFetching Google Ads accessible customers...")
    developer_token = config.get("ads", {}).get("developer_token")
    if not developer_token:
        print("Skipping Ads discovery (ads.developer_token not set).")
        return
    required = utils.require_values(
        [
            "ads.developer_token",
            "oauth.refresh_token",
        ]
    )
    login_customer = utils.get_value("ads.login_customer_id")
    ads_section = ensure_nested(config, ["ads"])
    ads_config = {
        "developer_token": str(required["ads.developer_token"]),
        "oauth2": {
            "client_id": str(required["oauth.client_id"]),
            "client_secret": str(required["oauth.client_secret"]),
            "refresh_token": str(required["oauth.refresh_token"]),
        },
        "use_proto_plus": True,
    }
    if login_customer:
        ads_config["login_customer_id"] = str(login_customer).replace("-", "")

    client = GoogleAdsClient.load_from_dict(ads_config, version="v17")
    try:
        service = client.get_service("CustomerService")
        resource_names = service.list_accessible_customers().resource_names
        customers = []
        ga_service = client.get_service("GoogleAdsService")
        query = (
            "SELECT customer_client.client_customer, "
            "customer_client.level, customer_client.manager, "
            "customer_client.descriptive_name "
            "FROM customer_client "
            "WHERE customer_client.level <= 1"
        )
        for resource_name in resource_names:
            customer_id = resource_name.split("/")[-1]
            stream = ga_service.search(customer_id=customer_id, query=query)
            for row in stream:
                client_id = row.customer_client.client_customer.split("/")[-1]
                customers.append(
                    {
                        "id": client_id,
                        "manager": row.customer_client.manager,
                        "level": row.customer_client.level,
                        "name": row.customer_client.descriptive_name or client_id,
                    }
                )
    except GoogleAdsException as exc:  # pragma: no cover - depends on live API
        print(f"Google Ads API error: {exc}")
        return

    selected = choose("Google Ads customer", customers, "name", ads_section.get("customer_id"))
    if not selected:
        return

    ads_section["customer_id"] = selected["id"]
    if selected["manager"]:
        ads_section["login_customer_id"] = selected["id"]


# ----------------------------- MAIN ----------------------------- #

def main() -> int:
    config = load_config_file()

    discover_gtm(config)
    discover_ga4(config)
    discover_ads(config)

    save_config_file(config)
    print(f"\nUpdated configuration saved to {CONFIG_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
Automate common Google Tag Manager tasks:
  * ensure a GA4 configuration tag exists and fires on all pages
  * ensure a conversion event tag fires when a given dataLayer event occurs
"""
from __future__ import annotations

import argparse
import sys
from typing import Any, Dict, List, Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

try:
    from . import utils
except ImportError:  # pragma: no cover - allow running as a script
    import utils  # type: ignore

GTM_SCOPE = "https://www.googleapis.com/auth/tagmanager.edit.containers"


def workspace_path(account_id: str, container_id: str, workspace_id: str) -> str:
    return f"accounts/{account_id}/containers/{container_id}/workspaces/{workspace_id}"


def fetch_items(method, parent: str, resource_key: str) -> List[Dict[str, Any]]:
    request = method(parent=parent)
    response = request.execute()
    return response.get(resource_key, [])


def find_by_name(items: List[Dict[str, Any]], name: str) -> Optional[Dict[str, Any]]:
    for item in items:
        if item.get("name") == name:
            return item
    return None


def ensure_custom_event_trigger(service, parent: str, event_name: str) -> str:
    trigger_api = service.accounts().containers().workspaces().triggers()
    triggers = fetch_items(trigger_api.list, parent, "trigger")
    trigger_name = f"Event - {event_name}"
    existing = find_by_name(triggers, trigger_name)
    if existing:
        return existing["triggerId"]

    body = {
        "name": trigger_name,
        "type": "customEvent",
        "customEventFilter": [
            {
                "type": "equals",
                "parameter": [
                    {"type": "template", "key": "arg0", "value": "{{_event}}"},
                    {"type": "template", "key": "arg1", "value": event_name},
                ],
            }
        ],
    }

    created = trigger_api.create(parent=parent, body=body).execute()
    return created["triggerId"]


def ensure_ga4_config_tag(service, parent: str, measurement_id: str, trigger_id: str) -> str:
    tags_api = service.accounts().containers().workspaces().tags()
    tags = fetch_items(tags_api.list, parent, "tag")
    tag_name = f"GA4 - Config {measurement_id}"
    existing = find_by_name(tags, tag_name)
    body = {
        "name": tag_name,
        "type": "gaawe",
        "tagFiringOption": "ONCE_PER_EVENT",
        "firingTriggerId": [trigger_id],
        "parameter": [
            {"type": "template", "key": "measurementId", "value": measurement_id},
            {"type": "boolean", "key": "sendPageView", "value": "true"},
        ],
    }

    if existing:
        tag_id = existing["tagId"]
        tags_api.update(path=f"{parent}/tags/{tag_id}", body=body).execute()
        return tag_id

    created = tags_api.create(parent=parent, body=body).execute()
    return created["tagId"]


def ensure_ga4_event_tag(
    service, parent: str, measurement_id: str, trigger_id: str, event_name: str
) -> str:
    tags_api = service.accounts().containers().workspaces().tags()
    tags = fetch_items(tags_api.list, parent, "tag")
    tag_name = f"GA4 Event - {event_name}"
    existing = find_by_name(tags, tag_name)

    body = {
        "name": tag_name,
        "type": "gaawe",
        "firingTriggerId": [trigger_id],
        "parameter": [
            {"type": "template", "key": "measurementId", "value": measurement_id},
            {"type": "template", "key": "eventName", "value": event_name},
        ],
    }

    if existing:
        tag_id = existing["tagId"]
        tags_api.update(path=f"{parent}/tags/{tag_id}", body=body).execute()
        return tag_id

    created = tags_api.create(parent=parent, body=body).execute()
    return created["tagId"]


def resolve_trigger_id(service, parent: str, trigger_name: str) -> str:
    trigger_api = service.accounts().containers().workspaces().triggers()
    triggers = fetch_items(trigger_api.list, parent, "trigger")
    existing = find_by_name(triggers, trigger_name)
    if not existing:
        raise RuntimeError(
            f"Could not find trigger '{trigger_name}'. "
            "Set GTM_ALL_PAGES_TRIGGER_NAME to match your existing 'All Pages' trigger."
        )
    return existing["triggerId"]


def main(argv: Optional[List[str]] = None) -> int:
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(description="Synchronise Google Tag Manager tags.")
    parser.add_argument(
        "--skip-event",
        action="store_true",
        help="Only ensure the GA4 configuration tag (skip conversion event tag).",
    )
    args = parser.parse_args(argv)

    required = utils.require_values(
        [
            "gtm.account_id",
            "gtm.container_id",
            "gtm.workspace_id",
            "gtm.all_pages_trigger",
            "ga4.measurement_id",
        ]
    )
    conversion_event_name = utils.get_value("gtm.conversion_event")

    credentials = utils.user_credentials([GTM_SCOPE])
    service = build("tagmanager", "v2", credentials=credentials, cache_discovery=False)
    account_id = str(required["gtm.account_id"]).strip()
    container_id = str(required["gtm.container_id"]).strip()
    workspace_id = str(required["gtm.workspace_id"]).strip()
    measurement_id = str(required["ga4.measurement_id"]).strip()
    trigger_name = str(required["gtm.all_pages_trigger"]).strip()

    parent = workspace_path(
        account_id.replace("GTM-", ""),
        container_id.replace("GTM-", ""),
        workspace_id,
    )

    try:
        all_pages_trigger_id = resolve_trigger_id(
            service, parent, trigger_name
        )
        config_tag_id = ensure_ga4_config_tag(service, parent, measurement_id, all_pages_trigger_id)
        print(f"GA4 configuration tag ready (ID: {config_tag_id})")

        if args.skip_event or not conversion_event_name:
            return 0

        event_trigger_id = ensure_custom_event_trigger(
            service, parent, conversion_event_name
        )
        event_tag_id = ensure_ga4_event_tag(
            service, parent, measurement_id, event_trigger_id, conversion_event_name
        )
        print(f"GA4 event tag ready (ID: {event_tag_id})")
        return 0
    except HttpError as exc:
        print(f"GTM API error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
Google Ads automation helper:
  * ensure a conversion action exists for the GA4/GTM conversion event
"""
from __future__ import annotations

import argparse
import sys
from typing import Optional

from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google.ads.googleads.v17.enums.types import (
    ConversionActionCategoryEnum,
    ConversionActionStatusEnum,
    ConversionActionTypeEnum,
)

try:
    from . import utils
except ImportError:  # pragma: no cover - allow running as a script
    import utils  # type: ignore


def build_client() -> GoogleAdsClient:
    required = utils.require_values(
        [
            "ads.developer_token",
            "ads.customer_id",
            "oauth.client_id",
            "oauth.client_secret",
            "oauth.refresh_token",
        ]
    )

    login_id = utils.get_value("ads.login_customer_id")
    login_id_clean = str(login_id).replace("-", "") if login_id else None

    config = {
        "developer_token": str(required["ads.developer_token"]),
        "login_customer_id": login_id_clean,
        "client_customer_id": str(required["ads.customer_id"]).replace("-", ""),
        "use_proto_plus": True,
        "oauth2": {
            "client_id": str(required["oauth.client_id"]),
            "client_secret": str(required["oauth.client_secret"]),
            "refresh_token": str(required["oauth.refresh_token"]),
        },
    }

    return GoogleAdsClient.load_from_dict(config, version="v17")


def find_conversion_action(client: GoogleAdsClient, customer_id: str, name: str):
    ga_service = client.get_service("GoogleAdsService")
    query = (
        "SELECT conversion_action.id, conversion_action.name "
        "FROM conversion_action "
        f"WHERE conversion_action.name = '{name}' "
        "LIMIT 1"
    )
    response = ga_service.search(customer_id=customer_id, query=query)
    for row in response:
        return row.conversion_action
    return None


def ensure_conversion_action(client: GoogleAdsClient, customer_id: str, name: str) -> str:
    existing = find_conversion_action(client, customer_id, name)
    if existing:
        return existing.resource_name

    conversion_action_service = client.get_service("ConversionActionService")
    operation = client.get_type("ConversionActionOperation")
    action = operation.create
    action.name = name
    action.type_ = ConversionActionTypeEnum.ConversionActionType.WEBPAGE
    action.category = ConversionActionCategoryEnum.ConversionActionCategory.LEAD
    action.status = ConversionActionStatusEnum.ConversionActionStatus.ENABLED
    action.primary_for_goal = True
    action.include_in_conversions_metric = True

    response = conversion_action_service.mutate_conversion_actions(
        customer_id=customer_id, operations=[operation]
    )
    return response.results[0].resource_name


def main(argv: Optional[list[str]] = None) -> int:
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(description="Configure Google Ads conversion actions.")
    parser.add_argument(
        "--name",
        default="Book appointment conversion",
        help="Conversion action name to ensure exists.",
    )
    args = parser.parse_args(argv)

    client = build_client()
    customer_id = str(utils.require_values(["ads.customer_id"])["ads.customer_id"]).replace("-", "")

    try:
        resource = ensure_conversion_action(client, customer_id, args.name)
        print(f"Google Ads conversion action ready: {resource}")
        return 0
    except GoogleAdsException as exc:
        print(f"Google Ads API error ({exc.error.code().name}): {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

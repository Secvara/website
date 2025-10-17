#!/usr/bin/env python3
"""
Google Analytics 4 automation helpers:
  * ensure an event is marked as a conversion
  * optionally create a Measurement Protocol secret for server-side events
"""
from __future__ import annotations

import argparse
import sys
from typing import Optional

from google.analytics.admin_v1beta import AnalyticsAdminServiceClient
from google.analytics.admin_v1beta.types import ConversionEvent, MeasurementProtocolSecret
from google.api_core.exceptions import AlreadyExists

try:
    from . import utils
except ImportError:  # pragma: no cover - allow running as a script
    import utils  # type: ignore

GA_SCOPE = "https://www.googleapis.com/auth/analytics.edit"


def ensure_conversion_event(
    client: AnalyticsAdminServiceClient, property_id: str, event_name: str
) -> str:
    parent = f"properties/{property_id}"
    existing = client.list_conversion_events(request={"parent": parent})
    for event in existing:
        if event.event_name == event_name:
            return event.name

    created = client.create_conversion_event(
        request={
            "parent": parent,
            "conversion_event": ConversionEvent(event_name=event_name),
        }
    )
    return created.name


def ensure_measurement_protocol_secret(
    client: AnalyticsAdminServiceClient, property_id: str, data_stream_id: str, display_name: str
) -> str:
    parent = f"properties/{property_id}/dataStreams/{data_stream_id}"
    secret = MeasurementProtocolSecret(display_name=display_name)
    try:
        created = client.create_measurement_protocol_secret(
            request={"parent": parent, "measurement_protocol_secret": secret}
        )
        return created.name
    except AlreadyExists:
        # Fetch existing secrets and reuse the first match.
        secrets = client.list_measurement_protocol_secrets(request={"parent": parent})
        for item in secrets:
            if item.display_name == display_name:
                return item.name
        raise


def main(argv: Optional[list[str]] = None) -> int:
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser(description="Configure GA4 property automation.")
    parser.add_argument(
        "--event",
        default=str(utils.get_value("gtm.conversion_event") or "book_appointment_conversion"),
        help="Event name to mark as a conversion.",
    )
    parser.add_argument(
        "--secret-name",
        help="If provided, create (or reuse) a Measurement Protocol secret with this display name.",
    )
    args = parser.parse_args(argv)

    property_id = str(utils.require_values(["ga4.property_id"])["ga4.property_id"])
    data_stream_id = utils.get_value("ga4.data_stream_id")

    credentials = utils.service_account_credentials([GA_SCOPE])
    client = AnalyticsAdminServiceClient(credentials=credentials)

    try:
        conversion_resource = ensure_conversion_event(client, property_id, args.event)
        print(f"Conversion event ensured: {conversion_resource}")

        if args.secret_name:
            if not data_stream_id:
                raise RuntimeError(
                    "GA_DATA_STREAM_ID is required to create a Measurement Protocol secret."
                )

            secret_resource = ensure_measurement_protocol_secret(
                client, property_id, str(data_stream_id), args.secret_name
            )
            print(f"Measurement Protocol secret ready: {secret_resource}")
        return 0
    except Exception as exc:  # noqa: BLE001
        print(f"GA4 setup error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

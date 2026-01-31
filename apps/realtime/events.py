import json

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def publish_calendar_event(evt, event_type: str):
    """
    Push calendar event changes to all subscribers of the plan.
    """
    channel_layer = get_channel_layer()
    plan_id = evt.placement.campaign.plan_id

    payload = {
        "type": "CALENDAR_EVENT",
        "eventType": event_type,
        "planId": plan_id,
        "event": {
            "id": evt.id,
            "title": evt.title,
            "startTs": evt.start_ts.isoformat(),
            "endTs": evt.end_ts.isoformat(),
            "status": evt.status,
            "updatedAt": evt.updated_at.isoformat(),
            "placement": {
                "id": evt.placement_id,
                "page": evt.placement.page,
                "section": evt.placement.section,
                "slot": evt.placement.slot,
            },
        },
    }

    async_to_sync(channel_layer.group_send)(
        f"plan_{plan_id}",
        {"type": "broadcast.message", "text": json.dumps(payload)},
    )

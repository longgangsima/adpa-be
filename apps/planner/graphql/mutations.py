from datetime import datetime

import strawberry
from django.utils.timezone import now

from apps.planner.models import CalendarEvent, Placement, MediaPlan
from apps.realtime.events import publish_calendar_event

from .types import CalendarEventType, MediaPlanType


def require_user(info: strawberry.Info):
    """Ensure the request has an authenticated user."""
    request = getattr(info.context, "request", None)
    if isinstance(info.context, dict):
        request = request or info.context.get("request")
    user = getattr(request, "user", None) if request else None
    if not user or not user.is_authenticated:
        raise Exception("Unauthorized")
    return user


@strawberry.input
class CreateEventInput:
    placement_id: strawberry.ID
    title: str
    start_ts: datetime
    end_ts: datetime


@strawberry.input
class UpdateEventInput:
    event_id: strawberry.ID
    title: str | None = None
    start_ts: datetime | None = None
    end_ts: datetime | None = None
    status: str | None = None


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_media_plan(self, info: strawberry.Info, name: str) -> MediaPlanType:
        user = require_user(info)
        plan = MediaPlan.objects.create(name=name, owner=user)
        return plan

    @strawberry.mutation
    def create_calendar_event(
        self, info: strawberry.Info, data: CreateEventInput
    ) -> CalendarEventType:
        user = require_user(info)

        placement = Placement.objects.get(id=data.placement_id)

        if data.start_ts >= data.end_ts:
            raise Exception("start_ts must be before end_ts")

        evt = CalendarEvent.objects.create(
            placement=placement,
            title=data.title,
            start_ts=data.start_ts,
            end_ts=data.end_ts,
            status=CalendarEvent.Status.BOOKED,
            last_updated_by=user,
        )

        publish_calendar_event(evt, event_type="CREATED")
        return evt

    @strawberry.mutation
    def update_calendar_event(
        self, info: strawberry.Info, data: UpdateEventInput
    ) -> CalendarEventType:
        user = require_user(info)

        evt = CalendarEvent.objects.select_related(
            "placement__campaign__plan"
        ).get(id=data.event_id)

        if data.title is not None:
            evt.title = data.title
        if data.start_ts is not None:
            evt.start_ts = data.start_ts
        if data.end_ts is not None:
            evt.end_ts = data.end_ts
        if data.status is not None:
            evt.status = data.status

        if evt.start_ts >= evt.end_ts:
            raise Exception("start_ts must be before end_ts")

        evt.last_updated_by = user
        evt.updated_at = now()
        evt.save(update_fields=["title", "start_ts", "end_ts", "status", "last_updated_by", "updated_at"])

        publish_calendar_event(evt, event_type="UPDATED")
        return evt

    @strawberry.mutation
    def cancel_calendar_event(
        self, info: strawberry.Info, event_id: strawberry.ID
    ) -> CalendarEventType:
        user = require_user(info)

        evt = CalendarEvent.objects.get(id=event_id)
        evt.status = CalendarEvent.Status.CANCELED
        evt.last_updated_by = user
        evt.save(update_fields=["status", "last_updated_by", "updated_at"])

        publish_calendar_event(evt, event_type="CANCELED")
        return evt

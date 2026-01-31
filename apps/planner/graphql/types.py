import strawberry
from strawberry_django import type as django_type

from apps.planner.models import MediaPlan, Campaign, Placement, CalendarEvent


@django_type(MediaPlan)
class MediaPlanType:
    id: strawberry.auto
    name: strawberry.auto
    created_at: strawberry.auto


@django_type(Campaign)
class CampaignType:
    id: strawberry.auto
    name: strawberry.auto
    start_date: strawberry.auto
    end_date: strawberry.auto
    plan: "MediaPlanType"


@django_type(Placement)
class PlacementType:
    id: strawberry.auto
    page: strawberry.auto
    section: strawberry.auto
    slot: strawberry.auto
    campaign: CampaignType


@django_type(CalendarEvent)
class CalendarEventType:
    id: strawberry.auto
    title: strawberry.auto
    start_ts: strawberry.auto
    end_ts: strawberry.auto
    status: strawberry.auto
    updated_at: strawberry.auto
    placement: PlacementType

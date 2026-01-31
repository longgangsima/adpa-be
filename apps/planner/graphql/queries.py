from datetime import datetime
from typing import List, Optional

import strawberry
from django.db.models import Q

from apps.planner.models import CalendarEvent

from .types import CalendarEventType


@strawberry.type
class Query:
    @strawberry.field
    def calendar_events(
        self,
        info: strawberry.Info,
        start: datetime,
        end: datetime,
        plan_id: Optional[int] = None,
        status: Optional[str] = None,
        page: Optional[str] = None,
        section: Optional[str] = None,
    ) -> List[CalendarEventType]:
        """Query calendar events overlapping the given time range."""
        qs = (
            CalendarEvent.objects.select_related("placement__campaign__plan")
            .filter(
                Q(start_ts__lt=end) & Q(end_ts__gt=start),
            )
        )

        if plan_id is not None:
            qs = qs.filter(placement__campaign__plan_id=plan_id)
        if status is not None:
            qs = qs.filter(status=status)
        if page is not None:
            qs = qs.filter(placement__page=page)
        if section is not None:
            qs = qs.filter(placement__section=section)

        return list(qs.order_by("start_ts"))

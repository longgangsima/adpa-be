from django.conf import settings
from django.db import models


class MediaPlan(models.Model):
    """Top-level media plan containing campaigns."""

    name = models.CharField(max_length=200)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Campaign(models.Model):
    """Campaign within a media plan."""

    plan = models.ForeignKey(MediaPlan, on_delete=models.CASCADE, related_name="campaigns")
    name = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name


class Placement(models.Model):
    """
    Where an ad appears: page/section/slot, etc.
    """

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="placements")
    page = models.CharField(max_length=120)  # e.g. "Home"
    section = models.CharField(max_length=120)  # e.g. "Hero Banner"
    slot = models.CharField(max_length=120)  # e.g. "Slot A"
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.page} / {self.section}"


class CalendarEvent(models.Model):
    """
    One booked item on the calendar (what users actually view).
    """

    class Status(models.TextChoices):
        BOOKED = "BOOKED"
        CANCELED = "CANCELED"

    placement = models.ForeignKey(Placement, on_delete=models.CASCADE, related_name="events")
    title = models.CharField(max_length=200)
    start_ts = models.DateTimeField()
    end_ts = models.DateTimeField()
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.BOOKED
    )
    last_updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["start_ts"]),
            models.Index(fields=["end_ts"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return self.title

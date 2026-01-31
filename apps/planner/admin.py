from django.contrib import admin
from .models import MediaPlan, Campaign, Placement, CalendarEvent


@admin.register(MediaPlan)
class MediaPlanAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "created_at")


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("name", "plan", "start_date", "end_date")


@admin.register(Placement)
class PlacementAdmin(admin.ModelAdmin):
    list_display = ("page", "section", "slot", "campaign")


@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ("title", "placement", "start_ts", "end_ts", "status")

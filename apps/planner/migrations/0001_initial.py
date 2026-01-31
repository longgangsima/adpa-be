from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="MediaPlan",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=models.PROTECT, to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Campaign",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                (
                    "plan",
                    models.ForeignKey(
                        on_delete=models.CASCADE,
                        related_name="campaigns",
                        to="planner.mediaplan",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Placement",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("page", models.CharField(max_length=120)),
                ("section", models.CharField(max_length=120)),
                ("slot", models.CharField(max_length=120)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "campaign",
                    models.ForeignKey(
                        on_delete=models.CASCADE,
                        related_name="placements",
                        to="planner.campaign",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="CalendarEvent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=200)),
                ("start_ts", models.DateTimeField()),
                ("end_ts", models.DateTimeField()),
                (
                    "status",
                    models.CharField(
                        choices=[("BOOKED", "Booked"), ("CANCELED", "Canceled")],
                        default="BOOKED",
                        max_length=20,
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "last_updated_by",
                    models.ForeignKey(
                        on_delete=models.PROTECT, to=settings.AUTH_USER_MODEL
                    ),
                ),
                (
                    "placement",
                    models.ForeignKey(
                        on_delete=models.CASCADE,
                        related_name="events",
                        to="planner.placement",
                    ),
                ),
            ],
        ),
        migrations.AddIndex(
            model_name="calendarevent",
            index=models.Index(fields=["start_ts"], name="planner_ce_start_ts_idx"),
        ),
        migrations.AddIndex(
            model_name="calendarevent",
            index=models.Index(fields=["end_ts"], name="planner_ce_end_ts_idx"),
        ),
        migrations.AddIndex(
            model_name="calendarevent",
            index=models.Index(fields=["status"], name="planner_ce_status_idx"),
        ),
    ]

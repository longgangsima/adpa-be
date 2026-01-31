import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Extended user model. Extend later: role, org, etc."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    pass

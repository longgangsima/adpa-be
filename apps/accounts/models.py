from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Extended user model. Extend later: role, org, etc."""

    pass

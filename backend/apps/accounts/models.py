from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom user skeleton for the hotel reservation system.

    Additional fields (role, phone, email_verified) will be added in task P1-03.
    """

    pass

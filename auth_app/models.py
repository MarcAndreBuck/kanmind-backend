from django.contrib.auth.models import User
from django.db import models


class UserProfile(models.Model):
    """
    Represents additional user profile information.

    Extends the default User model with a fullname field.
    Used to store and manage user-specific profile data.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    fullname = models.CharField(max_length=100)

    def __str__(self):
        """Return the full name of the user as string representation.

        This method provides a human-readable representation of the UserProfile instance.
        It uses the fullname field for display purposes.
        """
        return self.fullname
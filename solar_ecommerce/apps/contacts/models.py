from django.db import models

from apps.base import TimeStampedModel


class ContactMessage(TimeStampedModel):
    """Customer enquiry / support message."""

    class Status(models.TextChoices):
        NEW = 'new', 'New'
        IN_PROGRESS = 'in_progress', 'In Progress'
        RESOLVED = 'resolved', 'Resolved'

    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, default='')
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.NEW, db_index=True)
    admin_notes = models.TextField(blank=True, default='')

    class Meta(TimeStampedModel.Meta):
        pass

    def __str__(self):
        return f'{self.subject} – {self.email}'


class NewsletterSubscriber(TimeStampedModel):
    """Email newsletter subscription."""

    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)

    class Meta(TimeStampedModel.Meta):
        pass

    def __str__(self):
        return self.email
